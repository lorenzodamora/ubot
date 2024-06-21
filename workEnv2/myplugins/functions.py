"""
functions file
l'event handler stava diventando troppo lungo
"""
from pyrogram import Client
from pyrogram.types import Message as Msg, Chat
from pyrogram.enums import ParseMode
from pyrogram.errors.exceptions.flood_420 import FloodWait

from .myParameters import (
    TERMINAL_ID,
    PREFIX_COMMAND as PC,
    COMMANDS,
)
from asyncio import sleep

__all__ = (
    'check_cmd',
    'finder_cmd',
    'getchat', 'pong_', 'offline',
    'moon', 'pipo',
    'help_other', 'help_',
    'send_long_msg', 'slm',
    'eval_canc',
    'get_version',
    'benvenuto',
    'wait_read',
    'get_the_cmd'
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
    value = COMMANDS[name]['type']
    txt = txt.lower()
    for alias in COMMANDS[name]['alias']:
        alias = alias.lower()
        match value:
            case 1:
                if txt == alias:
                    return True
            case 2:
                if (txt[:len(alias) + 1].strip() + " ").startswith((alias + " ")):
                    return True
            case 3:
                if alias in txt:
                    return True
            case _:
                raise ValueError(f"Il dizionario contiene un valore non valido per il tipo di check: {value}\n"
                                 f"per i valori validi leggi la documentazione")
    return False


def finder_cmd(txt: str) -> str:
    """
    trova il comando associato al testo inserito.

    Fa una corrispondenza key insensitive.
    cerca nei COMMANDS, fa anche altri check personalizzati

    :param txt: Testo di input.
    :type txt: str
    :return: ritorna il nome del comando
    :rtype: str
    """

    for name in COMMANDS:
        if check_cmd(txt, name):
            return name

    return "not find"


async def getchat(client: Client, chat: Chat):
    from pyrogram.enums import ChatType
    text = (f"id:`{chat.id}`\ntype:{chat.type}\ntitle:{chat.title}\nusername:{chat.username}\nname:{chat.first_name}, "
            + (f"{chat.last_name}\n" if chat.last_name is not None else '\n'))
    if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        text += f"inviteLink:{chat.invite_link}\nmembri:{chat.members_count}\ndescription:\n{chat.description}\n\n"
    elif chat.type == ChatType.PRIVATE:
        text += (f"bio:{chat.bio}\nphone:{getattr(chat, 'phone_number', '\\')}\n"
                 f"restrictions:{getattr(chat, 'restrictions', '\\')}\n\n")
    await send_long_msg(text, client=client)

    if chat.type != ChatType.PRIVATE:
        return
    text = f"common chats:\n\n"
    chatlist = await client.get_common_chats(chat.id)
    for ch in chatlist:
        text += (f"id:`{ch.id}`\ntype:{ch.type}\ntitle:{ch.title}\nusername:{ch.username}\nname:{ch.first_name}"
                 + (f", {ch.last_name}\n" if ch.last_name is not None else '\n') +
                 f"inviteLink:{ch.invite_link}\nmembri:{ch.members_count}\ndescription:{ch.description}\n\n")
    await send_long_msg(text, client=client)


async def pong_(client: Client, msg: Msg, send_terminal=False):
    from time import perf_counter
    await client.delete_messages(msg.chat.id, msg.id)
    text = "📶 Pong!"
    chatid = TERMINAL_ID if send_terminal else msg.chat.id
    msg = await client.send_message(chatid, text)
    for i in range(1, 5):
        start = perf_counter()
        await msg.edit("📶 Pong!! 📶")
        end = perf_counter()
        text += f"\n{int((end - start) * 1000)}ms"
        await msg.edit(text)


async def offline(client: Client, seconds: float = 5, iter_: int = 4, from_: str = "Undefined"):
    try:
        from pyrogram.raw.functions.account import UpdateStatus  # offline
        if iter_ > -1:
            txt = []
            for i in range(iter_ - 1):
                _tmp = round(seconds * (i + 1), 3)
                _tmp = int(_tmp) if _tmp % 1 == 0 else _tmp
                txt.append(str(_tmp))
            _tmp = round(seconds * iter_, 3)
            _tmp = int(_tmp) if _tmp % 1 == 0 else _tmp

            txt = ', '.join(txt) + f" e {_tmp} sec"
            await send_long_msg(
                f"Verrai settato offline tra {txt}\nfrom: {from_}\n"
                f"sec:{int(seconds) if seconds % 1 == 0 else seconds} iter:{iter_}",
                client=client
            )

            await client.invoke(UpdateStatus(offline=True))  # 0s
            for i in range(iter_):
                await sleep(seconds)
                await client.invoke(UpdateStatus(offline=True))

        else:
            await client.send_message(
                TERMINAL_ID,
                f"Verrai settato offline ogni {seconds} sec\nfrom: {from_}"
            )
            while True:
                await sleep(seconds)
                await client.invoke(UpdateStatus(offline=True))
    except Exception as e:
        await client.send_message(TERMINAL_ID, f"sec: {seconds} n iteration: {iter_} from: {from_}\n"
                                               f"error:\n{e.__class__.__name__}: {e}")


async def moon(m: Msg, txt: str, other: bool):
    from .tasker import create_task_name

    async def _moon(_m: Msg):
        from pyrogram.errors.exceptions.bad_request_400 import MessageNotModified
        moon_list = ["🌕", "🌖", "🌗", "🌘", "🌑", "🌒", "🌓", "🌔"]
        if other:
            _m = await _m.reply_text("LUNA UAU")

        read_task = create_task_name(wait_read(message=_m), name="moon edit read waiting")

        try:
            sec = float(txt.split(" ")[1])
        except (IndexError, ValueError):
            sec = 0.1
        if sec < 0.1:
            sec = 0.1

        _ = create_task_name(_m.edit_text(''.join(moon_list[:5]) + "ㅤ"), name="moon edit -1")
        await read_task

        for i in range(29):
            moon_list = moon_list[-1:] + moon_list[:-1]
            text = ''.join(moon_list[:5]) + "ㅤ"

            async def editing_text():
                try:
                    await _m.edit_text(text)
                except (FloodWait, MessageNotModified):
                    pass

            _ = create_task_name(editing_text(), name=f"moon{m.date.second} edit {i}")
            await sleep(sec)

        moon_list = moon_list[-1:] + moon_list[:-1]
        text = ''.join(moon_list[:5]) + "ㅤ"
        while True:
            try:
                await _m.edit_text(text)
                return  # Successful edit
            except FloodWait as e:
                await sleep(e.value)
            except MessageNotModified:
                return

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
        cmd_or = COMMANDS
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
    from .myParameters import PREFIX_SEND_TO
    pre = PREFIX_SEND_TO if group_ == "send to" else PC
    ftext = f"**{group_}**:\n"
    for command_info in cmd_i:
        formatted_aliases = ' '.join([f'`{pre}{alias}`' for alias in command_info[1]])
        ftext += f"  {command_info[0]}\n"
        ftext += f"    {formatted_aliases}\n"
        ftext += f"    : {command_info[2].replace('\n', '\n      ')}\n"
    return ftext


def help_other():
    from .myParameters import MY_TAG
    text = (f"All commands usable from others:\n"
            f"The prefix is `{MY_TAG} {PC}`\n"
            "Requests: one every 20 sec, esecution excluded, all in queue (theorically)\n\n")
    all_other = {key: value for key, value in COMMANDS.items() if 'other' in value and value['other']}
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
        results = {key: COMMANDS[key] for key in COMMANDS
                   if txts[1] in key or any(txts[1] in alias for alias in COMMANDS[key]['alias'])}
        text = f"All cmd find by your query '{txts[1]}':\n\n"
        for group, cmd_info in h_groupping(results).items():
            text += h_format_group(group, cmd_info)

    return text


async def send_long_msg(
    text: str, chat_id: int | str = TERMINAL_ID, parse_mode: ParseMode | None = None,
    chunk_size: int = 4096, chunk_start: str = "", chunk_end: str = "", offset_first_chunk_start: int | None = None,
    client: Client | None = None,
):
    async def _send_chunk(_text):
        while True:
            try:
                await client.send_message(chat_id, str(_text), parse_mode=parse_mode, disable_web_page_preview=True)
                return  # Successful send
            except FloodWait as e:
                await sleep(e.value)

    if client is None:
        from .myParameters import app
        client = app

    c_s = chunk_size - len(chunk_start) - len(chunk_end)

    chunks = [text[i: i + c_s] for i in range(0, len(text), c_s)]

    # Handle first chunk with offset if applicable
    if offset_first_chunk_start is not None:
        first_chunk = (chunks[0][:offset_first_chunk_start]
                       + chunk_start
                       + chunks[0][offset_first_chunk_start:]
                       + chunk_end)
        await _send_chunk(first_chunk)
        chunks = chunks[1:]

    # Send remaining chunks
    for chunk in chunks:
        chunk_text = chunk_start + chunk + chunk_end
        await _send_chunk(chunk_text)


slm = send_long_msg


async def eval_canc(c, m, t):
    """
    :param c: client
    :param m: message
    :param t: task
    """
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
            await send_long_msg(f"{cancelled}\n\nerror:\n{e.__class__.__name__}: {e}", client=c)


def get_version():
    from . import __version__, __date__
    return f"my version: {__version__}\nversion date (italian format): {__date__}"


async def benvenuto(client: Client, msg: Msg):
    from pyrogram.raw.types import MessageService, MessageActionContactSignUp

    # Ottieni il numero di messaggi nella chat
    chat_id = msg.chat.id
    try:
        num_msg: int = await client.get_chat_history_count(chat_id)
    except FloodWait:
        return

    if num_msg == 1:
        if isinstance(msg.raw, MessageService):
            if isinstance(msg.raw.action, MessageActionContactSignUp):
                await client.send_message(
                    chat_id,
                    "Benvenutə su telegram! Se hai bisogno di una guida oppure semplicemente "
                    "abituarti a telegram conversiamo volentieri!"
                )
                await offline(client, 0, 1, f"benvenuto chat id: `{chat_id}`")

    if num_msg > 2:
        return
        # pass
    async for hmsg in client.get_chat_history(chat_id):
        if hmsg.from_user.is_self:
            return
    # client.send_message(chat_id=message.chat.id, text="num_msg : " + str(num_messaggi))
    from .myParameters import WELCOME_MSG
    await client.send_message(chat_id, WELCOME_MSG)
    await offline(client, 0, 1, f"welcome chat id: `{chat_id}`")


async def wait_read(
    chatid: int | str | None = None, msgid: int | str | None = None, top_msgid: int | str | None = None,
    message: Msg | None = None, target_userid: int | str | None = None, client: Client | None = None
):
    if (message is not None) and (chatid is None and msgid is None and top_msgid is None):
        chatid = message.chat.id
        msgid = message.id
        top_msgid = message.message_thread_id
        """
    elif (chatid is not None and msgid is not None) and (message is None):
        pass
    else:
        raise ValueError("devi specificare message oppure chatid, msgid e top_msgid, top_msgid può essere None.")
        """
    elif not ((chatid is not None and msgid is not None) and (message is None)):
        raise ValueError("devi specificare message oppure chatid, msgid e top_msgid, top_msgid può essere None.")

    chatid = str(chatid)
    msgid = int(msgid)

    if target_userid:
        target_userid = str(target_userid)

        # less or equal to  "chat_read_mark_size_threshold": 100,
        # "chat_read_mark_expire_period": 604800  seconds after the message was sent
        from pyrogram.raw.functions.messages import GetMessageReadParticipants
        from pyrogram.raw.types import ReadParticipantDate
        from pyrogram.errors.exceptions.bad_request_400 import BadRequest

        if client is None:
            from .myParameters import app
            client = app

        try:
            peer = await client.resolve_peer(chatid)
            while True:
                try:
                    r: list[ReadParticipantDate] = await client.invoke(
                        GetMessageReadParticipants(peer=peer, msg_id=msgid)
                    )
                    for i in r:
                        if str(i.user_id) == target_userid:
                            return
                    await sleep(1)
                except FloodWait as e:
                    await slm(f"wait_read exception:{e.__class__.__name__}\n{e}\n\nwaiting for FloodWait time")
                    await sleep(e.value)
                except Exception as e:
                    await slm(f"wait_read exception:{e.__class__.__name__}\n{e}\n\nunhandled error. stopped.")
                    return

        except BadRequest as e:
            await slm(f"wait_read exception:{e.__class__.__name__}\n{e}"
                      f"\n\nproceeding to general wait_read chatid: {chatid}  msgid: {msgid}")
        except Exception as e:
            await slm(f"wait_read exception:{e.__class__.__name__}\n{e}\n\nunhandled error. stopped.")
            return
    else:
        pass

    from pyrogram.raw.types import UpdateReadChannelOutbox, UpdateReadHistoryOutbox, UpdateReadChannelDiscussionOutbox
    from .myParameters import myDispatcher
    from asyncio import Event
    read_event = Event()

    async def _wait_read(update):
        if read_event.is_set():
            return
        elif isinstance(update, UpdateReadHistoryOutbox):
            if not (str(update.peer.user_id) == chatid and update.max_id >= msgid):
                return
        elif isinstance(update, UpdateReadChannelOutbox):
            if not (f"-100{update.channel_id}" == chatid and update.max_id >= msgid):
                return
        elif isinstance(update, UpdateReadChannelDiscussionOutbox):
            if not (
                f"-100{update.channel_id}" == chatid and update.top_msg_id == top_msgid and update.read_max_id >= msgid
            ):
                return
        else:
            return
        myDispatcher.remove(_wait_read)
        read_event.set()  # Set the event upon confirmation

    myDispatcher.add(_wait_read, 0)
    await read_event.wait()


def get_the_cmd(text: str):
    from .myParameters import PREFIX_SEND_TO
    prefix = text[0]
    cmd_txt = text[1:]

    try:
        cmd_split: list[str] = list(filter(lambda x: len(x) > 0, cmd_txt.split()))
        options = []
        for y in cmd_split[1:]:
            if y.startswith((PC, PREFIX_SEND_TO)):
                options.append(y[1:].lower())
            else:
                break
        _l = len(options) + 1
        arg = cmd_txt.split(maxsplit=_l)
        arg = arg[-1] if len(arg) > _l else ''
    except ValueError:
        cmd_split = cmd_txt.split(maxsplit=1)
        if len(cmd_split) < 2:
            options = []
            arg = ''
        else:
            options = []
            arg = cmd_split[1]

    the_cmd = {
        'prefix': prefix,
        'cmd': cmd_split[0] if len(cmd_split) > 0 else '',
        'options': options,
        'arg': arg
    }

    return the_cmd
