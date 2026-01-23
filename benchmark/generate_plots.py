"""
Generate visualization charts from existing benchmark results CSV.
Usage: python generate_plots.py [--input path/to/results.csv]
"""

import argparse
import csv
from pathlib import Path
import numpy as np

def load_results(csv_path: str) -> list:
    """Load benchmark results from CSV."""
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def generate_visualizations(results: list, output_dir: Path):
    """Generate benchmark visualization charts."""
    try:
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
    except ImportError:
        print("[ERROR] matplotlib not installed. Run: pip install matplotlib")
        return
    
    output_dir.mkdir(exist_ok=True)
    
    # Extract metrics (handle both old and new CSV formats)
    f1_scores = [float(r.get('f1', 0)) for r in results]
    rouge_scores = [float(r.get('rouge_l', 0)) for r in results]
    contains_scores = [float(r.get('contains', 0)) for r in results]
    cosine_scores = [float(r.get('cosine_similarity', 0)) for r in results]
    
    # Check which metrics are available
    has_cosine = any(cosine_scores)
    
    if has_cosine:
        metrics = ['F1 Score', 'ROUGE-L', 'Contains', 'Cosine Sim']
        averages = [np.mean(f1_scores), np.mean(rouge_scores), np.mean(contains_scores), np.mean(cosine_scores)]
        colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0']
        all_data = [f1_scores, rouge_scores, contains_scores, cosine_scores]
    else:
        metrics = ['F1 Score', 'ROUGE-L', 'Contains']
        averages = [np.mean(f1_scores), np.mean(rouge_scores), np.mean(contains_scores)]
        colors = ['#4CAF50', '#2196F3', '#FF9800']
        all_data = [f1_scores, rouge_scores, contains_scores]
    
    # 1. Bar chart of average metrics
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(metrics, averages, color=colors)
    ax.set_ylabel('Score')
    ax.set_title('RAG Benchmark - Average Metrics')
    ax.set_ylim(0, 1)
    for bar, avg in zip(bars, averages):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02, 
                f'{avg:.2%}', ha='center', va='bottom', fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_dir / 'metrics_average.png', dpi=150)
    plt.close()
    print(f"  [OK] Saved: metrics_average.png")
    
    # 2. Distribution boxplot
    fig, ax = plt.subplots(figsize=(10, 6))
    bp = ax.boxplot(all_data, labels=metrics, patch_artist=True)
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    ax.set_ylabel('Score')
    ax.set_title('RAG Benchmark - Score Distribution')
    ax.set_ylim(0, 1)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / 'metrics_distribution.png', dpi=150)
    plt.close()
    print(f"  [OK] Saved: metrics_distribution.png")
    
    # 3. Per-question line chart
    if len(results) <= 50:
        fig, ax = plt.subplots(figsize=(14, 6))
        x = range(len(results))
        ax.plot(x, f1_scores, marker='o', label='F1', color='#4CAF50', alpha=0.7, markersize=4)
        ax.plot(x, rouge_scores, marker='s', label='ROUGE-L', color='#2196F3', alpha=0.7, markersize=4)
        if has_cosine:
            ax.plot(x, cosine_scores, marker='^', label='Cosine', color='#9C27B0', alpha=0.7, markersize=4)
        ax.set_xlabel('Question Index')
        ax.set_ylabel('Score')
        ax.set_title('RAG Benchmark - Per-Question Scores')
        ax.legend()
        ax.set_ylim(0, 1)
        ax.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / 'per_question_scores.png', dpi=150)
        plt.close()
        print(f"  [OK] Saved: per_question_scores.png")
    
    # 4. Histogram of cosine similarity (if available)
    if has_cosine:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.hist(cosine_scores, bins=20, color='#9C27B0', alpha=0.7, edgecolor='white')
        ax.axvline(np.mean(cosine_scores), color='red', linestyle='--', label=f'Mean: {np.mean(cosine_scores):.2%}')
        ax.set_xlabel('Cosine Similarity')
        ax.set_ylabel('Frequency')
        ax.set_title('Distribution of Semantic Similarity Scores')
        ax.legend()
        plt.tight_layout()
        plt.savefig(output_dir / 'cosine_histogram.png', dpi=150)
        plt.close()
        print(f"  [OK] Saved: cosine_histogram.png")
    
    print(f"\n[DONE] All charts saved to: {output_dir}")

def main():
    parser = argparse.ArgumentParser(description='Generate plots from benchmark results')
    parser.add_argument('--input', '-i', 
                        default=str(Path(__file__).parent / 'result' / 'benchmark_results.csv'),
                        help='Path to benchmark_results.csv')
    parser.add_argument('--output', '-o',
                        default=str(Path(__file__).parent / 'result'),
                        help='Output directory for charts')
    
    args = parser.parse_args()
    
    print(f"[LOAD] Reading: {args.input}")
    results = load_results(args.input)
    print(f"[LOAD] Found {len(results)} results")
    
    print("\n[PLOT] Generating visualizations...")
    generate_visualizations(results, Path(args.output))

if __name__ == '__main__':
    main()
