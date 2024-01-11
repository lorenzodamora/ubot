from pyrogram import Client, filters as f
from pyrogram.types import Message as Msg
from asyncio import Lock

# Creare un lock globale per evitare concorrenza durante la scrittura del file
lock_rw = Lock()


# Dizionario per tenere traccia dello stato di risposta per ogni chat
# chat id; tempo atteso
# numerico; {1: un ora, 2: 8 ore, 3: 24 ore, 4: 36 ore, any: 48}
# reply_waiting = {}


async def get_tempo_atteso(chat_id) -> int:
    # Acquisire il lock prima di accedere al file
    async with lock_rw:
        for line in open('reply_waiting.txt', 'r'):
            parts = line.strip().split(';')
            # Controlla se il primo elemento (chat_id) è uguale a quello che stai cercando
            if parts[0] == str(chat_id):
                # Se trovi la corrispondenza, restituisci il valore num
                return int(parts[1])  # Converti il valore num in un intero
    return 0


async def get_ore_attese_id(chat_id):
    tempo_atteso = await get_tempo_atteso(chat_id)
    return get_ore_attese_t(tempo_atteso)


def get_ore_attese_t(tempo_atteso: int) -> int:
    if tempo_atteso == 0:
        return 0
    elif tempo_atteso == 1:
        return 1
    elif tempo_atteso == 2:
        return 8
    elif tempo_atteso == 3:
        return 24
    elif tempo_atteso == 4:
        return 36
    else:
        return 48


'''
def get_ore_attese_t(tempo_atteso: int) -> int:
    return tempo_atteso**2
'''


# bool invertito
async def check_chat_for_reply_waiting(chat_id) -> bool:
    # Acquisire il lock prima di accedere al file
    async with lock_rw:
        for line in open('reply_waiting.txt', 'r'):
            # Dividi la linea usando il punto e virgola come separatore
            parts = line.strip().split(';')

            # Controlla se il primo elemento (chat_id) è uguale a quello che stai cercando
            if parts[0] == str(chat_id):
                return False
    return True


async def non_risposto(client: Client, chat_id):
    import asyncio
    ore_attese = await get_ore_attese_id(chat_id)
    tempo_atteso = await get_tempo_atteso(chat_id)
    if ore_attese is None or tempo_atteso is None:
        return
    time = ore_attese * 60 * 60 - get_ore_attese_t(tempo_atteso-1) * 60 * 60
    # time = ore_attese - get_ore_attese_t(tempo_atteso - 1)
    if time == 0:
        from .myParameter import terminal_id
        await client.send_message(chat_id=terminal_id, text=f"una persona ha aspettato più di 48 ore."
                                                            f"id:\n(fare -search in reply)")
        await client.send_message(chat_id=terminal_id, text=str(chat_id))
        return
    await asyncio.sleep(time)  # un ora = 3600 secondi

    # Controlla se non hai ancora risposto
    if await check_chat_for_reply_waiting(chat_id):
        return

    await asyncio.sleep(1)
    from typing import Union
    last_msg: Union[None, Msg] = None
    while last_msg is None:
        # Ottieni la cronologia della chat (ultimi 1 messaggi)
        async for message in client.get_chat_history(chat_id, limit=1):
            last_msg = message
    # Verifica se l'ultimo messaggio è stato inviato da te
    from .myParameter import my_id
    if last_msg.from_user.id != my_id:
        ore_attese = await get_ore_attese_id(chat_id)
        await client.send_message(chat_id=chat_id,
                                  text="! Messaggio automatico !\n"
                                       f"Chiedo Scusa se non ti ho ancora risposto nelle ultime {ore_attese} ore"
                                       f".\nTi contatterò appena mi è possibile.")
        from .commands import offline
        _ = asyncio.create_task(offline(client, 2, "def: non_risposto; messaggio automatico"))

    async with lock_rw:
        with open("reply_waiting.txt", 'r+') as rwf:
            lines = rwf.readlines()
            rwf.seek(0)  # Posizionati all'inizio del file

            for line in lines:
                parts = line.split(';')

                # Controlla se il primo elemento (chat_id) è uguale a quello che stai cercando
                if parts[0] == str(chat_id):
                    # Modifica il secondo valore della linea
                    line = f"{parts[0]};{int(parts[1]) + 1}\n"  # Sostituisci il secondo valore +1

                # Scrivi la linea modificata o non modificata nel file
                rwf.write(line)

            # Tronca il file per eliminare eventuali caratteri extra se il nuovo contenuto è più corto del vecchio
            rwf.truncate()
    _ = asyncio.create_task(non_risposto(client, chat_id))


@Client.on_message(f.private & f.incoming & ~f.bot, group=3)
async def benvenuto(client: Client, message: Msg):
    # with open("output.txt", "a") as file:
    # Ottieni il numero di messaggi nella chat
    chat_id = message.chat.id
    num_msg: int = await client.get_chat_history_count(chat_id=chat_id)

    # Se è il primo messaggio nella chat, invia il messaggio di benvenuto
    if num_msg < 3:
        # client.send_message(chat_id=message.chat.id, text="num_msg : " + str(num_messaggi))
        await client.send_message(chat_id=chat_id,
                                  text="! messaggio automatico !"
                                       "\nTi ringrazio di avermi contattato, ti risponderò appena possibile."
                                       "\nChiedo Scusa in anticipo per il tempo che potrei metterci, ma siete in "
                                       "tantissimi!")
        if await check_chat_for_reply_waiting(chat_id):
            return
        async with lock_rw:
            open('reply_waiting.txt', 'a').write(f"{chat_id};1\n")
        await non_risposto(client, chat_id)


async def remove(chat_id: str):
    async with lock_rw:
        with open("reply_waiting.txt", 'r+') as rwf:
            lines = rwf.readlines()
            rwf.seek(0)  # Posizionati all'inizio del file

            for line in lines:
                parts = line.split(';')

                # Controlla se il primo elemento (chat_id) non è uguale a quello che stai cercando
                if parts[0] != chat_id:
                    # Scrivi solo se non presente
                    rwf.write(line)

            # Tronca il file per eliminare eventuali caratteri extra se il nuovo contenuto è più corto del vecchio
            rwf.truncate()


# vale anche per il bot stesso?? si, quindi attenzione all'ordine di chiamate
@Client.on_message(f.private & f.me, group=-1)
async def risposto(_, msg: Msg):
    if msg.text == "-1":
        return
    chat_id = str(msg.chat.id)
    # print(f"risposto in {chat_id}")
    # client.send_message(chat_id=terminal_id, text=chat_id)
    await remove(chat_id)
