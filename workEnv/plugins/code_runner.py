"""
exec manager
"""
import asyncio
import html
import re
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from time import perf_counter
from traceback import print_exc
from pyrogram import Client, types, enums

pre_exec = ("async def __todo(client, msg, *args):\n"
            " app = client\n"
            " m = msg\n"
            " r = m.reply_to_message\n"
            " u = m.from_user\n"
            " ru = getattr(r, 'from_user', None)\n"
            " here = getattr(m.chat, 'id', None)\n"
            " p = print\n"
            "# \"\".join(f\"\\n {_l}\" for _l in code.split(\"\\n\"))\n")


async def aexec(code, *args, timeout=None):
    exec(
        pre_exec
        + "".join(f"\n {_l}" for _l in code.split("\n"))
    )

    f = StringIO()
    with redirect_stdout(f), redirect_stderr(f):
        await asyncio.wait_for(locals()["__todo"](*args), timeout=timeout)

    return f.getvalue()


code_result = (
    "<b><emoji id={emoji_id}>🌐</emoji> Language:</b>\n"
    "<code>{language}</code>\n\n"
    "<b><emoji id=5431376038628171216>💻</emoji> Code:</b>\n"
    '<pre language="{pre_language}">{code}</pre>\n\n'
    "{result}"
)


async def python_exec(client: Client, msg: types.Message):
    is_r = msg.text[1:].startswith(("reval", "rexec"))
    if len(msg.text.split(maxsplit=1)) == 1 and not is_r:
        return await msg.edit_text("<b>Code to execute isn't provided</b>")

    if is_r:
        code = msg.reply_to_message.text

        # Check if msg is a reply to message with already executed code, and extract the code
        if msg.reply_to_message.text.startswith("🌐 Language:"):
            for entity in msg.reply_to_message.entities:
                if (
                    entity.type == enums.MessageEntityType.PRE
                    and entity.language == "python"
                ):
                    code = msg.reply_to_message.text[
                           entity.offset: entity.offset + entity.length
                           ]
                    break
    elif msg.text[1:].startswith(("feval", "fexec")):
        txts = msg.text.split(maxsplit=2)
        file = txts[1]
        code = txts[2]
        if not file.endswith('.py'):
            raise ValueError("Il nome del file deve terminare con `.py`")
        try:
            # Prova a creare un nuovo file con il nome specificato
            open(file, "w", encoding="utf-8").write(code)
        except OSError:
            # Se si è verificato un errore durante la creazione del file, restituisci False
            raise ValueError("OSError, impossibile creare il file (nome non valido?)")
    else:
        code = msg.text.split(maxsplit=1)[1]

    # fix character \u00A0
    code = code.replace("\u00A0", "").strip()

    await msg.edit_text(
        "<b><emoji id=5821116867309210830>🔃</emoji> Executing...</b>"
    )

    try:
        start_time = perf_counter()
        result = await aexec(code, client, msg, timeout=60)
        stop_time = perf_counter()

        if len(result) > 3072:
            # result = html.escape(await utils.paste_neko(result))
            open("database/result.txt", 'w', encoding='utf-8').write(result)
            from .myParameters import PREFIX_COMMAND
            result = f"view database/result.txt or print with `{PREFIX_COMMAND}pr`"
        elif re.match(r"^(https?)://[^\s/$.?#].\S*$", result):
            result = html.escape(result)
        else:
            result = f"<pre language=python>{html.escape(result)}</pre>"

        return await msg.edit_text(
            code_result.format(
                emoji_id=5260480440971570446,
                language="Python",
                pre_language="python",
                code=html.escape(code),
                result=f"<b><emoji id=5472164874886846699>✨</emoji> Result</b>:\n"
                       f"{result}\n"
                       f"<b>Completed in {round(stop_time - start_time, 5)}s.</b>",
            ),
            disable_web_page_preview=True,
        )
    except asyncio.TimeoutError:
        return await msg.edit_text(
            code_result.format(
                emoji_id=5260480440971570446,
                language="Python",
                pre_language="python",
                code=html.escape(code),
                result="<b><emoji id=5465665476971471368>❌</emoji> Timeout Error!</b>",
            ),
            disable_web_page_preview=True,
        )
    except Exception as e:
        err = StringIO()
        with redirect_stderr(err):
            print_exc()

        open("database/traceback.txt", 'w', encoding="utf-8").write(err.getvalue())
        from .myParameters import PREFIX_COMMAND
        err = f"see database/traceback.txt or print with `{PREFIX_COMMAND}pt`"

        return await msg.edit_text(
            code_result.format(
                emoji_id=5260480440971570446,
                language="Python",
                pre_language="python",
                code=html.escape(code),
                result=f"<b><emoji id=5465665476971471368>❌</emoji> {e.__class__.__name__}: {e}</b>\n"
                # f"Traceback: {html.escape(await utils.paste_neko(err.getvalue()))}",
                       f"Traceback: {err}",
            ),
            disable_web_page_preview=True
        )
