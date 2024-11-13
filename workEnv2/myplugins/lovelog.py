"""
manda nel canale shiro e neko lo status on e off
"""
import asyncio
from pyrogram.raw.types import UserStatusOnline, UserStatusOffline
from pyrogram.enums import UserStatus
from datetime import datetime
import pytz
from .functions import slm

chlog = -1002438524102
c = None


class UserStatusLogger:
    def __init__(self, user_id, name, utype: bool):
        """utype True è array di id, False è singolo elemento"""
        self.user_id = user_id
        self.utype = utype
        self.name = name
        self.sstr = f"a {self.name}'s list of log:"
        # self.wait_exp = asyncio.create_task(asyncio.sleep(0))
        self.wait_exp = None
        self.lock = asyncio.Lock()
        self.ad = {
            0: None,
            1: False,
            2: None,
            3: None
        }
        "dati asincroni, last_msg, is_on, msg_list, last_offtime_timestamp"
        fut = asyncio.get_event_loop().run_in_executor(None, lambda: asyncio.run(self.a_init()))
        _ = fut.result()

    async def a_init(self):
        global c
        if not c:
            from .myParameters import app
            c = app
        self.ad[2] = await c.send_message(chlog, self.sstr)

    async def rld(self, i):
        """read locked data"""
        # async with self.lock:
        return self.ad[i]

    async def wld(self, i, v):
        """write locked data"""
        # async with self.lock:
        self.ad[i] = v

    async def await_expires(self, raw):
        try:
            if self.wait_exp:
                self.wait_exp.cancel()

            exp = raw.status.expires
            wait_time = exp - datetime.now().timestamp()

            await asyncio.sleep(wait_time)
            await self.update_status(raw, True)
        except asyncio.CancelledError:
            # await slm("asyncio.CancelledError")
            pass

    async def loglist(self, time, onoff):
        lm = await self.rld(2)
        if lm.text.count("\n") >= 40:
            lm = await lm.reply(self.sstr + f"\n{onoff}  {time}")
            await self.wld(3, None)
        else:
            lm = await lm.edit(lm.text + f"\n{onoff}  {time}")
        await self.wld(2, lm)

    async def update_status(self, raw, force_off=False):
        async with self.lock:
            try:
                if isinstance(raw.status, UserStatusOnline) and not force_off:
                    ontime = gtime(raw.status.expires)

                    if await self.rld(1):
                        # già on
                        self.wait_exp = asyncio.create_task(self.await_expires(raw), name="Task-await_expires")

                        lm = await self.rld(0)
                        # lm =
                        try:
                            await lm.edit(format_msg(self.name, True, ontime))
                        except Exception as e:
                            await slm(f"errore in edit case 'già on': {e}\nuser: {self.name}\n")
                        # await self.wld(0, lm)
                        return
                    await self.wld(1, True)

                    # await slm("get loft")
                    loft = await self.rld(3)
                    # await slm(str(loft))
                    if not loft:
                        _loft = True
                    elif datetime.now().timestamp() >= loft + 30:
                        _loft = True
                    else:
                        _loft = False

                    # await slm(str(_loft))
                    # return
                    if _loft:
                        # o nuova lista o force_off o più di 30 secondi dall'ultimo off = nuovo log
                        lm = await c.send_message(chlog, format_msg(self.name, True, ontime))
                        # await slm('c. end me  age')
                        dm = await self.rld(0)
                        await self.wld(0, lm)
                        if dm:
                            await dm.delete()
                        await self.loglist(gtime(lm.raw.date), "on")

                    else:
                        # altrimenti cancella off log
                        lm = await self.rld(0)
                        await lm.edit(format_msg(self.name, True, ontime))
                        # await slm('lm.edit')

                        lm = await self.rld(2)
                        _pos = lm.text.rfind('\n')
                        _t = lm.text[:_pos] if _pos != -1 else lm.text
                        lm = await lm.edit(_t)
                        await self.wld(2, lm)

                    self.wait_exp = asyncio.create_task(self.await_expires(raw), name="Task-await_expires")

                elif isinstance(raw.status, UserStatusOffline) or force_off:
                    if not await self.rld(1):
                        # await slm(f"{self.name} già off", chlog)
                        return
                    elif await ifon(self.user_id, self.utype):
                        # await slm(f"{self.name} ancora on", chlog)
                        return
                    if self.wait_exp:
                        self.wait_exp.cancel()
                    await self.wld(1, False)

                    # await slm("get offts")
                    offts = getattr(raw.status, 'expires') if force_off else getattr(raw.status, 'was_online')
                    # await slm(str(offts))
                    # return
                    offtime = gtime(offts)
                    lm = await self.rld(0)
                    # if not lm: return # unreachable, fa già return a 'già off'
                    await lm.edit(format_msg(self.name, False, offtime))

                    await self.loglist(offtime, "                  off")
                    await self.wld(3, None if force_off else float(offts))

            except Exception as e:
                await slm(f"Errore in mydispatcher todo.lovelog update_status: {e}")


def format_msg(name, status, time):
    return f"{name} {'è on, scade' if status else 'era on.\n off da'}: {time}"


# Funzione per convertire il timestamp in ora formattata
def gtime(ts):
    return datetime.fromtimestamp(ts, pytz.timezone("Europe/Rome")).strftime("%H:%M:%S")


async def ifon(u, t):
    uu = await c.get_users(u)
    if t:
        return any(user.status == UserStatus.ONLINE for user in uu)
    return uu.status == UserStatus.ONLINE


"""
async def te():
    await asyncio.sleep(5)
    await slm("hi")


_ = asyncio.create_task(te())

import os
import sys


# Scrive direttamente in terminale, ignorando qualsiasi reindirizzamento
def pterm(t):
    os.write(sys.__stdout__.fileno(), (t + '\n').encode())
"""
