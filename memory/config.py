# LLM Configuration

# ollama setup

MODEL = "mistral"


# Chroma setup

CHROMA_HOST = "localhost"
CHROMA_PORT = 8010

# Streamlit Headers

STREAMLIT_PAGE_TITLE = "OpenChat: Chat with **your** Data"
STREAMLIT_BOT_TITLE = "OpenChat :female-teacher:"
STREAMLIT_SIDEBAR_TITLE = "Guidelines"

# STREAMLIT_SIDEBAR_TITLE = "Add additional sources for RAG (PDFs)"

USER_PROMPT = "How can I assist you?"
# TODO: Download and store in repo
USER_AVATAR = "https://cloudassembler.com/images/avatar.png"
BOT_AVATAR = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d8/Red_Hat_logo.svg/2560px-Red_Hat_logo.svg.png"

# RAG Setup and Vector Store (Chroma)

RAG_CHUNK_OVERLAP = 10
RAG_CHUNK_SIZE = 1000
RAG_COLLECTION_NAME = "openchat-collection-01"
RAG_INPUTS = "./rag-input-data"

# TODO: Setup embeddings here?
# RAG_EMBEDDING_MODEL = "nomic-embed-text-v1.5"
# RAG_PERSIST_DIR = "./rag-persist"