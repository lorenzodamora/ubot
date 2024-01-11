import sys

sys.path.append('/home/ubuntu/Magnus/PycharmProj/ubot2/python/python3.12/site-packages')

# Ora puoi importare i moduli Pyrogram e TgCrypto
import pyrogram
import tgcrypto

# Resto del tuo script...


from pyrogram import Client
from myClientParameter import t_id, t_hash, t_phone
from plugins.myParameter import terminal_id as tid
app = Client("my_account2", api_id=t_id, api_hash=t_hash, phone_number=t_phone)
app.start()
app.send_message(chat_id=tid, text="Stop")
app.stop()
