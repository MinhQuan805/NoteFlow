"""
Sample Test Dataset for RAG Evaluation
Customize this file with your own questions and ground truths based on your documents.
"""

# Example test cases - Replace with questions relevant to your documents
SAMPLE_TEST_CASES = [
    {
        'question': 'What is the main topic of the documents?',
        'ground_truth': 'The main topic covers the key concepts and methodologies presented in the uploaded documents.',
        # 'file_filters': ['document1.pdf']  # Optional: filter by specific files
    },
    {
        'question': 'Can you summarize the key findings?',
        'ground_truth': 'The key findings include the main results, conclusions, and insights from the analysis.',
    },
    {
        'question': 'What methodology was used in the research?',
        'ground_truth': 'The methodology involves systematic approaches including data collection, analysis techniques, and validation processes.',
    },
    {
        'question': 'What are the main conclusions?',
        'ground_truth': 'The main conclusions highlight the significance of the findings and their implications for future work.',
    },
    {
        'question': 'What datasets were used?',
        'ground_truth': 'The research utilized specific datasets for training, validation, and testing purposes.',
    },
]

# Tips for creating effective test cases:
# 1. Questions should be answerable from your documents
# 2. Ground truth should be accurate and specific
# 3. Include diverse question types (factual, analytical, summary)
# 4. Test both simple and complex queries
# 5. Use file_filters to test document-specific queries

# Example with file filters:
ADVANCED_TEST_CASES = [
    {
        'question': 'What does document A say about machine learning?',
        'ground_truth': 'Document A discusses machine learning applications in natural language processing.',
        'file_filters': ['document_a.pdf']
    },
    {
        'question': 'Compare the approaches in document A and B',
        'ground_truth': 'Document A focuses on supervised learning while document B emphasizes unsupervised methods.',
        'file_filters': ['document_a.pdf', 'document_b.pdf']
    },
]
