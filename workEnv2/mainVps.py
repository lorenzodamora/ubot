import sys

sys.path.append('/home/ubuntu/Magnus/PycharmProj/ubot2/python/python3.12/site-packages')

# Ora puoi importare i moduli Pyrogram e TgCrypto
import pyrogram
import tgcrypto

# Resto del tuo script...


from pyrogram import Client

# crea accanto a main.py il file myClientParameter.py con dentro queste tre variabili, io l'ho messo in .gitignore
from myClientParameter import t_id, t_hash, t_phone
from plugins.myParameter import terminal_id as tid
'''
t_id = "id numerico"
t_hash = "hash alfanumerico"
t_phone = "numero di telefono"
'''

plugins = dict(root="plugins")

open("reply_waiting.txt", 'w').truncate()

app = Client("my_account2", api_id=t_id, api_hash=t_hash, phone_number=t_phone, plugins=plugins)

with app:
    app.send_message(chat_id=tid, text="Ready")
    print("READY")

try:
    app.run()
finally:
    app.start()
    app.send_message(chat_id=tid, text="Stop")
    app.stop()
