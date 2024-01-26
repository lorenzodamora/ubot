from pyrogram import Client, idle

# crea accanto a main.py il file myClientParameter.py con dentro queste tre variabili, io l'ho messo in .gitignore
from myClientParameter import t_id, t_hash, t_phone, pushbullet_API_KEY as pushKey
from plugins.myParameters import TERMINAL_ID as TID

'''
from pushbullet import Pushbullet
t_id = "id numerico"
t_hash = "hash alfanumerico"
t_phone = "numero di telefono"
'''

# pb = Pushbullet(pushKey)
plugins = dict(root="plugins")
open("reply_waiting.txt", 'w').truncate()
title = "Ubot2"


async def main():
    app = Client(
        name=title,
        api_id=t_id,
        api_hash=t_hash,
        phone_number=t_phone,
        plugins=plugins
    )

    await app.start()
    await app.send_message(chat_id=TID, text="Ready")
    # pb.push_note(title, "Ready")
    print("READY")
    await idle()

    # pb.push_note(title, "Stop")
    await app.send_message(chat_id=TID, text="Stop")
    print("Stop")


if __name__ == "__main__":
    import uvloop
    uvloop.install()

    from platform import python_version_tuple

    if python_version_tuple() >= ("3", "11"):
        from asyncio import Runner

        with Runner() as runner:
            runner.get_loop().run_until_complete(main())

    else:
        from asyncio import new_event_loop

        loop = new_event_loop()
        loop.run_until_complete(main())
