import streamlit as st
import requests
import uuid
from loguru import logger


LANGUAGES_DICT = {
    "fr": {
        "prefix": "Votre sentiment : ",
        "flag": "🇫🇷",
        "positive": "Positif 😀",
        "negative": "Négatif 🙁",
        "neutral": "Neutre 😐",
        "lg_info": "Langue détectée : Français",
    },
    "en": {
        "flag": "🇬🇧", # 🇺🇸
        "prefix": "Your sentiment : ",
        "positive": "Positive 😀",
        "negative": "Negative 🙁",
        "neutral": "Neutral 😐",
        "lg_info": "Detected language: English",
    },
}


def get_sentiment(text, language=None):

    response = requests.post("http://127.0.0.1:9000/sentiment/", json={"text": text}) # , json={"text": text, "language": "fr"})
    data = response.json()
    sentiment = data["sentiment"]
    language = data["language"]
    lg = LANGUAGES_DICT[language]
    if sentiment['compound'] >= 0.05 :
        key = "positive"
    elif sentiment['compound'] <= -0.05 :
        key = "negative"
    else :
        key = "neutral"        
    return f"{lg['prefix']}{lg[key]} ({lg['lg_info']} {lg['flag']})"


def main():

    session_id = str(uuid.uuid4())

    logger.info(f"{session_id} Loading page...")

    # Session management
    if "session_uid" not in st.session_state:
        st.session_state.session_uid = str()
    # Store messages in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Set page configuration
    st.set_page_config(page_title="Sentiment Chatbot", page_icon="💬")

    # Title
    st.title("💬 Sentiment Chatbot")

    # Display chat messages from history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    logger.info(f"{session_id} Processing chat messages...")
                
    # Prompt for user input
    if prompt := st.chat_input("Say something..."):
        
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Assistant response
        logger.info(f"{session_id} Getting sentiment for user input...")
        res = get_sentiment(prompt)
        st.session_state.messages.append({"role": "assistant", "content": res})

        logger.info(f"{session_id} Sentiment response received, displaying...")

        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(res)

main()
