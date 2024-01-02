from pyrogram import Client

'''
# from pyrogram.enums import ChatType
# from pyrogram.types import ForceReply
# import time
'''

# crea accanto a main.py il file clientParameter.py con dentro queste tre variabili, io l'ho messo in .gitignore
from clientParameter import t_id, t_hash, t_phone
'''
t_id = "id numerico"
t_hash = "hash alfanumerico"
t_phone = "numero di telefono"
'''

plugins = dict(root="plugins")

# terminal_id = -4030133781
terminal_id = -1001995530063  # update to supergroup

open("reply_waiting.txt", 'w').truncate()

app = Client("my_account", api_id=t_id, api_hash=t_hash, phone_number=t_phone, plugins=plugins)
# app = Client("my_account", api_id=t_id, api_hash=t_hash)

'''
@app.on_message(filters.command("test", "-") & filters.me)
def test(client, message):
    client.edit_message_text(chat_id=message.chat.id, message_id=message.id, text="test text")
'''

'''
@app.on_message(filters.mentioned & filters.group)
def replyoffline(client, message):
    me = client.get_users("me")
    if me.status == pyrogram.enums.UserStatus.OFFLINE:
        client.send_message(message.chat.id, "Al momento sono offline..", reply_to_message_id=message.id)
'''


with app:
    app.send_message(chat_id=terminal_id, text="Ready")
    print("READY")

try:
    app.run()
finally:
    app.start()
    app.send_message(chat_id=terminal_id, text="Stop")
    app.stop()
