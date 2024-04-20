from pyrogram import Client, idle

# crea accanto a mMain.py il file myClientParameter.py con dentro queste tre variabili, io l'ho messo in .gitignore
from myClientParameter import t_id, t_hash, t_phone, pushbullet_API_KEY as pushKey, OPENAI_API_KEY
from myplugins.myParameters import TERMINAL_ID as TID, RW_PATH
from pushbullet import Pushbullet

'''
t_id = "id numerico"
t_hash = "hash alfanumerico"
t_phone = "numero di telefono"
'''

pb = Pushbullet(pushKey)
plugins = dict(root="myplugins")
open(RW_PATH, 'w').close()
title = "Ubot1"


async def main(dev=False):
    from os import environ
    if dev:
        environ['dev'] = '1'
        _title = "dev"
    else:
        environ['dev'] = '0'
        _title = title

    environ['OPENAI_API_KEY'] = OPENAI_API_KEY

    app = Client(
        name=_title,
        api_id=t_id,
        api_hash=t_hash,
        phone_number=t_phone,
        plugins=plugins
    )

    await app.start()
    await app.send_message(chat_id=TID, text="dev Ready" if dev else "Ready")

    if not dev:
        pb.push_note(title, "Ready")
    else:
        print("READY")
    await idle()

    if not dev:
        pb.push_note(title, "Stop")
    else:
        print("Stop")
    await app.send_message(chat_id=TID, text="dev Stop" if dev else "Stop")


if __name__ == "__main__":
    from sys import argv, exit

    if len(argv) > 2:
        print("Usage: python3 -u mMain.py [<parameter>]")
        exit(1)
    parameter = False
    if len(argv) == 2:
        if argv[1] == "dev":
            parameter = True
            print('dev on')
        else:
            print("parameters:\n\t[no parameter]\n\tdev")
            exit(1)

    from platform import python_version_tuple, system

    if system() == "Linux":
        import uvloop

        uvloop.install()

    if python_version_tuple() >= ("3", "11"):
        from asyncio import Runner

        with Runner() as runner:
            runner.get_loop().run_until_complete(main(parameter))

    else:
        from asyncio import new_event_loop

        loop = new_event_loop()
        loop.run_until_complete(main(parameter))
