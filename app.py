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

# Sidebar styling and controls
with st.sidebar:
    st.image("https://img.icons8.com/clouds/100/conference-call.png", width=80)
    st.title("Control Panel")
    st.markdown("Manage your assistant session and explore company guidelines effortlessly.")
    
    st.divider()
    
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("### Quick Tips")
    st.info("Ask about leave policies, code of conduct, insurance benefits, or office timings.")

# App Title & Description with an accent container
with st.container():
    st.title("📄 HR Policy Assistant")
    st.markdown("Get instant, accurate answers about your company's HR policies powered by your secure local RAG model.")
    st.divider()

# Initialize chat history in session state if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []

# Quick-start suggestion buttons if chat is empty
if not st.session_state.messages:
    st.markdown("##### 💡 Suggested Questions:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("What is the annual leave policy?"):
            st.session_state.pending_prompt = "What is the annual leave policy?"
    with col2:
        if st.button("How do I apply for medical reimbursement?"):
            st.session_state.pending_prompt = "How do I apply for medical reimbursement?"

# Display prior chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle prompt either from chat input or quick suggestion buttons
prompt = st.chat_input("Type your question here...")
if "pending_prompt" in st.session_state and st.session_state.pending_prompt:
    prompt = st.session_state.pending_prompt
    st.session_state.pending_prompt = None

if prompt:
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
                    answer = "I couldn't find any relevant details regarding that in the uploaded HR policy documents."
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