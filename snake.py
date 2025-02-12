import streamlit as st
import openai

# Carica la chiave API dai secrets di Streamlit
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Configura la pagina di Streamlit
st.set_page_config(page_title="ChatGPT Bot", page_icon="🤖")

st.title("🤖 Chat con il bot AI")

# Inizializza la sessione per la cronologia della chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra la cronologia dei messaggi
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input utente
if user_input := st.chat_input("Scrivi un messaggio..."):
    # Mostra il messaggio dell'utente nella chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Richiesta all'API di OpenAI
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Usa "gpt-3.5-turbo" se preferisci
            messages=[{"role": msg["role"], "content": msg["content"]} for msg in st.session_state.messages],
            temperature=0.7
        )
        bot_response = response["choices"][0]["message"]["content"]

        # Mostra la risposta del bot nella chat
        with st.chat_message("assistant"):
            st.markdown(bot_response)

        # Salva il messaggio del bot nella sessione
        st.session_state.messages.append({"role": "assistant", "content": bot_response})

    except Exception as e:
        st.error(f"Errore nella comunicazione con l'API: {str(e)}")
