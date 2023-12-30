from pyrogram import Client, filters
import asyncio

# Dizionario per tenere traccia dello stato di risposta per ogni chat
# chat id, tempo atteso
# numerico, {1: un ora, 2: 8 ore, 3: 24 ore, 4: 36 ore, any: 48}
# reply_waiting = {}
# rw_file = open('reply_waiting.txt', 'a+')


def get_tempo_atteso(chat_id):
    with open('reply_waiting.txt', 'r') as f:
        for line in f:
            parts = line.strip().split(';')
            # Controlla se il primo elemento (chat_id) è uguale a quello che stai cercando
            if parts[0] == str(chat_id):
                # Se trovi la corrispondenza, restituisci il valore num
                return int(parts[1])  # Converti il valore num in un intero


def get_ore_attese_id(chat_id):
    tempo_atteso = get_tempo_atteso(chat_id)

    if tempo_atteso == 1:
        return 1
    elif tempo_atteso == 2:
        return 8
    elif tempo_atteso == 3:
        return 24
    elif tempo_atteso == 4:
        return 36
    else:
        return 48


def get_ore_attese_t(tempo_atteso):

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


# bool invertito
def check_chat_for_reply_waiting(chat_id) -> bool:
    with open('reply_waiting.txt', 'r') as f:
        for line in f:
            # Dividi la linea usando il punto e virgola come separatore
            parts = line.strip().split(';')

            # Controlla se il primo elemento (chat_id) è uguale a quello che stai cercando
            if parts[0] == str(chat_id):
                return False
        return True


async def non_risposto(client, chat_id):
    ore_attese = get_ore_attese_id(chat_id)
    tempo_atteso = get_tempo_atteso(chat_id)
    await asyncio.sleep(ore_attese * 60 * 60 - get_ore_attese_t(tempo_atteso-1) * 60 * 60)  # un ora = 3600 secondi
    # await asyncio.sleep(ore_attese - get_ore_attese_t(tempo_atteso-1))  # un ora = 3600 secondi

    # Controlla se non hai ancora risposto
    if check_chat_for_reply_waiting(chat_id):
        return

    last_msg = None
    # Ottieni la cronologia della chat (ultimi 1 messaggi)
    async for message in client.get_chat_history(chat_id, limit=1):
        last_msg = message
    # Verifica se l'ultimo messaggio è stato inviato da te
    if last_msg.from_user != (await client.get_me()):
        ore_attese = get_ore_attese_id(chat_id)
        await client.send_message(chat_id=chat_id,
                                  text="! Messaggio automatico !\n"
                                       f"Chiedo Scusa se non ti ho ancora risposto nelle ultime {ore_attese} ore"
                                       f".\nTi contatterò appena mi è possibile.")
    with open("reply_waiting.txt", 'r+') as f:
        lines = f.readlines()
        f.seek(0)  # Posizionati all'inizio del file

        for line in lines:
            parts = line.split(';')

            # Controlla se il primo elemento (chat_id) è uguale a quello che stai cercando
            if parts[0] == str(chat_id):
                # Modifica il secondo valore della linea
                line = f"{parts[0]};{str(int(parts[1]) + 1)}\n"  # Sostituisci il secondo valore +1

            # Scrivi la linea modificata o non modificata nel file
            f.write(line)

        # Tronca il file per eliminare eventuali caratteri extra se il nuovo contenuto è più corto del vecchio
        f.truncate()
    await asyncio.create_task(non_risposto(client, chat_id))


@Client.on_message(filters.private & filters.incoming & ~filters.bot, group=3)
async def benvenuto(client, message):
    # with open("output.txt", "a") as file:
    # Ottieni il numero di messaggi nella chat
    chat_id = message.chat.id
    num_msg: int = await client.get_chat_history_count(chat_id=chat_id)

    # Se è il primo messaggio nella chat, invia il messaggio di benvenuto
    if num_msg == 1:
        # client.send_message(chat_id=message.chat.id, text="num_msg : " + str(num_messaggi))
        await client.send_message(chat_id=chat_id,
                                  text="! messaggio automatico !"
                                       "\nTi ringrazio di avermi contattato, ti risponderò appena possibile."
                                       "\nChiedo Scusa in anticipo per il tempo che potrei metterci, ma siete in "
                                       "tantissimi!")
        if check_chat_for_reply_waiting(chat_id):
            return
        with open('reply_waiting.txt', 'a') as file:
            file.write(f"{chat_id};1\n")
        await non_risposto(client, chat_id)

'''
            if num_msg < 10:
                file.write("true 10\n\n")
                nome_utente = message.from_user.first_name
                user_id = message.from_user.id
                testo = f"nome utente: {nome_utente}. id utente: {user_id}."

                client.send_message(chat_id=message.chat.id, text=testo)
            else:
            client.send_message(chat_id=message.chat.id, text="")
            file.write("false 10\n\n")

            client.send_message(chat_id=message.chat.id, text=vars(message.from_user))
'''


# vale anche per il bot stesso??
@Client.on_message(filters.private & filters.me, group=4)
def risposto(_, message):
    # print("risposto")
    chat_id = str(message.chat.id)
    with open("reply_waiting.txt", 'r+') as f:
        lines = f.readlines()
        f.seek(0)  # Posizionati all'inizio del file

        for line in lines:
            parts = line.split(';')

            # Controlla se il primo elemento (chat_id) è uguale a quello che stai cercando
            if parts[0] != chat_id:
                # Scrivi solo se non presente
                f.write(line)

        # Tronca il file per eliminare eventuali caratteri extra se il nuovo contenuto è più corto del vecchio
        f.truncate()
