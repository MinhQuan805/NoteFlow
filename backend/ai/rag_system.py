import os
import yaml
import json
import pickle
import warnings
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.storage import InMemoryStore
from langchain.retrievers import ParentDocumentRetriever

try:
    import ai.parser as parser
    from ai.rag_modules import IntentClassifier, LLMClient, VectorDBClient
except ModuleNotFoundError:
    import parser
    from rag_modules import IntentClassifier, LLMClient, VectorDBClient

@dataclass
class Config:
    token_threshold: int  # Switch to RAG mode if tokens exceed this
    chunk_size: int
    chunk_overlap: int
    llm_model_name: str
    llm_api_key_env: str
    llm_config: dict  # Full LLM config for provider switching
    embedding_model_name: str
    embedding_device: str
    retrieval_k: int
    parsing_api_key_env: str

    @classmethod
    def load(cls, path: str = "config.yaml"):
        with open(path, "r") as f:
            config_data = yaml.safe_load(f)
        return cls(
            token_threshold=config_data["system"]["token_threshold"],
            chunk_size=config_data["system"]["chunk_size"],
            chunk_overlap=config_data["system"]["chunk_overlap"],
            llm_model_name=config_data["llm"]["model_name"],
            llm_api_key_env=config_data["llm"]["api_key_env"],
            llm_config=config_data["llm"],  # Store full LLM config
            embedding_model_name=config_data["embedding"]["model_name"],
            embedding_device=config_data["embedding"]["device"],
            retrieval_k=config_data["retrieval"]["k"],
            parsing_api_key_env=config_data["parsing"]["api_key_env"]
        )

class RAGSystem:
    def __init__(self, config_path: str = "config.yaml", notebook_id: str = None):
        self.config = Config.load(config_path)
        self.notebook_id = notebook_id
        self._setup_environment()
        
        self.intent_classifier = IntentClassifier()
        self.llm_client = LLMClient(self.config.llm_model_name, self.config.llm_api_key_env, self.config.llm_config)
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.config.embedding_model_name,
            model_kwargs={'device': self.config.embedding_device}
        )
        
        # Per-notebook data isolation
        if notebook_id:
            self.data_dir = os.path.join("data", notebook_id)
        else:
            self.data_dir = os.path.join("data", "default")
            
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.index_path = os.path.join(self.data_dir, "faiss_index")
        self.vector_db_client = VectorDBClient(
            index_path=self.index_path,
            embedding_function=self.embeddings
        )
        self.vectorstore = self.vector_db_client.vectorstore
        
        self.docstore = InMemoryStore() # For Parent Document Retrieval
        
        self.child_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap
        )

        self.parent_retriever = ParentDocumentRetriever(
            vectorstore=self.vectorstore,
            docstore=self.docstore,
            child_splitter=self.child_splitter,
            # parent_splitter=None, # We will feed parent documents directly
        )
        
        self.bm25_retriever = None # Initialized after ingestion
        self.ensemble_retriever = None
        
        self.total_tokens = 0
        self.all_documents = [] 
        self.docs_path = os.path.join(self.data_dir, "documents.pkl")
        
        self._load_state()
        if self.all_documents:
            self.bm25_retriever = BM25Retriever.from_documents(self.all_documents)
            self.bm25_retriever.k = self.config.retrieval_k
            
            # Initialize Ensemble if we have both
            self.ensemble_retriever = EnsembleRetriever(
                retrievers=[self.parent_retriever, self.bm25_retriever],
                weights=[0.5, 0.5]
            )
        else:
            self.bm25_retriever = None
            self.ensemble_retriever = None

    def _save_state(self):
        state = {
            "documents": self.all_documents,
            "total_tokens": self.total_tokens
        }
        with open(self.docs_path, "wb") as f:
            pickle.dump(state, f)
        print(f"State saved to {self.docs_path}")

    def _load_state(self):
        if os.path.exists(self.docs_path):
            try:
                with open(self.docs_path, "rb") as f:
                    state = pickle.load(f)
                self.all_documents = state.get("documents", [])
                self.total_tokens = state.get("total_tokens", 0)
                print(f"Loaded {len(self.all_documents)} documents from {self.docs_path}")
            except Exception as e:
                print(f"Error loading state: {e}")
                self.all_documents = []
                self.total_tokens = 0

    def list_ingested_files(self) -> List[str]:
        """Return a list of unique source files ingested"""
        sources = set()
        for doc in self.all_documents:
            sources.add(doc.metadata.get("source", "Unknown"))
        return sorted(list(sources))

    def _setup_environment(self):
        if not os.environ.get(self.config.parsing_api_key_env):
            print(f"Warning: {self.config.parsing_api_key_env} not set.")
        if not os.environ.get(self.config.llm_api_key_env):
            print(f"Warning: {self.config.llm_api_key_env} not set.")

    def ingest(self, file_paths: List[str], source_names: Dict[str, str] = None):
        """
        Ingest files into the RAG system.
        
        Args:
            file_paths: List of file paths to ingest
            source_names: Optional dict mapping file_path -> custom source name
                         Used for Discover sources to store page title instead of path
        """
        print(f"Starting ingestion for {len(file_paths)} files...")
        
        results = parser.parse_multiple_paths_parallel(file_paths)
        
        new_documents = []
        
        for path, (data, tokens, all_text) in results.items():
            if isinstance(data, str) and data.startswith("Error"):
                print(f"Skipping {path}: {data}")
                continue
                
            self.total_tokens += tokens
            try:
                pages = data.pages
            except AttributeError:
                if isinstance(data, dict) and "pages" in data:
                    pages = data["pages"]
                else:
                    pages = [{"text": all_text, "page_number": 1}]
            
            # Use custom source name if provided, otherwise use file path
            source_name = source_names.get(path, path) if source_names else path
            
            for i, page in enumerate(pages):
                page_text = ""
                if hasattr(page, "text"):
                    page_text = parser.remove_footer(page.text)
                elif isinstance(page, dict):
                    page_text = parser.remove_footer(page.get("text", ""))
                
                if page_text.strip():
                    doc = Document(
                        page_content=page_text,
                        metadata={"source": source_name, "page": i + 1}
                    )
                    new_documents.append(doc)
        
        if not new_documents:
            print("No new documents to ingest.")
            return

        self.all_documents.extend(new_documents)
        
        self.parent_retriever.add_documents(new_documents)
        
        self.vector_db_client.save()
        
        self.bm25_retriever = BM25Retriever.from_documents(self.all_documents)
        self.bm25_retriever.k = self.config.retrieval_k
        
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[self.parent_retriever, self.bm25_retriever],
            weights=[0.5, 0.5] # Equal weight
        )
        
        self._save_state()
        
        print(f"Ingestion complete. Total estimated tokens: {self.total_tokens}")

    def query(self, user_query: str, file_filters: List[str] = None) -> str:
        # 1. Check Intent
        intent = self.intent_classifier.predict(user_query)
        print(f"Detected Intent: {intent}")
        
        if intent == "Hardcoded_Chat":
            return "Hi! How can you help you today? Need help with your documents?"
        
        if intent == "ML_Chat":
            return self.llm_client.invoke(user_query).content

        if file_filters:
            filtered_docs = self._get_filtered_docs(file_filters)
            current_tokens = int(sum(len(doc.page_content) / 4 for doc in filtered_docs))
        else:
            current_tokens = self.total_tokens
            filtered_docs = self.all_documents

        MAX_WINDOW = 1000000 
        threshold = self.config.token_threshold  # Use direct threshold from config
        
        print(f"Current tokens (filtered): {current_tokens}, Threshold: {threshold}")
        
        if current_tokens < threshold:
            print("Mode: Full Context")
            return self._query_full_context(user_query, filtered_docs)
        else:
            print("Mode: RAG (Hybrid)")
            return self._query_rag(user_query, file_filters)

    def _get_filtered_docs(self, file_filters: List[str]) -> List[Document]:
        filtered = []
        # Debug: show what sources are being checked
        all_sources = set(doc.metadata.get("source", "") for doc in self.all_documents)
        print(f"[DEBUG] All available sources: {list(all_sources)}")
        print(f"[DEBUG] File filters requested: {file_filters}")
        
        for doc in self.all_documents:
            source = doc.metadata.get("source", "")
            # Get basename of source for comparison (handles uploads\file.pdf vs file.pdf)
            source_basename = os.path.basename(source) if os.path.sep in source or '/' in source else source
            
            # Match if:
            # 1. Exact match (source == filter)
            # 2. Source ends with filter (uploads\file.pdf ends with file.pdf)
            # 3. Source basename equals filter (file.pdf == file.pdf)
            # 4. Filter equals source (for Discover sources which use titles)
            if (source in file_filters or 
                any(source.endswith(f) or source_basename == f or f == source for f in file_filters)):
                filtered.append(doc)
        
        print(f"[DEBUG] Filtered docs count: {len(filtered)} / {len(self.all_documents)}")
        return filtered
    
    def _save_debug_response(self, response_text: str, query: str):
        """Save raw LLM response to debug folder for troubleshooting"""
        import datetime
        
        # Create debug folder outside backend
        debug_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "debug")
        os.makedirs(debug_folder, exist_ok=True)
        
        # Create filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"llm_response_{timestamp}.txt"
        filepath = os.path.join(debug_folder, filename)
        
        # Save with query and response
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"=" * 60 + "\n")
            f.write(f"QUERY: {query}\n")
            f.write(f"=" * 60 + "\n\n")
            f.write(response_text)
        
        print(f"[DEBUG] Saved LLM response to: {filepath}")

    def _query_full_context(self, user_query: str, docs: List[Document]) -> str:
        context = ""
        for doc in docs:
            source = os.path.basename(doc.metadata.get("source", "unknown"))
            page = doc.metadata.get("page", "unknown")
            context += f"--- Source: {source}, Page: {page} ---\n{doc.page_content}\n\n"
        
        prompt = f"""
        You are a helpful assistant. Answer the user's question based on the following context.
        Always cite your sources using the format [Source: filename, Page: number].

        
        Context:
        {context}
        
        Question: {user_query}
        """
        
        response = self.llm_client.invoke(prompt)
        response_text = response.content
        
        # Save debug output
        self._save_debug_response(response_text, user_query)
        
        return response_text

    def _query_rag(self, user_query: str, file_filters: List[str] = None) -> str:
        if not self.ensemble_retriever:
            return "Error: No documents indexed."
            
        docs = self.ensemble_retriever.invoke(user_query)
        
        if file_filters:
            filtered_docs = []
            for doc in docs:
                source = doc.metadata.get("source", "")
                if any(f in source for f in file_filters):
                    filtered_docs.append(doc)
            docs = filtered_docs
            
        if not docs:
            return "No relevant documents found in the selected files."
        
        context = ""
        for doc in docs:
            source = os.path.basename(doc.metadata.get("source", "unknown"))
            page = doc.metadata.get("page", "unknown")
            context += f"--- Source: {source}, Page: {page} ---\n{doc.page_content}\n\n"
        
        prompt = f"""
        You are a helpful assistant. Answer the user's question based on the following retrieved context.
        Always cite your sources using the format [Source: filename, Page: number].
        
        Context:
        {context}
        
        Question: {user_query}
        """
        
        response = self.llm_client.invoke(prompt)
        response_text = response.content
        
        # Save debug output
        self._save_debug_response(response_text, user_query)
        
        return response_text

    def debug_retrieval(self, user_query: str):
        """Debug retrieval performance by showing vector and BM25 results"""
        print(f"\n{'='*60}")
        print(f"DEBUG RETRIEVAL: '{user_query}'")
        
        intent = self.intent_classifier.predict(user_query)
        print(f"Detected Intent: {intent}")
        
        if intent in ["Hardcoded_Chat", "ML_Chat"]:
            print("Intent is Chat. Skipping retrieval debug output.")
            print(f"{'='*60}")
            return

        print(f"{'='*60}")
        
        print("\n[Vector Search Results]")
        print("-" * 60)
        try:
            vector_results = self.vectorstore.similarity_search_with_score(user_query, k=self.config.retrieval_k)
            for i, (doc, score) in enumerate(vector_results):
                source = os.path.basename(doc.metadata.get("source", "unknown"))
                page = doc.metadata.get("page", "unknown")
                print(f"\n{i+1}. L2 Distance: {score:.4f}")
                print(f"   Source: {source} | Page: {page}")
                print(f"   Content: {doc.page_content[:150]}...")
        except Exception as e:
            print(f"Error during vector search: {e}")

        print("\n\n[BM25 Search Results]")
        print("-" * 60)
        if self.bm25_retriever:
            try:
                bm25_results = self.bm25_retriever.invoke(user_query)
                for i, doc in enumerate(bm25_results):
                    source = os.path.basename(doc.metadata.get("source", "unknown"))
                    page = doc.metadata.get("page", "unknown")
                    print(f"\n{i+1}. Source: {source} | Page: {page}")
                    print(f"   Content: {doc.page_content[:150]}...")
            except Exception as e:
                print(f"Error during BM25 search: {e}")
        else:
            print("BM25 Retriever not initialized.")
        
        print("\n\n[Ensemble (Combined) Results]")
        print("-" * 60)
        if self.ensemble_retriever:
            try:
                ensemble_results = self.ensemble_retriever.invoke(user_query)
                for i, doc in enumerate(ensemble_results):
                    source = os.path.basename(doc.metadata.get("source", "unknown"))
                    page = doc.metadata.get("page", "unknown")
                    print(f"\n{i+1}. Source: {source} | Page: {page}")
                    print(f"   Content: {doc.page_content[:150]}...")
            except Exception as e:
                print(f"Error during ensemble search: {e}")
        
        print(f"\n{'='*60}\n")

    def generate_slides_html(self, user_query: str, file_filters: List[str] = None) -> str:
        """
        Multi-phase slide generation:
        Phase 1: Generate presentation plan/outline (1 LLM call)
        Phase 2: Generate slides in batches (N LLM calls, 4 sections per batch)
        Phase 3: Assemble final HTML
        """
        print(f"\n{'='*60}")
        print(f"[SLIDES] Starting multi-phase slide generation")
        print(f"[SLIDES] Query: {user_query}")
        print(f"[SLIDES] File filters: {file_filters}")
        print(f"{'='*60}")
        
        # Hard limit: exactly 1 document
        if file_filters and len(file_filters) > 1:
            print(f"[SLIDES] ERROR: Too many documents selected ({len(file_filters)}). Exactly 1 allowed.")
            return "<html><body style='display:flex;justify-content:center;align-items:center;height:100vh;font-family:sans-serif;'><h1 style='color:#e53e3e;'>Error: Please select exactly 1 document for slide generation</h1></body></html>"
        
        if not self.all_documents:
            print(f"[SLIDES] ERROR: No documents indexed")
            return "<html><body><h1>Error: No documents indexed.</h1></body></html>"
        
        # Get FULL context from filtered docs (no RAG retrieval, use all content)
        if file_filters:
            filtered_docs = self._get_filtered_docs(file_filters)
        else:
            filtered_docs = self.all_documents
        
        if not filtered_docs:
            print(f"[SLIDES] ERROR: No documents after filtering")
            return "<html><body><h1>No relevant documents found.</h1></body></html>"
        
        # Build full context
        context = "\n\n".join(doc.page_content for doc in filtered_docs)
        print(f"[SLIDES] Context length: {len(context)} chars from {len(filtered_docs)} docs")
        
        # ============ PHASE 1: PLANNING ============
        print(f"\n[SLIDES] ===== PHASE 1: PLANNING =====")
        plan = self._generate_slide_plan(user_query, context)
        
        if not plan or "sections" not in plan:
            print(f"[SLIDES] ERROR: Failed to generate plan")
            # Fallback to old single-shot method
            return self._generate_slides_single_shot(user_query, context)
        
        sections = plan.get("sections", [])
        title = plan.get("title", user_query)
        print(f"[SLIDES] Plan generated: {len(sections)} sections")
        for i, section in enumerate(sections):
            print(f"[SLIDES]   {i+1}. {section}")
        
        # ============ PHASE 2: BATCHED GENERATION ============
        print(f"\n[SLIDES] ===== PHASE 2: BATCHED GENERATION =====")
        BATCH_SIZE = 4  # 4 sections per API call
        all_slides_html = []
        
        for batch_idx in range(0, len(sections), BATCH_SIZE):
            batch = sections[batch_idx : batch_idx + BATCH_SIZE]
            batch_num = (batch_idx // BATCH_SIZE) + 1
            total_batches = (len(sections) + BATCH_SIZE - 1) // BATCH_SIZE
            
            print(f"[SLIDES] Generating batch {batch_num}/{total_batches}: {batch}")
            
            batch_html = self._generate_batch_slides(batch, context, batch_num)
            all_slides_html.append(batch_html)
            print(f"[SLIDES] Batch {batch_num} complete: {len(batch_html)} chars")
        
        # ============ PHASE 3: ASSEMBLY ============
        print(f"\n[SLIDES] ===== PHASE 3: ASSEMBLY =====")
        final_html = self._assemble_presentation(title, sections, all_slides_html)
        print(f"[SLIDES] Final HTML length: {len(final_html)} chars")
        print(f"[SLIDES] Generation complete!")
        print(f"{'='*60}\n")
        
        return final_html
    
    def _generate_slide_plan(self, query: str, context: str) -> dict:
        """Phase 1: Generate presentation outline (1 LLM call)"""
        import json
        import re
        
        prompt = f"""You are a presentation planner. Create a detailed outline for a presentation.

Topic: {query}

Document content:
{context[:15000]}

Create a JSON outline with 8-12 sections that cover the key topics comprehensively.
Return ONLY valid JSON in this format (no markdown, no extra text):
{{"title": "Presentation Title", "sections": ["Section 1 Title", "Section 2 Title", ...]}}

Example:
{{"title": "Machine Learning Fundamentals", "sections": ["Introduction to ML", "Supervised Learning", "Unsupervised Learning", "Neural Networks", "Applications"]}}
"""
        
        print(f"[PLAN] Sending planning prompt ({len(prompt)} chars)")
        
        try:
            response = self.llm_client.invoke(prompt)
            raw_response = response.content.strip()
            print(f"[PLAN] Raw response: {raw_response[:500]}...")
            
            # Clean up response - remove markdown code blocks if present
            raw_response = raw_response.replace("```json", "").replace("```", "").strip()
            
            # Try to extract JSON
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
                print(f"[PLAN] Parsed successfully: {len(plan.get('sections', []))} sections")
                return plan
            else:
                print(f"[PLAN] ERROR: Could not find JSON in response")
                return None
                
        except json.JSONDecodeError as e:
            print(f"[PLAN] ERROR: JSON parse failed: {e}")
            return None
        except Exception as e:
            print(f"[PLAN] ERROR: {e}")
            return None
    
    def _generate_batch_slides(self, sections: List[str], context: str, batch_num: int) -> str:
        """Phase 2: Generate slides for a batch of sections (1 LLM call per batch)"""
        
        sections_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(sections))
        
        prompt = f"""Generate HTML slides for the following sections of a presentation.

Sections to cover:
{sections_text}

Document context:
{context[:12000]}

For each section, create 2-3 slides with:
- Clear heading (h2)
- 4-6 bullet points maximum
- Mathematical formulas using $...$ for inline and $$...$$ for display

Return ONLY the slide HTML divs (no DOCTYPE, html, head, body tags):
<div class="slide">
    <h2>Section Title</h2>
    <ul>
        <li>Point 1</li>
        <li>Point 2</li>
    </ul>
</div>
<div class="slide">
    ...next slide...
</div>

IMPORTANT: Return ONLY <div class="slide">...</div> elements. No other HTML structure.
"""
        
        print(f"[BATCH {batch_num}] Sending prompt ({len(prompt)} chars)")
        
        try:
            response = self.llm_client.invoke(prompt)
            html = response.content.strip()
            
            # Clean up markdown if present
            html = html.replace("```html", "").replace("```", "").strip()
            
            print(f"[BATCH {batch_num}] Generated {html.count('<div class=\"slide\">')} slides")
            return html
            
        except Exception as e:
            print(f"[BATCH {batch_num}] ERROR: {e}")
            return f'<div class="slide"><h2>Error generating slides for batch {batch_num}</h2><p>{str(e)}</p></div>'
    
    def _assemble_presentation(self, title: str, sections: List[str], slides_html: List[str]) -> str:
        """Phase 3: Assemble all slides into final HTML document"""
        
        # Create title slide
        title_slide = f'''<div class="slide active">
        <h1>{title}</h1>
        <p class="author">Generated Presentation</p>
    </div>'''
        
        # Create outline slide
        outline_items = "\n".join(f"<li>{s}</li>" for s in sections)
        outline_slide = f'''<div class="slide">
        <h2>Outline</h2>
        <ul>{outline_items}</ul>
    </div>'''
        
        # Combine all batch slides
        all_content_slides = "\n".join(slides_html)
        
        # Create summary slide
        summary_slide = f'''<div class="slide">
        <h2>Summary</h2>
        <div class="summary">
            <p>This presentation covered {len(sections)} key topics about {title}.</p>
        </div>
    </div>'''
        
        # Full HTML with CSS
        full_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .slide {{
            display: none;
            min-height: 100vh;
            padding: 80px 100px;
            box-sizing: border-box;
            background: white;
        }}
        .slide.active {{
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        h1 {{
            color: #2d3748;
            font-size: 4.5em;
            margin-bottom: 30px;
            text-align: center;
            line-height: 1.2;
        }}
        h2 {{
            color: #4a5568;
            font-size: 3em;
            margin-bottom: 40px;
            border-bottom: 4px solid #667eea;
            padding-bottom: 15px;
        }}
        h3 {{
            color: #718096;
            font-size: 2em;
            margin-bottom: 25px;
        }}
        p {{
            font-size: 1.8em;
            line-height: 1.6;
            color: #2d3748;
            margin-bottom: 25px;
        }}
        ul {{
            font-size: 1.8em;
            line-height: 1.8;
            color: #2d3748;
            margin-left: 40px;
        }}
        ul ul {{
            font-size: 0.85em;
            margin-top: 15px;
        }}
        li {{
            margin-bottom: 25px;
        }}
        code {{
            background: #f7fafc;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.9em;
            font-family: 'Courier New', monospace;
        }}
        .math-display {{
            font-size: 1.5em;
            text-align: center;
            margin: 35px 0;
            padding: 25px;
            background: #f7fafc;
            border-radius: 8px;
        }}
        .summary {{
            background: #f7fafc;
            padding: 40px;
            border-radius: 12px;
            border-left: 6px solid #667eea;
            font-size: 1.6em;
        }}
        .author {{
            font-size: 1.4em;
            color: #718096;
            margin-top: 40px;
            text-align: center;
        }}
        strong {{
            color: #667eea;
        }}
    </style>
</head>
<body>
    {title_slide}
    {outline_slide}
    {all_content_slides}
    {summary_slide}
</body>
</html>'''
        
        return full_html
    
    def _generate_slides_single_shot(self, query: str, context: str) -> str:
        """Fallback: Original single-shot generation if planning fails"""
        print(f"[SLIDES] Using fallback single-shot generation")
        
        prompt = f"""Create an HTML presentation about: {query}
Using: {context[:10000]}
Return complete HTML with embedded CSS and multiple <div class="slide"> elements."""
        
        response = self.llm_client.invoke(prompt)
        return response.content.replace("```html", "").replace("```", "").strip()
        
if __name__ == "__main__":
    pass

