import asyncio
from signal import SIGINT, signal
from datetime import datetime

print_time = False
print_time_lock = asyncio.Lock()


async def set_print_time():
    global print_time
    while True:
        async with print_time_lock:
            print_time = True
        await asyncio.sleep(1)


async def read_stream(stream, callback):
    while True:
        line = await stream.readline()
        if not line:
            break
        await callback(line.decode())


async def print_line(line):
    global print_time
    async with print_time_lock:
        p_time = print_time
    if p_time:
        t = datetime.now().replace(microsecond=0)
        print(f"time: {t}")
        async with print_time_lock:
            print_time = False

    print(line, end="")


async def handle_sigint(process):
    try:
        # print("Received SIGINT. Sending SIGINT to process...")
        process.send_signal(SIGINT)
    except ValueError:
        # print(f"Failed to send SIGINT to process: {type(e)}")
        pass


async def main(args: list[str]):
    from sys import executable
    # Run your async subprocess
    process = await asyncio.create_subprocess_exec(
        executable,
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    _ = asyncio.create_task(set_print_time())

    # Register signal handler for SIGINT (Ctrl+C)
    signal(SIGINT, lambda sig, frame: asyncio.create_task(handle_sigint(process)))

    # Start reading stdout and stderr concurrently
    await asyncio.gather(
        read_stream(process.stdout, print_line),
        read_stream(process.stderr, print_line),
    )

    # Wait for the process to complete
    await process.wait()


if __name__ == "__main__":
    from sys import argv, exit
    if len(argv) not in [2, 3]:
        print("Usage: python3 -u main.py [<script.py>] [<?parameter>]")
        exit(1)
    parameter = [argv[1]]

    if len(argv) == 3:
        if argv[2] == "dev":
            parameter.append('dev')
        else:
            print("parameters:\n\t[no parameter]\n\tdev")
            exit(1)

    from platform import python_version_tuple, system

    if system() == "Linux":
        import uvloop

        uvloop.install()

    if python_version_tuple() >= ("3", "11"):
        with asyncio.Runner() as runner:
            runner.get_loop().run_until_complete(main(parameter))

    else:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(main(parameter))
