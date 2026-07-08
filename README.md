<div align="center">

# 🤖 AI Research Assistant using Retrieval-Augmented Generation (RAG)

### *An Intelligent Document Question-Answering System powered by Google Gemini, LangChain, ChromaDB & FastAPI*

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Google-Gemini_2.5_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-RAG-00A67E?style=for-the-badge)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector_DB-7B2CBF?style=for-the-badge)

</p>

**📄 Upload PDFs • 🔍 Semantic Search • 🤖 Conversational AI • 📚 Source Citations**

</div>

---

# 📖 Overview

The **AI Research Assistant** is an intelligent document analysis application that enables users to upload PDF documents and interact with them using natural language.

Unlike traditional chatbots, this system leverages **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from uploaded documents before generating responses. This approach improves factual accuracy, reduces hallucinations, and ensures responses are grounded in the uploaded content.

The application integrates **Google Gemini 2.5 Flash**, **LangChain**, **ChromaDB**, **FastAPI**, and **Streamlit** to deliver a complete AI-powered research assistant.

---

# ✨ Key Features

- 📄 Upload and process PDF documents
- ✂️ Automatic document chunking
- 🧠 Gemini Embeddings for semantic understanding
- 🔍 Semantic similarity search using ChromaDB
- 🤖 Conversational Retrieval-Augmented Generation (RAG)
- 📚 Source citations for every response
- 💬 Interactive Streamlit chat interface
- 📤 Export conversation history
- 🗑 Remove uploaded documents
- 💾 Persistent vector database storage
- ⚡ FastAPI REST backend
- 🎯 Optimized prompt engineering
- 📊 Executive summaries
- 📋 Markdown table generation
- 📝 Structured and concise AI responses

---

# 🏗️ System Architecture

```text
                    User
                      │
                      ▼
           Streamlit Web Interface
                      │
                      ▼
             FastAPI Backend API
                      │
      ┌───────────────┴───────────────┐
      ▼                               ▼
 PDF Upload                     User Query
      │                               │
      ▼                               ▼
 Document Loader              Query Processing
      │                               │
      ▼                               ▼
 Text Chunking           MMR Semantic Retrieval
      │                               │
      ▼                               ▼
 Gemini Embeddings         Chroma Vector Store
      │                               │
      └───────────────┬───────────────┘
                      ▼
             Google Gemini 2.5 Flash
                      │
                      ▼
      AI Response + Source Citations
                      │
                      ▼
             Streamlit Chat Interface
```

---

# 🚀 Technology Stack

| Category | Technology |
|-----------|------------|
| **Programming Language** | Python |
| **Frontend** | Streamlit |
| **Backend** | FastAPI |
| **Large Language Model** | Google Gemini 2.5 Flash |
| **Framework** | LangChain |
| **Vector Database** | ChromaDB |
| **Embeddings** | Gemini Embeddings |
| **Retrieval Strategy** | Maximum Marginal Relevance (MMR) |
| **Document Loader** | PyPDF |
| **API Communication** | REST API |

---

# 📂 Project Structure

```text
AI-Research-Assistant-RAG/
│
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── embeddings.py
│   ├── rag.py
│   ├── retriever.py
│
├── frontend/
│   ├── app.py
│   ├── api.py
│   ├── components.py
│   ├── styles.py
│
├── storage/
│
├── architecture.png
│
├── README.md
│
├── .gitignore
│
└── requirements.txt
```

---

# ⚙️ Installation

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/Rashi14111/AI-Research-Assistant-RAG.git

cd AI-Research-Assistant-RAG
```

---

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Configure Environment Variables

Create a `.env` file.

```env
GOOGLE_API_KEY=YOUR_API_KEY
```

---

# ▶️ Run the Application

## Start FastAPI Backend

```bash
uvicorn backend.app:app --reload
```

Runs at

```
http://127.0.0.1:8000
```

---

## Start Streamlit Frontend

```bash
streamlit run frontend/app.py
```

---

# 🔄 RAG Workflow

```text
PDF Upload
     │
     ▼
PDF Processing
     │
     ▼
Document Chunking
     │
     ▼
Gemini Embeddings
     │
     ▼
ChromaDB Vector Store
     │
     ▼
MMR Semantic Retrieval
     │
     ▼
Relevant Context
     │
     ▼
Google Gemini 2.5 Flash
     │
     ▼
Answer with Source Citations
```

---

# 🎯 Prompt Engineering

The assistant is configured to:

- ✅ Use only retrieved context
- ✅ Reduce hallucinations
- ✅ Generate concise responses
- ✅ Produce executive summaries
- ✅ Format comparisons as markdown tables
- ✅ Group related technologies and concepts
- ✅ Avoid repetitive information
- ✅ Include source citations

---

# ⚙️ Retrieval Configuration

| Parameter | Value |
|-----------|--------|
| Chunk Size | 900 |
| Chunk Overlap | 120 |
| Retrieval Method | MMR |
| Retrieved Chunks | 5 |
| Fetch Chunks | 20 |
| Temperature | 0.2 |

---

# 💬 Example Questions

- Summarize this report.
- What are the key findings?
- Compare RAG and AI Agents.
- Which vector databases are discussed?
- What are the security recommendations?
- List all AI technologies mentioned.
- What deployment recommendations are provided?
- Create a short executive summary.

---

# 📷 Screenshots

> Add screenshots after completing the project.

| Home | Chat |
|------|------|
| *(Add Screenshot)* | *(Add Screenshot)* |

| PDF Upload | Source Citations |
|------------|------------------|
| *(Add Screenshot)* | *(Add Screenshot)* |

---

# 🔮 Future Enhancements

- Multi-document retrieval
- OCR support for scanned PDFs
- Authentication & user accounts
- Cloud deployment
- Chat history database
- Multi-LLM support
- Voice-enabled interaction

---

# 👩‍💻 Developer

**Rashi Garg**

AI Research Assistant Assignment

**Built with ❤️ using**

- Python
- FastAPI
- Streamlit
- Google Gemini
- LangChain
- ChromaDB
- Retrieval-Augmented Generation (RAG)

---

# 📜 License

This project was developed for **educational and academic purposes**.

---

<div align="center">

### ⭐ If you found this project interesting, consider giving it a star!

</div>
