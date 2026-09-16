import streamlit as st
from embedder import embed_User_query
from vectorstore import search_in_pinecone
from llm import query_llm_with_context

# Page Configuration
st.set_page_config(
    page_title="HR Policy RAG Assistant",
    page_icon="🤖",
    layout="centered"
)

# App Title & Description
st.title("📄 HR Policy Assistant")
st.markdown("Ask any question about your company's HR policy, and I'll find the answer for you using your local RAG model!")

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input box at the bottom of the screen
if prompt := st.chat_input("Type your question here (e.g., What is the leave policy?)..."):
    # Add user message to state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate the assistant response using your RAG pipeline
    with st.chat_message("assistant"):
        with st.spinner("Searching HR documents and generating response..."):
            try:
                # 1. Embed query locally
                query_vector = embed_User_query(prompt)
                
                # 2. Search Pinecone
                matched_chunks = search_in_pinecone(query_vector, top_k=3)
                
                # 3. Format context
                context = "\n\n".join(matched_chunks)
                
                # 4. Get response from Groq
                answer = query_llm_with_context(prompt, context)
                
                # Display output
                st.markdown(answer)
                
                # Save assistant response to state
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                st.error(error_msg)