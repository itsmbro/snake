import streamlit as st
import openai
import json
import requests
import re

# Carica la chiave API dai secrets di Streamlit
openai.api_key = st.secrets["OPENAI_API_KEY"]

# URL del file JSON su GitHub
GITHUB_USER = "itsmbro"
GITHUB_REPO = "snake"
GITHUB_BRANCH = "main"
USER_INFO_FILE = "user_data.json"  # Il file è presente nel repository GitHub

# Funzione per caricare le informazioni utente da GitHub
def load_user_info():
    url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{USER_INFO_FILE}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        # Se non trova il file, crea un file di base
        user_info = {
            "nome": "Michele",
            "cognome": "Belotti",
            "anno_di_nascita": 1998,
            "sesso": "Maschio",
            "interessi": ["suono il piamo"],
            "note_psicologiche": ["nessuna"]
        }
        update_user_info_on_github(user_info)
        return user_info

# Funzione per aggiornare il file JSON su GitHub
def update_user_info_on_github(user_info):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{USER_INFO_FILE}"
    github_token = st.secrets["GITHUB_TOKEN"]  # Token GitHub nei secrets di Streamlit
    headers = {"Authorization": f"token {github_token}"}

    # Ottieni l'hash del file per fare l'update
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_data = response.json()
        sha = file_data["sha"]  # Ottieni l'hash del file
    else:
        sha = None

    # Codifica i dati come stringa JSON in base64
    json_data = json.dumps(user_info, ensure_ascii=False, indent=4)
    encoded_data = json_data.encode('utf-8').decode('utf-8')

    data = {
        "message": "Aggiornamento delle informazioni utente",
        "content": encoded_data,
        "branch": GITHUB_BRANCH
    }

    if sha:
        data["sha"] = sha  # Aggiungi l'hash per fare il commit sull'esistente

    response = requests.put(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print("File JSON aggiornato su GitHub con successo!")
    else:
        print(f"Errore nell'aggiornamento del file su GitHub: {response.status_code}")

# Funzione per generare il prompt iniziale con il contesto
def generate_initial_prompt(user_info):
    return (
        "Sei il mio psicologo personale. Devi conoscermi e aiutarmi nel modo migliore possibile.\n"
        "Gestiamo un file JSON in Python che contiene le mie informazioni personali.\n"
        "Il JSON attuale con le mie informazioni è il seguente:\n\n"
        "00000000\n"
        f"{json.dumps(user_info, ensure_ascii=False, indent=4)}\n"
        "00000000\n\n"
        "Puoi aggiornarlo quando ritieni utile aggiungere dettagli importanti su di me.\n"
        "Quando vuoi aggiornare il file JSON, devi farlo seguendo questo formato ESATTO:\n\n"
        "00000000\n"
        "{\n"
        '  "chiave1": "valore1",\n'
        '  "chiave2": "valore2"\n'
        "}\n"
        "00000000\n\n"
        "Il JSON deve essere ben formato e contenere solo nuove informazioni pertinenti.\n"
        "Non modificare o rimuovere dati esistenti, ma solo aggiungere nuove informazioni se necessario.\n"
        "Ora iniziamo a parlare!"
    )

# Funzione per aggiornare il file JSON dalle risposte di ChatGPT
def update_user_info_from_response(response_text, user_info):
    match = re.search(r'00000000\n(.*?)\n00000000', response_text, re.DOTALL)
    if match:
        try:
            new_data = json.loads(match.group(1))
            user_info.update(new_data)
            update_user_info_on_github(user_info)  # Aggiorna il file su GitHub
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
