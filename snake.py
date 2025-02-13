import streamlit as st
import openai
import json
import os
import re

# Carica la chiave API dai secrets di Streamlit
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Percorso del file JSON con le informazioni personali
USER_INFO_FILE = "user_info.json"

# Funzione per caricare le informazioni utente
def load_user_info():
    if os.path.exists(USER_INFO_FILE):
        with open(USER_INFO_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        # Creiamo un file di base se non esiste
        user_info = {
            "nome": "Michele",
            "cognome": "Rossi",
            "anno_di_nascita": 1997,
            "sesso": "Maschio",
            "interessi": [],
            "note_psicologiche": []
        }
        save_user_info(user_info)
        return user_info

# Funzione per salvare le informazioni utente
def save_user_info(user_info):
    with open(USER_INFO_FILE, "w", encoding="utf-8") as file:
        json.dump(user_info, file, ensure_ascii=False, indent=4)

# Funzione per generare il prompt iniziale con il contesto
def generate_initial_prompt(user_info):
    return (
        "Sei il mio psicologo personale. Devi conoscermi e aiutarmi nel modo migliore possibile.\n"
        "Ecco alcune informazioni su di me:\n"
        f"- Nome: {user_info['nome']}\n"
        f"- Cognome: {user_info['cognome']}\n"
        f"- Anno di nascita: {user_info['anno_di_nascita']}\n"
        f"- Sesso: {user_info['sesso']}\n"
        f"- Interessi: {', '.join(user_info['interessi']) if user_info['interessi'] else 'Nessuno'}\n"
        f"- Note psicologiche: {', '.join(user_info['note_psicologiche']) if user_info['note_psicologiche'] else 'Nessuna'}\n"
        "Puoi aggiornare le mie informazioni se lo ritieni utile.\n"
        "Quando vuoi aggiungere qualcosa nel file, usa questo formato:\n"
        "00000000\n"
        "Parte di JSON da aggiornare\n"
        "00000000\n"
        "Ora iniziamo a parlare!"
    )

# Funzione per aggiornare il file JSON dalle risposte di ChatGPT
def update_user_info_from_response(response_text, user_info):
    match = re.search(r'00000000\n(.*?)\n00000000', response_text, re.DOTALL)
    if match:
        try:
            new_data = json.loads(match.group(1))
            user_info.update(new_data)
            save_user_info(user_info)
            return response_text.replace(match.group(0), "").strip()  # Rimuove la parte JSON dalla risposta
        except json.JSONDecodeError:
            pass  # Se il formato non è corretto, ignoriamo l'aggiornamento
    return response_text

# Carichiamo le informazioni utente
user_info = load_user_info()
initial_prompt = generate_initial_prompt(user_info)

# Inizializza la sessione
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": initial_prompt}]

# Configura la pagina di Streamlit
st.set_page_config(page_title="Chat Psicologo AI", page_icon="🧠")

st.title("🧠 Chat con il tuo Psicologo AI")

# Mostra la cronologia dei messaggi
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input utente
if user_input := st.chat_input("Parlami di te..."):
    # Mostra il messaggio dell'utente nella chat
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Richiesta a ChatGPT
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=st.session_state.messages,
            temperature=0.7
        )
        bot_response = response["choices"][0]["message"]["content"]

        # Analizziamo la risposta per vedere se ci sono aggiornamenti JSON
        updated_response = update_user_info_from_response(bot_response, user_info)

        # Mostra la risposta del bot nella chat
        with st.chat_message("assistant"):
            st.markdown(updated_response)

        # Aggiunge il messaggio del bot alla sessione
        st.session_state.messages.append({"role": "assistant", "content": updated_response})

    except Exception as e:
        st.error(f"Errore nella comunicazione con l'API: {str(e)}")
