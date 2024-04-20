"""
functions file
l'event handler stava diventando troppo lungo
"""
from pyrogram import Client
from pyrogram.types import Message as Msg, Chat
from pyrogram.enums import ChatType, ParseMode
from .myParameters import (
    TERMINAL_ID,
    PREFIX_COMMAND as PC, PREFIX_SEND_TO as PS,
    MY_TAG,
    COMMANDS,
)
from asyncio import sleep
from .tasker import create_task_name
from typing import Union, Optional


__all__ = (
    'check_cmd',
    'finder_cmd',
    'getchat', 'pong_', 'offline',
    'moon', 'pipo',
    'help_other', 'help_',
    'send_long_msg', 'slm',
    'eval_canc',
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
    await slm(client, text)


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
            await slm(
                client,
                f"Verrai settato offline tra {txt}\nfrom: {from_}\n"
                f"sec:{int(seconds) if seconds % 1 == 0 else seconds} iter:{iter_}"
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
                _ = create_task_name(_m.edit_text(text), name=f"moon edit {i}")
            except FloodWait:
                pass
            await sleep(sec)

        moon_list = moon_list[-1:] + moon_list[:-1]
        text = ''.join(moon_list[:5]) + "ㅤ"
        await _m.edit_text(text)

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
    c: Client, text: str, chat_id: Union[int, str] = TERMINAL_ID, parse_mode: Optional["ParseMode"] = None,
    chunk_size: int = 4096, chunk_start: str = "", chunk_end: str = "", offset_first_chunk_start: Optional[int] = None,
):
    from pyrogram.errors.exceptions.flood_420 import FloodWait

    async def _send_chunk(_text):
        while True:
            try:
                await c.send_message(chat_id, str(_text), parse_mode=parse_mode)
                return  # Successful send
            except FloodWait as e:
                await sleep(e.value)

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
            await slm(c, f"{cancelled}\n\nerror:\n{e.__class__.__name__}: {e}")
