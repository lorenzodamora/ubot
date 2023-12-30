'''
from pyrogram import Client, filters

terminal_id = -4030133781


async def log_event(text):
    # Registra l'evento nel file di log
    open("log.txt", "a").write(f"{text}\n")


@Client.on_user_status()
async def handle_user_status(_, status):
    # Registra il cambio di stato dell'utente nel file di log
    await log_event(f"status:{status}")
'''
