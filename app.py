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

# Cyber Grid Background & Styling Injection
st.markdown("""
<style>
    /* Cyber grid background pattern mimicking high-tech SaaS dashboards */
    .stApp {
        background-color: #050508;
        background-image: 
            linear-gradient(to right, rgba(30, 41, 59, 0.4) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(30, 41, 59, 0.4) 1px, transparent 1px);
        background-size: 40px 40px;
        color: #f8fafc;
    }

    /* Soft ambient glow effect that tracks cursor */
    #cursor-glow {
        position: fixed;
        width: 400px;
        height: 400px;
        background: radial-gradient(circle, rgba(56, 189, 248, 0.12) 0%, rgba(14, 116, 144, 0.04) 50%, transparent 80%);
        border-radius: 50%;
        pointer-events: none;
        transform: translate(-50%, -50%);
        z-index: 9999;
    }
</style>

<div id="cursor-glow"></div>

<script>
    // Smooth cursor movement for ambient glow
    const glow = document.getElementById('cursor-glow');
    document.addEventListener('mousemove', (e) => {
        glow.style.left = e.clientX + 'px';
        glow.style.top = e.clientY + 'px';
    });
</script>
""", unsafe_allow_html=True)

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
                
                # Handle empty vector search results gracefully
                if not matched_chunks:
                    answer = "I couldn't find any relevant information in the HR policy documents to answer your question."
                else:
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