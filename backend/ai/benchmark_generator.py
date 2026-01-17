import os
import json
import sys
import argparse
from typing import List, Dict, Any
from dotenv import load_dotenv

# Add parent directory to path to import modules
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)
sys.path.append(backend_dir)

# Load env vars
load_dotenv(os.path.join(backend_dir, ".env"))

from rag_modules import LLMClient
from parser import parse_single_path

class BenchmarkGenerator:
    def __init__(self, config_path: str = "config.yaml"):
        import yaml
        
        # Load config
        self.config = {}
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f)
        else:
            # Default config if file missing (fallback)
            self.config = {
                "llm": {
                    "model_name": "gemini-1.5-flash",
                    "provider": "gemini"
                }
            }
            
        self.llm_client = LLMClient(
            model_name=self.config.get("llm", {}).get("model_name", "gemini-1.5-flash"),
            api_key_env="GOOGLE_API_KEY",
            config=self.config.get("llm", {})
        )

    def generate_qa_pairs(self, file_path: str, num_pairs: int = 5) -> List[Dict[str, str]]:
        """
        Generate Q&A pairs from a single document.
        """
        print(f"Parsing document: {file_path}...")
        try:
            # Parse document contents
            _, _, text_content = parse_single_path(file_path)
            
            if not text_content:
                print(f"Warning: No text content found in {file_path}")
                return []
                
            print(f"Generating {num_pairs} Q&A pairs (this may take a moment)...")
            
            # Construct Prompt
            prompt = f"""
            You are an expert at creating educational and testing questions from documents.
            
            Context Document:
            {text_content[:20000]}  # Limit context window just in case
            
            Task:
            Generate {num_pairs} diverse question-answer pairs based STRICTLY on the text above.
            
            Requirements:
            1. Questions should be specific and unambiguous.
            2. Answers should be comprehensive but concise.
            3. Return ONLY a valid JSON array of objects.
            4. Format: [{{"question": "...", "answer": "..."}}, ...]
            
            Do not include markdown formatting like ```json ... ```. Just the raw JSON.
            """
            
            # Invoke LLM
            response = self.llm_client.invoke(prompt)
            content = response.content.strip()
            
            # Clean possible markdown
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            
            content = content.strip()
            
            # Parse JSON
            qa_pairs = json.loads(content)
            
            # Add metadata
            for pair in qa_pairs:
                pair["source_file"] = os.path.basename(file_path)
                
            return qa_pairs
            
        except Exception as e:
            print(f"Error generating Q&A for {file_path}: {e}")
            return []

    def process_directory(self, input_dir: str, output_file: str, num_pairs_per_file: int = 5):
        """
        Process all supported files in a directory and save benchmark dataset.
        """
        all_qa_pairs = []
        
        valid_extensions = ['.pdf', '.txt', '.md', '.docx']
        
        if not os.path.exists(input_dir):
            print(f"Error: Directory {input_dir} not found.")
            return

        files = [
            os.path.join(input_dir, f) 
            for f in os.listdir(input_dir) 
            if os.path.splitext(f)[1].lower() in valid_extensions
        ]
        
        print(f"Found {len(files)} documents to process.")
        
        for file_path in files:
            pairs = self.generate_qa_pairs(file_path, num_pairs_per_file)
            all_qa_pairs.extend(pairs)
            print(f"Generated {len(pairs)} pairs from {os.path.basename(file_path)}")
            
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_qa_pairs, f, indent=2, ensure_ascii=False)
            
        print(f"\nSuccess! Saved {len(all_qa_pairs)} benchmark pairs to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic Q&A benchmark dataset from documents.")
    parser.add_argument("input_path", help="Path to a document file or directory of documents")
    parser.add_argument("--output", "-o", default="benchmark_dataset.json", help="Output JSON file path")
    parser.add_argument("--num", "-n", type=int, default=5, help="Number of pairs per document")
    
    args = parser.parse_args()
    
    generator = BenchmarkGenerator(os.path.join(os.path.dirname(__file__), "config.yaml"))
    
    if os.path.isdir(args.input_path):
        generator.process_directory(args.input_path, args.output, args.num)
    elif os.path.isfile(args.input_path):
        pairs = generator.generate_qa_pairs(args.input_path, args.num)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(pairs, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(pairs)} pairs to {args.output}")
    else:
        print(f"Error: Invalid input path {args.input_path}")

if __name__ == "__main__":
    main()
