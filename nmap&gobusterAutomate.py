import nmap
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor

def is_valid_ip(ip):
    """Valide si l'adresse IP est correcte."""
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    return pattern.match(ip) is not None

def run_gobuster(url, protocol):
    """Lance Gobuster pour scanner un serveur HTTP/HTTPS."""
    print(f"Lancement de Gobuster pour {protocol}://{url}...")
    try:
        # Construction de la commande Gobuster
        cmd = [
            "gobuster", "dir", "-u", f"{protocol}://{url}",
            "-w", "/usr/share/wordlists/dirb/big.txt",  # Utilisation d'un gros wordlist par défaut
            "-t", "50"  # 50 threads
        ]
        # Exécution de la commande Gobuster
        subprocess.run(cmd, check=True)
    except Exception as error:
        print(f"Erreur lors du lancement de Gobuster : {error}")

def run_nmap(ip_address):
    try:
        scanner = nmap.PortScanner()
        print(f"Lancement de Nmap sur {ip_address}...")

        # Arguments optimisés, incluant la détection des services avec -sV
        scan_result = scanner.scan(ip_address, arguments='-T4 -A -Pn -p- -sV')

        # Affichage des résultats du scan
        print("Résultats du scan :\n")
        http_ports = []  # Liste pour stocker les ports HTTP/HTTPS trouvés
        for host in scanner.all_hosts():
            print(f"Host : {host} ({scanner[host].hostname()})")
            print(f"State : {scanner[host].state()}\n")
            
            for proto in scanner[host].all_protocols():
                print(f"Protocole : {proto}")
                ports = scanner[host][proto].keys()
                for port in sorted(ports):
                    state = scanner[host][proto][port]['state']
                    service = scanner[host][proto][port].get('name', 'N/A')  # Le service associé au port
                    print(f"Port : {port} | State : {state} | Service : {service}")

                    # Si le service est HTTP ou HTTPS, ajouter à la liste
                    if service in ['http', 'https']:
                        http_ports.append((port, service))
        
        # Lancer Gobuster en parallèle pour chaque port HTTP/HTTPS trouvé
        with ThreadPoolExecutor() as executor:
            for port, service in http_ports:
                protocol = "http" if service == "http" else "https"
                url = f"{ip_address}:{port}"
                executor.submit(run_gobuster, url, protocol)
        
        print("\nScan terminé.")
    except Exception as error:
        print(f"Erreur lors du lancement de Nmap : {error}")

# Entrée de l'utilisateur
ip = input("Entrez l'adresse IP à scanner : ").strip()

# Validation de l'adresse IP
if is_valid_ip(ip):
    run_nmap(ip)
else:
    print("Erreur : L'adresse IP entrée n'est pas valide.")
