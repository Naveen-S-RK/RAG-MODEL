# 📄 HR + Digital Workplace Policy RAG Assistant

A Retrieval-Augmented Generation (RAG) chatbot that answers questions about your company's HR and Digital Workplace policy. It reads a PDF policy document, chunks and embeds it locally, stores the vectors in Pinecone, and uses Groq's LLM API to generate grounded answers through a Streamlit chat interface.

🔗 **Live Demo**: https://rag-model-exd644htsyhkztvexswdgx.streamlit.app/
📦 **Repository**: https://github.com/Naveen-S-RK/RAG-MODEL

This project was built to satisfy a standard "document Q&A / RAG assistant" assignment: extract a document → chunk it → embed it → store/retrieve via a vector store → accept a user question → retrieve relevant chunks → generate an answer grounded in those chunks → expose it through a simple UI.

## Approach & Implementation

The RAG pipeline (chunking, embedding, retrieval, prompting) is implemented directly with plain Python, so each step is explicit and easy to inspect/modify. Below is how each core requirement is met, file by file.

| # | Requirement | Implementation |
|---|---|---|
| 1 | Document as knowledge source | A PDF document (`resources/HR_and_Digital_Workspace_Policy.pdf`) |
| 2 | Extract & process content | `pdfreader.py` — extracts text per page with `pypdf` |
| 3 | Split into chunks | `chunker.py` — fixed-size character chunking (default 900 chars) with 150-char overlap to preserve context across boundaries |
| 4 | Generate embeddings | `embedder.py` — local, free embeddings via `sentence-transformers` (`all-MiniLM-L6-v2`, 384-dim), so no API cost/key is needed just to embed |
| 5 | Store & retrieve (vector store) | `vectorstore.py` — Pinecone index; `store_in_pinecone()` upserts in batches of 100, `search_in_pinecone()` does top-k cosine/similarity search |
| 6 | Accept questions from user | `app.py` — Streamlit `st.chat_input` |
| 7 | Retrieve + generate answer via LLM | `app.py` / `QueryProcessor.py` orchestrate: embed query → Pinecone search → build context → `llm.py` calls Groq (`openai/gpt-oss-20b`) |
| 8 | Answers grounded in the source | The system prompt in `llm.py` explicitly instructs the model to answer only from the given context, and to say so when the context is insufficient — no answers from the model's own general knowledge |
| 9 | Simple, usable interface | `app.py` — a Streamlit chat UI with message history within the session |

### Why these technology choices

- **Local embeddings (sentence-transformers)**: keeps embedding free and fast, with no external API dependency for that step.
- **Groq** for generation: fast inference, OpenAI-compatible client, low latency for a chat-style UI.
- **Pinecone** for the vector store: managed and persistent, no local index files to manage.
- **Streamlit** for the UI: minimal code to get a working chat interface with history.

## Features

- 💬 **Chat UI** built with Streamlit, including persistent chat history for the session
- 🔍 **Semantic search** over your HR policy document using vector embeddings
- 🧠 **Local, free embeddings** via `sentence-transformers` (`all-MiniLM-L6-v2`) — no API cost for embedding
- ⚡ **Fast LLM responses** via Groq (`openai/gpt-oss-20b`)
- 🗂️ **Vector storage** in Pinecone for persistent, scalable retrieval
- ✂️ **Configurable chunking** with overlap to preserve context across chunk boundaries

## How It Works

The project has two pipelines:

**1. Ingestion pipeline** (`dataprocessor.py`) — run once (or whenever the policy document changes):
1. `pdfreader.py` extracts raw text from each page of the HR policy PDF
2. `chunker.py` splits the combined text into overlapping chunks (default: 900 characters, 150 overlap)
3. `embedder.py` converts each chunk into a vector embedding locally using `all-MiniLM-L6-v2`
4. `vectorstore.py` upserts the chunks and their embeddings into a Pinecone index, in batches of 100

**2. Query pipeline** (`app.py` / `QueryProcessor.py`) — runs on every user question:
1. The user's question is embedded with the same local model
2. `vectorstore.py` queries Pinecone for the top-k most similar chunks
3. The matched chunks are joined together as context
4. `llm.py` sends the question + context to Groq's LLM, which answers strictly from the provided context

## Project Structure

```
.
├── app.py               # Streamlit chat interface (main entry point)
├── dataprocessor.py      # One-time ingestion script: PDF → chunks → embeddings → Pinecone
├── QueryProcessor.py     # CLI script to test the query pipeline without the UI
├── pdfreader.py          # PDF text extraction (pypdf)
├── chunker.py            # Text chunking with overlap
├── embedder.py            # Local embedding model (sentence-transformers)
├── vectorstore.py        # Pinecone upsert & similarity search
├── llm.py                # Groq LLM call with context-grounded system prompt
├── requirements.txt
└── resources/
    └── HR_and_Digital_Workspace_Policy.pdf  # Your HR & Digital Workspace policy document (not included — add your own)
```

## Prerequisites

- Python 3.9+
- A [Pinecone](https://www.pinecone.io/) account and index
- A [Groq](https://groq.com/) API key

## Setup

1. **Clone the repository and install dependencies**

   ```bash
   git clone https://github.com/Naveen-S-RK/RAG-MODEL.git
   cd RAG-MODEL
   pip install -r requirements.txt
   ```

2. **Create a Pinecone index**

   Create an index in your Pinecone console whose dimension matches the embedding model's output size (`all-MiniLM-L6-v2` produces **384-dimensional** vectors).

3. **Configure environment variables**

   Create a `.env` file in the project root:

   ```env
   GROQ_API_KEY="your-groq-api-key"
   PINECONE_API_KEY="your-pinecone-api-key"
   PINECONE_INDEX_NAME="your-pinecone-index-name"
   ```

   > ⚠️ Never commit your `.env` file — it's already excluded via `.gitignore`.

4. **Add your HR policy document**

   Place your PDF at `./resources/HR_and_Digital_Workspace_Policy.pdf` (or update `pdf_path` in `dataprocessor.py`).

## Usage

### Step 1 — Ingest the HR policy document (run once)

This reads, chunks, embeds, and stores the policy document in Pinecone:

```bash
python dataprocessor.py
```

### Step 2 — Launch the chat app

```bash
streamlit run app.py
```

Open the local URL Streamlit provides, then ask questions like:
- "What is the leave policy?"
- "What are the work timings?"
- "Can I upload confidential documents to an external AI tool?"

### (Optional) Test the query pipeline from the command line

```bash
python QueryProcessor.py
```

This runs a sample query (`"What is the work timing policy?"`) through the pipeline and prints the answer to the console.

## Sample Interaction

**Q: What is the leave policy?**

The assistant retrieves the relevant chunks from the policy PDF and responds with a grounded, structured answer (rendered from the retrieved context, not the model's general knowledge):

| Leave Category | Key Points |
|---|---|
| Annual / Earned Leave | 24 days per calendar year, accrued monthly. Unused leave may be carried forward up to 15 days. Can be encashed on separation, subject to applicable rules. |
| Casual Leave | For short-term personal requirements. Must be approved by the reporting manager wherever reasonably practicable before the leave is taken. |
| Sick Leave | For periods when an employee is unable to work due to illness. A medical certificate may be requested for extended absences. |

This demonstrates the grounding behavior described in requirement #8 — the answer is composed entirely from the retrieved PDF chunks.

## Tech Stack

| Component        | Technology                          |
|-------------------|--------------------------------------|
| UI                | Streamlit                            |
| PDF parsing       | pypdf                                |
| Embeddings        | sentence-transformers (`all-MiniLM-L6-v2`) |
| Vector database   | Pinecone                             |
| LLM               | Groq (`openai/gpt-oss-20b`)          |
| Config            | python-dotenv                        |

## Configuration Notes

- **Chunk size / overlap**: adjust `chunk_size` and `chunk_overlap` in the `chunk_pages()` call in `dataprocessor.py`.
- **Top-k retrieved chunks**: the Streamlit app retrieves the top 3 matches (`app.py`); `QueryProcessor.py` uses the `search_in_pinecone` default of 4. Adjust as needed.
- **LLM behavior**: the system prompt in `llm.py` restricts answers strictly to the retrieved context, and tells the model to say so when the context is insufficient.

## Known Limitations & Future Improvements

- **Chunking strategy**: fixed-size character chunking is simple but can split sentences or table rows mid-way; semantic/recursive chunking could improve retrieval precision for structured tables like the leave policy.
- **No reranking step**: retrieval relies purely on top-k vector similarity; adding a reranker could improve answer quality for ambiguous questions.
- **No cross-session memory**: chat history persists only within a Streamlit session; there's no long-term conversation memory across sessions.
- **Single-document scope**: the pipeline is built around one PDF; ingesting multiple documents would need source-tagging in the vector metadata to disambiguate answers.

## AI Tools Disclosure

Parts of this project were built with the assistance of AI tools (Claude), used for:
- Debugging the Pinecone batch upsert logic
- Refining the system prompt in `llm.py` to enforce context-grounded answering
- Drafting and structuring this README

The core architecture — chunking strategy, retrieval pipeline design, and prompt design — was designed and implemented manually, and I can walk through any part of it in detail.

## Testing Notes

- Live demo verified working in an incognito/private browser window (see screenshot below — sample query "What is the leave policy?" returning a grounded, table-formatted answer from the ingested PDF).
- GitHub repository confirmed public and accessible.

## Submission

- **Live Demo**: https://rag-model-exd644htsyhkztvexswdgx.streamlit.app/
- **GitHub Repository**: https://github.com/Naveen-S-RK/RAG-MODEL
