from docling.document_converter import DocumentConverter
from sentence_transformers import SentenceTransformer
from fastapi import UploadFile

# embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

async def create_file_embedding(file: UploadFile):
    source = "https://arxiv.org/pdf/2408.09869"
    converter = DocumentConverter()
    doc = converter.convert(source).document

    print(doc.export_to_markdown())
    # await file.seek(0)

    # converter = DocumentConverter()
    # input_bytes = await file.read()
    # print(f"input_bytes length: {len(input_bytes)}")
    # print(f"file: {input_bytes}")

    # doc = converter.convert(input_bytes)
    # print(f"doc object: {doc.document.export_to_markdown()}")
    
    # text = doc.document.export_to_text()
    # print(f"text length: {len(text)}")

    # vector = embedding_model.encode(text, convert_to_numpy=True).tolist()
    # print(f"vector length: {len(vector)}")

    # return {
    #     "content": text,
    #     "embedding": vector
    # }
