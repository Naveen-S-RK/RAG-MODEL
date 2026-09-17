**📄 HR + Digital Worplace Policy RAG Assistant**
A Retrieval-Augmented Generation (RAG) chatbot that answers questions about your company's HR and Digital Workplace policy. It reads a PDF policy document, chunks and embeds it locally, stores the vectors in Pinecone, and uses Groq's LLM API to generate grounded answers through a Streamlit chat interface.
🔗 Live Demo: https://rag-model-exd644htsyhkztvexswdgx.streamlit.app/
📦 Repository: https://github.com/Naveen-S-RK/RAG-MODEL
This project was built to satisfy a standard "document Q&A / RAG assistant" assignment: extract a document → chunk it → embed it → store/retrieve via a vector store → accept a user question → retrieve relevant chunks → generate an answer grounded in those chunks → expose it through a simple UI.
Approach & Implementation
The RAG pipeline (chunking, embedding, retrieval, prompting) is implemented directly with plain Python, so each step is explicit and easy to inspect/modify. Below is how each core requirement is met, file by file.
#	Requirement	Implementation
1	Document as knowledge source	A PDF document (`resources/HR\_and\_Digital\_Workspace\_Policy.pdf`)
2	Extract & process content	`pdfreader.py` — extracts text per page with `pypdf`
3	Split into chunks	`chunker.py` — fixed-size character chunking (default 900 chars) with 150-char overlap to preserve context across boundaries
4	Generate embeddings	`embedder.py` — local, free embeddings via `sentence-transformers` (`all-MiniLM-L6-v2`, 384-dim), so no API cost/key is needed just to embed
5	Store & retrieve (vector store)	`vectorstore.py` — Pinecone index; `store\_in\_pinecone()` upserts in batches of 100, `search\_in\_pinecone()` does top-k cosine/similarity search
6	Accept questions from user	`app.py` — Streamlit `st.chat\_input`
7	Retrieve + generate answer via LLM	`app.py` / `QueryProcessor.py` orchestrate: embed query → Pinecone search → build context → `llm.py` calls Groq (`openai/gpt-oss-20b`)
8	Answers grounded in the source	The system prompt in `llm.py` explicitly instructs the model to answer only from the given context, and to say so when the context is insufficient — no answers from the model's own general knowledge
9	Simple, usable interface	`app.py` — a Streamlit chat UI with message history within the session
Why these technology choices
Local embeddings (sentence-transformers): keeps embedding free and fast, with no external API dependency for that step.
Groq for generation: fast inference, OpenAI-compatible client, low latency for a chat-style UI.
Pinecone for the vector store: managed and persistent, no local index files to manage.
Streamlit for the UI: minimal code to get a working chat interface with history.
Features
💬 Chat UI built with Streamlit, including persistent chat history for the session
🔍 Semantic search over your HR policy document using vector embeddings
🧠 Local, free embeddings via `sentence-transformers` (`all-MiniLM-L6-v2`) — no API cost for embedding
⚡ Fast LLM responses via Groq (`openai/gpt-oss-20b`)
🗂️ Vector storage in Pinecone for persistent, scalable retrieval
✂️ Configurable chunking with overlap to preserve context across chunk boundaries
How It Works
The project has two pipelines:
1. Ingestion pipeline (`dataprocessor.py`) — run once (or whenever the policy document changes):
`pdfreader.py` extracts raw text from each page of the HR policy PDF
`chunker.py` splits the combined text into overlapping chunks (default: 900 characters, 150 overlap)
`embedder.py` converts each chunk into a vector embedding locally using `all-MiniLM-L6-v2`
`vectorstore.py` upserts the chunks and their embeddings into a Pinecone index, in batches of 100
2. Query pipeline (`app.py` / `QueryProcessor.py`) — runs on every user question:
The user's question is embedded with the same local model
`vectorstore.py` queries Pinecone for the top-k most similar chunks
The matched chunks are joined together as context
`llm.py` sends the question + context to Groq's LLM, which answers strictly from the provided context
Project Structure
```
.
├── app.py               # Streamlit chat interface (main entry point)
├── dataprocessor.py      # One-time ingestion script: PDF → chunks → embeddings → Pinecone
├── QueryProcessor.py     # CLI script to test the query pipeline without the UI
├── pdfreader.py          # PDF text extraction (pypdf)
├── chunker.py            # Text chunking with overlap
├── embedder.py            # Local embedding model (sentence-transformers)
├── vectorstore.py        # Pinecone upsert \& similarity search
├── llm.py                # Groq LLM call with context-grounded system prompt
├── requirements.txt
└── resources/
    └── HR\_and\_Digital\_Workspace\_Policy.pdf  # Your HR \& Digital Workspace policy document (not included — add your own)
```
Prerequisites
Python 3.9+
A Pinecone account and index
A Groq API key
Setup
Clone the repository and install dependencies
```bash
   git clone https://github.com/Naveen-S-RK/RAG-MODEL.git
   cd RAG-MODEL
   pip install -r requirements.txt
   ```
Create a Pinecone index
Create an index in your Pinecone console whose dimension matches the embedding model's output size (`all-MiniLM-L6-v2` produces 384-dimensional vectors).
Configure environment variables
Create a `.env` file in the project root:
```env
   GROQ\_API\_KEY="your-groq-api-key"
   PINECONE\_API\_KEY="your-pinecone-api-key"
   PINECONE\_INDEX\_NAME="your-pinecone-index-name"
   ```
> ⚠️ Never commit your `.env` file — it's already excluded via `.gitignore`.
Add your HR policy document
Place your PDF at `./resources/HR\_and\_Digital\_Workspace\_Policy.pdf` (or update `pdf\_path` in `dataprocessor.py`).
Usage
Step 1 — Ingest the HR policy document (run once)
This reads, chunks, embeds, and stores the policy document in Pinecone:
```bash
python dataprocessor.py
```
Step 2 — Launch the chat app
```bash
streamlit run app.py
```
Open the local URL Streamlit provides, then ask questions like:
"What is the leave policy?"
"What are the work timings?"
"Can I upload confidential documents to an external AI tool?"
(Optional) Test the query pipeline from the command line
```bash
python QueryProcessor.py
```
This runs a sample query (`"What is the work timing policy?"`) through the pipeline and prints the answer to the console.
Tech Stack
Component	Technology
UI	Streamlit
PDF parsing	pypdf
Embeddings	sentence-transformers (`all-MiniLM-L6-v2`)
Vector database	Pinecone
LLM	Groq (`openai/gpt-oss-20b`)
Config	python-dotenv
Configuration Notes
Chunk size / overlap: adjust `chunk\_size` and `chunk\_overlap` in the `chunk\_pages()` call in `dataprocessor.py`.
Top-k retrieved chunks: the Streamlit app retrieves the top 3 matches (`app.py`); `QueryProcessor.py` uses the `search\_in\_pinecone` default of 4. Adjust as needed.
LLM behavior: the system prompt in `llm.py` restricts answers strictly to the retrieved context, and tells the model to say so when the context is insufficient.
Submission
Live Demo: https://rag-model-exd644htsyhkztvexswdgx.streamlit.app/
GitHub Repository: https://github.com/Naveen-S-RK/RAG-MODEL
