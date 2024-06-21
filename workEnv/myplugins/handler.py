"""
event handler
evito di usare i filter per evitare certi strani bug
"""
from pyrogram import Client
from pyrogram.types import Message as Msg, Chat, User
from pyrogram.raw.base import Update
from pyrogram.enums import ChatType, ParseMode
from .myParameters import \
    TERMINAL_ID, MY_TAG, HELP_PLUS_TEXT, PREFIX_COMMAND as PC, PREFIX_SEND_TO as PS, myDispatcher
from .functions import *
from asyncio import Lock, sleep
from .tasker import create_task_name as ctn

request_lock = Lock()


@Client.on_raw_update(group=1)
async def raw_update(_, update: Update, __, ___):
    myDispatcher.add_event(update)


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
        _ = ctn(benvenuto(client, msg), name=f"benvenuto{sec}")

    # group 4 | handle_commands_for_other trigger: start with (MY_TAG + ' ' + PC + {cmd_txt})
    if encode_valid:
        if incoming and msg.text:
            if msg.text.lower().startswith(MY_TAG.lower() + ' ' + PC):
                _ = ctn(handle_commands_for_other(client, msg), name=f"other{sec}")

    myDispatcher.add_event(msg)


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
                    await send_long_msg(f"errore in {m.text} `{m.chat.id}`:{e.__class__.__name__}:\n{e}", client=c)

            case 'un attimo':
                chat_id = m.chat.id
                sec_in = m.date.second
                await m.edit("Dammi un attimo e ti scrivo subito.")
                _ = ctn(offline(c, 4, 10, f"comando {PC}1"), f'offline{sec_in}')
            # endregion

            # region get
            case 'get msg id':
                rmsg = m.reply_to_message
                if rmsg:
                    if rmsg.message_thread_id:
                        txt = f"{rmsg.id} top:{rmsg.message_thread_id}"
                    else:
                        txt = str(rmsg.id)
                    await m.edit_text(txt)
                    return
                try:
                    n_input = int(cmd_txt.split(" ")[1])
                except (IndexError, ValueError):
                    n_input = 1

                top_id = m.message_thread_id
                if top_id:
                    txt = f"this msg id: `{m.id}`  top id: `{top_id}`"
                else:
                    txt = f"this msg id: `{m.id}`"
                await m.edit_text(txt)

                from pyrogram.errors.exceptions.flood_420 import FloodWait
                n_input -= 1
                chat_id = m.chat.id

                async def _cycle():
                    for _ in range(0, n_input):
                        while True:
                            try:
                                _m = await c.send_message(chat_id=chat_id, message_thread_id=top_id, text="get msg id")
                                await _m.edit_text(f"this msg id: `{_m.id}`")
                                break
                            except FloodWait as _e:
                                await sleep(_e.value)

                _ = ctn(_cycle(), f'get msg id{m.date.second}')

            case 'getall':
                _del(m)
                # Crea la directory se non esiste già
                from os import makedirs, path
                from pprint import PrettyPrinter
                from .myParameters import GA_FOLD

                if not path.exists(GA_FOLD):
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
                from os import listdir, path

                async def _internal():
                    from .myParameters import GA_FOLD
                    for file in [f for f in listdir(GA_FOLD)]:
                        ga_path = f"{GA_FOLD}/{file}"
                        if not path.exists(ga_path):
                            await c.send_message(chat_id=TERMINAL_ID, text=f"il file {ga_path} non esiste")
                            return
                        _txt = open(ga_path, "r", encoding='utf-8').read()
                        _title = f"{file}: \n\n"
                        if _txt == "":
                            _txt = f"{_title}file vuoto"
                        else:
                            _txt = _title + _txt
                        await send_long_msg(_txt, chunk_start="```\n", chunk_end="\n```",
                                            offset_first_chunk_start=len(_title), client=c)

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
                    await send_long_msg(_txt, chunk_start="```\n", chunk_end="\n```",
                                        offset_first_chunk_start=len(_title), client=c)

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
                from .myParameters import EVALCODE_PATH, RESULT_PATH, TRACEBACK_PATH
                match cmd_txt:
                    case 'pr':
                        rpath = RESULT_PATH
                    case 'pt':
                        rpath = TRACEBACK_PATH
                    case 'pc':
                        rpath = EVALCODE_PATH
                    case _:
                        raise ValueError("error in match case of print exec case")

                # rpath = RESULT_PATH if cmd_txt == 'pr' else TRACEBACK_PATH
                result_txt = open(rpath, "r", encoding='utf-8').read()
                title = f"{rpath.split("/")[-1]}: \n\n"
                if result_txt == "":
                    result_txt = f"{title}file vuoto"
                else:
                    result_txt = title + result_txt

                await send_long_msg(result_txt, chunk_start="```\n", chunk_end="\n```",
                                    offset_first_chunk_start=len(title), client=c)
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
                    _ = ctn(send_long_msg(
                        f"you send a delcmd\ntxt (prob parsed):\n\n{m.text}\n\nchat id:`{m.chat.id}` msg id:`{m.id}`",
                        client=c
                    ))
                    await _matcher(find, True, note=note)
                except Exception as e:
                    await send_long_msg(f"exception inside delcmd:\n{e.__class__.__name__}:\n{e}", client=c)

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
                    from .myParameters import PY_EXEC_FOLD
                    from .code_runner import python_exec
                    the_cmd = get_the_cmd(m.text)
                    opt = the_cmd['options']
                    arg = the_cmd['arg']
                    if len(opt) > 1:
                        await m.edit(f"{m.text}\n!! only one option, see `{PC}feval {PC}h`")
                        return

                    elif len(opt) == 1:
                        if opt[0] in ['h', '?'] and arg == '':
                            await m.edit(f"`{PC}feval `(file exec)  options with prefix {PC}:\n\n"
                                         "`h` / `?` : this help menù\n\n"
                                         "[fname] [code] : create file with fname and run code\n"
                                         "if exist overwrite. by default it add final '.txt'\n"
                                         "requirements: min 2 char; max one word\n\n"
                                         "`f `/ `r ` [fname] : run selected file\n"
                                         "don't include final '.txt'\n\n"
                                         "`L` : list of files\n"
                                         'read file comment too\n'
                                         'comment requirement: header: """\\n comment\\n""")\n\n'
                                         '`s` [fname]: see file\n\n'
                                         "`d ` [fname]: delete file\n\n"
                                         f"`{PC}eval ?` : see pre_exec")
                            return

                        elif opt[0] in ['f', 'F', 'r', 'R']:
                            if arg == '':
                                # await m.edit(f"per `{the_cmd['prefix']}{the_cmd['cmd']} {PC}{opt[0]} ` "
                                await m.edit(f"per `{m.text} ` "
                                             f"bisogna mettere il fileName")
                                return
                            from os.path import exists
                            fpath = f"{PY_EXEC_FOLD}/{arg}.txt"
                            if not exists(fpath):
                                await m.edit(f"`{m.text}`\nil file {arg} non esiste")
                                return
                            m.text = f"{PC}eval " + open(fpath, 'r', encoding='utf-8').read()
                            try:
                                await python_exec(c, m)
                            except ValueError as ve:
                                await m.edit(f"`{PC}{cmd_txt_original}`\n{ve.__class__.__name__}: {ve}")

                        elif opt[0] in ['l', 'L'] and arg == '':
                            from os import listdir
                            file_list = listdir(PY_EXEC_FOLD)
                            result = ""
                            for file_name in file_list:
                                fnote = ""
                                is_note = False

                                fstream = open(f"{PY_EXEC_FOLD}/{file_name}", 'r', encoding='utf-8')
                                next(fstream)  # skip first line with opening """
                                for line_number, line in enumerate(fstream, start=1):
                                    if line.startswith('"""'):  # if finded closing """ break
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
                                # open(RESULT_PATH, 'w', encoding='utf-8').write(result)
                                # await m.edit_text(f"file eval list: view {RESULT_PATH} or print with `{PC}pr")
                                await m.edit_text(f"file eval list: except MessageTooLong")
                                await send_long_msg(result)

                        elif opt[0] in ['s', 'S']:
                            if arg == '':
                                # await m.edit(f"per `{the_cmd['prefix']}{the_cmd['cmd']} {PC}{opt[0]} ` "
                                await m.edit(f"per `{m.text} ` "
                                             f"bisogna mettere il fileName")
                                return
                            from os.path import exists
                            fpath = f"{PY_EXEC_FOLD}/{arg}.txt"
                            if not exists(fpath):
                                await m.edit(f"`{m.text}`\nil file {arg} non esiste")
                                return

                            _del(m)
                            _title = f"{arg}: \n\n"
                            await send_long_msg(_title + open(fpath, 'r', encoding='utf-8').read(),
                                                chunk_start="```\n", chunk_end="\n```",
                                                offset_first_chunk_start=len(_title), client=c)

                        elif opt[0] in ['d', 'D']:
                            if arg == '':
                                await m.edit(f"per `{m.text} ` bisogna mettere il fileName")
                                return
                            from os.path import exists
                            fpath = f"{PY_EXEC_FOLD}/{arg}.txt"
                            if not exists(fpath):
                                await m.edit(f"il file {arg} non esiste")
                                return
                            from os import remove
                            remove(fpath)
                            await m.edit(f"`{m.text}`\n!! file deleted !!")

                        else:
                            await m.edit(f"`{m.text}`\n!! command not found !! see `{PC}feval {PC}h`")
                            return

                    elif arg != '':
                        fcrea: list[str] = arg.split(maxsplit=1)
                        if len(fcrea) == 1:
                            await m.edit(f"`{m.text}`\n!! see `{PC}feval {PC}h`")
                            return
                        fpath = f"{PY_EXEC_FOLD}/{fcrea[0]}.txt"
                        open(fpath, 'w', encoding='utf-8').write(fcrea[1].strip())
                        m.text = f"{PC}eval " + open(fpath, 'r', encoding='utf-8').read()
                        await python_exec(c, m)

                    else:
                        await m.edit(f"{PC}{cmd_txt_original}\n!! see `{PC}feval {PC}h`")
                        return

                task = ctn(_fexec(), f'exec file{m.date.second}')
                await eval_canc(c, m, task)

            case 'math' | 'math reply':
                is_r = m.text[1:].startswith(("rmath", "rcalc"))
                if (len(m.text.split(maxsplit=1)) == 1 and not is_r) or (is_r and not m.reply_to_message):
                    await m.edit_text(f"`{m.text}`\n<b>Expression required to calculate</b>")
                    return

                code = m.reply_to_message.text if is_r else m.text.split(maxsplit=1)[1]

                # fix character \u00A0
                code = code.replace("\u00A0", "").strip()

                try:
                    await m.reply(f"<code>{eval(code)}</code>",
                                  disable_web_page_preview=True, parse_mode=ParseMode.HTML)
                except Exception as e:
                    await m.reply(f"<i>{code}</i><b> = </b><code>{e}</code>",
                                  disable_web_page_preview=True, parse_mode=ParseMode.HTML)

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

            case 'target':
                _del(m)
                from .myParameters import set_target
                set_target(m.chat.id)
                await c.send_message(TERMINAL_ID, f"'target' var set to {m.chat.id}")

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
    r = m.reply_to_message if m.reply_to_message else None

    if r is None:
        await c.send_message(TERMINAL_ID, f"`{m.text}`\nnessun reply per i comandi 'send to'")
        return

    # ">." iniziali fanno in modo che venga scritto > senza comando
    if cmd_txt != "" and cmd_txt[0] == ".":
        await m.edit_text(PS + cmd_txt_original[1:])
        return

    the_cmd = get_the_cmd(m.text)

    async def _matcher(cmd_match, is_del: bool = False):
        nonlocal m, c, cmd_txt_original, cmd_txt, the_cmd

        def _del(_m: Msg):
            if not is_del:
                _ = ctn(_m.delete())

        match cmd_match:
            case 'pic':
                _del(m)
                from .myParameters import SAVED_MESSAGE_FORUM_ID, PIC_TOPIC_ID
                """
                return {
                    'c_id': SAVED_MESSAGE_FORUM_ID,
                    'thread_id': PIC_TOPIC_ID
                }
                """
                # return ['forum', SAVED_MESSAGE_FORUM_ID, PIC_TOPIC_ID]
                return [SAVED_MESSAGE_FORUM_ID, PIC_TOPIC_ID]

            case 'save':
                _del(m)
                return ['me', None]

            case 'second profile':
                _del(m)
                from .myParameters import MY_ID2
                return [MY_ID2, None]

            case 'terminal':
                _del(m)
                return [TERMINAL_ID, None]

            case _:
                _del(m)
                await c.send_message(
                    TERMINAL_ID,
                    f"! cmd don't found !\n{m.text}\nchat:{c_id if c_id != TERMINAL_ID else 'this chat'}"
                )
                return None

    target = await _matcher(finder_cmd(cmd_txt))
    if target is None:
        return

    grouped_id = r.media_group_id
    # r_id = m.reply_to_message_id
    r_id = r.id

    if grouped_id is not None and any((option in ['group', 'g', 'album', 'a']) for option in the_cmd['options']):
        # _ids = list(range(r_id - 9, r_id + 10))
        _ids = [i for i in range(r_id - 9, r_id + 9 + 1) if i > 0]

        from pyrogram.errors.exceptions.bad_request_400 import MessageIdsEmpty
        try:
            _msgs = await c.get_messages(c_id, _ids)

        except MessageIdsEmpty:  # last msg id < r_id + 10
            _msgs = await c.get_messages(c_id, [i for i in range(r_id - 9, r_id + 1) if i > 0])
            if not isinstance(_msgs, list):
                _msgs = [_msgs]

            for i in range(r_id + 1, r_id + 8 + 1):
                try:
                    _msgs.append(await c.get_messages(c_id, i))
                except MessageIdsEmpty:
                    break

        # ids, msgs = [], []
        ids = []
        for msg in _msgs:
            _grouped_id = getattr(msg, 'media_group_id', None)
            if _grouped_id is not None and _grouped_id == grouped_id:
                ids.append(msg.id)
                # msgs.append(msg)
    else:
        ids = [r_id]
        # msgs = [r]

    if any((option in ['copy', 'c']) for option in the_cmd['options']):
        # for msg in msgs:
        # await msg.copy(chat_id=target[0], message_thread_id=target[1])
        copy = True

    else:  # forward
        # await c.forward_messages(chat_id=target[0], message_thread_id=target[1], from_chat_id=c_id, message_ids=ids)
        copy = False

    await c.forward_messages(chat_id=target[0], message_thread_id=target[1],
                             from_chat_id=c_id, message_ids=ids, hide_sender_name=copy)


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
