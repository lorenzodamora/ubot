import sys

sys.path.append('/home/ubuntu/Magnus/PycharmProj/ubot/python/python3.12/site-packages')

# Ora puoi importare i moduli Pyrogram e TgCrypto
import pyrogram
import tgcrypto

# Resto del tuo script...


from pyrogram import Client
from myClientParameter import t_id, t_hash, t_phone, pushbullet_API_KEY as pushKey
from plugins.myParameter import terminal_id as tid
from pushbullet import Pushbullet
app = Client("my_account1", api_id=t_id, api_hash=t_hash, phone_number=t_phone)
app.start()
app.send_message(chat_id=tid, text="Stop")
app.stop()
Pushbullet(pushKey).push_note("Ubot1", "Stop")
