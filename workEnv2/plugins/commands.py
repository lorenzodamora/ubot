from pyrogram import Client, filters as f
from pyrogram.types import Message as Msg, Chat
from .myParameter import terminal_id


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
    await client.send_message(chat_id=terminal_id, text=text)
    if chat.type != Ct.PRIVATE:
        return
    text = f"common chats:\n\n"
    chatlist = await client.get_common_chats(chat.id)
    for ch in chatlist:
        text += f"id:{ch.id}\ntype:{ch.type}\ntitle:{ch.title}\nusername:{ch.username}\nname:{ch.first_name}"
        text += f", {ch.last_name}\n" if ch.last_name is not None else '\n'
        text += f"inviteLink:{ch.invite_link}\nmembri:{ch.members_count}\ndescription:{ch.description}\n\n"
    await client.send_message(chat_id=terminal_id, text=text)


async def pong(client: Client, msg: Msg, send_terminal=False):
    from datetime import datetime  # ping
    await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
    text = "📶 Pong!"
    if send_terminal:
        chatid = terminal_id
    else:
        chatid = msg.chat.id
    msgid = (await client.send_message(chat_id=chatid, text=text)).id
    for i in range(1, 5):
        ps = datetime.now()
        await client.edit_message_text(chat_id=chatid, message_id=msgid, text="📶 Pong!! 📶",
                                       disable_web_page_preview=True)
        pe = datetime.now()
        ping = (pe - ps).microseconds / 1000
        text += f"\n{ping}ms"
        await client.edit_message_text(chat_id=chatid, message_id=msgid, text=text,
                                       disable_web_page_preview=True)


async def offline(client: Client, seconds: int, from_: str):
    import pyrogram.raw.functions.account as acc  # offline
    import asyncio  # offline
    await client.send_message(chat_id=terminal_id,
                              text=f"Verrai settato offline tra {seconds},{seconds * 2},"
                                   f"{seconds * 3} e {seconds * 4}s\n"
                                   f"from: {from_}")
    await client.invoke(acc.UpdateStatus(offline=True))  # 0s
    await asyncio.sleep(seconds)
    await client.invoke(acc.UpdateStatus(offline=True))  # 5s
    await asyncio.sleep(seconds)
    await client.invoke(acc.UpdateStatus(offline=True))  # 10s
    await asyncio.sleep(seconds)
    await client.invoke(acc.UpdateStatus(offline=True))  # 15s
    await asyncio.sleep(seconds)
    await client.invoke(acc.UpdateStatus(offline=True))  # 20s


@Client.on_message(f.me & f.text & f.regex(r'^-'), group=1)
async def handle_commands(client: Client, msg: Msg):
    # Estrai il testo del messaggio dopo "-"
    cmd_txt = msg.text[1:].lower()

    # "-." iniziali fanno in modo che venga scritto - senza comando
    if cmd_txt != "" and cmd_txt[0] == ".":
        text = "-" + msg.text[2:]
        await client.edit_message_text(chat_id=msg.chat.id, message_id=msg.id,
                                       text=text)

    elif cmd_txt in ["h", "help", "?", "commands", "c"]:
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        text = ("Lista di comandi\n\n-h = -help = -? = -commands = -c : questo messaggio\n"
                "-0 : greetings\n-1 : Dammi un attimo + inserito in lista \"reply_waiting\"\n"
                "reply waiting::\n    -r = -remove : rimuovi dalla rw list la chat in cui hai scritto il comando\n"
                "    -grw = -gw : get reply waiting list (terminal)\n"
                "-output : stampa i file di output dei 3 bot\n"
                "-auto : \"uso i messaggi automatici perché..\"\n-offline : setta offline il profilo\n"
                "-ping : ping in chat\n-pingt : ping in terminale\n-getall = -ga : su 3 file\n"
                "-get = -g : -getchat or -getreply\n-getchat : ottiene info base della chat\n"
                "-getreply = -getr : come getchat ma del reply\n-getid = -id : ottiene id della chat\n"
                "-getme : ottiene l'istanza User di me stesso\n-search : cerca per id o per username di un reply\n"
                "-null = -vuoto = -void = - = -spazio : manda il text di spazio vuoto, se metti in reply un messaggio"
                " lo mantiene\n"
                "\ni comandi '>' sono \"send to\"\n>p = >pic : inoltra il reply in pic(saved message forum)\n"
                ">t = >terminal : inoltra il reply in terminale\n"
                "\ni comandi -. e >. modificano annullando il comando e cancellando il punto")
        await client.send_message(chat_id=terminal_id, text=text)
        await client.send_message(
            chat_id=terminal_id,
            text="cos'è la lista \"reply waiting\" ?\n"
                 "ogni tot tempo va a scrivere alle persone in lista che ancora non sei riuscito a dedicargli tempo"
                 "\n\ncome funziona la lista \"reply waiting\" ?\n - funziona solo nelle private\n"
                 " - i tempi di attesa sono 1,8,24,36,48 ore. una volta raggiunto 48 ore, si stoppa"
                 "\n - lo invia solo se l'ultimo messaggio non è tuo\n"
                 " - come togliere una persona dalla lista? appena invii un messaggio a quella persona\n"
                 "     oppure comando -r / -remove\n"
                 " - per ottenere la lista: comando -gw / -grw"
        )

    elif cmd_txt == "output":
        from .myParameter import ubot1output, ubot2output, infobotoutput
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)

        async def printoutput(path: str, title: str):
            text_ = open(path, "r").read()
            if text_ == "":
                text_ = f"{title}: output.txt\n\nfile vuoto"
            else:
                text_ = f"{title}: output.txt\n\n" + text_
            await client.send_message(chat_id=terminal_id, text=text_)
        # End def
        await printoutput(ubot1output, "Ubot1")
        await printoutput(ubot2output, "Ubot2")
        await printoutput(infobotoutput, "Infobot")

    elif cmd_txt == "0":
        await client.edit_message_text(chat_id=msg.chat.id, message_id=msg.id,
                                       text="buondì\ncome va?")

    elif cmd_txt == "1":
        from pyrogram.enums import ChatType as Ct
        import asyncio  # offline
        chat_id = msg.chat.id
        await client.edit_message_text(chat_id=chat_id, message_id=msg.id,
                                       text="Dammi un attimo e ti scrivo subito.")
        _ = asyncio.create_task(offline(client, 5, "comando -1"))
        if msg.chat.type != Ct.PRIVATE:
            return
        from .greetings import check_chat_for_reply_waiting as ccfrw, non_risposto as nr, lock_rw
        if not await ccfrw(chat_id):
            return
        async with lock_rw:
            open('reply_waiting.txt', 'a').write(f"{chat_id};1\n")
        await nr(client, chat_id)

    elif cmd_txt in ["r", "remove"]:
        c_id = msg.chat.id
        await client.delete_messages(chat_id=c_id, message_ids=msg.id)
        from .greetings import remove
        await remove(str(c_id))

    elif cmd_txt in ["grw", "gw"]:
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        from .greetings import lock_rw
        async with lock_rw:
            text = open("reply_waiting.txt", "r").read()
        if text == "":
            text = "reply_waiting.txt\n\nfile vuoto"
        else:
            text = "reply_waiting.txt\n\n" + text
        await client.send_message(chat_id=terminal_id, text=text)

    elif cmd_txt == "auto":
        await client.edit_message_text(chat_id=msg.chat.id, message_id=msg.id,
                                       text="uso i messaggi automatici solo per far prima e poter gestire più persone,"
                                            "senza andare ad ignorare qualcuno involontariamente")

    elif cmd_txt == "offline":
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        await offline(client, 5, "-offline")

    elif cmd_txt == "ping":
        await pong(client, msg)

    elif cmd_txt == "pingt":
        await pong(client, msg, True)

    elif cmd_txt in ["getall", "ga"]:
        m_ch = msg.chat
        await client.delete_messages(chat_id=m_ch.id, message_ids=msg.id)
        # Crea la directory se non esiste già
        import os
        if not os.path.exists("./ga"):
            os.makedirs("./ga")

        def custom_serializer(obj):
            if isinstance(obj, Client):
                return str(obj)

        from json import dumps
        open("ga/ga_chat.txt", "w", encoding='utf-8').write(str(dumps(vars(await client.get_chat(m_ch.id)), indent=2,
                                                                      default=custom_serializer)))
        open("ga/ga_msg.txt", "w", encoding='utf-8').write(str(dumps(vars(msg), indent=2,
                                                                     default=custom_serializer)))
        open("ga/ga_msg_chat.txt", "w", encoding='utf-8').write(str(dumps(vars(m_ch), indent=2,
                                                                          default=custom_serializer)))
        await client.send_message(chat_id=terminal_id, text="creati 3 file dal comando -getAll")

    elif cmd_txt in ["get", "g"]:
        if msg.reply_to_message:
            msg.text = "-getr"
        else:
            msg.text = "-getchat"
        await handle_commands(client, msg)

    elif cmd_txt == "getchat":
        c_id: int = msg.chat.id
        await client.delete_messages(chat_id=c_id, message_ids=msg.id)
        await getchat(client, await client.get_chat(c_id))

    elif cmd_txt in ["getr", "getreply"]:
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        # Ottieni il messaggio di risposta
        rmsg = msg.reply_to_message
        # Verifica se il messaggio ha una risposta
        if not rmsg:
            await client.send_message(chat_id=terminal_id, text="nessun reply per il comando -getreply")
            return
        await getchat(client, await client.get_chat(rmsg.chat.id))

    elif cmd_txt in ["getid", "id"]:
        c_id = msg.chat.id
        await client.delete_messages(chat_id=c_id, message_ids=msg.id)
        chat = await client.get_chat(c_id)
        await client.send_message(chat_id=terminal_id, text=str(chat.id))

    elif cmd_txt == "getme":
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        text = str(vars(await client.get_me())).split(', \'')
        await client.send_message(chat_id=terminal_id, text='\n\''.join(text))

    elif cmd_txt == "search":
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        # Verifica se il messaggio ha una risposta
        if not msg.reply_to_message:
            await client.send_message(chat_id=terminal_id, text="nessun reply per il comando -search")
            return
        rmsg = msg.reply_to_message
        try:
            chat = await client.get_chat(rmsg.text)
            await getchat(client, chat)
        except Exception as e:
            await client.send_message(chat_id=terminal_id, text=f"{e}\n\nil comando cerca per id o per username")

    elif cmd_txt in ["null", "vuoto", "void", " ", "", "spazio", None]:
        c_id = msg.chat.id
        await client.delete_messages(chat_id=c_id, message_ids=msg.id)
        rmsg = msg.reply_to_message
        if rmsg:
            await client.send_message(chat_id=c_id, text="ㅤ", reply_to_message_id=rmsg.id)
        else:
            await client.send_message(chat_id=c_id, text="ㅤ")

    else:
        c_id = msg.chat.id
        await client.delete_messages(chat_id=c_id, message_ids=msg.id)
        await client.send_message(chat_id=terminal_id,
                                  text=f"! Nessun comando trovato !\n-{cmd_txt}\n"
                                       f"chat:{c_id if c_id != terminal_id else 'this chat'}")


@Client.on_message(f.me & f.text & f.regex(r'^\>'), group=2)
async def handle_send_to(client: Client, msg: Msg):
    cmd_txt = msg.text[1:].lower()

    # ">." iniziali fanno in modo che venga scritto - senza comando
    if cmd_txt != "" and cmd_txt[0] == ".":
        text = ">" + msg.text[2:]
        await client.edit_message_text(chat_id=msg.chat.id, message_id=msg.id,
                                       text=text)

    elif cmd_txt in ["pic", "p"]:
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        if not msg.reply_to_message:
            await client.send_message(chat_id=terminal_id, text="nessun reply per il comando >pic")
            return
        from .pyrogram_forward_to_topic import forward_to_topic as for_top
        from .myParameter import saved_message_forum_id, pic_topic_id
        await for_top(source_channel_id=msg.chat.id, destination_channel_id=saved_message_forum_id,
                      forwarded_message_id=msg.reply_to_message_id, topic_init_message_id=pic_topic_id, client=client)

    elif cmd_txt in ["t", "terminal"]:
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        if not msg.reply_to_message:
            await client.send_message(chat_id=terminal_id, text="nessun reply per il comando >terminal")
            return
        await client.forward_messages(chat_id=terminal_id, from_chat_id=msg.chat.id,
                                      message_ids=msg.reply_to_message_id)

    else:
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        await client.send_message(chat_id=terminal_id,
                                  text=f"! Nessun comando trovato !\n>{cmd_txt}\n"
                                       f"chat:{msg.chat.id if msg.chat.id != terminal_id else 'this chat'}")
