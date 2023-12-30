from testEnv.plugins.greetings import check_chat_for_reply_waiting, non_risposto
from testEnv.plugins.pyrogram_forward_to_topic import forward_to_topic

from pyrogram import Client, filters
from pyrogram.enums import ChatType
import pyrogram.raw.functions.account  # offline

from datetime import datetime  # ping
import asyncio  # offline
import time  # offline

# terminal_id = -4030133781
terminal_id = -1001995530063


async def getchat(client, chat):
    text = f"id:{chat.id}\ntype:{chat.type}\ntitle:{chat.title}\nusername:{chat.username}\nname:{chat.first_name}"
    text += f", {chat.last_name}\n" if chat.last_name is not None else '\n'
    if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
        text += (f"inviteLink:{chat.invite_link}\nmembri:{chat.members_count}\n"
                 f"description:{chat.description}\n")
    elif chat.type == ChatType.PRIVATE:
        text += f"bio:{chat.bio}\n"
        text += f"phone:{getattr(chat, 'phone_number', 'non presente')}\n"
        text += f"restrictions:{getattr(chat, 'restrictions', 'non presente')}\n\n"
    await client.send_message(chat_id=terminal_id, text=text)
    if chat.type != ChatType.PRIVATE:
        return
    text = f"common chats:\n\n"
    chatlist = await client.get_common_chats(chat.id)
    for ch in chatlist:
        text += f"id:{ch.id}\ntype:{ch.type}\ntitle:{ch.title}\nusername:{ch.username}\nname:{ch.first_name}"
        text += f", {ch.last_name}\n" if ch.last_name is not None else '\n'
        text += f"inviteLink:{ch.invite_link}\nmembri:{ch.members_count}\ndescription:{ch.description}\n\n"
    await client.send_message(chat_id=terminal_id, text=text)


async def pong(client, msg, send_terminal=False):
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


async def offline(client):
    await client.send_message(chat_id=terminal_id, text="Verrai settato offline tra 5,10,15 e 20s")
    await client.invoke(pyrogram.raw.functions.account.UpdateStatus(offline=True))  # 0s
    time.sleep(5)
    await client.invoke(pyrogram.raw.functions.account.UpdateStatus(offline=True))  # 5s
    time.sleep(5)
    await client.invoke(pyrogram.raw.functions.account.UpdateStatus(offline=True))  # 10s
    time.sleep(5)
    await client.invoke(pyrogram.raw.functions.account.UpdateStatus(offline=True))  # 15s
    time.sleep(5)
    await client.invoke(pyrogram.raw.functions.account.UpdateStatus(offline=True))  # 20s


@Client.on_message(filters.me & filters.text & filters.regex(r'^-'), group=1)
async def handle_commands(client, msg):
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
                "-auto : \"uso i messaggi automatici perché..\"\n-offline : setta offline il profilo\n"
                "-ping : ping in chat\n-pingt : ping in terminale\n-getall = -ga : su 3 file\n"
                "-get = -g : -getchat or -getreply\n-getchat : ottiene info base della chat\n"
                "-getreply = -getr : come getchat ma del reply\n-getid = -id : ottiene id della chat\n"
                "-getme : ottiene l'istanza User di me stesso\n-search : cerca per id o per username di un reply\n"
                "-null = -vuoto = -void = - = -spazio : manda il text di spazio vuoto\n"
                "\ni comandi '>' sono \"send to\"\n>p = >pic : inoltra il reply in pic(saved message forum)\n"
                ">t = >terminal : inoltra il reply in terminale\n"
                "\ni comandi -. e >. modificano annullando il comando e cancellando il punto")
        await client.send_message(chat_id=terminal_id, text=text)

    # Esegui le azioni desiderate in base al comando
    elif cmd_txt == "0":
        await client.edit_message_text(chat_id=msg.chat.id, message_id=msg.id,
                                       text="buondì\ncome va?")

    elif cmd_txt == "1":
        chat_id = msg.chat.id
        await client.edit_message_text(chat_id=chat_id, message_id=msg.id,
                                       text="Dammi un attimo e ti scrivo subito.")
        await asyncio.create_task(offline(client))
        if msg.chat.type != ChatType.PRIVATE:
            return
        if not check_chat_for_reply_waiting(chat_id):
            return
        with open('reply_waiting.txt', 'a') as f:
            f.write(f"{chat_id};1\n")
        await non_risposto(client, chat_id)

    elif cmd_txt == "auto":
        await client.edit_message_text(chat_id=msg.chat.id, message_id=msg.id,
                                       text="uso i messaggi automatici solo per far prima e poter gestire più persone,"
                                            "senza andare ad ignorare qualcuno involontariamente")

    elif cmd_txt == "offline":
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        await offline(client)

    elif cmd_txt == "ping":
        await pong(client, msg)

    elif cmd_txt == "pingt":
        await pong(client, msg, True)

    elif cmd_txt in ["getall", "ga"]:
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        chat = await client.get_chat(msg.chat.id)
        open("ga/ga_chat.txt", "w").write(str(vars(chat)))
        open("ga/ga_msg.txt", "w").write(str(vars(msg)))
        open("ga/ga_msg_chat.txt", "w").write(str(vars(msg.chat)))
        await client.send_message(chat_id=terminal_id, text="creati 3 file")

    elif cmd_txt in ["get", "g"]:
        if msg.reply_to_message:
            msg.text = "-getr"
        else:
            msg.text = "-getchat"
        await handle_commands(client, msg)

    elif cmd_txt == "getchat":
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        chat = await client.get_chat(msg.chat.id)
        await getchat(client, chat)

    elif cmd_txt in ["getr", "getreply"]:
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        # Verifica se il messaggio ha una risposta
        if not msg.reply_to_message:
            await client.send_message(chat_id=terminal_id, text="nessun reply per il comando -getreply")
            return
        # Ottieni il messaggio di risposta
        rmsg = msg.reply_to_message
        chat = await client.get_chat(rmsg.chat.id)
        await getchat(client, chat)

    elif cmd_txt in ["getid", "id"]:
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        chat = await client.get_chat(msg.chat.id)
        await client.send_message(chat_id=terminal_id, text=chat.id)

    elif cmd_txt == "getme":
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        text = str(vars(await client.get_me())).split(', \'')
        await client.send_message(chat_id=terminal_id, text='\n\''.join(text))

        '''
    elif cmd_txt == "getfullme":
        
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        userme = await client.get_me()
        input_user = await client.resolve_peer(userme.id)
        fullme = await client.invoke(pyrogram.raw.functions.users.GetFullUser(id=input_user))

        text = ""
        # Ottieni tutti gli attributi dell'oggetto full_user_me
        attributes = dir(fullme)
        # Stampa tutti gli attributi e i loro valori
        for attribute in attributes:
            try:
                value = getattr(fullme, attribute)
                text = f"{attribute}: {value}\n"
                # Divide il testo in parti più piccole
                chunk_size = 4096  # Lunghezza massima del messaggio consentita da Telegram
                chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
                # Invia ciascuna parte separatamente
                for chunk in chunks:
                    await client.send_message(chat_id=terminal_id, text=chunk)
                await client.send_message(chat_id=terminal_id, text=f"end attribute {attribute}\ntime sleep 3")
                time.sleep(3)
            except AttributeError:
                pass  # Ignora gli attributi che non possono essere ottenuti
        print("done")
        '''

    elif cmd_txt == "search":
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        # Verifica se il messaggio ha una risposta
        if not msg.reply_to_message:
            await client.send_message(chat_id=terminal_id, text="nessun reply per il comando -search")
            return
        # Ottieni il messaggio di risposta
        rmsg = msg.reply_to_message
        try:
            chat = await client.get_chat(rmsg.text)
            await getchat(client, chat)
        except Exception as e:
            await client.send_message(chat_id=terminal_id, text=f"{e}\n\nil comando cerca per id o per username")

    elif cmd_txt in ["null", "vuoto", "void",  " ", "", "spazio"]:
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        await client.send_message(chat_id=msg.chat.id, text="ㅤ")

    else:
        # message.reply_text("Nessun comando trovato!")
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        await client.send_message(chat_id=terminal_id,
                                  text=f"! Nessun comando trovato !\n-{cmd_txt}\n"
                                       f"chat:{msg.chat.id if msg.chat.id != terminal_id else "this chat"}")


@Client.on_message(filters.me & filters.text & filters.regex(r'^\>'), group=2)
async def handle_send_to(client, msg):
    cmd_txt = msg.text[1:].lower()

    # ">." iniziali fanno in modo che venga scritto - senza comando
    if cmd_txt != "" and cmd_txt[0] == ".":
        text = ">" + msg.text[2:]
        await client.edit_message_text(chat_id=msg.chat.id, message_id=msg.id,
                                       text=text)

    elif cmd_txt in ["pic", "p"]:
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        await forward_to_topic(source_channel_id=msg.chat.id, destination_channel_id=-1001971247646,
                               forwarded_message_id=msg.reply_to_message_id, topic_init_message_id=18, client=client)

    elif cmd_txt in ["t", "terminal"]:
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        await client.forward_messages(chat_id=terminal_id, from_chat_id=msg.chat.id,
                                      message_ids=msg.reply_to_message_id)

        '''
    elif cmd_txt == "test":
        from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        try:
            await client.send_message(
                chat_id=802468337,
                text="testoconinline",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="test", url="t.me/ill_magnus")]])
            )
        except Exception as e:
            await client.send_message(
                chat_id=802468337,
                text=f"errore:{e}"
            )
        '''

    else:
        # message.reply_text("Nessun comando trovato!")
        await client.delete_messages(chat_id=msg.chat.id, message_ids=msg.id)
        await client.send_message(chat_id=terminal_id,
                                  text=f"! Nessun comando trovato !\n>{cmd_txt}\n"
                                       f"chat:{msg.chat.id if msg.chat.id != terminal_id else "this chat"}")
