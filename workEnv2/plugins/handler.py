"""
event handler
evito di usare i filter per evitare certi strani bug
"""
from pyrogram import Client
from pyrogram.types import Message as Msg, Chat, User
from pyrogram.enums import ChatType, ParseMode
from .myParameters import TERMINAL_ID, PREFIX_COMMAND as PC, PREFIX_SEND_TO as PS, MY_TAG
from asyncio import Lock, sleep
from .tasker import create_task_name
from typing import Union, Optional

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
        'type': 2,
        'note': "\"uso i messaggi automatici perché..\"\n arg: 'e' for english version",
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
        'note': "edit text with his id\n__{n?: int = 1}__ : send n message with id\nif have a reply it sends only the"
                " id of that",
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
        'note': "get id of chat or replyed user",
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
        'type': 1,
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
        'note': f"print output files\n `{PC}out h` for args",
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
        'note': f"remove from rw list an user\nsee `{PC}r h`",
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
        'note': "search for id or username",
        'group': "get"
    },
    'search reply': {
        'alias': ['rsearch'],
        'type': 1,
        'note': "search for id or username of reply",
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
        'type': 2,
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
                if (txt + " ").startswith((alias + " ")):
                    return True
            case 3:
                if alias in txt:
                    return True
            case _:
                raise ValueError(f"Il dizionario contiene un valore non valido per il tipo di check: {value}\n"
                                 f"per i valori validi leggi la documentazione")
    return False


@Client.on_message()
async def event_handler(client: Client, msg: Msg):
    import chardet
    encode_valid = True
    if msg.text:
        result = chardet.detect(msg.text.encode())
        if str(result['encoding']) == 'None':
            encode_valid = False

    ch: Chat = msg.chat
    fr_u: User = msg.from_user
    # c_type: ChatType = ch.type
    # pvt = ChatType.PRIVATE
    is_pvt: bool = bool(msg.chat and ch.type == ChatType.PRIVATE)
    incoming: bool = not msg.outgoing  # chat:"me" = True
    is_me: bool = bool(fr_u and fr_u.is_self or msg.outgoing)
    sec = msg.date.second

    # group -1
    if encode_valid:
        if is_me and is_pvt and not (msg.text and msg.text.startswith(PC + '1')):
            from .waiting import remove_rw
            _ = create_task_name(remove_rw(str(ch.id)), name=f'remove{sec}')

    if encode_valid:
        if is_me and msg.text:
            # group 1
            if msg.text.startswith(PC):
                _ = create_task_name(handle_commands(client, msg), name=f"handle{sec}")
            # group 2
            elif msg.text.startswith(PS):
                _ = create_task_name(handle_send_to(client, msg), name=f"handle{sec}")

    # group 3
    if is_pvt and incoming:
        from .waiting import benvenuto
        _ = create_task_name(benvenuto(client, msg), name=f"benvenuto{sec}")

    # group 4 | handle_commands_for_other trigger: start with (MY_TAG + ' ' + PC + {cmd_txt})
    if encode_valid:
        if incoming and msg.text:
            if msg.text.lower().startswith(MY_TAG + ' ' + PC):
                _ = create_task_name(handle_commands_for_other(client, msg), name=f"other{sec}")


# @Client.on_message(f.me & f.text & f.regex(r'^\,'), group=1)
async def handle_commands(c: Client, m: Msg):
    # Estrai il testo del messaggio dopo ","
    cmd_txt_original = m.text[1:]
    cmd_txt = cmd_txt_original.lower()

    # region generic
    # ",." iniziali fanno in modo che venga scritto , senza comando
    if cmd_txt != "" and cmd_txt[0] == ".":
        await m.edit_text(PC + m.text[2:])

    elif check_cmd(cmd_txt, '?+'):
        await m.delete()
        await c.send_message(TERMINAL_ID, help_plus_text)

    elif check_cmd(cmd_txt, '?'):
        await m.delete()
        await c.send_message(TERMINAL_ID, help_(cmd_txt_original))
    # endregion

    # region fast
    elif check_cmd(cmd_txt, 'automatici'):
        txts: list[str] = cmd_txt_original.split(maxsplit=1)
        if len(txts) == 1:
            text = ("uso i messaggi automatici solo per far prima e poter gestire più persone, "
                    "senza andare ad ignorare qualcuno involontariamente")
        elif txts[1] == 'e':
            text = ("I use automatic messages just to save time and manage more people, "
                    "without unintentionally ignoring anyone")
        else:
            await m.delete()
            c_id = m.chat.id
            await c.send_message(chat_id=TERMINAL_ID,
                                 text=f"! No lang found !\n{m.text}\nchat:"
                                      f"{c_id if c_id != TERMINAL_ID else 'this chat'}")
            return
        await m.edit(text=text)

    elif check_cmd(cmd_txt, 'greetings'):
        txts: list[str] = cmd_txt_original.split(maxsplit=1)
        if len(txts) == 1:
            text = "buondì\ncome va?"
        elif txts[1] == 'e':
            text = "Hii!!\nwhat's up?"
        else:
            await m.delete()
            c_id = m.chat.id
            await c.send_message(chat_id=TERMINAL_ID,
                                 text=f"! No greetings found !\n{m.text}\n"
                                      f"chat:{c_id if c_id != TERMINAL_ID else 'this chat'}")
            return
        await m.edit(text=text)

    elif check_cmd(cmd_txt, 'strikethrough'):
        rmsg = m.reply_to_message
        await m.delete()
        check = bool(rmsg)
        if check:
            check = bool(rmsg.text) and bool(rmsg.from_user.is_self)
        if not check:
            await c.send_message(TERMINAL_ID, f"il comando {PC}done vuole un reply a un mio text msg")
            return
        try:
            await rmsg.edit_text(f"~~{rmsg.text}~~")
        except Exception as e:
            await c.send_message(TERMINAL_ID, f"errore in {m.text}:\n{e}")

    elif check_cmd(cmd_txt, 'un attimo'):
        chat_id = m.chat.id
        sec = m.date.second
        await m.edit("Dammi un attimo e ti scrivo subito.")
        _ = create_task_name(offline(c, 4, f"comando {PC}1"), f'offline{sec}')
        if m.chat.type != ChatType.PRIVATE:
            return
        from .waiting import check_chat_for_reply_waiting, non_risposto, lock_rw
        if not await check_chat_for_reply_waiting(chat_id):
            return
        async with lock_rw:
            open('database/reply_waiting.txt', 'a').write(f"{chat_id};1\n")
        _ = create_task_name(non_risposto(c, chat_id), f"non_risposto{sec}")
    # endregion

    # region get
    elif check_cmd(cmd_txt, 'get msg id'):
        rmsg = m.reply_to_message
        if rmsg:
            await m.edit_text(str(rmsg.id))
            return
        try:
            n = int(cmd_txt.split(" ")[1])
        except (IndexError, ValueError):
            n = 1
        from pyrogram.errors.exceptions.flood_420 import FloodWait
        await m.edit_text(f"this msg id: `{m.id}`")
        n -= 1
        chat_id = m.chat.id

        async def _cycle():
            for _ in range(0, n):
                uncomplete = True
                while uncomplete:
                    try:
                        _m = await c.send_message(chat_id=chat_id, text="thisid")
                        await _m.edit_text(f"this msg id: `{_m.id}`")
                        uncomplete = False
                    except FloodWait as _e:
                        await sleep(_e.value)

        _ = create_task_name(_cycle(), f'thisid{m.date.second}')

    elif check_cmd(cmd_txt, 'getall'):
        await m.delete()
        # Crea la directory se non esiste già
        from os import makedirs
        from os.path import exists
        ga_fold = "./database/ga"
        if not exists(ga_fold):
            makedirs(ga_fold)

        from pprint import PrettyPrinter
        pp = PrettyPrinter(indent=2)

        open(ga_fold + "/ga_msg.txt", "w", encoding='utf-8').write(pp.pformat(vars(m)))
        open(ga_fold + "/ga_chat.txt",
             "w",
             encoding='utf-8').write(pp.pformat(vars(await c.get_chat(m.chat.id))))
        if m.reply_to_message:
            open(ga_fold + "/ga_rmsg.txt", "w", encoding='utf-8').write(pp.pformat(vars(m.reply_to_message)))
            open(ga_fold + "/ga_rchat.txt",
                 "w",
                 encoding='utf-8').write(pp.pformat(vars(await c.get_chat(m.reply_to_message.chat.id))))
        else:
            open(ga_fold + "/ga_rmsg.txt", "w", encoding='utf-8').truncate()
            open(ga_fold + "/ga_rchat.txt", "w", encoding='utf-8').truncate()
        await c.send_message(chat_id=TERMINAL_ID, text=f"creati 4 file dal comando {PC}getAll\n"
                                                       f"per stamparli: {PC}pga o printga")

    elif check_cmd(cmd_txt, 'getchat'):
        await m.delete()
        await getchat(c, await c.get_chat(m.chat.id))

    elif check_cmd(cmd_txt, 'getchat reply'):
        await m.delete()
        # Ottieni il messaggio di risposta
        rmsg = m.reply_to_message
        # Verifica se il messaggio ha una risposta
        if not rmsg:
            await c.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PC}getreply")
            return
        await getchat(c, await c.get_chat(rmsg.chat.id))

    elif check_cmd(cmd_txt, 'getid'):
        await m.delete()
        id_ = m.reply_to_message.from_user.id if m.reply_to_message else m.chat.id
        await c.send_message(TERMINAL_ID, f"`{id_}`")

    elif check_cmd(cmd_txt, 'getme'):
        await m.delete()
        from pprint import PrettyPrinter
        from pyrogram.raw.functions.users import GetFullUser
        from pyrogram.raw.types import InputUserSelf

        ppf = PrettyPrinter(indent=2).pformat

        await c.send_message(TERMINAL_ID, f"client.get_me():\n```\n{ppf(vars(await c.get_me()))}\n```")
        await c.send_message(TERMINAL_ID, f"GetFullUser:\n```\n"
                                          f"{ppf(await c.invoke(GetFullUser(id=InputUserSelf())))}\n```")
        await c.send_message(TERMINAL_ID, f"client.me:\n```\n{ppf(c.me)}\n```")

    elif check_cmd(cmd_txt, 'gets'):
        await m.delete()
        m.text = PC + ('getr' if m.reply_to_message else 'getchat')
        await handle_commands(c, m)

    elif check_cmd(cmd_txt, 'search'):
        await m.delete()
        txts: list[str] = cmd_txt_original.split(maxsplit=1)
        if len(txts) == 1:
            await c.send_message(TERMINAL_ID, f"query missing for `{PC}search`")
            return
        try:
            await getchat(c, await c.get_chat(txts[1]))
        except Exception as e:
            await c.send_message(TERMINAL_ID, f"{e}\n\n`{m.text}`:\nil comando cerca per id o per username")

    elif check_cmd(cmd_txt, 'search reply'):
        await m.delete()
        rmsg = m.reply_to_message
        if not rmsg:
            await c.send_message(TERMINAL_ID, f"nessun reply per il comando `{PC}rsearch`")
            return
        try:
            await getchat(c, await c.get_chat(rmsg.text))
        except Exception as e:
            await c.send_message(TERMINAL_ID,
                                 f"{e}\n\nil comando cerca per id o per username",
                                 parse_mode=ParseMode.DISABLED)
    # endregion

    # region print
    elif check_cmd(cmd_txt, 'getall print'):
        await m.delete()
        from os.path import exists
        from os import listdir

        async def _internal():
            for file in [f for f in listdir("./database/ga")]:
                path = f"database/ga/{file}"
                if not exists(path):
                    await c.send_message(chat_id=TERMINAL_ID, text=f"il file {path} non esiste")
                    return
                txt = open(path, "r", encoding='utf-8').read()
                if txt == "":
                    txt = f"{file}: \n\nfile vuoto"
                else:
                    txt = f"{file}: \n\n{txt}"
                await send_long_message(c, txt, chunk_start="```\n", chunk_end="\n```")

        await create_task_name(_internal(), name=f"pga{m.date.second}")

        await c.send_message(chat_id=TERMINAL_ID, text="end print")

    elif check_cmd(cmd_txt, 'output'):
        await m.delete()
        txts: list[str] = cmd_txt_original.split(maxsplit=1)
        if len(txts) == 1:
            txts: list[int] = [1, 2, 3, 4]
        elif txts[1] in ['h', '?']:
            await c.send_message(TERMINAL_ID,
                                 f"`{PC}po `(print output)  parameters (merge-able):\n\n"
                                 "`h` / `?` : this help\n\n"
                                 "`1 2 3 4` / None : all output\n"
                                 "`1` : ubot1\n"
                                 "`2` : ubot2\n"
                                 "`3` : infobot\n"
                                 "`4` : meteobot\n")
            return

        else:
            txts: list[str | int] = txts[1].split()
            try:
                for i in range(len(txts)):
                    n = int(txts[i])
                    if n not in [1, 2, 3, 4]:
                        raise ValueError
                    txts[i] = n
            except (IndexError, ValueError):
                await c.send_message(TERMINAL_ID, f"`{m.text}`\ninvalid args, see `{PC}po h`")

        from platform import system

        async def printoutput(path: str, title: str):
            txt = open(path, "r").read()
            if txt == "":
                txt = f"{title}: output.txt\n\nfile vuoto"
            else:
                txt = f"{title}: output.txt\n\n" + txt
            await send_long_message(c, txt, chunk_start="```\n", chunk_end="\n```")

        async def _internal():
            if system() == "Windows":
                ind = 1
            elif system() == "Linux":
                ind = 0
            else:
                raise SystemError("Undefined operating system")

            from .myParameters import botlist
            for _n in txts:
                match _n:
                    case 1:
                        await printoutput(botlist['Ubot1']['paths'][ind], "Ubot1")
                    case 2:
                        await printoutput(botlist['Ubot2']['paths'][ind], "Ubot2")
                    case 3:
                        await printoutput(botlist['Infobot']['paths'][ind], "Infobot")
                    case 4:
                        await printoutput(botlist['MeteoATbot']['paths'][ind], "MeteoATbot")

        _ = create_task_name(_internal(), f"output{m.date.second}")

    elif check_cmd(cmd_txt, 'print exec'):
        await m.delete()
        rpath = "database/result.txt" if cmd_txt == 'pr' else "database/traceback.txt"
        result_txt = open(rpath, "r", encoding='utf-8').read()
        if result_txt == "":
            result_txt = f"{rpath[9:]}: \n\nfile vuoto"
        else:
            result_txt = f"{rpath[9:]}: \n\n" + result_txt

        await send_long_message(c, result_txt, chunk_start="```\n", chunk_end="\n```")
    # endregion

    # region reply-wait
    elif check_cmd(cmd_txt, 'get reply waiting'):
        await m.delete()
        from .waiting import lock_rw
        async with lock_rw:
            text = open('database/reply_waiting.txt', "r").read()
        if text == "":
            text = "reply_waiting.txt\n\nfile vuoto"
        else:
            text = "reply_waiting.txt\n\n" + text
        await send_long_message(c, text)

    elif check_cmd(cmd_txt, 'remove'):
        await m.delete()
        txts: list[str] = cmd_txt_original.split(maxsplit=1)
        if len(txts) == 1:
            c_id = m.chat.id

        elif txts[1] in ['h', '?']:
            await c.send_message(TERMINAL_ID,
                                 f"`{PC}r `(remove from reply-wait list)  parameters:\n\n"
                                 "`h` / `?` : this help\n\n"
                                 "None : this chat\n"
                                 "id : chat id\n"
                                 "`@`username : chat id from username\n")
            return

        elif len(txts[1].split(maxsplit=1)) > 1:
            await c.send_message(TERMINAL_ID, f"`{m.text}`\ninvalid arguments, see `{PC}r h`")
            return

        elif txts[1].startswith('@'):
            from pyrogram.errors.exceptions.bad_request_400 import UsernameInvalid
            try:
                c_id = (await c.get_chat(txts[1])).id
            except UsernameInvalid:
                await c.send_message(TERMINAL_ID, f"`{m.text}`\ninvalid username")
                return

        else:
            c_id = txts[1]

        from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
        try:
            if (await c.get_chat(c_id)).type != ChatType.PRIVATE:
                return
        except PeerIdInvalid:
            await c.send_message(TERMINAL_ID, f"`{m.text}`\ninvalid id")
            return

        from .waiting import remove_rw
        _ = create_task_name(remove_rw(str(c_id)), f"remove{m.date.second}")
    # endregion

    # region service-cmd
    # TODO upgrade
    elif check_cmd(cmd_txt, 'delete'):
        await m.delete()
        rmsg = m.reply_to_message
        if not rmsg:
            await c.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PC}del ")
            return
        await rmsg.delete()

    elif check_cmd(cmd_txt, 'eval') or check_cmd(cmd_txt, 'eval reply'):
        txts = cmd_txt.split(maxsplit=1)
        if len(txts) == 2:
            if txts[1] in ['h', '?']:
                from .code_runner import pre_exec
                await m.edit(f"`{PC}eval ` pre exec code is:\n\n"
                             f"<pre language=\"python\">{pre_exec}</pre>\nfirst line:{pre_exec.count('\n') + 2}")
                return
        from .code_runner import python_exec
        task = create_task_name(python_exec(c, m), f'exec{m.date.second}')
        await eval_canc(c, m, task)

    elif check_cmd(cmd_txt, 'eval file'):
        async def _fexec():
            _txts = cmd_txt_original.split(maxsplit=1)
            if len(_txts) == 1:
                await m.edit(m.text + f"\n!! see `{PC}feval h`")
                return
            from .code_runner import python_exec

            # if 1 char then command
            if len(_txts[1].split(maxsplit=1)[0]) == 1:
                if _txts[1] in ['h', '?']:
                    await m.edit(f"`{PC}feval `(file exec)  parameters:\n\n"
                                 "`h` / `?` : this help\n\n"
                                 "[fname] [code] : run code, create file with fname\n"
                                 "if exist overwrite (min 2 char, one word)\n\n"
                                 "`f ` [fname] : run selected file\n\n"
                                 "`l` / `L` : list of files\n"
                                 'read file comment too (header: """\\n comment\\n""")\n\n'
                                 "`d `/`r `[Any]: delete file\n\n"
                                 f"`{PC}eval ?` : see pre_exec")
                    return

                elif _txts[1].startswith('f'):
                    _txts = _txts[1].split(maxsplit=2)
                    if len(_txts) != 2:
                        await m.edit(f"per `{PC}feval f ` bisogna mettere il fileName")
                        return
                    from os.path import exists
                    fpath = "database/py_exec/" + _txts[1]
                    if not exists(fpath):
                        await m.edit(f"`{m.text}`\nil file {_txts[1]} non esiste")
                        return
                    m.text = f"{PC}eval " + open(fpath, 'r', encoding='utf-8').read()
                    await python_exec(c, m)

                elif _txts[1] in ['l', 'L']:
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
                        await m.edit_text(result)
                    except MessageTooLong:
                        open("database/result.txt", 'w', encoding='utf-8').write(result)
                        await m.edit_text(f"file eval list: view database/result.txt or print with `{PC}pr")

                elif _txts[1].startswith(('d', 'r')):
                    _txts = _txts[1].split(maxsplit=2)
                    if len(_txts) != 2:
                        await m.edit(f"per `{PC}feval d ` bisogna mettere il fileName")
                        return
                    from os.path import exists
                    fpath = "database/py_exec/" + _txts[1]
                    if not exists(fpath):
                        await m.edit(f"il file {_txts[1]} non esiste")
                        return
                    from os import remove
                    remove(fpath)
                    await m.edit(f"`{m.text}`\n!! file deleted !!")

                else:
                    await m.edit(f"`{m.text}`\n!! command not found !!")
                    return

            else:
                fcrea = _txts[1].split(maxsplit=1)
                if len(fcrea) == 1:
                    await m.edit(f"`{m.text}`\n!! see `{PC}feval h`")
                    return
                fpath = "database/py_exec/" + fcrea[0]
                open(fpath, 'w', encoding='utf-8').write(fcrea[1])
                m.text = f"{PC}eval " + open(fpath, 'r', encoding='utf-8').read()
                await python_exec(c, m)

        task = create_task_name(_fexec(), f'exec file{m.date.second}')
        await eval_canc(c, m, task)

    # TODO parametro seconds
    elif check_cmd(cmd_txt, 'offline'):
        await m.delete()
        _ = create_task_name(offline(c, 5, f"{PC}offline"), f"offline{m.date.second}")

    elif check_cmd(cmd_txt, 'ping'):  # or pingt
        await pong(c, m, cmd_txt != "ping")
    # endregion

    # region special
    elif check_cmd(cmd_txt, 'moon'):
        await moon(m, cmd_txt, False)

    elif check_cmd(cmd_txt, 'pipo'):
        await m.edit(text='pipoo')

    elif check_cmd(cmd_txt, 'null'):
        rmsg = m.reply_to_message
        await m.delete()
        if rmsg:
            await rmsg.reply("ㅤ")
        else:
            await c.send_message(chat_id=m.chat.id, text="ㅤ")
    # endregion

    else:
        c_id = m.chat.id
        await m.delete()
        await c.send_message(TERMINAL_ID, f"! cmd don't found !\n"
                                          f"{m.text}\nchat:{c_id if c_id != TERMINAL_ID else 'this chat'}")


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
        await for_top(source_channel_id=c_id,
                      destination_channel_id=SAVED_MESSAGE_FORUM_ID,
                      forwarded_message_id=msg.reply_to_message_id,
                      topic_init_message_id=PIC_TOPIC_ID,
                      client=client)

    elif check_cmd(cmd_txt, 'save'):
        await msg.delete()
        if not msg.reply_to_message:
            await client.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PS}save")
            return
        await client.forward_messages('me', msg.chat.id, msg.reply_to_message_id)

    elif check_cmd(cmd_txt, 'second profile'):
        await msg.delete()
        from .myParameters import MY_ID2
        await client.forward_messages(chat_id=MY_ID2, from_chat_id=c_id, message_ids=msg.reply_to_message_id)

    # TODO parametri
    elif check_cmd(cmd_txt, 'terminal'):
        await msg.delete()
        if not msg.reply_to_message:
            await client.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PS}terminal")
            return
        await client.forward_messages(chat_id=TERMINAL_ID, from_chat_id=c_id, message_ids=msg.reply_to_message_id)

    else:
        await msg.delete()
        await client.send_message(chat_id=TERMINAL_ID,
                                  text=f"! Nessun comando trovato !\n{msg.text}\nchat:"
                                       f"{c_id if c_id != TERMINAL_ID else 'this chat'}")


# group 4 | handle_commands_for_other trigger: start with (MY_TAG + ' ' + PC + {cmd_txt}
# if incoming and m.text:
async def handle_commands_for_other(client: Client, msg: Msg):
    async with request_lock:
        _ = create_task_name(
            client.send_message(TERMINAL_ID, f"Nella chat `{msg.chat.id}` è stato richiesto da "
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
    text = (f"id:`{chat.id}`\ntype:{chat.type}\ntitle:{chat.title}\nusername:{chat.username}\nname:{chat.first_name}, "
            f"{chat.last_name}\n" if chat.last_name is not None else '\n')
    if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        text += f"inviteLink:{chat.invite_link}\nmembri:{chat.members_count}\ndescription:\n{chat.description}\n\n"
    elif chat.type == ChatType.PRIVATE:
        text += (f"bio:{chat.bio}\nphone:{getattr(chat, 'phone_number', '\\')}\n"
                 f"restrictions:{getattr(chat, 'restrictions', '\\')}\n\n")
    await client.send_message(TERMINAL_ID, text)
    if chat.type != ChatType.PRIVATE:
        return
    text = f"common chats:\n\n"
    chatlist = await client.get_common_chats(chat.id)
    for ch in chatlist:
        text += f"id:`{ch.id}`\ntype:{ch.type}\ntitle:{ch.title}\nusername:{ch.username}\nname:{ch.first_name}"
        text += f", {ch.last_name}\n" if ch.last_name is not None else '\n'
        text += f"inviteLink:{ch.invite_link}\nmembri:{ch.members_count}\ndescription:{ch.description}\n\n"
    await send_long_message(client, text)


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
    await client.send_message(chat_id=TERMINAL_ID, text=f"Verrai settato offline tra {seconds},{seconds * 2},"
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
    async def _moon(_m):
        from pyrogram.errors.exceptions.flood_420 import FloodWait
        moon_list = ["🌕", "🌖", "🌗", "🌘", "🌑", "🌒", "🌓", "🌔"]
        if other:
            _m = await _m.reply_text("LUNA UAU")
        try:
            sec = float(txt.split(" ")[1])
        except (IndexError, ValueError):
            sec = 0.1
        if sec < 0.1:
            sec = 0.1

        for i in range(29):
            moon_list = moon_list[-1:] + moon_list[:-1]
            text = ''.join(moon_list[:5]) + "ㅤ"
            try:
                _ = create_task_name(m.edit_text(text), name=f"moon edit {i}")
            except FloodWait:
                pass
            await sleep(sec)

        moon_list = moon_list[-1:] + moon_list[:-1]
        text = ''.join(moon_list[:5]) + "ㅤ"
        await m.edit_text(text)

    _ = create_task_name(_moon(m), name=f'moon{m.date.second}')


async def pipo(txt: str, m: Msg, other: bool):
    if other:
        msg = await m.reply_text("PIPO GROSSO")
    else:
        msg = m
    try:
        num = int(txt.split(" ")[1])
    except (IndexError, ValueError):
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
    text = (f"All commands usable from others:\n"
            f"Il prefix è `{MY_TAG} {PC}`\n"
            "Richieste: una ogni 20 sec, esclusa esecuzione, tutte in coda (in teoria)\n\n")
    all_other = {key: value for key, value in commands.items() if 'other' in value and value['other']}
    for group, cmd_info in h_groupping(all_other).items():
        text += h_format_group(group, cmd_info)
    return text


def help_(cmd_text):
    txts: list[str] = cmd_text.split(maxsplit=1)
    if len(txts) == 1:
        text = ("**help menu**\n\n"
                f"see all commands: `{PC}help a`\n"
                f"see other info `{PC}help+`\n"
                f"see all 'for others' commands: `{PC}help o`\n"
                f"see single `{PC}help ` cmd\n"
                f"see a group `{PC}help g ` name\n"
                f"search cmd `{PC}help ` query\n"
                f"search group `{PC}help g` query\n")
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
        results = {key: commands[key] for key in commands
                   if txts[1] in key or any(txts[1] in alias for alias in commands[key]['alias'])}
        text = f"All cmd find by your query '{txts[1]}':\n\n"
        for group, cmd_info in h_groupping(results).items():
            text += h_format_group(group, cmd_info)

    return text


# TODO upgrade
async def send_long_message(c: Client, text: str, chat_id: Union[int, str] = TERMINAL_ID,
                            parse_mode: Optional["ParseMode"] = None, chunk_size: int = 4096, chunk_start: str = "",
                            chunk_end: str = ""):
    from pyrogram.errors.exceptions.flood_420 import FloodWait
    chunk_size -= len(chunk_start) + len(chunk_end)

    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    for chunk in chunks:
        chunk = chunk_start + chunk + chunk_end
        uncomplete = True
        while uncomplete:
            try:
                await c.send_message(chat_id, str(chunk), parse_mode=parse_mode)
                uncomplete = False
            except FloodWait as e:
                await sleep(e.value)


async def eval_canc(c, m, t):
    from asyncio.exceptions import CancelledError
    try:
        await t
    except CancelledError:
        cancelled = f"m.chat.id:{m.chat.id} m.id:{m.id}"
        try:
            m = await c.get_messages(m.chat.id, m.id)
            from pyrogram.types import MessageEntity
            from pyrogram.enums import MessageEntityType
            m.entities.append(MessageEntity(
                type=MessageEntityType.CUSTOM_EMOJI,
                offset=len(m.text) + 2,
                length=1,
                custom_emoji_id=5465665476971471368
            ))
            # cancelled = f"{m.text}\n\n<b><emoji id=5465665476971471368>❌</emoji> Cancelled Error! </b>"
            cancelled = f"{m.text}\n\n❌ Cancelled Error! "
            await m.edit_text(
                cancelled,
                disable_web_page_preview=True,
                entities=m.entities
            )
        except Exception as e:
            await send_long_message(c, f"{cancelled}\n\nerror:\n{e.__class__.__name__}: {e}")
