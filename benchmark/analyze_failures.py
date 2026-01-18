"""
Analyze benchmark results to find poorly performing questions.
Usage: python analyze_failures.py [--threshold 0.5] [--metric cosine_similarity]
"""

import argparse
import csv
from pathlib import Path

def load_results(csv_path: str) -> list:
    """Load benchmark results from CSV."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def analyze_failures(results: list, metric: str = 'cosine_similarity', threshold: float = 0.5, top_n: int = None):
    """Find questions with scores below threshold."""
    
    failures = []
    for i, r in enumerate(results):
        score = float(r.get(metric, 0))
        if score < threshold:
            failures.append({
                'index': i + 1,
                'score': score,
                'question': r.get('question', ''),
                'ground_truth': r.get('ground_truth', ''),
                'prediction': r.get('prediction', ''),
                'source': r.get('source', ''),
                'f1': float(r.get('f1', 0)),
                'rouge_l': float(r.get('rouge_l', 0)),
                'cosine_similarity': float(r.get('cosine_similarity', 0))
            })
    
    # Sort by score (worst first)
    failures.sort(key=lambda x: x['score'])
    
    if top_n:
        failures = failures[:top_n]
    
    return failures

def print_failure(f: dict, metric: str):
    """Pretty print a single failure."""
    print("=" * 80)
    print(f"[#{f['index']}] {metric.upper()}: {f['score']:.2%}")
    print(f"Source: {f['source']}")
    print("-" * 80)
    print(f"QUESTION:\n  {f['question']}")
    print()
    print(f"EXPECTED ANSWER:\n  {f['ground_truth']}")
    print()
    print(f"RAG RESPONSE:\n  {f['prediction'][:500]}{'...' if len(f['prediction']) > 500 else ''}")
    print()
    print(f"ALL SCORES: F1={f['f1']:.2%} | ROUGE-L={f['rouge_l']:.2%} | Cosine={f['cosine_similarity']:.2%}")
    print()

def save_failures_to_file(failures: list, output_path: Path, metric: str):
    """Save failures to a markdown file for easier reading."""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(f"# Benchmark Failure Analysis\n\n")
        f.write(f"**Metric:** {metric}\n")
        f.write(f"**Total Failures:** {len(failures)}\n\n")
        
        for fail in failures:
            f.write(f"---\n\n")
            f.write(f"## Question #{fail['index']} (Score: {fail['score']:.2%})\n\n")
            f.write(f"**Source:** `{fail['source']}`\n\n")
            f.write(f"### Question\n{fail['question']}\n\n")
            f.write(f"### Expected Answer\n{fail['ground_truth']}\n\n")
            f.write(f"### RAG Response\n{fail['prediction']}\n\n")
            f.write(f"**Scores:** F1={fail['f1']:.2%} | ROUGE-L={fail['rouge_l']:.2%} | Cosine={fail['cosine_similarity']:.2%}\n\n")
    
    print(f"[SAVED] Failures saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Analyze benchmark failures')
    parser.add_argument('--input', '-i', 
                        default=str(Path(__file__).parent / 'result' / 'benchmark_results.csv'),
                        help='Path to benchmark_results.csv')
    parser.add_argument('--metric', '-m', default='cosine_similarity',
                        choices=['f1', 'rouge_l', 'contains', 'cosine_similarity'],
                        help='Metric to use for filtering')
    parser.add_argument('--threshold', '-t', type=float, default=0.5,
                        help='Score threshold (below = failure)')
    parser.add_argument('--top', '-n', type=int, default=None,
                        help='Show only top N worst failures')
    parser.add_argument('--save', '-s', action='store_true',
                        help='Save failures to markdown file')
    
    args = parser.parse_args()
    
    print(f"[LOAD] Reading: {args.input}")
    results = load_results(args.input)
    print(f"[LOAD] Found {len(results)} results")
    
    print(f"\n[ANALYZE] Finding questions with {args.metric} < {args.threshold:.0%}...")
    failures = analyze_failures(results, args.metric, args.threshold, args.top)
    
    if not failures:
        print(f"\n[OK] No failures found! All questions scored above {args.threshold:.0%}")
        return
    
    print(f"\n[FOUND] {len(failures)} questions below threshold\n")
    
    for f in failures:
        print_failure(f, args.metric)
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total questions analyzed: {len(results)}")
    print(f"Questions below {args.threshold:.0%}: {len(failures)} ({len(failures)/len(results):.1%})")
    avg_score = sum(f['score'] for f in failures) / len(failures)
    print(f"Average score of failures: {avg_score:.2%}")
    
    if args.save:
        output_path = Path(args.input).parent / 'failure_analysis.md'
        save_failures_to_file(failures, output_path, args.metric)

if __name__ == '__main__':
    main()
