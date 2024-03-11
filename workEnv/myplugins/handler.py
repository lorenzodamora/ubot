"""
event handler
evito di usare i filter per evitare certi strani bug
"""
from pyrogram import Client
from pyrogram.types import Message as Msg, Chat, User
from pyrogram.enums import ChatType, ParseMode
from .myParameters import (
    TERMINAL_ID,
    PREFIX_COMMAND as PC, PREFIX_SEND_TO as PS,
    MY_TAG,
    RW_PATH,
    HELP_PLUS_TEXT,
)
from .functions import *
from asyncio import Lock, sleep
from .tasker import create_task_name

request_lock = Lock()


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
        await c.send_message(TERMINAL_ID, HELP_PLUS_TEXT)

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
        _ = create_task_name(offline(c, 4, 10, f"comando {PC}1"), f'offline{sec}')
        if m.chat.type != ChatType.PRIVATE:
            return
        from .waiting import check_chat_for_reply_waiting, non_risposto, lock_rw
        if not await check_chat_for_reply_waiting(chat_id):
            return
        async with lock_rw:
            open(RW_PATH, 'a').write(f"{chat_id};1\n")
        _ = create_task_name(non_risposto(c, chat_id), f"non_risposto{sec}")
    # endregion

    # region get
    elif check_cmd(cmd_txt, 'get msg id'):
        rmsg = m.reply_to_message
        if rmsg:
            await m.edit_text(str(rmsg.id))
            return
        try:
            sec = int(cmd_txt.split(" ")[1])
        except (IndexError, ValueError):
            sec = 1
        from pyrogram.errors.exceptions.flood_420 import FloodWait
        await m.edit_text(f"this msg id: `{m.id}`")
        sec -= 1
        chat_id = m.chat.id

        async def _cycle():
            for _ in range(0, sec):
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
        from .myParameters import GA_FOLD
        if not exists(GA_FOLD):
            makedirs(GA_FOLD)

        from pprint import PrettyPrinter
        pp = PrettyPrinter(indent=2)

        open(GA_FOLD + '/ga_msg.txt', "w", encoding='utf-8').write(pp.pformat(vars(m)))
        open(GA_FOLD + '/ga_chat.txt',
             "w",
             encoding='utf-8').write(pp.pformat(vars(await c.get_chat(m.chat.id))))
        if m.reply_to_message:
            open(GA_FOLD + "/ga_rmsg.txt", "w", encoding='utf-8').write(pp.pformat(vars(m.reply_to_message)))
            open(GA_FOLD + "/ga_rchat.txt",
                 "w",
                 encoding='utf-8').write(pp.pformat(vars(await c.get_chat(m.reply_to_message.chat.id))))
        else:
            open(GA_FOLD + "/ga_rmsg.txt", "w", encoding='utf-8').truncate()
            open(GA_FOLD + "/ga_rchat.txt", "w", encoding='utf-8').truncate()
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
            from .myParameters import GA_FOLD
            for file in [f for f in listdir(GA_FOLD)]:
                path = f"{GA_FOLD}/{file}"
                if not exists(path):
                    await c.send_message(chat_id=TERMINAL_ID, text=f"il file {path} non esiste")
                    return
                txt = open(path, "r", encoding='utf-8').read()
                _title = f"{file}: \n\n"
                if txt == "":
                    txt = f"{_title}file vuoto"
                else:
                    txt = _title + txt
                await send_long_message(c, txt, chunk_start="```\n", chunk_end="\n```",
                                        offset_first_chunk_start=len(_title))

        await create_task_name(_internal(), name=f"pga{m.date.second}")

        await c.send_message(TERMINAL_ID, "end print")

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
                    sec = int(txts[i])
                    if sec not in [1, 2, 3, 4]:
                        raise ValueError
                    txts[i] = sec
            except (IndexError, ValueError):
                await c.send_message(TERMINAL_ID, f"`{m.text}`\ninvalid args, see `{PC}po h`")

        from platform import system

        async def printoutput(path: str, title_: str):
            txt = open(path, "r").read()
            _title = f"{title_}: output.txt\n\n"
            if txt == "":
                txt = f"{_title}file vuoto"
            else:
                txt = _title + txt
            await send_long_message(c, txt, chunk_start="```\n", chunk_end="\n```",
                                    offset_first_chunk_start=len(_title))

        async def _internal():
            if system() == "Windows":
                ind = 1
            elif system() == "Linux":
                ind = 0
            else:
                raise SystemError("Undefined operating system")

            from .myParameters import BOTLIST
            for _n in txts:
                match _n:
                    case 1:
                        await printoutput(BOTLIST['Ubot1']['paths'][ind], "Ubot1")
                    case 2:
                        await printoutput(BOTLIST['Ubot2']['paths'][ind], "Ubot2")
                    case 3:
                        await printoutput(BOTLIST['Infobot']['paths'][ind], "Infobot")
                    case 4:
                        await printoutput(BOTLIST['MeteoATbot']['paths'][ind], "MeteoATbot")

        _ = create_task_name(_internal(), f"output{m.date.second}")

    elif check_cmd(cmd_txt, 'print exec'):
        await m.delete()
        from .myParameters import RESULT_PATH, TRACEBACK_PATH
        rpath = RESULT_PATH if cmd_txt == 'pr' else TRACEBACK_PATH
        result_txt = open(rpath, "r", encoding='utf-8').read()
        title = f"{rpath[9:]}: \n\n"
        if result_txt == "":
            result_txt = f"{title}file vuoto"
        else:
            result_txt = title + result_txt

        await send_long_message(c, result_txt, chunk_start="```\n", chunk_end="\n```",
                                offset_first_chunk_start=len(title))
    # endregion

    # region reply-wait
    elif check_cmd(cmd_txt, 'get reply waiting'):
        await m.delete()
        from .waiting import lock_rw
        async with lock_rw:
            text = open(RW_PATH, "r").read()
        title = "reply_waiting.txt\n\n"
        if text == "":
            text = title + "file vuoto"
        else:
            text = title + text
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
    elif check_cmd(cmd_txt, 'delete'):
        await m.delete()
        try:
            sec = int(cmd_txt.split(" ")[1])
            if sec > 100:
                sec = 100
        except (ValueError, IndexError):
            sec = 1

        rmsg = m.reply_to_message
        of_id = m.id if not rmsg else rmsg.id
        ids = [item.id async for item in c.get_chat_history(m.chat.id, sec, offset_id=of_id)]

        effettivi = await c.delete_messages(m.chat.id, ids)
        if effettivi != sec:
            await c.send_message(TERMINAL_ID, f"{m.text}\nchat id:`{m.chat.id}`; msg offset id:`{of_id}`"
                                              f"\neliminati effettivi:{effettivi}")

    elif check_cmd(cmd_txt, 'eval') or check_cmd(cmd_txt, 'eval reply'):
        txts = cmd_txt.split(maxsplit=1)
        if len(txts) == 2:
            if txts[1] in ['h', '?']:
                from .code_runner import PRE_EXEC
                await m.edit(f"`{PC}eval ` pre exec code is:\n\n"
                             f"<pre language=\"python\">{PRE_EXEC}</pre>\nfirst line:{PRE_EXEC.count('\n') + 2}")
                return
        from .code_runner import python_exec
        task = create_task_name(python_exec(c, m), f'exec{m.date.second}')
        await eval_canc(c, m, task)

    elif check_cmd(cmd_txt, 'eval file'):

        async def _fexec():
            from .myParameters import PY_EXEC_FOLD, RESULT_PATH
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
                    fpath = f"{PY_EXEC_FOLD}/{_txts[1]}"
                    if not exists(fpath):
                        await m.edit(f"`{m.text}`\nil file {_txts[1]} non esiste")
                        return
                    m.text = f"{PC}eval " + open(fpath, 'r', encoding='utf-8').read()
                    await python_exec(c, m)

                elif _txts[1] in ['l', 'L']:
                    from os import listdir
                    file_list = listdir(PY_EXEC_FOLD)
                    result = ""
                    for file_name in file_list:
                        fnote = ""
                        is_note = False

                        fstream = open(f"{PY_EXEC_FOLD}/{file_name}", 'r', encoding='utf-8')
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
                        open(RESULT_PATH, 'w', encoding='utf-8').write(result)
                        await m.edit_text(f"file eval list: view {RESULT_PATH} or print with `{PC}pr")

                elif _txts[1].startswith(('d', 'r')):
                    _txts = _txts[1].split(maxsplit=2)
                    if len(_txts) != 2:
                        await m.edit(f"per `{PC}feval d ` bisogna mettere il fileName")
                        return
                    from os.path import exists
                    fpath = f"{PY_EXEC_FOLD}/{_txts[1]}"
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
                fpath = f"{PY_EXEC_FOLD}/{fcrea[0]}"
                open(fpath, 'w', encoding='utf-8').write(fcrea[1])
                m.text = f"{PC}eval " + open(fpath, 'r', encoding='utf-8').read()
                await python_exec(c, m)

        task = create_task_name(_fexec(), f'exec file{m.date.second}')
        await eval_canc(c, m, task)

    elif check_cmd(cmd_txt, 'offline'):
        await m.delete()
        try:
            sec = float(cmd_txt.split(" ")[1])
        except (ValueError, IndexError):
            sec = 5
        try:
            iter_ = int(cmd_txt.split(" ")[2])
        except (ValueError, IndexError):
            iter_ = 4
        _ = create_task_name(offline(c, sec, iter_, f"{PC}offline"), f"offline{m.date.second}")

    elif check_cmd(cmd_txt, 'ping'):  # or pingt
        await pong_(c, m, cmd_txt != "ping")
    # endregion

    # region special
    elif check_cmd(cmd_txt, 'moon'):
        await moon(m, cmd_txt, False)

    elif check_cmd(cmd_txt, 'pipo'):
        await pipo(cmd_txt, m, False)

    elif check_cmd(cmd_txt, 'null'):
        rmsg = m.reply_to_message
        await m.delete()
        if rmsg:
            await rmsg.reply("ㅤ")
        else:
            await c.send_message(chat_id=m.chat.id, text="ㅤ")
    # endregion

    else:
        await m.delete()
        await c.send_message(
            TERMINAL_ID,
            f"! cmd don't found !\n{m.text}\nchat:{m.chat.id if m.chat.id != TERMINAL_ID else 'this chat'}"
        )


async def handle_send_to(client: Client, msg: Msg):
    cmd_txt = msg.text[1:].lower()
    c_id = msg.chat.id

    # ">." iniziali fanno in modo che venga scritto > senza comando
    if cmd_txt != "" and cmd_txt[0] == ".":
        await msg.edit_text(PS + msg.text[2:])

    elif check_cmd(cmd_txt, 'pic'):
        await msg.delete()
        if not msg.reply_to_message:
            await client.send_message(TERMINAL_ID, f"nessun reply per il comando {PS}pic")
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
            await client.send_message(TERMINAL_ID, f"nessun reply per il comando {PS}save")
            return
        await client.forward_messages('me', msg.chat.id, msg.reply_to_message_id)

    elif check_cmd(cmd_txt, 'second profile'):
        await msg.delete()
        from .myParameters import MY_ID2
        await client.forward_messages(MY_ID2, c_id, msg.reply_to_message_id)

    # TODO parametri  ???
    elif check_cmd(cmd_txt, 'terminal'):
        await msg.delete()
        if not msg.reply_to_message:
            await client.send_message(TERMINAL_ID, f"nessun reply per il comando {PS}terminal")
            return
        await client.forward_messages(TERMINAL_ID, c_id, msg.reply_to_message_id)

    else:
        await msg.delete()
        await client.send_message(
            TERMINAL_ID,
            f"! Nessun comando trovato !\n{msg.text}\nchat:{c_id if c_id != TERMINAL_ID else 'this chat'}")


async def handle_commands_for_other(client: Client, msg: Msg):
    async with request_lock:
        _ = create_task_name(client.send_message(
            TERMINAL_ID,
            f"Nella chat `{msg.chat.id}` è stato richiesto da `{msg.from_user.id}` il comando\n{msg.text}"
        ))

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
