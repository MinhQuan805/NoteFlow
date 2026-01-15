import os
import argparse
import sys
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from langchain_community.chat_models import ChatOllama
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.run_config import RunConfig

from dotenv import load_dotenv

# Thêm thư mục backend vào path để import RAGSystem
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(SCRIPT_DIR)
sys.path.append(BACKEND_DIR)

# Load environment variables from .env file
load_dotenv(os.path.join(BACKEND_DIR, ".env"))

from ai.rag_system import RAGSystem

run_config = RunConfig(
    timeout=180,        # Max seconds per operation (default: 180)
    max_retries=10,     # Retry attempts (default: 10)
    max_wait=60,        # Max seconds between retries (default: 60)
    max_workers=10,     # Concurrent workers (default: 16)
    log_tenacity=False, # Log retry attempts (default: False)
    seed=42,            # Random seed (default: 42)
)

def run_benchmark(notebook_id: str = "default"):
    print("=" * 50)
    print("NoteFlow RAG Benchmark (using Ragas)")
    print("=" * 50)

    # Change to backend directory so data paths work correctly
    os.chdir(BACKEND_DIR)

    # 1. Khởi tạo hệ thống RAG
    print("Initializing RAG System...")
    config_path = os.path.join(SCRIPT_DIR, "config.yaml")
    rag = RAGSystem(config_path=config_path, notebook_id=notebook_id)
    
    if not rag.all_documents:
        print("Error: No documents found in the RAG system. Please ingest documents first using pipeline.py.")
        return

    # 2. Định nghĩa bộ dữ liệu kiểm thử (Testset)
    # Bạn nên thay thế bằng các câu hỏi thực tế liên quan đến tài liệu của bạn
    test_questions = [
        {
            "question": "What is the main purpose of this document?",
            "ground_truth": "To explain the functionality of the NoteFlow system." # Ground truth là câu trả lời mong đợi (cần thiết cho context_recall)
        },
        # Thêm các câu hỏi khác tại đây...
    ]

    print(f"Running benchmark on {len(test_questions)} questions...")
    
    results = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }

    # 3. Chạy RAG để lấy câu trả lời và ngữ cảnh
    for item in test_questions:
        question = item["question"]
        ground_truth = item.get("ground_truth", "")
        
        print(f"Processing: {question}")
        
        # Sử dụng hàm query_with_context mới để lấy cả answer và contexts
        answer, contexts = rag.query_with_context(question)
        
        results["question"].append(question)
        results["answer"].append(answer)
        results["contexts"].append(contexts)
        results["ground_truth"].append(ground_truth)

    # 4. Chuẩn bị Dataset cho Ragas
    dataset = Dataset.from_dict(results)
    
    # Chạy Ollama local với model llama3
    local_llm = ChatOllama(model="llama3")
    evaluator_llm = LangchainLLMWrapper(local_llm)
    # Cấu hình Embeddings cho Ragas (Sử dụng lại cấu hình của RAGSystem)
    evaluator_embeddings = LangchainEmbeddingsWrapper(rag.embeddings)

    # 5. Chọn các metrics để đánh giá
    metrics = [
        faithfulness,       # Câu trả lời có dựa trên ngữ cảnh không?
        answer_relevancy,   # Câu trả lời có liên quan đến câu hỏi không?
        context_precision,  # Ngữ cảnh tìm được có chính xác không?
    ]
    
    # Chỉ thêm context_recall nếu có ground_truth
    if any(results["ground_truth"]):
        metrics.append(context_recall) # Hệ thống có tìm được tất cả thông tin cần thiết không?

    print("\nEvaluating with Ragas (this may take a while)...")
    evaluation_results = evaluate(
        dataset=dataset,
        metrics=metrics,
        llm=evaluator_llm,
        embeddings=evaluator_embeddings,
        run_config=run_config
    )

    # 6. Xuất kết quả
    print("\n" + "=" * 50)
    print("Evaluation Results:")
    print(evaluation_results)
    print("=" * 50)
    
    # Lưu kết quả chi tiết ra file CSV
    df = evaluation_results.to_pandas()
    output_file = os.path.join(SCRIPT_DIR, "benchmark_results.csv")
    df.to_csv(output_file, index=False)
    print(f"\nDetailed results saved to: {output_file}")

if __name__ == "__main__":
    # Chạy benchmark (có thể thay đổi notebook_id nếu cần)
    # Ví dụ: python benchmark.py --notebook_id my_notebook
    parser = argparse.ArgumentParser(description="Run RAG Benchmark")
    parser.add_argument("--notebook_id", type=str, default="default", help="Notebook ID to benchmark")
    args = parser.parse_args()
    run_benchmark(notebook_id=args.notebook_id)