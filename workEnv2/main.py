from pyrogram import Client

# crea accanto a main.py il file myClientParameter.py con dentro queste tre variabili, io l'ho messo in .gitignore
from myClientParameter import t_id, t_hash, t_phone, pushbullet_API_KEY as pushKey
from plugins.myParameter import terminal_id as tid
from pushbullet import Pushbullet
'''
t_id = "id numerico"
t_hash = "hash alfanumerico"
t_phone = "numero di telefono"
'''

pb = Pushbullet(pushKey)
plugins = dict(root="plugins")
open("reply_waiting.txt", 'w').truncate()
app = Client("my_account2", api_id=t_id, api_hash=t_hash, phone_number=t_phone, plugins=plugins)

with app:
    app.send_message(chat_id=tid, text="Ready")
    # print("READY")
    pb.push_note("Ubot2", "Ready")

try:
    app.run()
finally:
    # print("Stop")
    pb.push_note("Ubot2", "Stop")
    app.start()
    app.send_message(chat_id=tid, text="Stop")
    app.stop()
