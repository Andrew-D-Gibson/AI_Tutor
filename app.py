import requests
from pathlib import Path

import streamlit as st
import chromadb
from chromadb.utils import embedding_functions

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.1:8b"

BASE_DIR = Path(__file__).resolve().parent
DB_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "rag_files"
EMBED_MODEL = "all-MiniLM-L6-v2"


def get_collection():
    client = chromadb.PersistentClient(path=str(DB_DIR))
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=embed_fn,
    )


def retrieve_context(query, k=4):
    if not DB_DIR.exists():
        return ""

    collection = get_collection()
    results = collection.query(query_texts=[query], n_results=k)
    docs = (results.get("documents") or [[]])[0]
    metas = (results.get("metadatas") or [[]])[0]

    if not docs:
        return ""

    parts = []
    for doc, meta in zip(docs, metas):
        source = (meta or {}).get("source", "unknown")
        parts.append(f"Source: {source}\n{doc}")

    return "\n\n---\n\n".join(parts)


def chat_with_ollama(user_message, history, context):
    # history: list of {"role": ..., "content": ...} from past turns this session

    system_prompt = (
        "You are a helpful tutor for undergraduate students.\n\n"
        #"Your job is to guide students to an answer when they're having difficulties.\n"
        #"Use the Socratic method (asking guided questions designed to lead students to get themselves to a correct answer).\n"
        #"Do not give away the answer, simply guide students to the correct answer.\n"
        #"If students struggle for multiple message rounds, build up their knowledge slowly by hinting towards the correct answer.\n"
    )

    if context.strip():
        system_prompt += "\nRelevant context:\n" + context

    messages = [{"role": "system", "content": system_prompt}] + history + [
        {"role": "user", "content": user_message}
    ]

    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "messages": messages,
            "stream": False,
        },
        timeout=60,
    )
    resp.raise_for_status()
    data = resp.json()
    reply = data["message"]["content"]
    return reply


def main() -> None:
    st.set_page_config(page_title="AI Tutor Chat", page_icon="💬")

    st.title("AI Tutor Chat")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Type your message")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            context = retrieve_context(prompt)
            response = chat_with_ollama(prompt, st.session_state.messages[:-1], context)
            print("Still working!")
            print(f"Prompt: {prompt}")
            print(f"History: {st.session_state.messages[:-1]}")
            print(f"Context: {context}")
            
        except requests.RequestException as exc:
            response = f"Error contacting Ollama: {exc}"
        except Exception as exc:
            response = f"Error during retrieval: {exc}"

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)


if __name__ == "__main__":
    print("It's working!")
    main()