from pushbullet import Pushbullet
import time
import os

# Imposta la tua chiave API Pushbullet
API_KEY = 'o.4zmKeCXBUZZgSMMuemPJJLJ3b6eQAEEx'
pb = Pushbullet(API_KEY)

# Percorso al file da monitorare
file_path = './output.txt'
# Leggi lo stato iniziale del file
last_modified_time = os.path.getmtime(file_path)

print("Ubot1: script check_output.py partito")
push = pb.push_note("Ubot1", " script check_output.py partito")
try:
    while True:
        # Verifica se il file è stato modificato
        current_modified_time = os.path.getmtime(file_path)
        if current_modified_time != last_modified_time:
            # Invia una notifica Pushbullet
            push = pb.push_note("Ubot1", " ha mandato testo in terminale. apri il file output.txt")
            # Aggiorna il tempo dell'ultima modifica
            last_modified_time = current_modified_time
        # Attendi un po' prima di verificare nuovamente
        time.sleep(60)  # Aspetta 60 secondi prima di verificare di nuovo
finally:
    print("Ubot1: script check_output.py stoppato")
    push = pb.push_note("Ubot1", " script check_output.py stoppato")
