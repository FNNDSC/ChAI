import chromadb
from chromadb.config import Settings
import pandas as pd
import streamlit as st
import config as cfg


def view_collections():
    st.title("📂 ChromaDB Collections Viewer")

    client = chromadb.HttpClient(
        host=cfg.CHROMA_HOST,
        port=cfg.CHROMA_PORT,
        settings=Settings(allow_reset=False),
    )

    collections = client.list_collections()

    if not collections:
        st.warning("No collections found.")
        return

    for collection in collections:
        st.markdown(f"### Collection: `{collection.name}`")
        try:
            data = collection.get()
            df = pd.DataFrame.from_dict(data)
            st.dataframe(df)
        except Exception as e:
            st.error(f"Failed to fetch data from `{collection.name}`: {e}")


if __name__ == "__main__":
    try:
        view_collections()
    except Exception as e:
        print(f"Error: {e}")
