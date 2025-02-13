import streamlit as st
import openai
import json
import requests
import base64
import re






# Configurazione delle API
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Configurazione GitHub
GITHUB_USER = "itsmbro"
GITHUB_REPO = "snake"
GITHUB_BRANCH = "main"
GITHUB_FILE_PATH = "user_data.json"

# Funzione per caricare user_info.json da GitHub
def load_user_info():
    url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}/{GITHUB_FILE_PATH}"
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
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

# Funzione per salvare user_info.json su GitHub
def save_user_info(user_info):
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents/{GITHUB_FILE_PATH}"
    headers = {
        "Authorization": f"token {st.secrets['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Ottieni SHA del file per aggiornamento
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        sha = response.json()["sha"]
    else:
        sha = None  # Il file sarà creato da zero

    # Converte il JSON in base64
    json_data = json.dumps(user_info, ensure_ascii=False, indent=4)
    json_base64 = base64.b64encode(json_data.encode()).decode()

    # Prepara la richiesta
    data = {
        "message": "Aggiornamento user_data.json",
        "content": json_base64,
        "branch": GITHUB_BRANCH
    }
    
    if sha:
        data["sha"] = sha  # Necessario per l'aggiornamento

    response = requests.put(url, headers=headers, json=data)
    if response.status_code not in [200, 201]:
        st.error(f"Errore aggiornamento GitHub: {response.json()}")

# Genera il prompt iniziale con il contesto
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

# Funzione per aggiornare user_info.json dalle risposte di ChatGPT
def update_user_info_from_response(response_text, user_info):
    match = re.search(r'00000000\n(.*?)\n00000000', response_text, re.DOTALL)
    if match:
        try:
            new_data = json.loads(match.group(1))
            user_info.update(new_data)
            save_user_info(user_info)  # Salva su GitHub
            return response_text.replace(match.group(0), "").strip()
        except json.JSONDecodeError:
            pass  # Ignora errori di parsing JSON
    return response_text

# Carichiamo il JSON da GitHub
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

        # Aggiorna user_info.json se necessario
        updated_response = update_user_info_from_response(bot_response, user_info)

        # Mostra la risposta nella chat
        with st.chat_message("assistant"):
            st.markdown(updated_response)

        # Salva il messaggio nella sessione
        st.session_state.messages.append({"role": "assistant", "content": updated_response})

    except Exception as e:
        st.error(f"Errore nella comunicazione con OpenAI: {str(e)}")
