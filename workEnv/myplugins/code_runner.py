"""
exec manager
"""
from asyncio import wait_for, TimeoutError
from html import escape
from re import match
from json import loads, dumps
from requests import post, patch
from contextlib import redirect_stderr, redirect_stdout
from traceback import print_exc
from io import StringIO
from time import perf_counter
from pyrogram import Client, types, enums
from .myParameters import PREFIX_COMMAND, EVALCODE_PATH, RESULT_PATH, TRACEBACK_PATH

from .functions import *
from .myParameters import *

PRE_EXEC = ("async def __todo(client, msg, redirecting, *args):\n"
            " def p(text):\n"
            "  redirecting.write(f\"{text}\\n\")\n"
            " # from .functions import *\n"
            " # from .myParameters import *\n"
            " from .myParameters import target\n"
            " from .tasker import cancel_tasks_by_name as ctn, cancel_tasks_by_start as cts, "
            "cancel_tasks_by_end as cte, read_all_my_tasks as rat\n"
            " # ctn  cts  cte  auto-print the count of task cancelled\n"
            " c, m = client, msg\n"
            " r, u, here = m.reply_to_message, m.from_user, getattr(m.chat, 'id', None)\n"
            " # \"\".join(f\"\\n {_l}\" for _l in code.split(\"\\n\"))\n")


async def aexec(code, *args, timeout=None):
    """
    :param code: to run
    :param args: client + msg
    :param timeout: max time for running
    :return: the result string
    """
    exec(
        PRE_EXEC
        + "".join(f"\n {_l}" for _l in code.split("\n"))
    )

    """
    with open(RESULT_PATH, 'w', encoding='utf-8') as file:
        with redirect_stdout(file), redirect_stderr(file):
            await wait_for(locals()["__todo"](*args), timeout=timeout)
    """
    redirecting = StringIO()
    # redirect non è il massimo, se fai due eval oppure ricevi un'errore o un messaggio da qualche altra parte,
    # il tutto viene messo in questo redirecting, a menoché ne fai un altro, a quel punto questo viene spostato
    with redirect_stdout(redirecting), redirect_stderr(redirecting):
        await wait_for(locals()["__todo"](*args, redirecting), timeout=timeout)

    try:
        open(RESULT_PATH, 'w', encoding='utf-8').write(redirecting.getvalue())
    except Exception as e:
        await send_long_msg(f"error in code_runner while opening result file\n{e.__class__.__name__}:\n{e}\n")

    return redirecting.getvalue()


code_ = (
    "<b><emoji id={emoji_id}>🌐</emoji> Language:</b>\n"
    "<code>{language}</code>\n\n"
    "<b><emoji id=5431376038628171216>💻</emoji> Code:</b>\n"
    '<pre language="{pre_language}">{code}</pre>\n\n'
)

code_executing = (
    code_ +
    "<b><emoji id=5821116867309210830>🔃</emoji> Executing...</b>\n\n"
    "code: {gistlink}"
)
code_result = (
    code_ +
    "{result}\n"
    "see code & result & traceback: {gistlink}\n"
    f"or print with <code>{PREFIX_COMMAND}pc</code> & <code>{PREFIX_COMMAND}pr</code> & <code>{PREFIX_COMMAND}pt</code>"
)

PYTHON_EMOJI_ID = 5260480440971570446
X_EMOJI_ID = 5465665476971471368


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
        # non ci entra mai perchè modifica il msg.text con eval invece di feval
        """
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
        """
    else:
        code = msg.text.split(maxsplit=1)[1]

    # fix character \u00A0
    code = code.replace("\u00A0", "").strip()

    async def _end_exceptor(_e, _result):
        le = ""
        str_traceback = ""
        if _e[0]:
            le = f"error in edit -> code_executing\n{_e[0].__class__.__name__}: {_e[0]}\n"
            str_traceback = f"error in edit -> code_executing, traceback0:\n{_e['traceback0'].getvalue()}\n"
        if _e[1]:
            le += f"error in aexec or later\n{_e[1].__class__.__name__}: {_e[1]}\n"
            str_traceback += f"error in aexec or later, traceback1:\n{_e['traceback1'].getvalue()}\n"

        if le == "":
            return

        open(TRACEBACK_PATH, 'w', encoding="utf-8").write(str_traceback)
        res = f"<b><emoji id={X_EMOJI_ID}>❌</emoji> {le}</b>"

        if _e['text1'] != "":
            msg_text = f"{_e['text1']}\n{res}"
        else:
            msg_text = code_result.format(
                emoji_id=PYTHON_EMOJI_ID,
                language="Python",
                pre_language="python",
                code=escape(code),
                result=res,
                gistlink=escape(await paste_githubgist(
                    [
                        _result,
                        le,
                        str_traceback,
                    ],
                    [
                        f'result{msg.raw.date}',
                        f'error{msg.raw.date}',
                        f'traceback{msg.raw.date}',
                    ],
                    gist_id=gistid
                )),
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

    gistlink, gistid = await paste_githubgist(
        [code],
        [f'code{msg.raw.date}']
    )

    try:
        is_error['text0'] = code_executing.format(
            emoji_id=5821116867309210830,
            language="Python",
            pre_language="python",
            code=escape(code),
            gistlink=gistlink
        )
        await msg.edit_text(
            is_error['text0'],
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )

    except Exception as e:
        is_error[0] = e
        with redirect_stderr(is_error['traceback0']):
            print_exc()

    result = ""

    try:
        open(TRACEBACK_PATH, 'w').truncate()
        open(RESULT_PATH, 'w').truncate()
        open(EVALCODE_PATH, 'w', encoding='utf-8').write(code)

        start_time = perf_counter()
        result = escape(await aexec(code, client, msg, timeout=None))
        # no timeout because I have implemented my own task logic,
        # I see all the code_runner in running and can interrupt them as tasks using tasker.py and imports in PRE_EXEC
        stop_time = perf_counter()

        # result = escape(open(RESULT_PATH, 'r', encoding='utf-8').read())

        if match(r"^(https?)://[^\s/$.?#].\S*$", result):
            parse_result = result
        else:
            parse_result = f"<pre language=python>{result}</pre>"

        is_error['text1'] = code_result.format(
            emoji_id=PYTHON_EMOJI_ID,
            language="Python",
            pre_language="python",
            code=escape(code),
            result=f"<b><emoji id=5472164874886846699>✨</emoji> Result</b>:\n"
                   f"{parse_result}\n"
                   f"<b>Completed in {round(stop_time - start_time, 5)}s.</b>",
            gistlink=escape(await paste_githubgist(
                [result],
                [f'result{msg.raw.date}'],
                gistid
            )),
        )

        await msg.edit_text(is_error['text1'], disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)

    except TimeoutError:
        is_error['text1'] = code_result.format(
            emoji_id=PYTHON_EMOJI_ID,
            language="Python",
            pre_language="python",
            code=escape(code),
            result=f"<b><emoji id={X_EMOJI_ID}>❌</emoji> Timeout Error!</b>",
            gistlink=escape(await paste_githubgist(
                [result],
                [f'result{msg.raw.date}'],
                gistid
            )),
        )
        await msg.edit_text(is_error['text1'], disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)

    except Exception as e:
        is_error[1] = e
        with redirect_stderr(is_error['traceback1']):
            print_exc()

    await _end_exceptor(is_error, result)


async def paste_githubgist(codes: list[str], pastenames: list[str], gist_id: str = None):
    """
    based on https://gist.github.com/lambdamusic/df01e068f74d979d778d13db2acaa03c
    and https://stackoverflow.com/a/65761251

    :param codes: the contents of all files
    :param pastenames: the filesname
    :param gist_id: if None create, else update
    :return:
    """
    gist_api_url = "https://api.github.com/gists"
    from . import GIST_TOKEN
    api_token = GIST_TOKEN

    headers = {
        'Authorization': 'token %s' % api_token
    }
    params = {
        'scope': 'gist'
    }

    payload_files = {}
    for code, pastename in zip(codes, pastenames):
        if code == "":
            continue
        payload_files[pastename] = {
            "content": code
        }

    payload = {
        "description": "github.com/lorenzodamora/ubot   eval command result",
        "public": False,
        "files": payload_files,
    }

    try:
        if gist_id is None:
            # make a request
            res = post(gist_api_url, headers=headers, params=params, data=dumps(payload))
            # print("Status:", res.status_code)
            # print("Result:", j['html_url'])
            j = loads(res.text)
            return [j['html_url'], j['id']]
        else:
            res = patch(f"{gist_api_url}/{gist_id}", headers=headers, data=dumps(payload))
            return loads(res.text)['html_url']

    except Exception as e:
        ret = f"Pasting failed with error:\n{e.__class__.__name__}: {e}"
        if gist_id is None:
            return [ret, None]
        else:
            return ret
