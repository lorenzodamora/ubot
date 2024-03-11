import asyncio


def read_all_my_tasks():
    tasks = asyncio.all_tasks()
    ret = ""
    for task in tasks:
        n = task.get_name()
        if not n.startswith("Task"):
            ret += n + "\n"
    return ret[:-1]


def cancel_tasks_by_name(name: str):
    tasks = asyncio.all_tasks()
    ndel = 0
    for task in tasks:
        if task.get_name() == name:
            task.cancel()
            ndel += 1
    return ndel


def cancel_tasks_by_start(name: str):
    tasks = asyncio.all_tasks()
    ndel = 0
    for task in tasks:
        if task.get_name().startswith(name):
            task.cancel()
            ndel += 1
    return ndel


async def _internal_ct(task):
    print(f"task {task.get_name()} in progress")
    await task
    print(f"task {task.get_name()} done")


def create_task_name(coro, name=None):
    task = asyncio.create_task(coro, name=name)

    # _ = asyncio.create_task(_internal_ct(task), name=f"internal_ct {name}")

    return task
