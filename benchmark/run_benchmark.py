"""
RAG Benchmark Runner
- Reads benchmark CSV
- Queries RAG system
- Evaluates with non-LLM metrics (F1, ROUGE-L, Cosine Similarity)
- Generates visualization charts

Usage:
    python run_benchmark.py                    # Run full benchmark
    python run_benchmark.py --limit 10         # Run first 10 questions
    python run_benchmark.py --limit 10 --random # Run 10 random questions
    python run_benchmark.py --skip-ingest      # Skip ingestion (if already ingested)
"""

import os
import sys
import csv
import argparse
import re
from pathlib import Path
from collections import Counter
from typing import List, Tuple
import random

# Setup paths
SCRIPT_DIR = Path(__file__).parent
BACKEND_DIR = SCRIPT_DIR.parent / 'backend'
AI_DIR = BACKEND_DIR / 'ai'
sys.path.insert(0, str(AI_DIR))
sys.path.insert(0, str(BACKEND_DIR))

from dotenv import load_dotenv
load_dotenv(BACKEND_DIR / '.env')

from rag_system import RAGSystem

# Embedding model for cosine similarity
from sentence_transformers import SentenceTransformer
import numpy as np

EMBEDDING_MODEL = None

def get_embedding_model():
    global EMBEDDING_MODEL
    if EMBEDDING_MODEL is None:
        print("[INIT] Loading embedding model for cosine similarity...")
        EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    return EMBEDDING_MODEL

# ============ Evaluation Metrics (No LLM needed) ============

def normalize_text(text: str) -> str:
    """Lowercase, remove punctuation, extra whitespace."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize(text: str) -> List[str]:
    """Simple whitespace tokenization."""
    return normalize_text(text).split()

def f1_score(prediction: str, ground_truth: str) -> float:
    """Token-level F1 score between prediction and ground truth."""
    pred_tokens = tokenize(prediction)
    gt_tokens = tokenize(ground_truth)
    
    if not pred_tokens or not gt_tokens:
        return 0.0
    
    pred_counter = Counter(pred_tokens)
    gt_counter = Counter(gt_tokens)
    
    common = sum((pred_counter & gt_counter).values())
    
    if common == 0:
        return 0.0
    
    precision = common / len(pred_tokens)
    recall = common / len(gt_tokens)
    
    return 2 * precision * recall / (precision + recall)

def rouge_l(prediction: str, ground_truth: str) -> float:
    """ROUGE-L score (Longest Common Subsequence based F1)."""
    pred_tokens = tokenize(prediction)
    gt_tokens = tokenize(ground_truth)
    
    if not pred_tokens or not gt_tokens:
        return 0.0
    
    m, n = len(pred_tokens), len(gt_tokens)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if pred_tokens[i-1] == gt_tokens[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    
    lcs_length = dp[m][n]
    
    if lcs_length == 0:
        return 0.0
    
    precision = lcs_length / m
    recall = lcs_length / n
    
    return 2 * precision * recall / (precision + recall)

def contains_answer(prediction: str, ground_truth: str) -> float:
    """Check if key terms from ground truth appear in prediction."""
    gt_tokens = set(tokenize(ground_truth))
    pred_tokens = set(tokenize(prediction))
    
    if not gt_tokens:
        return 0.0
    
    overlap = len(gt_tokens & pred_tokens)
    return overlap / len(gt_tokens)

def cosine_similarity(prediction: str, ground_truth: str) -> float:
    """Compute cosine similarity using sentence embeddings."""
    model = get_embedding_model()
    
    embeddings = model.encode([prediction, ground_truth])
    
    # Cosine similarity
    similarity = np.dot(embeddings[0], embeddings[1]) / (
        np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
    )
    
    return float(similarity)

# ============ Visualization ============

def generate_visualizations(results: List[dict], output_dir: Path):
    """Generate benchmark visualization charts."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
    except ImportError:
        print("[WARN] matplotlib not installed. Skipping visualization.")
        return
    
    output_dir.mkdir(exist_ok=True)
    
    # Extract metrics
    f1_scores = [r['f1'] for r in results]
    rouge_scores = [r['rouge_l'] for r in results]
    contains_scores = [r['contains'] for r in results]
    cosine_scores = [r['cosine_similarity'] for r in results]
    
    # 1. Bar chart of average metrics
    fig, ax = plt.subplots(figsize=(10, 6))
    metrics = ['F1 Score', 'ROUGE-L', 'Contains', 'Cosine Sim']
    averages = [
        np.mean(f1_scores),
        np.mean(rouge_scores),
        np.mean(contains_scores),
        np.mean(cosine_scores)
    ]
    colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0']
    bars = ax.bar(metrics, averages, color=colors)
    ax.set_ylabel('Score')
    ax.set_title('RAG Benchmark - Average Metrics')
    ax.set_ylim(0, 1)
    for bar, avg in zip(bars, averages):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
                f'{avg:.2%}', ha='center', va='bottom', fontsize=12)
    plt.tight_layout()
    plt.savefig(output_dir / 'metrics_average.png', dpi=150)
    plt.close()
    print(f"  [CHART] Saved: metrics_average.png")
    
    # 2. Distribution boxplot
    fig, ax = plt.subplots(figsize=(10, 6))
    data = [f1_scores, rouge_scores, contains_scores, cosine_scores]
    bp = ax.boxplot(data, labels=metrics, patch_artist=True)
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_ylabel('Score')
    ax.set_title('RAG Benchmark - Score Distribution')
    ax.set_ylim(0, 1)
    plt.tight_layout()
    plt.savefig(output_dir / 'metrics_distribution.png', dpi=150)
    plt.close()
    print(f"  [CHART] Saved: metrics_distribution.png")
    
    # 3. Per-question line chart (if not too many questions)
    if len(results) <= 30:
        fig, ax = plt.subplots(figsize=(14, 6))
        x = range(len(results))
        ax.plot(x, f1_scores, marker='o', label='F1', color='#4CAF50', alpha=0.7)
        ax.plot(x, rouge_scores, marker='s', label='ROUGE-L', color='#2196F3', alpha=0.7)
        ax.plot(x, cosine_scores, marker='^', label='Cosine', color='#9C27B0', alpha=0.7)
        ax.set_xlabel('Question Index')
        ax.set_ylabel('Score')
        ax.set_title('RAG Benchmark - Per-Question Scores')
        ax.legend()
        ax.set_ylim(0, 1)
        plt.tight_layout()
        plt.savefig(output_dir / 'per_question_scores.png', dpi=150)
        plt.close()
        print(f"  [CHART] Saved: per_question_scores.png")
    
    print(f"  [VIS] All charts saved to {output_dir}")

# ============ Benchmark Runner ============

def run_benchmark(csv_path: str, pdf_dir: str, limit: int = None, skip_ingest: bool = False, random_sample: bool = False):
    """Run the full benchmark."""
    
    # Initialize RAG
    config_path = AI_DIR / 'config.yaml'
    os.chdir(BACKEND_DIR)
    
    rag = RAGSystem(str(config_path), notebook_id='benchmark')
    print(f"[RAG] Initialized. Existing docs: {len(rag.all_documents)}")
    
    # Ingest PDFs if needed
    if not skip_ingest:
        pdf_files = list(Path(pdf_dir).glob('*.pdf'))
        if pdf_files:
            print(f"\n[INGEST] Found {len(pdf_files)} PDF files")
            rag.ingest([str(p) for p in pdf_files])
            print(f"[INGEST] Complete. Total docs: {len(rag.all_documents)}")
        else:
            print(f"[WARN] No PDFs found in {pdf_dir}")
    
    # Load benchmark data
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    if limit:
        if random_sample:
            rows = random.sample(rows, min(limit, len(rows)))
            print(f"[SAMPLING] Randomly selected {len(rows)} questions")
        else:
            rows = rows[:limit]
    
    print(f"\n[BENCHMARK] Running {len(rows)} questions...")
    print("=" * 70)
    
    results = []
    
    for i, row in enumerate(rows):
        question = row['question']
        ground_truth = row['ground_truth']
        source_file = row['source_file']
        
        print(f"\n[{i+1}/{len(rows)}] Q: {question[:60]}...")
        
        # Query RAG
        try:
            prediction = rag.query_benchmark(question, file_filters=[source_file])
        except Exception as e:
            print(f"  [ERROR] {e}")
            prediction = ""
        
        # Calculate metrics
        f1 = f1_score(prediction, ground_truth)
        rl = rouge_l(prediction, ground_truth)
        contains = contains_answer(prediction, ground_truth)
        cosine = cosine_similarity(prediction, ground_truth)
        
        results.append({
            'question': question,
            'ground_truth': ground_truth,
            'prediction': prediction,
            'source': source_file,
            'f1': f1,
            'rouge_l': rl,
            'contains': contains,
            'cosine_similarity': cosine
        })
        
        print(f"  F1: {f1:.2f} | ROUGE-L: {rl:.2f} | Contains: {contains:.2f} | Cosine: {cosine:.2f}")
    
    # Summary
    print("\n" + "=" * 70)
    print("BENCHMARK RESULTS")
    print("=" * 70)
    
    avg_f1 = sum(r['f1'] for r in results) / len(results)
    avg_rl = sum(r['rouge_l'] for r in results) / len(results)
    avg_contains = sum(r['contains'] for r in results) / len(results)
    avg_cosine = sum(r['cosine_similarity'] for r in results) / len(results)
    
    print(f"  Questions:        {len(results)}")
    print(f"  F1 Score:         {avg_f1:.2%}")
    print(f"  ROUGE-L:          {avg_rl:.2%}")
    print(f"  Contains:         {avg_contains:.2%}")
    print(f"  Cosine Similarity:{avg_cosine:.2%}")
    
    # Save detailed results
    output_path = SCRIPT_DIR / 'result' / 'benchmark_results.csv'
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n[SAVED] Detailed results: {output_path}")
    
    # Generate visualizations
    print("\n[VIS] Generating visualization charts...")
    generate_visualizations(results, SCRIPT_DIR / 'result')
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Run RAG benchmark')
    parser.add_argument('--csv', default=str(SCRIPT_DIR / 'benchmark_dataset.csv'),
                        help='Path to benchmark CSV')
    parser.add_argument('--pdfs', default=str(SCRIPT_DIR.parent / 'cs224n_slides'),
                        help='Path to PDF directory')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of questions')
    parser.add_argument('--skip-ingest', action='store_true',
                        help='Skip PDF ingestion')
    parser.add_argument('--random', action='store_true',
                        help='Randomly sample questions (use with --limit)')
    
    args = parser.parse_args()
    
    run_benchmark(args.csv, args.pdfs, args.limit, args.skip_ingest, args.random)

if __name__ == '__main__':
    main()
