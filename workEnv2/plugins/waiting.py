"""
questo file gestisce la reply waiting e il benvenuto
"""
from pyrogram import Client
from pyrogram.types import Message as Msg
from asyncio import Lock

# Creare un lock globale per evitare concorrenza durante la scrittura del file
lock_rw = Lock()


# Dizionario per tenere traccia dello stato di risposta per ogni chat
# chat id; tempo atteso
# numerico; {1: un ora, 2: 8 ore, 3: 24 ore, 4: 36 ore, any: 48}
# reply_waiting = {}


async def check_chat_for_reply_waiting(chat_id) -> bool:
    """ bool invertito """
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
    async def get_tempo_atteso() -> int:
        # Acquisire il lock prima di accedere al file
        async with lock_rw:
            for line_ in open('reply_waiting.txt', 'r'):
                parts_ = line_.strip().split(';')
                # Controlla se il primo elemento (chat_id) è uguale a quello che stai cercando
                if parts_[0] == str(chat_id):
                    # Se trovi la corrispondenza, restituisci il valore num
                    return int(parts_[1])  # Converti il valore num in un intero
        return 0

    async def get_ore_attese_id():
        return get_ore_attese_t(await get_tempo_atteso())

    def get_ore_attese_t(t_atteso: int) -> int:
        match t_atteso:
            case 0:
                return 0
            case 1:
                return 1
            case 2:
                return 8
            case 3:
                return 24
            case 4:
                return 36
            case _:
                return 48

    '''
    def get_ore_attese_t(tempo_atteso: int) -> int:
        return tempo_atteso**2
    '''
    # end def
    from asyncio import sleep, create_task
    ore_attese = await get_ore_attese_id()
    tempo_atteso = await get_tempo_atteso()
    if ore_attese is None or tempo_atteso is None:
        return
    time = ore_attese * 60 * 60 - get_ore_attese_t(tempo_atteso-1) * 60 * 60
    # time = ore_attese - get_ore_attese_t(tempo_atteso - 1)
    if time == 0:
        from .myParameters import TERMINAL_ID, PREFIX_COMMAND as PC
        await client.send_message(chat_id=TERMINAL_ID, text=f"una persona ha aspettato più di 48 ore."
                                                            f"id:\n(fare {PC}search in reply)")
        await client.send_message(chat_id=TERMINAL_ID, text=str(chat_id))
        return

    await sleep(time)  # un ora = 3600 secondi

    # Controlla se non hai ancora risposto dopo il tempo aspettato
    if await check_chat_for_reply_waiting(chat_id):
        return

    await sleep(1)
    from typing import Union
    last_msg: Union[None, Msg] = None
    # Ottieni la cronologia della chat (ultimi 1 messaggi)
    async for last_msg in client.get_chat_history(chat_id, limit=1):
        break
    if not isinstance(last_msg, Msg):
        print(f"file waiting.py | def non_risposto | il last_msg non è tipo Message | type: {type(last_msg)}")
    # Verifica se l'ultimo messaggio è stato inviato da te
    # if True:
    if not last_msg.from_user.is_self:
        ore_attese = await get_ore_attese_id()
        await client.send_message(chat_id=chat_id,
                                  text="! Messaggio automatico !\n"
                                       f"Chiedo Scusa se non ti ho ancora risposto nelle ultime {ore_attese} ore"
                                       f".\nTi contatterò appena mi è possibile.")
        from .handler import offline
        _ = create_task(offline(client, 2, "def: non_risposto; messaggio automatico"))

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
    _ = create_task(non_risposto(client, chat_id))


# @Client.on_message(f.private & f.incoming & ~f.bot, group=3)
async def benvenuto(client: Client, msg: Msg):
    # Ottieni il numero di messaggi nella chat
    chat_id = msg.chat.id
    num_msg: int = await client.get_chat_history_count(chat_id=chat_id)

    if num_msg == 1:
        from .handler import raw_lock, raw_msgs
        async with raw_lock:
            raw_msg = raw_msgs[msg.id][0]
        from pyrogram.raw.types import MessageService, MessageActionContactSignUp
        if isinstance(raw_msg, MessageService):
            if isinstance(raw_msg.action, MessageActionContactSignUp):
                await client.send_message(chat_id=chat_id,
                                          text="Benvenutə su telegram! Se hai bisogno di una guida oppure semplicemente "
                                               "abituarti a telegram conversiamo volentieri!")

    if num_msg > 2:
        return
        # pass
    async for hmsg in client.get_chat_history(chat_id):
        if hmsg.from_user.is_self:
            return
    from .myParameters import AUTO_MSG
    # client.send_message(chat_id=message.chat.id, text="num_msg : " + str(num_messaggi))
    await client.send_message(chat_id=chat_id, text=AUTO_MSG)
    if not await check_chat_for_reply_waiting(chat_id):  # false se è presente
        return
    async with lock_rw:
        open('reply_waiting.txt', 'a').write(f"{chat_id};1\n")
    await non_risposto(client, chat_id)


async def remove_rw(chat_id: str):
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
