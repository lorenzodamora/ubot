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
from .tasker import create_task_name as ctn

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
            _ = ctn(remove_rw(str(ch.id)), name=f'remove{sec}')

    if encode_valid:
        if is_me and msg.text:
            # group 1
            if msg.text.startswith(PC):
                _ = ctn(handle_commands(client, msg), name=f"handle{sec}")
            # group 2
            elif msg.text.startswith(PS):
                _ = ctn(handle_send_to(client, msg), name=f"handle{sec}")

    # group 3
    if is_pvt and incoming:
        from .waiting import benvenuto
        _ = ctn(benvenuto(client, msg), name=f"benvenuto{sec}")

    # group 4 | handle_commands_for_other trigger: start with (MY_TAG + ' ' + PC + {cmd_txt})
    if encode_valid:
        if incoming and msg.text:
            if msg.text.lower().startswith(MY_TAG + ' ' + PC):
                _ = ctn(handle_commands_for_other(client, msg), name=f"other{sec}")


async def handle_commands(c: Client, m: Msg):
    # Estrai il testo del messaggio dopo ","
    cmd_txt_original = m.text[1:]
    cmd_txt = cmd_txt_original.lower()

    # ",." iniziali fanno in modo che venga scritto , senza comando
    if cmd_txt != "" and cmd_txt[0] == ".":
        await m.edit_text(PC + cmd_txt_original[1:])
        return

    async def _matcher(cmd_match, is_del: bool = False, note: str = ""):
        nonlocal m, c, cmd_txt_original, cmd_txt

        def _del(_m: Msg):
            if not is_del:
                _ = ctn(_m.delete())

        match cmd_match:
            case '?+':
                _del(m)
                await c.send_message(TERMINAL_ID, HELP_PLUS_TEXT)

            case '?':
                _del(m)
                await c.send_message(TERMINAL_ID, help_(cmd_txt_original))

            # region fast
            case 'automatici':
                txts: list[str] = cmd_txt_original.split(maxsplit=1)
                if len(txts) == 1:
                    text = ("uso i messaggi automatici solo per far prima e poter gestire più persone, "
                            "senza andare ad ignorare qualcuno involontariamente")
                elif txts[1] == 'e':
                    text = ("I use automatic messages just to save time and manage more people, "
                            "without unintentionally ignoring anyone")
                else:
                    _del(m)
                    c_id = m.chat.id
                    await c.send_message(chat_id=TERMINAL_ID,
                                         text=f"! No lang found !\n{m.text}\nchat:"
                                              f"{c_id if c_id != TERMINAL_ID else 'this chat'}")
                    return
                await m.edit(text=text)

            case 'greetings':
                txts: list[str] = cmd_txt_original.split(maxsplit=1)
                if len(txts) == 1:
                    text = "buondì\ncome va?"
                elif txts[1] == 'e':
                    text = "Hii!!\nwhat's up?"
                else:
                    _del(m)
                    c_id = m.chat.id
                    await c.send_message(chat_id=TERMINAL_ID,
                                         text=f"! No greetings found !\n{m.text}\n"
                                              f"chat:{c_id if c_id != TERMINAL_ID else 'this chat'}")
                    return
                await m.edit(text=text)

            case 'strikethrough':
                rmsg = m.reply_to_message
                _del(m)
                check = bool(rmsg)
                if check:
                    check = bool(rmsg.text)
                    if rmsg.from_user:
                        check = check and bool(rmsg.from_user.is_self)
                if not check:
                    await c.send_message(TERMINAL_ID, f"il comando {PC}done vuole un reply a un mio text msg")
                    return
                try:
                    # await rmsg.edit_text(f"~~{rmsg.text}~~")  # this applies avoided markdown
                    from pyrogram.types import MessageEntity
                    from pyrogram.enums import MessageEntityType
                    if rmsg.entities is None:
                        rmsg.entities = []
                    rmsg.entities.append(
                        MessageEntity(type=MessageEntityType.STRIKETHROUGH, offset=0, length=len(rmsg.text))
                    )
                    await rmsg.edit_text(rmsg.text, entities=rmsg.entities)
                except Exception as e:
                    await send_long_msg(c, f"errore in {m.text} {m.chat.id}:{e.__class__.__name__}:\n{e}")

            case 'un attimo':
                chat_id = m.chat.id
                sec_in = m.date.second
                await m.edit("Dammi un attimo e ti scrivo subito.")
                _ = ctn(offline(c, 4, 10, f"comando {PC}1"), f'offline{sec_in}')
                if m.chat.type != ChatType.PRIVATE:
                    return
                from .waiting import check_chat_for_reply_waiting as ccfrw, lock_rw, non_risposto
                if not await ccfrw(chat_id):
                    return
                async with lock_rw:
                    open(RW_PATH, 'a').write(f"{chat_id};1\n")
                _ = ctn(non_risposto(c, chat_id), f"non_risposto{sec_in}")
            # endregion

            # region get
            case 'get msg id':
                rmsg = m.reply_to_message
                if rmsg:
                    await m.edit_text(str(rmsg.id))
                    return
                try:
                    n_input = int(cmd_txt.split(" ")[1])
                except (IndexError, ValueError):
                    n_input = 1
                from pyrogram.errors.exceptions.flood_420 import FloodWait
                await m.edit_text(f"this msg id: `{m.id}`")
                n_input -= 1
                chat_id = m.chat.id

                async def _cycle():
                    for _ in range(0, n_input):
                        uncomplete = True
                        while uncomplete:
                            try:
                                _m = await c.send_message(chat_id=chat_id, text="thisid")
                                await _m.edit_text(f"this msg id: `{_m.id}`")
                                uncomplete = False
                            except FloodWait as _e:
                                await sleep(_e.value)

                _ = ctn(_cycle(), f'thisid{m.date.second}')

            case 'getall':
                _del(m)
                # Crea la directory se non esiste già
                from os import makedirs
                from os.path import exists
                from pprint import PrettyPrinter
                from .myParameters import GA_FOLD

                if not exists(GA_FOLD):
                    makedirs(GA_FOLD)

                pp = PrettyPrinter(indent=2)
                ppf = pp.pformat

                open(GA_FOLD + '/ga_msg.txt', "w", encoding='utf-8').write(ppf(vars(m)))
                open(GA_FOLD + '/ga_chat.txt',
                     "w",
                     encoding='utf-8').write(ppf(vars(await c.get_chat(m.chat.id))))
                if m.reply_to_message:
                    open(GA_FOLD + "/ga_rmsg.txt", "w", encoding='utf-8').write(ppf(vars(m.reply_to_message)))
                    open(GA_FOLD + "/ga_rchat.txt",
                         "w",
                         encoding='utf-8').write(ppf(vars(await c.get_chat(m.reply_to_message.chat.id))))
                else:
                    open(GA_FOLD + "/ga_rmsg.txt", "w", encoding='utf-8').truncate()
                    open(GA_FOLD + "/ga_rchat.txt", "w", encoding='utf-8').truncate()
                await c.send_message(chat_id=TERMINAL_ID, text=f"creati 4 file dal comando {PC}getAll\n"
                                                               f"per stamparli: {PC}pga o printga")

            case 'getchat':
                _del(m)
                await getchat(c, await c.get_chat(m.chat.id))

            case 'getchat reply':
                _del(m)
                # Ottieni il messaggio di risposta
                rmsg = m.reply_to_message
                # Verifica se il messaggio ha una risposta
                if not rmsg:
                    await c.send_message(chat_id=TERMINAL_ID, text=f"nessun reply per il comando {PC}getreply")
                    return
                await getchat(c, await c.get_chat(rmsg.chat.id))

            case 'getid':
                _del(m)
                id_ = m.reply_to_message.from_user.id if m.reply_to_message else m.chat.id
                await c.send_message(TERMINAL_ID, f"`{id_}`")

            case 'getme':
                _del(m)
                from pprint import PrettyPrinter
                from pyrogram.raw.functions.users import GetFullUser
                from pyrogram.raw.types import InputUserSelf

                pp = PrettyPrinter(indent=2)
                ppf = pp.pformat

                await c.send_message(TERMINAL_ID, f"client.get_me():\n```\n{ppf(vars(await c.get_me()))}\n```")
                await c.send_message(TERMINAL_ID, f"GetFullUser:\n```\n"
                                                  f"{ppf(await c.invoke(GetFullUser(id=InputUserSelf())))}\n```")
                await c.send_message(TERMINAL_ID, f"client.me:\n```\n{ppf(c.me)}\n```")

            case 'gets':
                _del(m)
                # m.text = PC + ('getr' if m.reply_to_message else 'getchat')
                find = finder_cmd('getr' if m.reply_to_message else 'getchat')
                await _matcher(find, True)

            case 'search':
                _del(m)
                txts: list[str] = cmd_txt_original.split(maxsplit=1)
                if len(txts) == 1:
                    await c.send_message(TERMINAL_ID, f"query missing for `{PC}search`")
                    return
                try:
                    await getchat(c, await c.get_chat(txts[1]))
                except Exception as e:
                    await c.send_message(TERMINAL_ID, f"{e}\n\n`{m.text}`:\nil comando cerca per id o per username")

            case 'search reply':
                _del(m)
                rmsg = m.reply_to_message
                if not rmsg:
                    await c.send_message(TERMINAL_ID, f"nessun reply per il comando `{PC}rsearch`")
                    return
                try:
                    await getchat(c, await c.get_chat(rmsg.text))
                except Exception as e:
                    await c.send_message(TERMINAL_ID,
                                         f"{e.__class__.__name__}: {e}\n\nil comando cerca per id o per username",
                                         parse_mode=ParseMode.DISABLED)
            # endregion

            # region print
            case 'getall print':
                _del(m)
                from os.path import exists
                from os import listdir

                async def _internal():
                    from .myParameters import GA_FOLD
                    for file in [f for f in listdir(GA_FOLD)]:
                        path = f"{GA_FOLD}/{file}"
                        if not exists(path):
                            await c.send_message(chat_id=TERMINAL_ID, text=f"il file {path} non esiste")
                            return
                        _txt = open(path, "r", encoding='utf-8').read()
                        _title = f"{file}: \n\n"
                        if _txt == "":
                            _txt = f"{_title}file vuoto"
                        else:
                            _txt = _title + _txt
                        await send_long_msg(c, _txt, chunk_start="```\n", chunk_end="\n```",
                                            offset_first_chunk_start=len(_title))

                await ctn(_internal(), name=f"pga{m.date.second}")
                await c.send_message(TERMINAL_ID, "end print")

            case 'output':
                _del(m)
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
                            n_input = int(txts[i])
                            if n_input not in [1, 2, 3, 4]:
                                raise ValueError
                            txts[i] = n_input
                    except (IndexError, ValueError):
                        await c.send_message(TERMINAL_ID, f"`{m.text}`\ninvalid args, see `{PC}po h`")

                from platform import system

                async def printoutput(path: str, title_: str):
                    _txt = open(path, "r").read()
                    _title = f"{title_}: output.txt\n\n"
                    if _txt == "":
                        _txt = f"{_title}file vuoto"
                    else:
                        _txt = _title + _txt
                    await send_long_msg(c, _txt, chunk_start="```\n", chunk_end="\n```",
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

                _ = ctn(_internal(), f"output{m.date.second}")

            case 'print exec':
                _del(m)
                from .myParameters import RESULT_PATH, TRACEBACK_PATH
                rpath = RESULT_PATH if cmd_txt == 'pr' else TRACEBACK_PATH
                result_txt = open(rpath, "r", encoding='utf-8').read()
                title = f"{rpath[9:]}: \n\n"
                if result_txt == "":
                    result_txt = f"{title}file vuoto"
                else:
                    result_txt = title + result_txt

                await send_long_msg(c, result_txt, chunk_start="```\n", chunk_end="\n```",
                                    offset_first_chunk_start=len(title))
            # endregion

            # region reply-wait
            case 'get reply waiting':
                _del(m)
                from .waiting import lock_rw
                async with lock_rw:
                    text = open(RW_PATH, "r").read()
                title = "reply_waiting.txt\n\n"
                if text == "":
                    text = title + "file vuoto"
                else:
                    text = title + text
                await send_long_msg(c, text)

            case 'remove':
                _del(m)
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
                _ = ctn(remove_rw(str(c_id)), f"remove{m.date.second}")
            # endregion

            # region service-cmd
            case 'delete':
                _del(m)
                try:
                    n_input = int(cmd_txt.split(" ")[1])
                    if n_input > 100:
                        n_input = 100
                except (ValueError, IndexError):
                    n_input = 1

                rmsg = m.reply_to_message
                of_id = m.id if not rmsg else rmsg.id
                ids = [item.id async for item in c.get_chat_history(m.chat.id, n_input, offset_id=of_id)]

                effettivi = await c.delete_messages(m.chat.id, ids)
                if effettivi != n_input:
                    await c.send_message(TERMINAL_ID, f"{m.text}\nchat id:`{m.chat.id}`; msg offset id:`{of_id}`"
                                                      f"\neliminati effettivi:{effettivi}")

            case 'delcmd':
                m = await m.edit(PC + cmd_txt_original[cmd_txt_original.find(PC) + 2:])
                cmd_txt_original = m.text[1:]
                cmd_txt = m.text[1:].lower()
                find = finder_cmd(cmd_txt_original)
                _del(m)
                note = note + ("" if note == "" else '\n') + 'delcmd'
                try:
                    _ = ctn(slm(c, f"you send a delcmd\ntxt (prob parsed):\n\n{m.text}\n\nchat id:`{m.chat.id}`"
                                   f" msg id:`{m.id}`"))
                    await _matcher(find, True, note=note)
                except Exception as e:
                    await slm(c, f"exception inside delcmd:\n{e}")

            case 'eval' | 'eval reply':
                txts = cmd_txt.split(maxsplit=1)
                if len(txts) == 2:
                    if txts[1] in ['h', '?']:
                        from .code_runner import PRE_EXEC
                        await m.edit(f"`{PC}eval ` pre exec code is:\n\n"
                                     f"<pre language=\"python\">{PRE_EXEC}</pre>\n"
                                     f"first line:{PRE_EXEC.count('\n') + 2}")
                        return
                from .code_runner import python_exec
                task = ctn(python_exec(c, m), f'exec{m.date.second}')
                await eval_canc(c, m, task)

            case 'eval file':
                async def _fexec():
                    from .myParameters import PY_EXEC_FOLD, RESULT_PATH
                    _txts = cmd_txt_original.split(maxsplit=1)
                    if len(_txts) == 1:
                        await m.edit(f"{PC}{cmd_txt_original}\n!! see `{PC}feval h`")
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
                                await m.edit(f"`{PC}{cmd_txt_original}`\nil file {_txts[1]} non esiste")
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
                            await m.edit(f"`{PC}{cmd_txt_original}`\n!! file deleted !!")

                        else:
                            await m.edit(f"`{PC}{cmd_txt_original}`\n!! command not found !!")
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

                task = ctn(_fexec(), f'exec file{m.date.second}')
                await eval_canc(c, m, task)

            case 'offline':
                _del(m)
                try:
                    n_input = float(cmd_txt.split(" ")[1])
                except (ValueError, IndexError):
                    n_input = 5
                try:
                    iter_ = int(cmd_txt.split(" ")[2])
                except (ValueError, IndexError):
                    iter_ = 4
                _ = ctn(offline(c, n_input, iter_, f"{PC}offline"), f"offline{m.date.second}")

            case 'ping':  # or pingt
                await pong_(c, m, cmd_txt != "ping")

            case 'version':
                _del(m)
                await c.send_message(m.chat.id, get_version())

            case 'source code':
                _del(m)
                from .myParameters import SOURCE_CODE_LINK
                await c.send_message(
                    m.chat.id,
                    f"this is my source code: [link]({SOURCE_CODE_LINK})",
                    disable_web_page_preview=True
                )
            # endregion

            # region special
            case 'moon':
                await moon(m, cmd_txt, False)

            case 'pipo':
                await pipo(cmd_txt, m, False)

            case 'null':
                rmsg = m.reply_to_message
                _del(m)
                if rmsg:
                    await rmsg.reply("ㅤ", quote=True)
                else:
                    await c.send_message(chat_id=m.chat.id, text="ㅤ")
            # endregion

            case _:
                _del(m)
                await c.send_message(
                    TERMINAL_ID,
                    f"! cmd don't found !\n{m.text}\nchat:{m.chat.id if m.chat.id != TERMINAL_ID else 'this chat'}"
                )

    await _matcher(finder_cmd(cmd_txt))


async def handle_send_to(c: Client, m: Msg):
    cmd_txt_original = m.text[1:]
    cmd_txt = cmd_txt_original.lower()
    c_id = m.chat.id

    # ">." iniziali fanno in modo che venga scritto > senza comando
    if cmd_txt != "" and cmd_txt[0] == ".":
        await m.edit_text(PC + cmd_txt_original[1:])
        return

    async def _matcher(cmd_match, is_del: bool = False):
        nonlocal m, c, cmd_txt_original, cmd_txt

        def _del(_m: Msg):
            if not is_del:
                _ = ctn(_m.delete())

        match cmd_match:
            case 'pic':
                _del(m)
                if not m.reply_to_message:
                    await c.send_message(TERMINAL_ID, f"nessun reply per il comando {PS}pic")
                    return
                from .pyrogram_forward_to_topic import forward_to_topic as for_top
                from .myParameters import SAVED_MESSAGE_FORUM_ID, PIC_TOPIC_ID
                await for_top(source_channel_id=c_id,
                              destination_channel_id=SAVED_MESSAGE_FORUM_ID,
                              forwarded_message_id=m.reply_to_message_id,
                              topic_init_message_id=PIC_TOPIC_ID,
                              client=c)

            case 'save':
                _del(m)
                if not m.reply_to_message:
                    await c.send_message(TERMINAL_ID, f"nessun reply per il comando {PS}save")
                    return
                await c.forward_messages('me', m.chat.id, m.reply_to_message_id)

            case 'second profile':
                _del(m)
                from .myParameters import MY_ID2
                await c.forward_messages(MY_ID2, c_id, m.reply_to_message_id)

            # TODO parametri, copy or forward, ???
            case 'terminal':
                _del(m)
                if not m.reply_to_message:
                    await c.send_message(TERMINAL_ID, f"nessun reply per il comando {PS}terminal")
                    return
                await c.forward_messages(TERMINAL_ID, c_id, m.reply_to_message_id)

            case _:
                _del(m)
                await c.send_message(
                    TERMINAL_ID,
                    f"! cmd don't found !\n{m.text}\nchat:{c_id if c_id != TERMINAL_ID else 'this chat'}"
                )

    await _matcher(finder_cmd(cmd_txt))


async def handle_commands_for_other(c: Client, m: Msg):
    async with request_lock:
        _ = ctn(c.send_message(
            TERMINAL_ID,
            f"Nella chat `{m.chat.id}` è stato richiesto da `{m.from_user.id}` il comando\n{m.text}"
        ))
        secs = 20
        cmd_txt_original = m.text[len(MY_TAG + ' ' + PC):]
        cmd_txt = cmd_txt_original.lower()

        if check_cmd(cmd_txt, '?'):
            await m.reply_text(help_other())
            secs = 5

        elif check_cmd(cmd_txt, 'moon'):
            await moon(m, cmd_txt, True)

        elif check_cmd(cmd_txt, 'pipo'):
            await pipo(cmd_txt, m, True)

        elif check_cmd(cmd_txt, 'null'):
            await (m.reply_to_message if m.reply_to_message else m).reply_text("ㅤ")
            secs = 3

        elif check_cmd(cmd_txt, 'version'):
            await m.reply(get_version())
            secs = 1

        elif check_cmd(cmd_txt, 'source code'):
            from .myParameters import SOURCE_CODE_LINK
            await m.reply(f"this is my source code: [link]({SOURCE_CODE_LINK})", disable_web_page_preview=True)
            secs = 2

        else:
            await m.reply_text(f"! No cmd founded !\n`{m.text}`")
            secs = 5

        await sleep(secs)
