from embedder import embed_User_query
from vectorstore import search_in_pinecone
from llm import query_llm_with_context

def process_user_query(query: str):
    # Embed the user's query to create a vector representation 
    query_vector = embed_User_query(query)
    
    # Search the vector DB to find top matching chunks related to the user's question
    matched_chunks = search_in_pinecone(query_vector)
    
    # Combine the list of chunks into a single string context
    context = "\n\n".join(matched_chunks)
    
    # Send the user query and the combined context string to the LLM for generating a response
    generated_response = query_llm_with_context(query, context)
    
    print("\n--- Answer ---")
    print(generated_response)

if __name__ == "__main__":
    user_query = "What is the work timing policy?"
    process_user_query(user_query)