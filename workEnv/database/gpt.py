from openai import OpenAI, RateLimitError
from pyrogram.enums import ParseMode
from pyrogram.types import Message as Msg
from ..plugins.utils.db import db


# @Client.on_message(command(["gpt", "rgpt"]) & filters.me & ~filters.forwarded & ~filters.scheduled)
async def chatpgt(m: Msg):
    query = m.text[len(m.text.split(" ")[0])+1:]  # [query]
    if not query:
        return await m.reply(
            "<emoji id=5260342697075416641>❌</emoji><b> You didn't ask a question GPT</b>",
            quote=True,
        )

    # api_key = db.get("ChatGPT", "api_key")
    from os import getenv
    api_key = getenv('OPENAI_API_KEY')

    if not api_key:
        return await m.reply(
            "<emoji id=5260342697075416641>❌</emoji><b> You didn't provide an api key for GPT</b>",
            quote=True,
        )

    client = OpenAI()

    # ottieni tutti i dati della chat
    data: dict = db.get(
        "ChatGPT",
        f"gpt_id{m.chat.id}",
        {
            "enabled": True,
            "gpt_messages": [],
        },
    )
    if not data.get("enabled"):
        return await m.reply(
            "<emoji id=5260342697075416641>❌</emoji><b> GPT is not available right now</b>",
            quote=True,
        )

    data["enabled"] = False
    db.set("ChatGPT", f"gpt_id{m.chat.id}", data)

    msg = await m.reply(
        "<emoji id=5443038326535759644>💬</emoji><b> GPT is generating response, please wait</b>",
        quote=True,
    )
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=data["gpt_messages"] + [{"role": "user", "content": query}],
        )
    except RateLimitError as r:
        await m.reply(str(r))
        data["enabled"] = True
        db.set("ChatGPT", f"gpt_id{m.chat.id}", data)
        return await msg.edit_text(
            "<emoji id=5260342697075416641>❌</emoji><b> Model is currently overloaded with other requests.</b>"
        )
    except Exception as e:
        data["enabled"] = True
        db.set("ChatGPT", f"gpt_id{m.chat.id}", data)
        return await msg.edit_text(
            f"<emoji id=5260342697075416641>❌</emoji><b> Something went wrong: {e}</b>"
        )

    response = completion.choices[0].message.content

    data["gpt_messages"].append({"role": "user", "content": query})
    data["gpt_messages"].append({"role": completion.choices[0].message.role, "content": response})
    data["enabled"] = True
    db.set("ChatGPT", f"gpt_id{m.chat.id}", data)

    await msg.edit_text(response, parse_mode=ParseMode.MARKDOWN)


# @Client.on_message(command(["gptst"]) & filters.me & ~filters.forwarded & ~filters.scheduled)
# @with_args("<emoji id=5260342697075416641>❌</emoji><b> You didn't provide an api key</b>")
async def chatpgt_set_key(m: Msg):
    query = m.text[len(m.text.split(" ")[0])+1:]  # key
    # db.set("ChatGPT", "api_key", query)
    from os import environ
    environ['OPENAI_API_KEY'] = query
    await m.edit_text(
        "<emoji id=5260726538302660868>✅</emoji><b> You set api key for GPT</b>"
    )


# @Client.on_message(command(["gptcl"]) & filters.me & ~filters.forwarded & ~filters.scheduled)
async def chatpgt_clear(m: Msg):
    db.remove_rw("ChatGPT", f"gpt_id{m.chat.id}")

    await m.edit_text(
        "<emoji id=5258130763148172425>✅</emoji><b> You cleared messages context</b>"
    )
