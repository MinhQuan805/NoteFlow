"""
Merge all benchmark markdown tables into a single CSV file.
Handles multi-line markdown table cells.
Usage: python merge_benchmark.py
"""

import os
import csv
import re
from pathlib import Path

def parse_markdown_table(filepath: str) -> list[dict]:
    """Parse a markdown table file and return list of row dictionaries."""
    rows = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove header row and separator
    lines = content.split('\n')
    # Find where data starts (after header + separator)
    data_start = 0
    for i, line in enumerate(lines):
        if line.strip().startswith('| ---'):
            data_start = i + 1
            break
    
    # Join remaining content and split by row pattern
    data_content = '\n'.join(lines[data_start:])
    
    # Split by line starting with | followed by non-whitespace (new row)
    # This regex finds rows that start with | and a question
    row_pattern = re.compile(r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|\n]+\.pdf)\s*\|', re.DOTALL)
    
    matches = row_pattern.findall(data_content)
    
    for match in matches:
        question = match[0].strip().replace('\n', ' ').replace('\r', '')
        answer = match[1].strip().replace('\n', ' ').replace('\r', '')
        source = match[2].strip().replace('\n', ' ').replace('\r', '')
        
        # Clean up multiple spaces
        question = re.sub(r'\s+', ' ', question)
        answer = re.sub(r'\s+', ' ', answer)
        
        if question and answer and source:
            rows.append({
                'question': question,
                'ground_truth': answer,
                'source_file': source
            })
    
    return rows

def main():
    # Paths
    script_dir = Path(__file__).parent
    dataset_dir = script_dir / 'dataset'
    output_file = script_dir / 'benchmark_dataset.csv'
    
    if not dataset_dir.exists():
        print(f"Error: {dataset_dir} not found")
        return
    
    # Find all .md files
    md_files = sorted(dataset_dir.glob('*.md'))
    print(f"Found {len(md_files)} markdown files in {dataset_dir}")
    
    all_rows = []
    
    for md_file in md_files:
        print(f"  Processing: {md_file.name}")
        rows = parse_markdown_table(md_file)
        all_rows.extend(rows)
        print(f"    -> {len(rows)} questions")
    
    # Write to CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['question', 'ground_truth', 'source_file'])
        writer.writeheader()
        writer.writerows(all_rows)
    
    print(f"\n[OK] Merged {len(all_rows)} questions into {output_file}")
    print(f"  Columns: question, ground_truth, source_file")

if __name__ == "__main__":
    main()
