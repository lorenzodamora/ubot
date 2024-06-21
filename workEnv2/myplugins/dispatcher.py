from asyncio import Queue, Lock, Task, create_task, get_event_loop, sleep
from concurrent.futures.thread import ThreadPoolExecutor
from datetime import timedelta, datetime
from inspect import iscoroutinefunction
from os import cpu_count
from typing import Callable
# from .myParameters import app, TERMINAL_ID  # ImportError: cannot import name 'app' from partially initialized \
#   module 'myplugins.myParameters' (most likely due to a circular import)


# TODO invia messaggio delle task cancellate anche quando viene stoppato client,
#  se non riesce per connessione fare un file che viene inviato quando viene restartato
class Dispatcher:

    def __init__(self, default_lifetime: float = 28800):
        """
        :param default_lifetime: of an event_handler, in seconds, default 8 hours.
        """
        self.default_lifetime = default_lifetime
        self.loop = get_event_loop()
        self.workers = min(32, cpu_count() + 4)
        self.executor = ThreadPoolExecutor(self.workers, thread_name_prefix="myHandler")

        self.handler_worker_tasks: list[Task] = []
        self.locks_list: list[Lock] = []

        self.updates_queue = Queue()
        self.handlers: list[Callable] = []

    async def start(self):
        self.loop = get_event_loop()
        for i in range(self.workers):
            self.locks_list.append(Lock())

            self.handler_worker_tasks.append(
                self.loop.create_task(
                    self.handler_worker(
                        self.locks_list[-1]
                    ),
                    name=f"handler_worker_{i}"
                )
            )

    async def stop(self, forced: bool = False):
        for i in range(self.workers):
            self.updates_queue.put_nowait(None)

        if not forced:
            for i in self.handler_worker_tasks:
                await i

        self.handler_worker_tasks.clear()
        self.clear()

    async def restart(self, forced: bool = True):
        await self.stop(forced)
        self.locks_list.clear()
        self.updates_queue = Queue()
        await self.start()

    def clear(self):
        self.handlers.clear()

    clear_handlers = clear

    def add(self, handler: Callable, lifetime: float = -1):
        """
        :param handler:
        :param lifetime: if negative: default, if == 0 no death
        """

        async def fn():
            for lock in self.locks_list:
                await lock.acquire()

            try:
                self.handlers.append(handler)
            finally:
                for lock in self.locks_list:
                    lock.release()

            from .myParameters import app, TERMINAL_ID
            _ = create_task(
                app.send_message(TERMINAL_ID, f"#add_handler\nadded an handler to myDispatcher with "
                                              f"lifetime:{lifetime}:\n{handler}"),
                name="add_handler msg")

        self.loop.create_task(fn(), name="add_handler myDispatcher")

        if lifetime < 0:
            lifetime = self.default_lifetime
        elif lifetime == 0:
            return

        self.remove(handler, lifetime)

    add_handler = add

    def remove(self, handler: Callable, wait_time: float = 0):
        async def fn():
            await sleep(wait_time)
            for lock in self.locks_list:
                await lock.acquire()

            try:
                self.handlers.remove(handler)
            finally:
                for lock in self.locks_list:
                    lock.release()

            from .myParameters import app, TERMINAL_ID
            _ = create_task(
                app.send_message(TERMINAL_ID, f"removed an handler to myDispatcher: {handler}"),
                name="add_handler msg")

        self.loop.create_task(
            fn(),
            name=f"remove_handler myDispatcher, wait_time: {wait_time}, end: "
                 f"{(datetime.now() + timedelta(seconds=wait_time)).strftime('%d-%m-%Y %H:%M:%S')}"
        )

    remove_handler = remove

    async def handler_worker(self, lock: Lock):
        while True:
            packet = await self.updates_queue.get()
            # print(packet)

            if packet is None:
                break

            try:
                async with lock:
                    for handler in self.handlers:
                        # args = (packet,)

                        # if args is None:
                        if packet is None:
                            print(f"no args for {handler}")
                            continue

                        try:
                            if iscoroutinefunction(handler):
                                # await handler(*args)
                                await handler(packet)
                            else:
                                await self.loop.run_in_executor(
                                    self.executor,
                                    handler,
                                    # *args
                                    packet
                                )
                        except Exception as e:
                            print(f"error during execute my handler: {e.__class__.__name__}\n{e}")

            except Exception as e:
                print(f"generic error: {e.__class__.__name__}\n{e}")

    def add_event(self, packet):
        self.updates_queue.put_nowait(packet)
