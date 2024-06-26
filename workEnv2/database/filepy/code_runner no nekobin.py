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
from .myParameters import PREFIX_COMMAND, RESULT_PATH, TRACEBACK_PATH

from .functions import *
from .myParameters import *
PRE_EXEC = ("async def __todo(client, msg, *args):\n"
            " # from .functions import *\n"
            " # from .myParameters import *\n"
            " from .tasker import cancel_tasks_by_name as ctn, cancel_tasks_by_start as cts, "
            "cancel_tasks_by_end as cte, read_all_my_tasks as rat\n"
            " # ctn  cts  cte  auto-print the count of task cancelled\n"
            " c, m, p = client, msg, print\n"
            " r, u, here = m.reply_to_message, m.from_user, getattr(m.chat, 'id', None)\n"
            " # \"\".join(f\"\\n {_l}\" for _l in code.split(\"\\n\"))\n")


async def aexec(code, *args, timeout=None):
    """

    :param code: to run
    :param args: client + msg
    :param timeout: max time for running
    """
    exec(
        PRE_EXEC
        + "".join(f"\n {_l}" for _l in code.split("\n"))
    )

    with open(RESULT_PATH, 'w', encoding='utf-8') as file:
        with redirect_stdout(file), redirect_stderr(file):
            await asyncio.wait_for(locals()["__todo"](*args), timeout=timeout)


code_ = (
    "<b><emoji id={emoji_id}>🌐</emoji> Language:</b>\n"
    "<code>{language}</code>\n\n"
    "<b><emoji id=5431376038628171216>💻</emoji> Code:</b>\n"
    '<pre language="{pre_language}">{code}</pre>\n\n'
)

code_executing = (
    code_ +
    "<b><emoji id=5821116867309210830>🔃</emoji> Executing...</b>"
)
code_result = (
    code_ +
    "{result}\n"
    f"see result.txt & traceback.txt or print with"
    f" <code>{PREFIX_COMMAND}pr</code> & <code>{PREFIX_COMMAND}pt</code>"
)


async def python_exec(client: Client, msg: types.Message):
    is_r = msg.text[len(PREFIX_COMMAND):].startswith(("reval", "rexec"))
    if (len(msg.text.split(maxsplit=1)) == 1 and not is_r) or (is_r and not msg.reply_to_message):
        await msg.edit_text(f"`{msg.text}`\n<b>Code to execute isn't provided</b>")
        return

    if is_r:
        code = msg.reply_to_message.text

        # Check if msg is a reply to message with already executed code, and extract the code
        if code.startswith("🌐 Language:") and msg.reply_to_message.entities:
            for entity in msg.reply_to_message.entities:
                if entity.type == enums.MessageEntityType.PRE and entity.language == "python":
                    code = code[entity.offset: entity.offset + entity.length]
                    break
    elif msg.text[1:].startswith(("feval", "fexec")):
        txts = msg.text.split(maxsplit=2)
        file = txts[1] + ".txt"
        code = txts[2]
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

    async def _end_exceptor(_e):
        le = ""
        file_traceback = open(TRACEBACK_PATH, 'w', encoding="utf-8")
        if _e[0]:
            le += f"error in edit -> code_executing\n{_e[0].__class__.__name__}: {_e[0]}\n"
            file_traceback.write(f"error in edit -> code_executing, traceback0:\n{_e['traceback0'].getvalue()}\n")
        if _e[1]:
            le += f"error in aexec or later\n{_e[1].__class__.__name__}: {_e[1]}\n"
            file_traceback.write(f"error in aexec or later, traceback1:\n{_e['traceback1'].getvalue()}\n")
        file_traceback.close()

        if le == "":
            return

        res = f"<b><emoji id=5465665476971471368>❌</emoji> {le}</b>"

        if _e['text1'] != "":
            msg_text = f"{_e['text1']}\n{res}"
        else:
            msg_text = code_result.format(
                emoji_id=5260480440971570446,
                language="Python",
                pre_language="python",
                code=html.escape(code),
                result=res
            )

        try:
            await msg.edit_text(
                msg_text,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML
            )

        except Exception as ee:
            await msg.delete()
            await send_long_msg(f"{msg_text}\nnew error:\n{ee.__class__.__name__}: {ee}", client=client)

    is_error = {
        0: False,
        1: False,
        'text0': '',
        'text1': '',
        'traceback0': StringIO(),
        'traceback1': StringIO(),
    }

    try:
        is_error['text0'] = code_executing.format(
            emoji_id=5821116867309210830,
            language="Python",
            pre_language="python",
            code=html.escape(code),
        )
        await msg.edit_text(is_error['text0'], disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)

    except Exception as e:
        is_error[0] = e
        with redirect_stderr(is_error['traceback0']):
            print_exc()

    try:
        open(TRACEBACK_PATH, 'w').truncate()
        open(RESULT_PATH, 'w').truncate()

        start_time = perf_counter()
        await aexec(code, client, msg, timeout=None)
        stop_time = perf_counter()

        result = open(RESULT_PATH, 'r', encoding='utf-8').read()

        if re.match(r"^(https?)://[^\s/$.?#].\S*$", result):
            result = html.escape(result)
        else:
            result = f"<pre language=python>{html.escape(result)}</pre>"

        is_error['text1'] = code_result.format(
            emoji_id=5260480440971570446,
            language="Python",
            pre_language="python",
            code=html.escape(code),
            result=f"<b><emoji id=5472164874886846699>✨</emoji> Result</b>:\n"
                   f"{result}\n"
                   f"<b>Completed in {round(stop_time - start_time, 5)}s.</b>",
        )
        await msg.edit_text(is_error['text1'], disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)

    except asyncio.TimeoutError:
        is_error['text1'] = code_result.format(
            emoji_id=5260480440971570446,
            language="Python",
            pre_language="python",
            code=html.escape(code),
            result="<b><emoji id=5465665476971471368>❌</emoji> Timeout Error!</b>",
        )
        await msg.edit_text(is_error['text1'], disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)

    except Exception as e:
        is_error[1] = e
        with redirect_stderr(is_error['traceback1']):
            print_exc()

    await _end_exceptor(is_error)
