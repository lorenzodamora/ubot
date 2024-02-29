"""
event handler
evito di usare i filter per evitare certi strani bug
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

        '''
    elif cmd_txt == 'tg':
        await msg.edit_text(str(msg.reply_to_message_id))

    elif cmd_txt == 'delp':
        from asyncio import sleep
        await msg.edit_text(f"del perpetuo starting")
        iid = msg.id
        while True:
            ids = []
            for i in range(0, 10):
                ids.append(iid)
                if iid == 730:
                    return
                iid -= 1
            # uncomplete = True
            # while uncomplete:
                # try:
            await client.delete_messages(chat_id=TERMINAL_ID, message_ids=ids)
            print(ids)
                    # uncomplete = False
                # except:
                    # await sleep(1)
        '''

        '''
    elif cmd_txt == 'test':
    # \'''
        st = 408
        await msg.edit_text(f"test starting\nst:{st} = {st*198}, msgs per blocco: 198")
        # for j in range(st, 50000):
          #  open(f"./search/search{j}.json", 'w').truncate()
        from asyncio import sleep
        await sleep(2)
        pass
        # jenny id = 6395926932
        from pyrogram.raw.functions.messages import GetMessages
        from pyrogram.raw.types import InputMessageID
        from pyrogram.raw.types.messages import Messages
        from typing import Union
        from pyrogram.enums import ParseMode
        ps = ParseMode.DISABLED
        for j in range(st, 10000):
            input_msgs = []
            fr = 198 * j + 1  # parte da 1 # comincia da 199
            to = 198 * j + 1 + 197 + 1  # si ferma a 198 incluso
            ra = range(fr, to)
            # print(f"range: {fr},{to}", end=" ")
            for i in ra:
                input_msgs.append(InputMessageID(id=i))
            get_messages_request = GetMessages(id=input_msgs)
            uncomplete = True
            result: Union[Messages | None] = None
            while uncomplete:
                try:
                    result = await client.invoke(get_messages_request)
                    uncomplete = False
                except:
                    await sleep(30); print("30", end=" ")

            ret = str(result)
            with open(f"./search/search{j}.json", 'w', encoding='utf-8')as file:
                file.write(ret)
                file.truncate()
            ret = ''
            for i in range(0, 198):  # da 0 a 197
                m = result.messages[i]
                # print(i, end=" ")
                pre = f"id: {m.id} => "
                t = str(type(m))
                if "pyrogram.raw.types.message.Message" in t:
                    text = False
                    if hasattr(getattr(m, "peer_id", None), "user_id"):
                        uid = m.peer_id.user_id
                        if 572621020 == uid:
                            pre += "Hexa"
                        elif 198626752 == uid:
                            pre += "WereWolf"
                        elif 311460626 == uid:
                            pre += "Social8Ball"
                        elif 319945680 == uid:
                            pre += "BgSchool"
                        elif 1976201765 == uid:
                            pre += "WaifuGacha"
                        else:
                            pre += f"user id: {uid}\n"
                            text = True
                    else:
                        pre += "m.peer_id.user_id non esiste\n"
                        text = True
                    if m.message and text:
                        pre += f"text: {m.message}"
                    elif text:
                        pre += "m.message non esiste"
                else:
                    if "pyrogram.raw.types.message_empty.MessageEmpty" in t:
                        continue
                    else:
                        pre += t
                ret += pre + "\n"

            chunk_size = 4096
            chunks = [ret[i:i + chunk_size] for i in range(0, len(ret), chunk_size)]

            mmsg: Union[Msg | None] = None
            uncomplete = True
            while uncomplete:
                try:
                    mmsg = await client.send_message(chat_id=TERMINAL_ID, text=f"from {fr} to {to}",
                                                     parse_mode=ps)
                    uncomplete = False
                except:
                    await sleep(20); print("20.1", end=" ")

            if ret == '':
                uncomplete = True
                while uncomplete:
                    try:
                        await client.send_message(chat_id=TERMINAL_ID, text=f"empty", parse_mode=ps)
                        uncomplete = False
                    except:
                        await sleep(20); print("20.2", end=" ")

            else:
                for chunk in chunks:
                    uncomplete = True
                    while uncomplete:
                        try:
                            await client.send_message(chat_id=TERMINAL_ID, text=str(chunk), parse_mode=ps)
                            uncomplete = False
                        except:
                            await sleep(20); print("20.3", end=" ")
                    # end while
                # end for
            uncomplete = True
            while uncomplete:
                try:
                    await mmsg.reply_text(text="fine blocco", parse_mode=ps)
                    uncomplete = False
                except:
                    await sleep(5); print("5", end=" ")
        # \'''
        await sleep(60)
        await client.send_message(chat_id=TERMINAL_ID, text="End test")
        print("END")
        from pushbullet import Pushbullet
        from ..myClientParameter import pushbullet_API_KEY as pushKey
        pb = Pushbullet(pushKey)
        pb.push_note("Ubot2", "END TEST")
        '''

        '''
    # TODO check parametri, rename, add to help, exceptions
    elif check_cmd(cmd_txt, {'test': 2}):
        from pyrogram.raw.functions.messages import GetMessages
        from pyrogram.raw.types import InputMessageID
        from asyncio import sleep
        in_ms = []
        fr, to = map(int, cmd_txt[4:].split(" "))

        # print(fr, end=' ')
        # print(to, end=' ')
        for i in range(fr, to):
            in_ms.append(InputMessageID(id=i))
        get_messages_request = GetMessages(id=in_ms)
        result = await client.invoke(get_messages_request)
        open(f"./search.json", 'w', encoding='utf-8').write(str(result))
        ret = ''
        for i in range(0, len(in_ms)):
            m = result.messages[i]
            print(i, end=" ")
            pre = f"id: {m.id} => "
            t = str(type(m))
            if "pyrogram.raw.types.message.Message" in t:
                text = False
                if hasattr(getattr(m, "peer_id", None), "user_id"):
                    uid = m.peer_id.user_id
                    # print(uid, end=' ')
                    if 572621020 == uid:
                        pre += "Hexa"
                    elif 198626752 == uid:
                        pre += "WereWolf"
                    elif 311460626 == uid:
                        pre += "Social8Ball"
                    elif 319945680 == uid:
                        pre += "BgSchool"
                    elif 1976201765 == uid:
                        pre += "WaifuGacha"
                    else:
                        pre += f"user id: {uid}\n"
                        text = True
                else:
                    pre += "m.peer_id.user_id non esiste\n"
                    text = True
                if m.message and text:
                    pre += f"text: {m.message}"
                elif text:
                    pre += "m.message non esiste"
            else:
                if "pyrogram.raw.types.message_empty.MessageEmpty" in t:
                    continue
                else:
                    pre += t
            ret += pre + "\n"

        chunk_size = 4096
        chunks = [ret[i:i + chunk_size] for i in range(0, len(ret), chunk_size)]

        if ret == '':
            uncomplete = True
            while uncomplete:
                try:
                    await client.send_message(chat_id=TERMINAL_ID, text=f"empty", parse_mode=ps)
                    uncomplete = False
                except:
                    await sleep(20)
                    print("20.2", end=" ")

        else:
            for chunk in chunks:
                uncomplete = True
                while uncomplete:
                    try:
                        await client.send_message(chat_id=TERMINAL_ID, text=str(chunk), parse_mode=ps)
                        uncomplete = False
                    except:
                        await sleep(20)
                        print("20.3", end=" ")
        '''

    # TODO rifare più ordinato, con parametri
    elif check_cmd(cmd_txt, {'h': 2, 'help': 2, '?': 2, 'commands': 2, 'c': 2}):
        await msg.delete()
        text = (f"**Lista di comandi**\n\nIl prefix è '`{PC}`'\n\n"
                f"`h` / `help` / `?` / `commands` / `c` : questo messaggio\n"
                "`0` : greetings\n`1` : Dammi un attimo + inserito in lista \"reply_waiting\"\n"
                "\nreply waiting::\n    `r` / `remove` : rimuovi dalla rw list la chat in cui hai scritto il comando\n"
                "    `grw` / `gw` : get reply waiting list (terminal)\n\n"
                "`del` : elimina il messaggio in reply\n"
                "`thisid` / `thisMsgId` / `MsgId` : modifica il messaggio col suo id\n"
                "  \"  __{n: int}__ : invia n messaggi con id\n"
                "`output` / `out` / `po`: stampa i file di output dei bot\n"
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
                "`eval h` / `exec ?` : guarda l'help di exec\n"
                "`reval h` / `rexec ?` : guarda l'help di reply exec\n"
                "`fe h` : guarda l'help di file-exec\n"
                "`pr` / `pt` : stampa result o traceback (eval)\n"
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

        '''
    # region ChatGPT
    elif check_cmd(cmd_txt, {'gpt': 2, 'chatGPT': 2}):
        from .gpt import chatpgt
        await chatpgt(msg)

    elif check_cmd(cmd_txt, {'rgpt': 2, 'replyChatGPT': 2}):
        rmsg = msg.reply_to_message
        if rmsg:
            from .gpt import chatpgt
            await chatpgt(rmsg)
        else:
            await client.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PC}rgpt")

    elif check_cmd(cmd_txt, {'gptst': 2, 'gptSet': 2}):
        from .gpt import chatpgt_set_key
        await chatpgt_set_key(msg)

    elif check_cmd(cmd_txt, {'gptcl': 2, 'gptClear': 2}):
        from .gpt import chatpgt_clear
        await chatpgt_clear(msg)
    # endregion
        '''

    # region print
    # TODO parametri
    elif check_cmd(cmd_txt, {'output': 2, 'out': 2, 'po': 2}):
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
            chunks = [txt[i_:i_ + chunk_s] for i_ in range(0, len(txt), chunk_s)]

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
            from pyrogram.errors.exceptions.flood_420 import FloodWait
            if not exists(path):
                await client.send_message(chat_id=TERMINAL_ID, text=f"il file {path} non esiste", parse_mode=ps)
                return
            txt = open(path, "r").read()
            if txt == "":
                txt = f"{path[12:]}: \n\nfile vuoto"
            else:
                txt = f"{path[12:]}: \n\n" + txt
            chunk_s = 4096
            chunks = [txt[i:i + chunk_s] for i in range(0, len(txt), chunk_s)]

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

        # End def
        from os import listdir
        for file in [f for f in listdir("./database/ga")]:
            await printoutput(f"database/ga/{file}")
        await client.send_message(chat_id=TERMINAL_ID, text="end print")

    elif check_cmd(cmd_txt, {'pr': 1, 'pt': 1}):
        from asyncio import sleep
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

    # region fast
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

    elif check_cmd(cmd_txt, {'auto': 1}):
        await client.edit_message_text(chat_id=msg.chat.id, message_id=msg.id,
                                       text="uso i messaggi automatici solo per far prima e poter gestire più persone,"
                                            "senza andare ad ignorare qualcuno involontariamente")
    # endregion

    # region reply-wait
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
    # endregion

    # region service commands
    elif check_cmd(cmd_txt, {'eval': 2, 'reval': 2, 'exec': 2, 'rexec': 2}):
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

    elif check_cmd(cmd_txt, {'feval': 2, 'fexec': 2, 'fe': 2}):
        txts = cmd_txt.split(maxsplit=1)
        if len(txts) == 1:
            await msg.edit(msg.text + f"\n!! see `{PC}feval h`")
            return

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
                from .code_runner import python_exec
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
            from .code_runner import python_exec
            await python_exec(client, msg)

    # TODO parametro seconds
    elif check_cmd(cmd_txt, {'offline': 2}):
        await msg.delete()
        await offline(client, 5, f"{PC}offline")

    elif check_cmd(cmd_txt, {'ping': 2}):
        await pong(client, msg, cmd_txt != "ping")

        '''
    elif cmd_txt == 'pingt':
        from .commands import pong
        await pong(client, msg, True)
        '''

    elif check_cmd(cmd_txt, {'del': 1}):
        await msg.delete()
        rmsg = msg.reply_to_message
        if not rmsg:
            await client.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PC}del ")
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
        
    # endregion

    # region get
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

    # TODO parameters
    elif check_cmd(cmd_txt, {'getall': 2, 'ga': 2}):
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
    # endregion

    # region special
    elif check_cmd(cmd_txt, {'moon': 2, 'luna': 2}):
        await moon(msg, cmd_txt, False)

        '''
    elif check_cmd(cmd_txt, {'genera': 2}):
        from asyncio import sleep
        txt = msg.text[8:]
        pri = ''
        for c in txt:
            pri += c
            try:
                await msg.edit_text(pri)
            except:
                pass
        '''

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
        # await client.send_message(chat_id=msg.chat.id, text=str(vars(client)) + "\ndone")
    # endregion

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
            await moon(msg, cmd_txt, True)

        elif check_cmd(cmd_txt, {'pipo': 2}):
            await pipo(cmd_txt, msg)

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


async def moon(m: Msg, txt: str, other: bool):
    moon_list = ["🌕", "🌖", "🌗", "🌘", "🌑", "🌒", "🌓", "🌔"]
    from asyncio import sleep, create_task
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


async def pipo(txt: str, m: Msg):
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
            text = "error. i numeri disponibili sono: 0, 1, 2, 3"
    await m.reply(text)
