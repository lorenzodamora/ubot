"""
questo file è l'event handler, evito di usare i filter per evitare certi strani bug
"""
from pyrogram import Client
from pyrogram.types import Message as Msg, Chat, User
from pyrogram.enums import ChatType
from pyrogram.raw.base import Update
from pyrogram.raw.types import UpdateNewMessage
from .myParameters import TERMINAL_ID, PREFIX_COMMAND as PC, PREFIX_SEND_TO as PS
from asyncio import create_task, Lock

raw_msgs = {}
raw_lock = Lock()
request_lock = Lock()


def check_cmd(cmd: str, comandi: dict[str, int]) -> bool:
    """
    Controlla se l'input dell'utente corrisponde a uno dei comandi specificati.

    Fa una corrispondenza key sensitive.

    :param cmd: Testo di input.
    :type cmd: str
    :param comandi: Dizionario contenente coppie key-value, dove:
        - Key (str): il testo del comando da cercare.
        - Value (int): il tipo di check da effettuare sul comando.
          - 1 '^$': 'only' cerca una corrispondenza esatta.
          - 2 '/': 'command' cerca se la stringa inizia con il testo del comando.
          - 3 '': 'within' cerca se è presente
    :type comandi: dict[str, int]
    :return: True se c'è una corrispondenza, False altrimenti.
    :rtype: bool
    :raises ValueError: Se il dizionario contiene un valore non valido per il tipo di check.
    """
    for key, value in comandi.items():
        key = key.lower()
        # cmd = cmd.lower()
        match value:
            case 1:
                if cmd == key:
                    return True
            case 2:
                if cmd.startswith(key):
                    return True
            case 3:
                if key in cmd:
                    return True
            case _:
                raise ValueError(f"Il dizionario contiene un valore non valido per il tipo di check: {value}\n"
                                 f"per i valori validi leggi la documentazione")
    return False


async def raw_remove(msg_id: int):
    from asyncio import sleep
    await sleep(60)

    async with raw_lock:
        if msg_id in raw_msgs:
            del raw_msgs[msg_id]


@Client.on_raw_update(group=0)
async def raw_handler(_, update: Update, __, ___):
    if isinstance(update, UpdateNewMessage):
        async with raw_lock:
            msg_id = update.message.id
            raw_msgs[msg_id] = []
            raw_msgs[msg_id].append(update.message)

        _ = create_task(raw_remove(msg_id))


@Client.on_message(group=1)
async def event_handler(client: Client, m: Msg):
    import chardet
    encode_valid = True
    if m.text:
        result = chardet.detect(m.text.encode())
        if str(result['encoding']) == 'None':
            encode_valid = False

    ch: Chat = m.chat
    fr_u: User = m.from_user
    c_type: ChatType = ch.type
    pvt = ChatType.PRIVATE
    is_pvt: bool = bool(m.chat and c_type == pvt)
    incoming: bool = not m.outgoing  # chat:"me" = True
    is_me: bool = bool(fr_u and fr_u.is_self or not incoming)

    # group -1
    if encode_valid and is_me and is_pvt and not (m.text and m.text.startswith(PC + '1')):
        from .waiting import remove_rw
        _ = create_task(remove_rw(str(ch.id)))

    if encode_valid and is_me and m.text:
        # group 1
        if m.text[0] == PC:
            _ = create_task(handle_commands(client, m))
        # group 2
        elif m.text[0] == PS:
            _ = create_task(handle_send_to(client, m))

    # group 3
    if is_pvt and incoming:
        from .waiting import benvenuto
        _ = create_task(benvenuto(client, m))

    # group 4 | handle_commands_for_other trigger: start with (MY_TAG + ' ' + PC + {cmd_txt})
    if encode_valid and incoming and m.text:
        from .myParameters import MY_TAG
        if m.text.lower().startswith(MY_TAG + ' ' + PC):
            _ = create_task(handle_commands_for_other(client, m))


# @Client.on_message(f.me & f.text & f.regex(r'^\,'), group=1)
async def handle_commands(client: Client, msg: Msg):
    from pyrogram.enums import ParseMode
    ps = ParseMode.DISABLED
    # Estrai il testo del messaggio dopo ","
    cmd_txt = msg.text[1:].lower()

    # ",." iniziali fanno in modo che venga scritto , senza comando
    if cmd_txt != "" and cmd_txt[0] == ".":
        await msg.edit_text(PC + msg.text[2:])

    # TODO rifare più ordinato, con parametri
    elif check_cmd(cmd_txt, {'h': 2, 'help': 2, '?': 2, 'commands': 2, 'c': 2}):
        await msg.delete()
        text = (f"**Lista di comandi**\n\nIl prefix è '{PC}'\n\n"
                f"`h` / `help` / `?` / `commands` / `c` : questo messaggio\n"
                "`0` : greetings\n`1` : Dammi un attimo + inserito in lista \"reply_waiting\"\n"
                "\nreply waiting::\n    `r` / `remove` : rimuovi dalla rw list la chat in cui hai scritto il comando\n"
                "    `grw` / `gw` : get reply waiting list (terminal)\n\n"
                "`del` : elimina il messaggio in reply\n"
                "`thisid` / `thisMsgId` / `MsgId` : modifica il messaggio col suo id\n"
                "  \"  __{n: int}__ : invia n messaggi con id\n"
                "`output` : stampa i file di output dei bot\n"
                "`auto` : \"uso i messaggi automatici perché..\"\n`offline` : setta offline il profilo\n"
                "`ping` : ping in chat\n`pingt` : ping in terminale\n`getall` / `ga` : su 4 file\n"
                "    `pga` / `printga` : stampa file ga in terminale\n"
                "`get` / `g` : getchat or getreply\n`getchat` : ottiene info base della chat\n"
                "`getreply` / `getr` : come getchat ma del reply\n`getid` / `id` : ottiene id della chat\n"
                "`getme` : ottiene l'istanza User di me stesso\n`search` : cerca per id o per username di un reply\n"
                "`moon` / `luna` : luna grafica UAU\n  \"  __{n: float / 0.1}__ : secondi tra una modifica e l'altra\n"
                "`null` / `vuoto` / `void` /  / `spazio` : manda il text di spazio vuoto, se metti in reply un "
                "messaggio lo mantiene\n"
                f"\ni comandi '{PS}' sono \"send to\"\n\n`p` / `pic` : inoltra il reply in pic(saved message forum)\n"
                f"`save` : inoltra in saved message\n"
                "`t` / `terminal` : inoltra il reply in terminale\n"
                "`2` : inoltra il reply al secondo profilo\n"
                f"\ni comandi {PC}. e {PS}. modificano annullando il comando e cancellando il punto")
        await client.send_message(chat_id=TERMINAL_ID, text=text)
        await client.send_message(
            chat_id=TERMINAL_ID,
            text="cos'è la lista \"reply waiting\" ?\n"
                 "ogni tot tempo va a scrivere alle persone in lista che ancora non sei riuscito a dedicargli tempo"
                 "\n\ncome funziona la lista \"reply waiting\" ?\n - funziona solo nelle private\n"
                 " - i tempi di attesa sono 1,8,24,36,48 ore. una volta raggiunto 48 ore, si stoppa"
                 "\n - lo invia solo se l'ultimo messaggio non è tuo\n"
                 " - come togliere una persona dalla lista? appena invii un messaggio a quella persona\n"
                 "     oppure comando r / remove\n"
                 " - per ottenere la lista: comando gw / grw"
        )

        '''
    elif cmd_txt == 'fold':
        from pyrogram.raw.functions.messages import GetDialogFilters
        from asyncio import sleep
        raw_folders = await client.invoke(GetDialogFilters())
        txt = str(vars(raw_folders))
        if txt == "":
            txt = "empty"
        chunk_s = 4096
        chunks = [txt[i:i + chunk_s] for i in range(0, len(txt), chunk_s)]

        for chunk in chunks:
            uncomplet = True
            while uncomplet:
                try:
                    await client.send_message(chat_id=TERMINAL_ID, text=str(chunk), parse_mode=ps)
                    uncomplet = False
                except:
                    await sleep(20)
            # end while
        # end for
        '''

    elif check_cmd(cmd_txt, {'del': 1}):
        await msg.delete()
        rmsg = msg.reply_to_message
        if not rmsg:
            await client.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PC}del")
            return
        await rmsg.delete()

        '''
    elif check_cmd(cmd_txt, {'del': 2}):
        await msg.delete()
        ids = []
        try:
            n = int(cmd_txt.split(" ")[1])
        except:
            n = 1
        try:
            rmsg = msg.reply_to_message
            start = rmsg.id if rmsg else msg.id - 1
            for i in range(0, n):
                ids.append(start - i)
            effettivi = await client.delete_messages(chat_id=msg.chat.id, message_ids=ids)
            x = 0
            while effettivi != n:
                x += 1
                effettivi += await client.delete_messages(chat_id=msg.chat.id, message_ids=start-n-x)
        except Exception as e:
            await client.send_message(chat_id=TERMINAL_ID, text=f"comando {msg.text}\n"
                                                                f"Errore:\n{e}\n{e.with_traceback(None)}")
        '''

    elif check_cmd(cmd_txt, {'thisid': 2, 'thisMsgId': 2, 'MsgId': 2}):
        rmsg = msg.reply_to_message
        if rmsg:
            await msg.edit_text(str(rmsg.id))
            return
        try:
            n = int(cmd_txt.split(" ")[1])
        except:
            n = 1
        await msg.edit_text(str(msg.id))
        n -= 1
        from asyncio import sleep
        for i in range(0, n):
            uncomplete = True
            while uncomplete:
                try:
                    msg = await client.send_message(chat_id=msg.chat.id, text="thisid")
                    uncomplete = False
                    await msg.edit_text(str(msg.id))
                except:
                    await sleep(10)

    # TODO parametri
    elif check_cmd(cmd_txt, {'output': 2}):
        from pyrogram.enums import ParseMode
        from platform import system
        ps = ParseMode.DISABLED
        await msg.delete()

        async def printoutput(path: str, title: str):
            txt = open(path, "r").read()
            if txt == "":
                txt = f"{title}: output.txt\n\nfile vuoto"
            else:
                txt = f"{title}: output.txt\n\n" + txt
            chunk_s = 4096
            chunks = [txt[i:i + chunk_s] for i in range(0, len(txt), chunk_s)]

            for chunk in chunks:
                uncomplet = True
                while uncomplet:
                    try:
                        await client.send_message(chat_id=TERMINAL_ID, text=str(chunk), parse_mode=ps)
                        uncomplet = False
                    except:
                        await sleep(20)
                # end while
            # end for

        # End def
        if system() == "Windows":
            from .myParameters import ubot1_output, ubot2_output, infobot_output, meteo_output
            await printoutput(ubot1_output, "Ubot1")
            await printoutput(ubot2_output, "Ubot2")
            await printoutput(infobot_output, "Infobot")
            await printoutput(meteo_output, "MeteoATbot")
        elif system() == "Linux":
            from .myParameters import all_output
            import os

            # Filtra solo i file di collegamento
            shortcut_files = [file for file in os.listdir(all_output) if os.path.islink(os.path.join(all_output, file))]
            # Itera sui file di collegamento
            for shortcut_file in shortcut_files:
                percorso_collegamento = os.path.join(all_output, shortcut_file)
                percorso_file = os.path.realpath(percorso_collegamento)

                await printoutput(percorso_file, shortcut_file)

    elif check_cmd(cmd_txt, {'pga': 1, 'printga': 1}):
        from pyrogram.enums import ParseMode
        from os.path import exists
        ps = ParseMode.DISABLED
        await msg.delete()

        async def printoutput(path: str):
            if not exists(path):
                await client.send_message(chat_id=TERMINAL_ID, text=f"il file {path} non esiste", parse_mode=ps)
                return
            txt = open(path, "r").read()
            if txt == "":
                txt = f"{path[3:]}: \n\nfile vuoto"
            else:
                txt = f"{path[3:]}: \n\n" + txt
            chunk_s = 4096
            chunks = [txt[i:i + chunk_s] for i in range(0, len(txt), chunk_s)]

            for chunk in chunks:
                uncomplet = True
                while uncomplet:
                    try:
                        await client.send_message(chat_id=TERMINAL_ID, text=str(chunk), parse_mode=ps)
                        uncomplet = False
                    except:
                        await sleep(20)
                # end while
            # end for

        # End def
        from os import listdir
        for file in [f for f in listdir("./ga")]:
            await printoutput(f"ga/{file}")
        await client.send_message(chat_id=TERMINAL_ID, text="end print")

    elif check_cmd(cmd_txt, {'0': 1}):
        await client.edit_message_text(chat_id=msg.chat.id, message_id=msg.id,
                                       text="buondì\ncome va?")

    elif check_cmd(cmd_txt, {'1': 1}):
        from pyrogram.enums import ChatType as Ct
        import asyncio  # offline
        chat_id = msg.chat.id
        await client.edit_message_text(chat_id=chat_id, message_id=msg.id,
                                       text="Dammi un attimo e ti scrivo subito.")
        _ = asyncio.create_task(offline(client, 5, f"comando {PC}1"))
        if msg.chat.type != Ct.PRIVATE:
            return
        from .waiting import check_chat_for_reply_waiting, non_risposto, lock_rw
        if not await check_chat_for_reply_waiting(chat_id):
            return
        async with lock_rw:
            open('reply_waiting.txt', 'a').write(f"{chat_id};1\n")
        await non_risposto(client, chat_id)

    elif check_cmd(cmd_txt, {'r': 1, 'remove': 1}):
        c_id = msg.chat.id
        await msg.delete()
        from .waiting import remove_rw
        await remove_rw(str(c_id))

    elif check_cmd(cmd_txt, {'grw': 1, 'gw': 1}):
        await msg.delete()
        from .waiting import lock_rw
        async with lock_rw:
            text = open('reply_waiting.txt', "r").read()
        if text == "":
            text = "reply_waiting.txt\n\nfile vuoto"
        else:
            text = "reply_waiting.txt\n\n" + text
        await client.send_message(chat_id=TERMINAL_ID, text=text)

    elif check_cmd(cmd_txt, {'auto': 1}):
        await client.edit_message_text(chat_id=msg.chat.id, message_id=msg.id,
                                       text="uso i messaggi automatici solo per far prima e poter gestire più persone,"
                                            "senza andare ad ignorare qualcuno involontariamente")

    # TODO parametro seconds
    elif check_cmd(cmd_txt, {'offline': 2}):
        await msg.delete()
        await offline(client, 5, f"{PC}offline")

    elif check_cmd(cmd_txt, {'ping': 2}):
        await pong(client, msg, cmd_txt != "ping")

    # TODO parameters
    elif check_cmd(cmd_txt, {'getall': 2, 'ga': 2}):
        await msg.delete()
        # Crea la directory se non esiste già
        from os import makedirs
        from os.path import exists
        if not exists("./ga"):
            makedirs("./ga")

        def custom_serializer(obj):
            if isinstance(obj, Client):
                return str(obj)

        from json import dumps
        open("ga/ga_msg.txt", "w", encoding='utf-8').write(
            str(dumps(vars(msg), indent=2, default=custom_serializer)))
        open("ga/ga_chat.txt", "w", encoding='utf-8').write(
            str(dumps(vars(await client.get_chat(msg.chat.id)), indent=2, default=custom_serializer)))
        if msg.reply_to_message:
            open("ga/ga_rmsg.txt", "w", encoding='utf-8').write(
                str(dumps(vars(msg.reply_to_message), indent=2, default=custom_serializer)))
            open("ga/ga_rchat.txt", "w", encoding='utf-8').write(str(
                dumps(vars(await client.get_chat(msg.reply_to_message.chat.id)), indent=2, default=custom_serializer)))
        else:
            open("ga/ga_rmsg.txt", "w", encoding='utf-8').write("")
            open("ga/ga_rchat.txt", "w", encoding='utf-8').write("")
        await client.send_message(chat_id=TERMINAL_ID, text=f"creati 4 file dal comando {PC}getAll\n"
                                                            f"per stamparli: {PC}pga o printga")

    elif check_cmd(cmd_txt, {'g': 1, 'get': 1}):
        msg.text = PC + ('getr' if msg.reply_to_message else 'getchat')
        await handle_commands(client, msg)

    elif check_cmd(cmd_txt, {'getchat': 1}):
        c_id: int = msg.chat.id
        await client.delete_messages(chat_id=c_id, message_ids=msg.id)
        await getchat(client, await client.get_chat(c_id))

    elif check_cmd(cmd_txt, {'getr': 1, 'getreply': 1}):
        await msg.delete()
        # Ottieni il messaggio di risposta
        rmsg = msg.reply_to_message
        # Verifica se il messaggio ha una risposta
        if not rmsg:
            await client.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PC}getreply")
            return
        await getchat(client, await client.get_chat(rmsg.chat.id))

    elif check_cmd(cmd_txt, {'getid': 1, 'id': 1}):
        id_ = msg.reply_to_message.from_user.id if msg.reply_to_message else msg.chat.id
        await msg.delete()
        await client.send_message(chat_id=TERMINAL_ID, text=str(id_))

    # TODO get full user
    elif check_cmd(cmd_txt, {'getme': 1}):
        await msg.delete()

        def custom_serializer(obj):
            if isinstance(obj, Client):
                return str(obj)

        from json import dumps
        text = str(dumps(vars(await client.get_me()), indent=2, default=custom_serializer))
        await client.send_message(chat_id=TERMINAL_ID, text='\n\''.join(text))

    # TODO parametro
    elif check_cmd(cmd_txt, {'search': 2}):
        await msg.delete()
        # Verifica se il messaggio ha una risposta
        rmsg = msg.reply_to_message
        if not rmsg:
            await client.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PC}search")
            return
        try:
            chat = await client.get_chat(rmsg.text)
            await getchat(client, chat)
        except Exception as e:
            await client.send_message(chat_id=TERMINAL_ID, text=f"{e}\n\nil comando cerca per id o per username",
                                      parse_mode=ps)

    elif check_cmd(cmd_txt, {'moon': 2, 'luna': 2}):
        moon_list = ["🌕", "🌖", "🌗", "🌘", "🌑", "🌒", "🌓", "🌔"]
        from asyncio import sleep, create_task
        try:
            sec = float(cmd_txt.split(" ")[1])
        except:
            sec = 0.1
        if sec < 0.1:
            sec = 0.1
        for _ in range(30):
            moon_list = moon_list[-1:] + moon_list[:-1]
            text = ''.join(moon_list[:5]) + "ㅤ"
            try:
                _ = create_task(msg.edit_text(text))
            except:
                pass
            await sleep(sec)

    elif check_cmd(cmd_txt, {'strikethrough': 1, 'done': 1, 'v': 1}):
        rmsg = msg.reply_to_message
        if not rmsg and not rmsg.text and rmsg.from_user.is_self:
            await client.send_message(TERMINAL_ID, f"il comando {PC}done vuole un reply a un mio text msg")
            return
        try:
            await rmsg.edit_text(f"~~{rmsg.text}~~")
        except Exception as e:
            await client.send_message(TERMINAL_ID, f"errore in {msg.text}:\n{e}")
        await msg.delete()

    elif cmd_txt in ['null', 'vuoto', 'void', ' ', '', 'spazio', None]:
        await msg.delete()
        rmsg = msg.reply_to_message
        if rmsg:
            await rmsg.reply_text("ㅤ")
        else:
            await client.send_message(chat_id=msg.chat.id, text="ㅤ")

    else:
        c_id = msg.chat.id
        await msg.delete()
        await client.send_message(
            chat_id=TERMINAL_ID,
            text=f"! Nessun comando trovato !\n{msg.text}\nchat:{c_id if c_id != TERMINAL_ID else 'this chat'}"
        )


# @Client.on_message(f.me & f.text & f.regex(r'^\>'), group=2)
async def handle_send_to(client: Client, msg: Msg):
    cmd_txt = msg.text[1:].lower()
    c_id = msg.chat.id

    # ">." iniziali fanno in modo che venga scritto > senza comando
    if cmd_txt != "" and cmd_txt[0] == ".":
        await msg.edit_text(PS + msg.text[2:])

    elif check_cmd(cmd_txt, {"pic": 1, "p": 1}):
        await msg.delete()
        if not msg.reply_to_message:
            await client.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PS}pic")
            return
        from .pyrogram_forward_to_topic import forward_to_topic as for_top
        from .myParameters import SAVED_MESSAGE_FORUM_ID, PIC_TOPIC_ID
        await for_top(source_channel_id=c_id, destination_channel_id=SAVED_MESSAGE_FORUM_ID,
                      forwarded_message_id=msg.reply_to_message_id, topic_init_message_id=PIC_TOPIC_ID, client=client)

    elif cmd_txt == 'save':
        await msg.delete()
        if not msg.reply_to_message:
            await client.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PS}save")
            return
        await client.forward_messages("me", msg.chat.id, msg.reply_to_message_id)

    # TODO parametri
    elif check_cmd(cmd_txt, {"t": 2, "terminal": 2}):
        await msg.delete()
        if not msg.reply_to_message:
            await client.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PS}terminal")
            return
        await client.forward_messages(chat_id=TERMINAL_ID, from_chat_id=c_id,
                                      message_ids=msg.reply_to_message_id)

    elif check_cmd(cmd_txt, {'2': 1}):
        await msg.delete()
        from .myParameters import MY_ID2
        await client.forward_messages(chat_id=MY_ID2, from_chat_id=c_id,
                                      message_ids=msg.reply_to_message_id)

    else:
        await msg.delete()
        await client.send_message(
            chat_id=TERMINAL_ID,
            text=f"! Nessun comando trovato !\n{msg.text}\nchat:{c_id if c_id != TERMINAL_ID else 'this chat'}"
        )


# group 4 | handle_commands_for_other trigger: start with (MY_TAG + ' ' + PC + {cmd_txt}
# if incoming and m.text:
async def handle_commands_for_other(client: Client, msg: Msg):
    async with request_lock:
        async def log():
            cmsg = await client.send_message(TERMINAL_ID, f"Nella chat {msg.chat.id} è stato richiesto da "
                                                          f"{msg.from_user.id} il comando\n{msg.text}")
            await cmsg.reply_text(str(msg.chat.id))
            await cmsg.reply_text(str(msg.from_user.id if msg.from_user is not None else None))

        # end def
        from asyncio import create_task
        _ = create_task(log())
        from .myParameters import MY_TAG
        # from pyrogram.enums import ParseMode
        # ps = ParseMode.DISABLED
        # mytaglen = len(MY_TAG)
        # pre_len = len(MY_TAG + ' ' + PC)
        # cmd_txt = msg.text[pre_len:].lower()
        cmd_txt = msg.text[len(MY_TAG + ' ' + PC):].lower()

        if check_cmd(cmd_txt, {'h': 2, 'help': 2, '?': 2, 'commands': 2, 'c': 2}):
            text = (f"Richieste: una ogni 20 sec, esclusa esecuzione, tutte in coda (in teoria)\n"
                    f"Lista di comandi\n\nIl prefix è {MY_TAG + ' ' + PC}\n\n"
                    f"h = help = ? = commands = c : questo messaggio\n"
                    "moon = luna : luna grafica UAU\n  \"  {n: float = 0.1} : secondi tra una modifica e l'altra\n"
                    "pipo : ascii art\n  \"  {n: int = rnd} : scelta del pipo, da 0 a 3 compresi\n"
                    "null = vuoto = void =  = spazio : manda il text di spazio vuoto, se metti in reply un messaggio"
                    " lo mantiene\n"
                    )
            await msg.reply_text(text)

        elif check_cmd(cmd_txt, {'moon': 2, 'luna': 2}):
            moon_list = ["🌕", "🌖", "🌗", "🌘", "🌑", "🌒", "🌓", "🌔"]
            from asyncio import sleep, create_task
            msg = await msg.reply_text("LUNA UAU")
            try:
                sec = float(cmd_txt.split(" ")[1])
            except:
                sec = 0.1
            if sec < 0.1:
                sec = 0.1
            for _ in range(30):
                moon_list = moon_list[-1:] + moon_list[:-1]
                text = ''.join(moon_list[:5]) + "ㅤ"
                try:
                    _ = create_task(msg.edit_text(text))
                except:
                    pass
                await sleep(sec)

        elif check_cmd(cmd_txt, {'pipo': 2}):
            try:
                num = int(cmd_txt.split(" ")[1])
            except:
                import random
                num = random.randint(0, 3)

            match num:
                case 0:
                    text = ("..............\u2584\u2584 \u2584\n........\u2590\u2590\u2591\u2591\u2580\u2591\u2591"
                            "\u2590\u2590\n..... \u2590\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u258c"
                            "\n...\u2590\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u258c\n....\u2590"
                            "\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u258c\n....\u2590\u2580\u2584"
                            "\u2584\u2584\u2584\u2584\u2584\u2584\u2584\u2580\u258c\n....\u2590\u2591\u2591\u2591\u2591"
                            "\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n....\u2590\u2591\u2591\u2591\u2591\u2591\u2591"
                            "\u2591\u2591\u2591\u2591\u258c\n....\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591"
                            "\u2591\u2591\u258c\n....\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591"
                            "\u258c\n....\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n...."
                            "\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n....\u2590\u2591"
                            "\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n....\u2590\u2591\u2591\u2591"
                            "\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n....\u2590\u2591\u2591\u2591\u2591\u2591"
                            "\u2591\u2591\u2591\u2591\u2591\u258c\n....\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u2591"
                            "\u2591\u2591\u2591\u258c\n..\u2590.\u2580\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592"
                            "\u2592\u2592\u2580\u2590\n..\u2584\u2580\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591"
                            "\u2591\u2591\u2591\u2591\u2580\u2584\n.\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u2591"
                            "\u2580\u2584\u2592\u2584\u2580\u2591\u2591\u2591\u2591\u258c\n\u2590\u2591\u2591\u2591"
                            "\u2591\u2591\u2591\u2591\u2592\u2592\u2590\u2592\u2592\u2591\u2591\u2591\u2591\u2591"
                            "\u258c\n\u2590\u2592\u2591\u2591\u2591\u2591\u2591\u2592\u2592\u2592\u2590\u2592\u2592"
                            "\u2592\u2591\u2591\u2591\u2592\u258c\n.\u2580\u2584\u2592\u2592\u2592\u2592\u2592\u2584"
                            "\u2580\u2592\u2580\u2584\u2592\u2592\u2592\u2592\u2584,")
                case 1:
                    text = ("\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u281f\u2820"
                            "\u2870\u28d5\u28d7\u28f7\u28e7\u28c0\u28c5\u2818\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff"
                            "\u28ff\u28ff\u28ff\u28ff\u28ff\u2803\u28e0\u28f3\u28df\u28ff\u28ff\u28f7\u28ff\u287f"
                            "\u28dc\u2804\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u28ff\u28ff\u287f\u2801\u2804"
                            "\u28f3\u28b7\u28ff\u28ff\u28ff\u28ff\u287f\u28dd\u2816\u2804\u28ff\u28ff\u28ff\u28ff"
                            "\u28ff \u28ff\u28ff\u28ff\u28ff\u2803\u2804\u28a2\u2879\u28ff\u28b7\u28ef\u28bf\u28b7"
                            "\u286b\u28d7\u280d\u28b0\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u28ff\u284f\u2880"
                            "\u2884\u2824\u28c1\u280b\u283f\u28d7\u28df\u286f\u284f\u288e\u2801\u28b8\u28ff\u28ff"
                            "\u28ff\u28ff\u28ff \u28ff\u28ff\u28ff\u2804\u2894\u2895\u28ef\u28ff\u28ff\u2872\u2864"
                            "\u2844\u2864\u2804\u2840\u28a0\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u2807"
                            "\u2820\u2873\u28ef\u28ff\u28ff\u28fe\u28b5\u28eb\u288e\u288e\u2806\u2880\u28ff\u28ff"
                            "\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u2804\u28a8\u28eb\u28ff\u28ff\u287f\u28ff"
                            "\u28fb\u288e\u2857\u2855\u2845\u28b8\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff"
                            "\u28ff\u2804\u289c\u28be\u28fe\u28ff\u28ff\u28df\u28d7\u28af\u286a\u2873\u2840\u28b8"
                            "\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u2804\u28b8\u28bd\u28ff\u28f7"
                            "\u28ff\u28fb\u286e\u2867\u2873\u2871\u2841\u28b8\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff"
                            " \u28ff\u28ff\u2844\u28a8\u28fb\u28fd\u28ff\u28df\u28ff\u28de\u28d7\u287d\u2878\u2850"
                            "\u28b8\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u2847\u2880\u2897\u28ff"
                            "\u28ff\u28ff\u28ff\u287f\u28de\u2875\u2863\u28ca\u28b8\u28ff\u28ff\u28ff\u28ff\u28ff"
                            "\u28ff\u28ff \u28ff\u28ff\u28ff\u2840\u2863\u28d7\u28ff\u28ff\u28ff\u28ff\u28ef\u286f"
                            "\u287a\u28fc\u280e\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u28ff\u28e7"
                            "\u2810\u2875\u28fb\u28df\u28ef\u28ff\u28f7\u28df\u28dd\u289e\u287f\u28b9\u28ff\u28ff"
                            "\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u28ff\u28ff\u2846\u2898\u287a\u28fd\u28bf\u28fb"
                            "\u28ff\u28d7\u2877\u28f9\u28a9\u2883\u28bf\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff"
                            "\u28ff\u28ff\u28f7\u2804\u282a\u28ef\u28df\u28ff\u28af\u28ff\u28fb\u28dc\u288e\u2886\u281c\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u28ff\u28ff\u28ff\u2846\u2804\u28a3\u28fb\u28fd\u28ff\u28ff\u28df\u28fe\u286e\u287a\u2878\u2838\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u287f\u281b\u2809\u2801\u2804\u2895\u2873\u28fd\u287e\u28ff\u28bd\u28ef\u287f\u28ee\u289a\u28c5\u2839\u28ff\u28ff\u28ff \u287f\u280b\u2804\u2804\u2804\u2804\u2880\u2812\u281d\u28de\u28bf\u287f\u28ff\u28fd\u28bf\u287d\u28e7\u28f3\u2845\u280c\u283b\u28ff \u2801\u2804\u2804\u2804\u2804\u2804\u2810\u2850\u2831\u2871\u28fb\u287b\u28dd\u28ee\u28df\u28ff\u28fb\u28f7\u28cf\u28fe")
                case 2:
                    text = ("\u28a0\u28de\u28fb\u28ff\u28f6\u28e4\u2840                   \n\u28b8\u28ff\u28ff\u28ff"
                            "\u28ff\u28ff\u28ff\u28e6                  \n\u28b8\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff"
                            "\u28ff\u2840                 \n \u28bb\u28ff\u28ff\u28ff\u28ff\u28ff\u28df\u28f5\u28e6\u2840               \n  \u2808\u2833\u28bf\u28fb\u28f5\u28ff\u28ff\u28ff\u28f7\u28c4              \n    \u2818\u28bf\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28f7\u28c4            \n      \u2839\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28f7\u28e6\u28c0         \n       \u2808\u283b\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28f6\u28e4\u28e4\u28e4\u2840   \n         \u2808\u283b\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u2846  \n           \u2808\u2819\u283f\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff  \n              \u2808\u2819\u283f\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u2847 \n               \u28e0\u28fe\u28f6\u28b9\u28ff\u28ff\u28ff\u28ff\u28ff\u28f7 \n              \u28f0\u28ff\u28ff\u284f\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u2847\n              \u28ff\u28ff\u28ff\u28b0\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28f7\n              \u281b\u283f\u283f\u2838\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u284f\n                  \u2819\u283f\u28ff\u28ff\u28ff\u287f\u281f")
                case 3:
                    text = ("....... \u2584\u2588\u2593\u2591\u2591\u2591\u2591\u2591\u2591\u2593\u2588\u2584\n...."
                            "\u2584\u2580\u2591\u2591\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\u2591\u2592"
                            "\u258c\n.\u2590\u2591\u2591\u2591\u2591\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\u2591\u2591\u2591\u258c\n\u2590 \u2591\u2591\u2591\u2591\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\u2591\u2591\u2591\u2590\n\u2590 \u2592\u2591\u2591\u2591 \u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\u2591\u2592\u2592\u2590\n\u2590 \u2592\u2591\u2591\u2591\u2591\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\u2591\u2592\u2590\n..\u2580\u2584\u2592\u2592\u2592\u2592\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\u2584\u2580\n........ \u2580\u2580\u2580 \u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n.................\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n.................\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n.................\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n.................\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n.................\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n................\u2590\u2584\u2580\u2580\u2580\u2580\u2580\u2584\u258c\n...............\u2590\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u258c\n...............\u2590\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u258c\n................\u2590\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u258c\n..................\u2580\u258c\u2592\u2580\u2592\u2590\u2580")
                case _:
                    text = "error. i numeri disponibili sono: 0, 1, 2, 3"
            await msg.reply(text)

        elif cmd_txt in ['null', 'vuoto', 'void', ' ', '', 'spazio', None]:
            await (msg.reply_to_message if msg.reply_to_message else msg).reply_text("ㅤ")

        else:
            await msg.reply_text(f"! Nessun comando trovato !\n{msg.text}")

        from asyncio import sleep
        await sleep(20)


async def getchat(client: Client, chat: Chat):
    from pyrogram.enums import ChatType as Ct
    text = f"id:{chat.id}\ntype:{chat.type}\ntitle:{chat.title}\nusername:{chat.username}\nname:{chat.first_name}"
    text += f", {chat.last_name}\n" if chat.last_name is not None else '\n'
    if chat.type in [Ct.GROUP, Ct.SUPERGROUP]:
        text += (f"inviteLink:{chat.invite_link}\nmembri:{chat.members_count}\n"
                 f"description:{chat.description}\n")
    elif chat.type == Ct.PRIVATE:
        text += f"bio:{chat.bio}\n"
        text += f"phone:{getattr(chat, 'phone_number', 'non presente')}\n"
        text += f"restrictions:{getattr(chat, 'restrictions', 'non presente')}\n\n"
    await client.send_message(chat_id=TERMINAL_ID, text=text)
    if chat.type != Ct.PRIVATE:
        return
    text = f"common chats:\n\n"
    chatlist = await client.get_common_chats(chat.id)
    for ch in chatlist:
        text += f"id:{ch.id}\ntype:{ch.type}\ntitle:{ch.title}\nusername:{ch.username}\nname:{ch.first_name}"
        text += f", {ch.last_name}\n" if ch.last_name is not None else '\n'
        text += f"inviteLink:{ch.invite_link}\nmembri:{ch.members_count}\ndescription:{ch.description}\n\n"
    await client.send_message(chat_id=TERMINAL_ID, text=text)


async def pong(client: Client, msg: Msg, send_terminal=False):
    from time import perf_counter
    await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
    text = "📶 Pong!"
    chatid = TERMINAL_ID if send_terminal else msg.chat.id
    msg = await client.send_message(chat_id=chatid, text=text)
    for i in range(1, 5):
        start = perf_counter()
        await msg.edit("📶 Pong!! 📶")
        end = perf_counter()
        text += f"\n{int((end - start) * 1000)}ms"
        await msg.edit(text)


async def offline(client: Client, seconds: int, from_: str):
    from pyrogram.raw.functions.account import UpdateStatus  # offline
    from asyncio import sleep  # offline
    await client.send_message(chat_id=TERMINAL_ID,
                              text=f"Verrai settato offline tra {seconds},{seconds * 2},"
                                   f"{seconds * 3} e {seconds * 4}s\n"
                                   f"from: {from_}")
    await client.invoke(UpdateStatus(offline=True))  # 0s
    await sleep(seconds)
    await client.invoke(UpdateStatus(offline=True))  # 5s
    await sleep(seconds)
    await client.invoke(UpdateStatus(offline=True))  # 10s
    await sleep(seconds)
    await client.invoke(UpdateStatus(offline=True))  # 15s
    await sleep(seconds)
    await client.invoke(UpdateStatus(offline=True))  # 20s
