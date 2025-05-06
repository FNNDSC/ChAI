# ChAI - A Natural Language Assistant for ChRIS 🧠 [WIP]

<img width="1475" alt="Screenshot 2025-05-06 at 8 14 12 AM" src="https://github.com/user-attachments/assets/6edf75dc-c83b-4683-a4ce-9408ec8b672a" />

This repository sets up a local development environment for the ChAI assistant.

It uses:

- **Ollama** for local LLM inference
- **ChromaDB** (in HTTP server mode) for memory and document storage
- **Streamlit** for the user interface
- **LlamaStack** for agentic related

---

## 🔧 Prerequisites

Before getting started, ensure you have:

- Python **3.11**
- [Ollama](https://ollama.com) installed locally
- [LlamaStack](https://github.com/llama-index/llama-stack) installed
- `streamlit` and `chromadb` installed via pip

---

## 📦 Setup Instructions

### 1. Clone the Repo and Create a Virtual Environment

```bash
git clone https://github.com/YOUR_USERNAME/ChAI
cd ChAI
python3.11 -m venv .chenv
source .chenv/bin/activate
````

---

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

> Ensure your `requirements.txt` includes:
>
> ```text
> chromadb[server]
> streamlit
> llama-stack
> ```

---

### 3. Start the ChromaDB Server Locally

ChromaDB v1.x no longer supports direct Python clients. You must run the Chroma server:

```bash
chroma run --path .chroma_store
```

This starts the ChromaDB server at `http://localhost:8000` and stores data in the `.chroma_store/` folder (acts like a volume).

Leave this terminal running.

---

### 4. Start the Ollama Model

In a new terminal tab (also inside your virtual env):

```bash
INFERENCE_MODEL=llama3.2:3b llama stack build --template ollama --image-type venv --run
```

This builds and runs the local inference container using the specified model.

---

### 5. Launch the Streamlit UI

In another terminal tab (still in the same `.chenv`):

```bash
streamlit run app.py
```

You’ll see something like:

```
Local URL: http://localhost:8501
```

Open this URL in your browser to interact with ChAI.

---

## 🧠 Architecture Overview

```text
User → Streamlit UI (app.py)
           ↓
      LlamaStack (Ollama)
           ↓
     ┌──────────────┐
     │ ChromaDB API │ ← chroma run --path .chroma_store
     └──────────────┘
```

* **Chat memory** and document context are stored in ChromaDB collections.
* **LLM responses** are generated via LlamaStack → Ollama.
* **Everything runs locally**, but is production-aligned (e.g. OpenShift-ready).

---

## 🛠️ Common Commands

| Command                                   | Purpose                            |
| ----------------------------------------- | ---------------------------------- |
| `chroma run --path .chroma_store`         | Starts ChromaDB HTTP server        |
| `llama stack build --template ollama ...` | Starts Ollama model via LlamaStack |
| `streamlit run app.py`                    | Launches the ChAI frontend         |

---

## 🩺 Troubleshooting

### Chroma Errors

* **Error:** `PersistentClient not supported`

  * **Fix:** Make sure you're running `chroma run --path .chroma_store` and using `HttpClient` in code

* **Error:** `localhost:8000 refused connection`

  * **Fix:** Ensure the Chroma server is running before launching the app

---

## 📁 File/Folder Structure

```
ChAI/
├── app.py                  # Streamlit UI
├── memory/
│   └── chroma_store.py     # ChromaMemoryStore using HttpClient
├── agents/
│   └── chai.py             # ChAI agent logic
├── .chroma_store/          # Auto-created persistent vector store
├── requirements.txt
└── README.md
```

---

## 📌 Notes

* The `.chroma_store/` folder is your persistent vector DB — similar to a PVC in production.
* You can use the same architecture on OpenShift by deploying the Chroma server and mounting this folder via a PVC.

---

## 🚀 Future Enhancements

* Add OpenShift `Deployment + PVC` YAMLs
* Dockerize ChromaDB
* Integrate RAG document upload in UI
* Add `analyze` mode for input summarization

---

## 🧩 Credits

Built using:

* [ChromaDB](https://github.com/chroma-core/chroma)
* [Ollama](https://ollama.com)
* [LlamaStack](https://llama-stack.readthedocs.io/en/latest)
* [Streamlit](https://streamlit.io)

---

## 📄 License

This project is licensed under the [MIT License](./LICENSE). You are free to use, modify, and distribute this software with proper attribution.

