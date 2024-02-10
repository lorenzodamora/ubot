from pushbullet import Pushbullet
from time import sleep
from os.path import getmtime
from pushbullet_APIKEY import API_KEY
# Imposta la tua chiave API Pushbullet
# API_KEY = 'https://www.pushbullet.com/#settings'
pb = Pushbullet(API_KEY)
# Percorso al file da monitorare
file_path = './output.txt'
# Leggi lo stato iniziale del file
last_modified_time = getmtime(file_path)
title = "Ubot1"
print(f"{title}: script check_output.py partito")
pb.push_note(title, " script check_output.py partito")
try:
    while True:
        # Verifica se il file è stato modificato
        current_modified_time = getmtime(file_path)
        if current_modified_time != last_modified_time:
            # Invia una notifica Pushbullet
            pb.push_note(title, " ha mandato testo in terminale. apri il file output.txt")
            # Aggiorna il tempo dell'ultima modifica
            last_modified_time = current_modified_time
        # Attendi un po' prima di verificare nuovamente
        sleep(60)  # Aspetta 60 secondi prima di verificare di nuovo
finally:
    print(f"{title}: script check_output.py stoppato")
    pb.push_note(title, " script check_output.py stoppato")
