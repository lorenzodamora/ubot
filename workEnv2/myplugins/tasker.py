import asyncio


def read_all_my_tasks(print_=True):
    tasks = asyncio.all_tasks()
    ret = ""
    for task in tasks:
        n = task.get_name()
        if not n.startswith(("Task", "handler_worker_")):
            ret += n + "\n"
    if print_:
        print(f"all my tasks:\n{ret[:-1]}")
    return ret[:-1]


rat = read_all_my_tasks


def cancel_tasks_by_name(name: str, print_=True):
    tasks = asyncio.all_tasks()
    ndel = 0
    for task in tasks:
        if task.get_name() == name:
            task.cancel()
            ndel += 1
    if print_:
        print(f"n task cancelled: {ndel}")
    return ndel


ctn = cancel_tasks_by_name


def cancel_tasks_by_start(name: str, print_=True):
    tasks = asyncio.all_tasks()
    ndel = 0
    for task in tasks:
        if task.get_name().startswith(name):
            task.cancel()
            ndel += 1
    if print_:
        print(f"n task cancelled: {ndel}")
    return ndel


cts = cancel_tasks_by_start


def cancel_tasks_by_end(name: str, print_=True):
    tasks = asyncio.all_tasks()
    ndel = 0
    for task in tasks:
        if task.get_name().endswith(name):
            task.cancel()
            ndel += 1
    if print_:
        print(f"n task cancelled: {ndel}")
    return ndel


cte = cancel_tasks_by_end


async def _internal_ct(task):
    print(f"task {task.get_name()} in progress")
    await task
    print(f"task {task.get_name()} done")


def create_task_name(coro, name=None):
    task = asyncio.create_task(coro, name=name)

    # _ = asyncio.create_task(_internal_ct(task), name=f"internal_ct {name}")

    return task


create_task = create_task_name
