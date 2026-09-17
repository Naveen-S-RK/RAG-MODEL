from pdfreader import read_pdf
from chunker import chunk_pages
from embedder import embed_chunks
from vectorstore import store_in_pinecone
from typing import List
from dotenv import load_dotenv
load_dotenv()  # This loads the variables from the .env file automatically
pdf_path = "./resources/HR_and_Digital_Workspace_Policy.pdf"
def run():
    # Read HR Policy PDF and extract text
    pages = read_pdf(pdf_path)

    # Chunk the extracted text into manageable pieces
    chunks = chunk_pages(pages, chunk_size=900, chunk_overlap=150)

    embedded_chunks = embed_chunks(chunks)
    
    
    store_in_pinecone(chunks, embedded_chunks, namespace="")
   
    
if __name__ == "__main__":
    run()