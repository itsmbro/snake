import json
import requests
import streamlit as st
from base64 import b64encode

# Funzione per caricare il file JSON da GitHub
def load_user_info_from_github():
    url = "https://raw.githubusercontent.com/itsmbro/snake/main/user_data.json"  # Modifica USER, REPO e BRANCH
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        # Se il file non esiste, ritorniamo dati predefiniti
        default_data = {
            "nome": "Michele",
            "cognome": "Rossi",
            "anno_di_nascita": 1998,
            "sesso": "Maschio",
            "interessi": [],
            "note_psicologiche": []
        }
        return default_data

# Funzione per aggiornare il file JSON su GitHub
def update_user_info_on_github(new_data):
    url = "https://api.github.com/repos/USER/REPO/contents/user_data.json"  # Modifica USER e REPO
    github_token = "your_github_token"  # Se repository privato
    headers = {"Authorization": f"token {github_token}"}

    # Ottieni l'hash del file per fare l'update
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_data = response.json()
        sha = file_data["sha"]  # Ottieni l'hash del file per fare il commit
    else:
        sha = None

    # Codifica i dati come stringa JSON in base64
    json_data = json.dumps(new_data, ensure_ascii=False, indent=4)
    encoded_data = b64encode(json_data.encode('utf-8')).decode('utf-8')

    data = {
        "message": "Aggiornamento delle informazioni utente",
        "content": encoded_data,
        "branch": "main"
    }

    if sha:
        data["sha"] = sha  # Aggiungi l'hash per fare il commit sull'esistente

    response = requests.put(url, json=data, headers=headers)
    
    if response.status_code == 200:
        print("File JSON aggiornato con successo!")
    else:
        print(f"Errore nell'aggiornamento del file: {response.status_code}")

# Funzione per eliminare il file JSON da GitHub
def delete_json_from_github():
    url = "https://api.github.com/repos/USER/REPO/contents/user_data.json"  # Modifica USER e REPO
    github_token = "your_github_token"  # Se repository privato
    headers = {"Authorization": f"token {github_token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        file_data = response.json()
        sha = file_data["sha"]  # Ottieni l'hash del file per il DELETE

        # Fai una richiesta DELETE per eliminare il file
        delete_url = f"https://api.github.com/repos/USER/REPO/contents/user_data.json"
        data = {
            "message": "Eliminazione del file JSON",
            "sha": sha,
            "branch": "main"
        }

        delete_response = requests.delete(delete_url, json=data, headers=headers)
        if delete_response.status_code == 200:
            print("File JSON eliminato su GitHub con successo.")
        else:
            print(f"Errore nell'eliminazione del file: {delete_response.status_code}")
    else:
        print(f"Errore nell'ottenere il file da GitHub: {response.status_code}")

# Funzione principale per l'app Streamlit
def main():
    st.title("Chat con il bot psicologo")

    # Carica il JSON da GitHub
    user_info = load_user_info_from_github()

    # Visualizza le informazioni
    st.write("Benvenuto! Queste sono le tue informazioni di base:", user_info)

    # Mostra un campo di testo per interagire con il bot
    user_message = st.text_input("Scrivi qualcosa al tuo psicologo:")

    if user_message:
        # Logica per rispondere, e aggiornare il JSON se necessario
        # Simula un messaggio del bot che aggiunge una nuova informazione (esempio)
        if "cane" in user_message.lower():
            user_info["note_psicologiche"].append("Possiede un cane.")
            update_user_info_on_github(user_info)

        # Risposta del bot
        st.write("Bot: Ho aggiunto una nuova informazione sulla tua conversazione.")

    # Pulsante per eliminare il JSON (per il caso in cui desideri eliminare il file)
    if st.button("Elimina il file JSON su GitHub"):
        delete_json_from_github()

if __name__ == "__main__":
    main()
