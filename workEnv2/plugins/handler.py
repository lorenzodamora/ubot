"""
event handler
evito di usare i filter per evitare certi strani bug
"""
from pyrogram import Client
from pyrogram.types import Message as Msg, Chat, User
from pyrogram.enums import ChatType
from .myParameters import TERMINAL_ID, PREFIX_COMMAND as PC, PREFIX_SEND_TO as PS, MY_TAG
from asyncio import create_task, Lock, sleep

request_lock = Lock()
commands = {
    '?': {
        'alias': ['h', 'help', '?', 'commands', 'c'],
        'type': 2,
        'note': "see help menu",
        'group': "generic",
        'other': True
    },
    '?+': {
        'alias': ['h+', 'help+', '?+', 'commands+', 'c+'],
        'type': 1,
        'note': "see extra help info",
        'group': "generic",
    },
    'automatici': {
        'alias': ['auto'],
        'type': 1,
        'note': "\"uso i messaggi automatici perché..\"",
        'group': "fast"
    },
    'delete': {
        'alias': ['del'],
        'type': 2,
        'note': "delete replyed msg (wip: arg num msg)",
        'group': "service-cmd"
    },
    'eval': {
        'alias': ['eval', 'exec'],
        'type': 2,
        'note': "`eval h` / `exec ?` to see this help",
        'group': "service-cmd"
    },
    'eval reply': {
        'alias': ['reval', 'rexec'],
        'type': 2,
        'note': "`reval h` / `rexec ?` to see this help",
        'group': "service-cmd"
    },
    'eval file': {
        'alias': ['feval', 'fexec', 'fe'],
        'type': 2,
        'note': "`fe h` to see this help",
        'group': "service-cmd"
    },
    'gets': {
        'alias': ['get', 'g'],
        'type': 1,
        'note': "getchat or getreply",
        'group': "get"
    },
    'get msg id': {
        'alias': ['thisid', 'thisMsgId', 'MsgId'],
        'type': 2,
        'note': "edit text with his id\n__{n?: int = 1}__ : send n message with id",
        'group': "get",
        'other': True
    },
    'getall': {
        'alias': ['getAll', 'ga'],
        'type': 1,
        'note': "edit text with his id\n__{n: int}__ : send n message with id",
        'group': "get"
    },
    'getall print': {
        'alias': ['pga', 'printga'],
        'type': 1,
        'note': "print all ga files",
        'group': "print"
    },
    'getchat': {
        'alias': ['getchat', 'gc'],
        'type': 1,
        'note': "get basic info of chat",
        'group': "get"
    },
    'getchat reply': {
        'alias': ['getreply', 'getr'],
        'type': 1,
        'note': " = getchat, but of reply",
        'group': "get"
    },
    'getid': {
        'alias': ['getid', 'id'],
        'type': 1,
        'note': "get id of chat",
        'group': "get"
    },
    'getme': {
        'alias': ['getme'],
        'type': 1,
        'note': "get User instance of myself",
        'group': "get"
    },
    'get reply waiting': {
        'alias': ['grw', 'gw'],
        'type': 1,
        'note': "get reply waiting list (terminal)",
        'group': "reply-wait"
    },
    'greetings': {
        'alias': ['0'],
        'type': 2,
        'note': "write \"buondì\\n come va?\"\n arg: 'e' for english version",
        'group': "fast"
    },
    'moon': {
        'alias': ['moon', 'luna'],
        'type': 2,
        'note': "graphic moon UAU\n__{n: float / 0.1}__ : seconds between edits",
        'group': "special",
        'other': True
    },
    'null': {
        'alias': ['null', 'vuoto', 'void', '', 'spazio', 'space'],
        'type': 0,
        'note': "sends the text with empty space, if you reply a message it keeps it",
        'group': "special",
        'other': True
    },
    'offline': {
        'alias': ['offline', 'off'],
        'type': 2,
        'note': "set your status offline (wip: arg)",
        'group': "service-cmd"
    },
    'output': {
        'alias': ['output', 'out', 'po'],
        'type': 2,
        'note': "print output files (wip: arg)",
        'group': "print"
    },
    'pic': {
        'alias': ['p', 'pic'],
        'type': 1,
        'note': "forward reply to pic topic",
        'group': "send to"
    },
    'ping': {
        'alias': ['ping'],
        'type': 1,
        'note': "ping in chat",
        'group': "service-cmd"
    },
    'pingt': {
        'alias': ['pingt'],
        'type': 1,
        'note': "ping in terminal",
        'group': "service-cmd"
    },
    'pipo': {
        'alias': ['pipo'],
        'type': 2,
        'note': "pipo : ascii art\n__{n?: int = rnd}__ : scelta del pipo, da 0 a 3 compresi",
        'group': "special",
        'other': True
    },
    'print exec': {
        'alias': ['pr', 'pt'],
        'type': 1,
        'note': "print result or traceback (of exec)",
        'group': "print"
    },
    'remove': {
        'alias': ['r', 'remove'],
        'type': 2,
        'note': "remove from rw list the chat in which you wrote the command (wip: arg)",
        'group': "reply-wait"
    },
    'save': {
        'alias': ['save'],
        'type': 1,
        'note': "forward reply to saved",
        'group': "send to"
    },
    'search': {
        'alias': ['search'],
        'type': 2,
        'note': "search for id or username of reply (wip: arg)\nor see @tgdb_bot",
        'group': "get"
    },
    'second profile': {
        'alias': ['2'],
        'type': 1,
        'note': "forward reply to second profile",
        'group': "send to"
    },
    'strikethrough': {
        'alias': ['strikethrough', 'done', 'v'],
        'type': 1,
        'note': "strikethrough the replyed message",
        'group': "fast"
    },
    'terminal': {
        'alias': ['t', 'terminal'],
        'type': 1,
        'note': "forward reply to terminal",
        'group': "send to"
    },
    'un attimo': {
        'alias': ['1'],
        'type': 1,
        'note': "\"Dammi un attimo\" + add to 'reply_waiting' list",
        'group': "fast"
    },
}
""" '': {
        'alias': ['',' '],
        'type': 0,
        'note': "",
        'group': "generic",
        'other': True
    },
"""
help_plus_text = (
    f"Il prefix è '`{PC}`'\ni comandi '`{PS}`' sono \"send to\"\n"
    f"i comandi `{PC}.` e `{PS}.` ignorano il comando (e cancellano il punto)\n\n"
    f"cos'è la lista \"reply waiting\" ?\n"
    "ogni tot tempo va a scrivere alle persone in lista che ancora non sei riuscito a dedicargli tempo\n\n"
    "come funziona la lista \"reply waiting\" ?\n"
    " - funziona solo nelle private\n"
    " - i tempi di attesa sono 1,8,24,36,48 ore. una volta raggiunto 48 ore, si stoppa\n"
    " - lo invia solo se l'ultimo messaggio non è tuo\n"
    " - come togliere una persona dalla lista? appena invii un messaggio a quella persona\n"
    f"     oppure comando `{PC}r` / `{PC}remove`\n"
    f" - per ottenere la lista: comando `{PC}gw` / `{PC}grw`\n\n\n"
    f"Others Commands:\n\n"
    f"Il prefix è `{MY_TAG} {PC}`\n"
    "Richieste: una ogni 20 sec, esclusa esecuzione, tutte in coda (in teoria)"
)


def check_cmd(txt: str, name: str) -> bool:
    """
    Controlla se l'input dell'utente corrisponde a uno dei comandi specificati.

    Fa una corrispondenza key insensitive.

    :param txt: Testo di input.
    :type txt: str
    :param name: key del dizionario 'commands'
        - type (int): il tipo di check da effettuare sul comando.
          - 1 '^$': 'only' cerca una corrispondenza esatta.
          - 2 '/': 'command' cerca se la stringa inizia con il testo del comando.
          - 3 '': 'within' cerca se è presente
    :type name: str
    :return: True se c'è una corrispondenza, else False.
    :rtype: bool
    :raises ValueError: Se il dizionario contiene un valore non valido per il tipo di check.
    """
    value = commands[name]['type']
    txt = txt.lower()
    for alias in commands[name]['alias']:
        alias = alias.lower()
        match value:
            case 1:
                if txt == alias:
                    return True
            case 2:
                if txt.startswith(alias):
                    return True
            case 3:
                if alias in txt:
                    return True
            case _:
                raise ValueError(f"Il dizionario contiene un valore non valido per il tipo di check: {value}\n"
                                 f"per i valori validi leggi la documentazione")
    return False


@Client.on_message()
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
    if encode_valid:
        if is_me and is_pvt and not (m.text and m.text.startswith(PC + '1')):
            from .waiting import remove_rw
            _ = create_task(remove_rw(str(ch.id)))

    if encode_valid:
        if is_me and m.text:
            # group 1
            if m.text.startswith(PC):
                _ = create_task(handle_commands(client, m))
            # group 2
            elif m.text.startswith(PS):
                _ = create_task(handle_send_to(client, m))

    # group 3
    if is_pvt and incoming:
        from .waiting import benvenuto
        _ = create_task(benvenuto(client, m))

    # group 4 | handle_commands_for_other trigger: start with (MY_TAG + ' ' + PC + {cmd_txt})
    if encode_valid:
        if incoming and m.text:
            if m.text.lower().startswith(MY_TAG + ' ' + PC):
                _ = create_task(handle_commands_for_other(client, m))


# @Client.on_message(f.me & f.text & f.regex(r'^\,'), group=1)
async def handle_commands(client: Client, msg: Msg):
    from pyrogram.enums import ParseMode
    ps = ParseMode.DISABLED
    # Estrai il testo del messaggio dopo ","
    cmd_txt_original = msg.text[1:]
    cmd_txt = cmd_txt_original.lower()

    # region generic
    # ",." iniziali fanno in modo che venga scritto , senza comando
    if cmd_txt != "" and cmd_txt[0] == ".":
        await msg.edit_text(PC + msg.text[2:])

    elif check_cmd(cmd_txt, '?+'):
        await client.send_message(
            chat_id=TERMINAL_ID,
            text=help_plus_text
        )

    elif check_cmd(cmd_txt, '?'):
        await msg.delete()
        await client.send_message(chat_id=TERMINAL_ID, text=help_(cmd_txt_original))
    # endregion

    # region fast
    elif check_cmd(cmd_txt, 'automatici'):
        await msg.edit("uso i messaggi automatici solo per far prima e poter gestire più persone,"
                       "senza andare ad ignorare qualcuno involontariamente")

    elif check_cmd(cmd_txt, 'greetings'):
        txts: list[str] = cmd_txt_original.split(maxsplit=1)
        if len(txts) == 1:
            text = "buondì\ncome va?"
        elif txts[1] == 'e':
            text = "Hii!!\nwhat's up?"
        else:
            await msg.delete()
            c_id = msg.chat.id
            await client.send_message(
                chat_id=TERMINAL_ID,
                text=f"! No greetings found !\n{msg.text}\nchat:{c_id if c_id != TERMINAL_ID else 'this chat'}"
            )
            return
        await msg.edit(text=text)

    elif check_cmd(cmd_txt, 'strikethrough'):
        rmsg = msg.reply_to_message
        await msg.delete()
        if not rmsg and not rmsg.text and rmsg.from_user.is_self:
            await client.send_message(TERMINAL_ID, f"il comando {PC}done vuole un reply a un mio text msg")
            return
        try:
            await rmsg.edit_text(f"~~{rmsg.text}~~")
        except Exception as e:
            await client.send_message(TERMINAL_ID, f"errore in {msg.text}:\n{e}")

    elif check_cmd(cmd_txt, 'un attimo'):
        from pyrogram.enums import ChatType as Ct
        chat_id = msg.chat.id
        await msg.edit("Dammi un attimo e ti scrivo subito.")
        _ = create_task(offline(client, 4, f"comando {PC}1"))
        if msg.chat.type != Ct.PRIVATE:
            return
        from .waiting import check_chat_for_reply_waiting, non_risposto, lock_rw
        if not await check_chat_for_reply_waiting(chat_id):
            return
        async with lock_rw:
            open('reply_waiting.txt', 'a').write(f"{chat_id};1\n")
        await non_risposto(client, chat_id)
    # endregion

    # region get
    elif check_cmd(cmd_txt, 'get msg id'):
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
        for i in range(0, n):
            uncomplete = True
            while uncomplete:
                try:
                    msg = await client.send_message(chat_id=msg.chat.id, text="thisid")
                    uncomplete = False
                    await msg.edit_text(str(msg.id))
                except:
                    await sleep(10)

    # TODO parameters
    elif check_cmd(cmd_txt, 'getall'):
        await msg.delete()
        # Crea la directory se non esiste già
        from os import makedirs
        from os.path import exists
        ga_fold = "./database/ga"
        if not exists(ga_fold):
            makedirs(ga_fold)

        def custom_serializer(obj):
            if isinstance(obj, Client):
                return str(obj)

        from json import dumps
        open(ga_fold + "/ga_msg.txt", "w", encoding='utf-8').write(
            str(dumps(vars(msg), indent=2, default=custom_serializer)))
        open(ga_fold + "/ga_chat.txt", "w", encoding='utf-8').write(
            str(dumps(vars(await client.get_chat(msg.chat.id)), indent=2, default=custom_serializer)))
        if msg.reply_to_message:
            open(ga_fold + "/ga_rmsg.txt", "w", encoding='utf-8').write(
                str(dumps(vars(msg.reply_to_message), indent=2, default=custom_serializer)))
            open(ga_fold + "/ga_rchat.txt", "w", encoding='utf-8').write(str(
                dumps(vars(await client.get_chat(msg.reply_to_message.chat.id)), indent=2, default=custom_serializer)))
        else:
            open(ga_fold + "/ga_rmsg.txt", "w", encoding='utf-8').write("")
            open(ga_fold + "/ga_rchat.txt", "w", encoding='utf-8').write("")
        await client.send_message(chat_id=TERMINAL_ID, text=f"creati 4 file dal comando {PC}getAll\n"
                                                            f"per stamparli: {PC}pga o printga")

    elif check_cmd(cmd_txt, 'getchat'):
        c_id: int = msg.chat.id
        await client.delete_messages(chat_id=c_id, message_ids=msg.id)
        await getchat(client, await client.get_chat(c_id))

    elif check_cmd(cmd_txt, 'getchat reply'):
        await msg.delete()
        # Ottieni il messaggio di risposta
        rmsg = msg.reply_to_message
        # Verifica se il messaggio ha una risposta
        if not rmsg:
            await client.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PC}getreply")
            return
        await getchat(client, await client.get_chat(rmsg.chat.id))

    elif check_cmd(cmd_txt, 'getid'):
        id_ = msg.reply_to_message.from_user.id if msg.reply_to_message else msg.chat.id
        await msg.delete()
        await client.send_message(chat_id=TERMINAL_ID, text=str(id_))

    # TODO get full user
    elif check_cmd(cmd_txt, 'getme'):
        await msg.delete()

        def custom_serializer(obj):
            if isinstance(obj, Client):
                return str(obj)

        from json import dumps
        text = str(dumps(vars(await client.get_me()), indent=2, default=custom_serializer))
        await client.send_message(chat_id=TERMINAL_ID, text='\n\''.join(text))

    elif check_cmd(cmd_txt, 'gets'):
        msg.text = PC + ('getr' if msg.reply_to_message else 'getchat')
        await handle_commands(client, msg)

    # TODO parametro
    elif check_cmd(cmd_txt, 'search'):
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
    # endregion

    # region print
    elif check_cmd(cmd_txt, 'getall print'):
        from pyrogram.enums import ParseMode
        from os.path import exists
        ps = ParseMode.DISABLED
        await msg.delete()

        async def printoutput(path: str):
            from pyrogram.errors.exceptions.flood_420 import FloodWait
            if not exists(path):
                await client.send_message(chat_id=TERMINAL_ID, text=f"il file {path} non esiste", parse_mode=ps)
                return
            txt = open(path, "r").read()
            if txt == "":
                txt = f"{path[12:]}: \n\nfile vuoto"
            else:
                txt = f"{path[12:]}: \n\n" + txt
            chunk__s = 4096
            chunks__ = [txt[it:it + chunk__s] for it in range(0, len(txt), chunk__s)]

            for chunk__ in chunks__:
                un_complet = True
                while un_complet:
                    try:
                        await client.send_message(chat_id=TERMINAL_ID, text=str(chunk__), parse_mode=ps)
                        un_complet = False
                    except FloodWait:
                        await sleep(20)
                # end while
            # end for

        # End def
        from os import listdir
        for file in [f for f in listdir("./database/ga")]:
            await printoutput(f"database/ga/{file}")
        await client.send_message(chat_id=TERMINAL_ID, text="end print")

    # TODO parametri
    elif check_cmd(cmd_txt, 'output'):
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
            chunk_s_ = 4096
            chunks_ = [txt[i_:i_ + chunk_s_] for i_ in range(0, len(txt), chunk_s_)]

            for chunk_ in chunks_:
                uncomplet_ = True
                while uncomplet_:
                    try:
                        await client.send_message(chat_id=TERMINAL_ID, text=str(chunk_), parse_mode=ps)
                        uncomplet_ = False
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

    elif check_cmd(cmd_txt, 'print exec'):
        from pyrogram.errors.exceptions.flood_420 import FloodWait
        rpath = "database/result.txt" if cmd_txt == 'pr' else "database/traceback.txt"
        result_txt = open(rpath, "r", encoding='utf-8').read()
        if result_txt == "":
            result_txt = f"{rpath[9:]}: \n\nfile vuoto"
        else:
            result_txt = f"{rpath[9:]}: \n\n" + result_txt
        chunk_s = 4096
        chunks = [result_txt[i:i + chunk_s] for i in range(0, len(result_txt), chunk_s)]

        for chunk in chunks:
            uncomplet = True
            while uncomplet:
                try:
                    await client.send_message(chat_id=TERMINAL_ID, text=str(chunk), parse_mode=ps)
                    uncomplet = False
                except FloodWait:
                    await sleep(20)
            # end while
        # end for
    # endregion

    # region reply-wait
    elif check_cmd(cmd_txt, 'get reply waiting'):
        await msg.delete()
        from .waiting import lock_rw
        async with lock_rw:
            text = open('reply_waiting.txt', "r").read()
        if text == "":
            text = "reply_waiting.txt\n\nfile vuoto"
        else:
            text = "reply_waiting.txt\n\n" + text
        await client.send_message(chat_id=TERMINAL_ID, text=text)

    elif check_cmd(cmd_txt, 'remove'):
        c_id = msg.chat.id
        await msg.delete()
        from .waiting import remove_rw
        await remove_rw(str(c_id))
    # endregion

    # region service-cmd
    elif check_cmd(cmd_txt, 'delete'):
        await msg.delete()
        rmsg = msg.reply_to_message
        if not rmsg:
            await client.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PC}del ")
            return
        await rmsg.delete()

    elif check_cmd(cmd_txt, 'eval') or check_cmd(cmd_txt, 'eval reply'):
        txts = cmd_txt.split(maxsplit=1)
        if len(txts) == 2:
            if txts[1] in ['h', '?']:
                from .code_runner import pre_exec
                await msg.edit(
                    f"`{PC}eval ` pre exec code is:\n\n"
                    f"<pre language=\"python\">{pre_exec}</pre>\nfirst line:{pre_exec.count('\n') + 2}"
                )
                return
        from .code_runner import python_exec
        await python_exec(client, msg)

    elif check_cmd(cmd_txt, 'eval file'):
        txts = cmd_txt_original.split(maxsplit=1)
        if len(txts) == 1:
            await msg.edit(msg.text + f"\n!! see `{PC}feval h`")
            return
        from .code_runner import python_exec

        # if 1 char then command
        if len(txts[1].split(maxsplit=1)[0]) == 1:
            if txts[1] in ['h', '?']:
                await msg.edit(
                    f"`{PC}feval `(file exec)  parameters:\n\n"
                    "`h` / `?` : this help\n\n"
                    "[fname] [code] : run code, create file with fname\n"
                    "if exist overwrite (min 2 char, one word)\n\n"
                    "`f ` [fname] : run selected file\n\n"
                    "`l` / `L` : list of files\n"
                    'read file comment too (header: """\\n comment\\n""")\n\n'
                    "`d `/`r `[Any]: delete file\n\n"
                    f"`{PC}eval ?` : see pre_exec"
                )
                return

            elif txts[1].startswith('f'):
                txts = txts[1].split(maxsplit=2)
                if len(txts) != 2:
                    await msg.edit(f"per `{PC}feval f ` bisogna mettere il fileName")
                    return
                from os.path import exists
                fpath = "database/py_exec/" + txts[1]
                if not exists(fpath):
                    await msg.edit(f"`{msg.text}`\nil file {txts[1]} non esiste")
                    return
                msg.text = f"{PC}eval " + open(fpath, 'r', encoding='utf-8').read()
                await python_exec(client, msg)

            elif txts[1] in ['l', 'L']:
                from os import listdir
                file_list = listdir("database/py_exec/")
                result = ""
                for file_name in file_list:
                    fnote = ""
                    is_note = False

                    fstream = open("database/py_exec/" + file_name, 'r', encoding='utf-8')
                    next(fstream)
                    for line_number, line in enumerate(fstream, start=1):
                        if line.startswith('"""'):
                            is_note = True
                            break
                        elif line_number == 6:
                            break
                        else:
                            fnote += line
                    fstream.close()

                    if not is_note:
                        fnote = "no notes"
                    result += f"{file_name}:\n{fnote}\n\n"
                result = "list of py exec file:\n\n" + result
                from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
                try:
                    await msg.edit_text(result)
                except MessageTooLong:
                    open("database/result.txt", 'w', encoding='utf-8').write(result)
                    await msg.edit_text(f"file eval list: view database/result.txt or print with `{PC}pr")

            elif txts[1].startswith(('d', 'r')):
                txts = txts[1].split(maxsplit=2)
                if len(txts) != 2:
                    await msg.edit(f"per `{PC}feval d ` bisogna mettere il fileName")
                    return
                from os.path import exists
                fpath = "database/py_exec/" + txts[1]
                if not exists(fpath):
                    await msg.edit(f"il file {txts[1]} non esiste")
                    return
                from os import remove
                remove(fpath)
                await msg.edit(f"`{msg.text}`\n!! file deleted !!")

            else:
                await msg.edit(f"`{msg.text}`\n!! command not found !!")
                return

        else:
            fcrea = txts[1].split(maxsplit=1)
            if len(fcrea) == 1:
                await msg.edit(f"`{msg.text}`\n!! see `{PC}feval h`")
                return
            fpath = "database/py_exec/" + fcrea[0]
            open(fpath, 'w', encoding='utf-8').write(fcrea[1])
            msg.text = f"{PC}eval " + open(fpath, 'r', encoding='utf-8').read()
            await python_exec(client, msg)

    # TODO parametro seconds
    elif check_cmd(cmd_txt, 'offline'):
        await msg.delete()
        await offline(client, 5, f"{PC}offline")

    elif check_cmd(cmd_txt, 'ping'):  # or pingt
        await pong(client, msg, cmd_txt != "ping")
    # endregion

    # region special
    elif check_cmd(cmd_txt, 'moon'):
        await moon(msg, cmd_txt, False)

        '''
    elif check_cmd(cmd_txt, {'genera': 2}):
        txt = msg.text[8:]
        pri = ''
        for c in txt:
            pri += c
            try:
                await msg.edit_text(pri)
            except:
                pass
        '''

    elif check_cmd(cmd_txt, 'pipo'):
        await msg.edit(text='pipoo')

    elif check_cmd(cmd_txt, 'null'):
        rmsg = msg.reply_to_message
        await msg.delete()
        if rmsg:
            await rmsg.reply("ㅤ")
        else:
            await client.send_message(chat_id=msg.chat.id, text="ㅤ")
    # endregion

    else:
        c_id = msg.chat.id
        await msg.delete()
        await client.send_message(
            chat_id=TERMINAL_ID,
            text=f"! cmd don't found !\n{msg.text}\nchat:{c_id if c_id != TERMINAL_ID else 'this chat'}"
        )


# @Client.on_message(f.me & f.text & f.regex(r'^\>'), group=2)
async def handle_send_to(client: Client, msg: Msg):
    cmd_txt = msg.text[1:].lower()
    c_id = msg.chat.id

    # ">." iniziali fanno in modo che venga scritto > senza comando
    if cmd_txt != "" and cmd_txt[0] == ".":
        await msg.edit_text(PS + msg.text[2:])

    elif check_cmd(cmd_txt, 'pic'):
        await msg.delete()
        if not msg.reply_to_message:
            await client.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PS}pic")
            return
        from .pyrogram_forward_to_topic import forward_to_topic as for_top
        from .myParameters import SAVED_MESSAGE_FORUM_ID, PIC_TOPIC_ID
        await for_top(source_channel_id=c_id, destination_channel_id=SAVED_MESSAGE_FORUM_ID,
                      forwarded_message_id=msg.reply_to_message_id, topic_init_message_id=PIC_TOPIC_ID, client=client)

    elif check_cmd(cmd_txt, 'save'):
        await msg.delete()
        if not msg.reply_to_message:
            await client.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PS}save")
            return
        await client.forward_messages('me', msg.chat.id, msg.reply_to_message_id)

    elif check_cmd(cmd_txt, 'second profile'):
        await msg.delete()
        from .myParameters import MY_ID2
        await client.forward_messages(chat_id=MY_ID2, from_chat_id=c_id,
                                      message_ids=msg.reply_to_message_id)

    # TODO parametri
    elif check_cmd(cmd_txt, 'terminal'):
        await msg.delete()
        if not msg.reply_to_message:
            await client.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PS}terminal")
            return
        await client.forward_messages(chat_id=TERMINAL_ID, from_chat_id=c_id,
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
        # end def
        _ = create_task(client.send_message(TERMINAL_ID, f"Nella chat `{msg.chat.id}` è stato richiesto da "
                                                         f"`{msg.from_user.id}` il comando\n{msg.text}"))
        # from pyrogram.enums import ParseMode
        # ps = ParseMode.DISABLED
        # mytaglen = len(MY_TAG)
        # pre_len = len(MY_TAG + ' ' + PC)
        # cmd_txt = msg.text[pre_len:].lower()
        cmd_txt_original = msg.text[len(MY_TAG + ' ' + PC):]
        cmd_txt = cmd_txt_original.lower()

        if check_cmd(cmd_txt, '?'):
            await msg.reply_text(help_other())

        elif check_cmd(cmd_txt, 'moon'):
            await moon(msg, cmd_txt, True)

        elif check_cmd(cmd_txt, 'pipo'):
            await pipo(cmd_txt, msg, True)

        elif check_cmd(cmd_txt, 'null'):
            await (msg.reply_to_message if msg.reply_to_message else msg).reply_text("ㅤ")

        else:
            await msg.reply_text(f"! Nessun comando trovato !\n`{msg.text}`")

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


async def offline(client: Client, seconds: float, from_: str):
    from pyrogram.raw.functions.account import UpdateStatus  # offline
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


async def moon(m: Msg, txt: str, other: bool):
    moon_list = ["🌕", "🌖", "🌗", "🌘", "🌑", "🌒", "🌓", "🌔"]
    if other:
        m = await m.reply_text("LUNA UAU")
    try:
        sec = float(txt.split(" ")[1])
    except:
        sec = 0.1
    if sec < 0.1:
        sec = 0.1
    for _ in range(30):
        moon_list = moon_list[-1:] + moon_list[:-1]
        text = ''.join(moon_list[:5]) + "ㅤ"
        try:
            _ = create_task(m.edit_text(text))
        except:
            pass
        await sleep(sec)


async def pipo(txt: str, m: Msg, other: bool):
    if other:
        msg = await m.reply_text("PIPO GROSSO")
    else:
        msg = m
    try:
        num = int(txt.split(" ")[1])
    except:
        import random
        num = random.randint(0, 3)

    from .myParameters import ASCII_ART
    match num:
        case 0:
            text = ASCII_ART['pipo0']
        case 1:
            text = ASCII_ART['pipo1']
        case 2:
            text = ASCII_ART['pipo2']
        case 3:
            text = ASCII_ART['pipo3']
        case _:
            text = f"{m.text}\nerror. i numeri disponibili sono: 0, 1, 2, 3"
    await msg.edit(text)


def h_groupping(cmd_or=None):
    if cmd_or is None:
        cmd_or = commands
    grouped_cmd = {}
    for key, value in cmd_or.items():
        gr = value['group']
        if gr not in grouped_cmd:
            grouped_cmd[gr] = []
        grouped_cmd[gr].append((key, value['alias'], value['note']))

    # Sort alphabetically
    for grou_p, command_s in grouped_cmd.items():
        grouped_cmd[grou_p] = sorted(command_s, key=lambda x: x[0])
    grouped_cmd = dict(sorted(grouped_cmd.items()))
    return grouped_cmd


def h_format_group(group_, cmd_i):
    pre = PS if group_ == "send to" else PC
    ftext = f"**{group_}**:\n"
    for command_info in cmd_i:
        formatted_aliases = ' '.join([f'`{pre}{alias}`' for alias in command_info[1]])
        ftext += f"  {command_info[0]}\n"
        ftext += f"    {formatted_aliases}\n"
        ftext += f"    : {command_info[2].replace('\n', '\n      ')}\n"
    return ftext


def help_other():
    text = (
        f"All commands usable from others:\n"
        f"Il prefix è `{MY_TAG} {PC}`\n"
        "Richieste: una ogni 20 sec, esclusa esecuzione, tutte in coda (in teoria)\n\n"
    )
    all_other = {key: value for key, value in commands.items() if 'other' in value and value['other']}
    for group, cmd_info in h_groupping(all_other).items():
        text += h_format_group(group, cmd_info)
    return text


def help_(cmd_text):
    txts: list[str] = cmd_text.split(maxsplit=1)
    if len(txts) == 1:
        text = (
            "**help menu**\n\n"
            f"see all commands: `{PC}help a`\n"
            f"see other info `{PC}help+`\n"
            f"see all 'for others' commands: `{PC}help o`\n"
            f"see single `{PC}help ` cmd\n"
            f"see a group `{PC}help g ` name\n"
            f"search cmd `{PC}help ` query\n"
            f"search group `{PC}help g` query\n"
        )
        return text

    if txts[1] == 'a':
        text = "All commands sorted by group:\n\n"
        for group, cmd_info in h_groupping().items():
            text += h_format_group(group, cmd_info)

    elif txts[1] == 'o':
        text = help_other()

    elif txts[1].startswith('g '):
        gcmd = h_groupping()
        query = txts[1][2:]
        results = {}
        for group in gcmd.keys():
            if query.lower() in group.lower():
                results[group] = gcmd[group]

        text = f"All groups find by your query '{query}':\n\n"
        for group, cmd_info in results.items():
            text += h_format_group(group, cmd_info)

    else:
        results = {key: commands[key] for key in commands if
                   txts[1] in key or any(txts[1] in alias for alias in commands[key]['alias'])}
        text = f"All cmd find by your query '{txts[1]}':\n\n"
        for group, cmd_info in h_groupping(results).items():
            text += h_format_group(group, cmd_info)

    return text
