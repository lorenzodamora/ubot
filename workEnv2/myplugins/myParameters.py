"""
parametri globali
"""
BOTLIST = {
    'Ubot1': {
        # linux, windows
        'paths': ['/home/ubuntu/Magnus/PycharmProj/ubot/output.txt', '../output.txt'],
        'id': 1
    },
    'Ubot2': {
        'paths': ['/home/ubuntu/Magnus/PycharmProj/ubot2/output.txt', '../output.txt'],
        'id': 2
    },
    'Infobot': {
        'paths': ['/home/ubuntu/Magnus/PycharmProj/infobot/output.txt', '../../infobot/mazzobot/output.txt'],
        'id': 3
    },
    'MeteoATbot': {
        'paths': ['/home/ubuntu/Magnus/PycharmProj/persone/Adora/meteobot/output.txt', '../../meteoATbot/output.txt'],
        'id': 4
    }
}
MY_ID2, MY_ID = 649363031, 1259233812
MY_TAG2, MY_TAG = '@Ill_Magnus', '@ill_lore'
TERMINAL_ID = -1001995530063
SAVED_MESSAGE_FORUM_ID, PIC_TOPIC_ID = -1001971247646, 18  # Forum: Saved Message > Topic:Pic
PREFIX_COMMAND, PREFIX_SEND_TO = ',', '>'
WELCOME_MSG, WELCOME_MSG1 = "Ti ringrazio di avermi contattato, ti risponderò appena possibile.", (
    "! messaggio automatico !\nTi ringrazio di avermi contattato, ti risponderò appena possibile.\n"
    "Chiedo Scusa in anticipo per il tempo che potrei metterci, ma siete in tantissimi!")
ASCII_ART = {
    'pipo0':
        "..............\u2584\u2584 \u2584\n........\u2590\u2590\u2591\u2591\u2580\u2591\u2591"
        "\u2590\u2590\n..... \u2590\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u258c"
        "\n...\u2590\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u258c\n....\u2590"
        "\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u258c\n....\u2590\u2580\u2584"
        "\u2584\u2584\u2584\u2584\u2584\u2584\u2584\u2580\u258c\n....\u2590\u2591\u2591\u2591\u2591"
        "\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n....\u2590\u2591\u2591\u2591\u2591\u2591\u2591"
        "\u2591\u2591\u2591\u2591\u258c\n....\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591"
        "\u2591\u2591\u258c\n....\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591"
        "\u258c\n....\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n...."
        "\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n....\u2590\u2591"
        "\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n....\u2590\u2591\u2591\u2591"
        "\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n....\u2590\u2591\u2591\u2591\u2591\u2591"
        "\u2591\u2591\u2591\u2591\u2591\u258c\n....\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u2591"
        "\u2591\u2591\u2591\u258c\n..\u2590.\u2580\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u2592"
        "\u2592\u2592\u2580\u2590\n..\u2584\u2580\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591"
        "\u2591\u2591\u2591\u2591\u2580\u2584\n.\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u2591"
        "\u2580\u2584\u2592\u2584\u2580\u2591\u2591\u2591\u2591\u258c\n\u2590\u2591\u2591\u2591"
        "\u2591\u2591\u2591\u2591\u2592\u2592\u2590\u2592\u2592\u2591\u2591\u2591\u2591\u2591"
        "\u258c\n\u2590\u2592\u2591\u2591\u2591\u2591\u2591\u2592\u2592\u2592\u2590\u2592\u2592"
        "\u2592\u2591\u2591\u2591\u2592\u258c\n.\u2580\u2584\u2592\u2592\u2592\u2592\u2592\u2584"
        "\u2580\u2592\u2580\u2584\u2592\u2592\u2592\u2592\u2584,",
    'pipo1':
        "\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u281f\u2820"
        "\u2870\u28d5\u28d7\u28f7\u28e7\u28c0\u28c5\u2818\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff"
        "\u28ff\u28ff\u28ff\u28ff\u28ff\u2803\u28e0\u28f3\u28df\u28ff\u28ff\u28f7\u28ff\u287f"
        "\u28dc\u2804\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u28ff\u28ff\u287f\u2801\u2804"
        "\u28f3\u28b7\u28ff\u28ff\u28ff\u28ff\u287f\u28dd\u2816\u2804\u28ff\u28ff\u28ff\u28ff"
        "\u28ff \u28ff\u28ff\u28ff\u28ff\u2803\u2804\u28a2\u2879\u28ff\u28b7\u28ef\u28bf\u28b7"
        "\u286b\u28d7\u280d\u28b0\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u28ff\u284f\u2880"
        "\u2884\u2824\u28c1\u280b\u283f\u28d7\u28df\u286f\u284f\u288e\u2801\u28b8\u28ff\u28ff"
        "\u28ff\u28ff\u28ff \u28ff\u28ff\u28ff\u2804\u2894\u2895\u28ef\u28ff\u28ff\u2872\u2864"
        "\u2844\u2864\u2804\u2840\u28a0\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u2807"
        "\u2820\u2873\u28ef\u28ff\u28ff\u28fe\u28b5\u28eb\u288e\u288e\u2806\u2880\u28ff\u28ff"
        "\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u2804\u28a8\u28eb\u28ff\u28ff\u287f\u28ff"
        "\u28fb\u288e\u2857\u2855\u2845\u28b8\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff"
        "\u28ff\u2804\u289c\u28be\u28fe\u28ff\u28ff\u28df\u28d7\u28af\u286a\u2873\u2840\u28b8"
        "\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u2804\u28b8\u28bd\u28ff\u28f7"
        "\u28ff\u28fb\u286e\u2867\u2873\u2871\u2841\u28b8\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff"
        " \u28ff\u28ff\u2844\u28a8\u28fb\u28fd\u28ff\u28df\u28ff\u28de\u28d7\u287d\u2878\u2850"
        "\u28b8\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u2847\u2880\u2897\u28ff"
        "\u28ff\u28ff\u28ff\u287f\u28de\u2875\u2863\u28ca\u28b8\u28ff\u28ff\u28ff\u28ff\u28ff"
        "\u28ff\u28ff \u28ff\u28ff\u28ff\u2840\u2863\u28d7\u28ff\u28ff\u28ff\u28ff\u28ef\u286f"
        "\u287a\u28fc\u280e\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u28ff\u28e7"
        "\u2810\u2875\u28fb\u28df\u28ef\u28ff\u28f7\u28df\u28dd\u289e\u287f\u28b9\u28ff\u28ff"
        "\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u28ff\u28ff\u2846\u2898\u287a\u28fd\u28bf\u28fb"
        "\u28ff\u28d7\u2877\u28f9\u28a9\u2883\u28bf\u28ff\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff"
        "\u28ff\u28ff\u28f7\u2804\u282a\u28ef\u28df\u28ff\u28af\u28ff\u28fb\u28dc\u288e\u2886\u281c\u28ff\u28ff"
        "\u28ff\u28ff\u28ff \u28ff\u28ff\u28ff\u28ff\u28ff\u2846\u2804\u28a3\u28fb\u28fd\u28ff\u28ff\u28df\u28fe"
        "\u286e\u287a\u2878\u2838\u28ff\u28ff\u28ff\u28ff \u28ff\u28ff\u287f\u281b\u2809\u2801\u2804\u2895\u2873"
        "\u28fd\u287e\u28ff\u28bd\u28ef\u287f\u28ee\u289a\u28c5\u2839\u28ff\u28ff\u28ff \u287f\u280b\u2804\u2804"
        "\u2804\u2804\u2880\u2812\u281d\u28de\u28bf\u287f\u28ff\u28fd\u28bf\u287d\u28e7\u28f3\u2845\u280c\u283b"
        "\u28ff \u2801\u2804\u2804\u2804\u2804\u2804\u2810\u2850\u2831\u2871\u28fb\u287b\u28dd\u28ee\u28df\u28ff"
        "\u28fb\u28f7\u28cf\u28fe",
    'pipo2':
        "\u28a0\u28de\u28fb\u28ff\u28f6\u28e4\u2840                   \n\u28b8\u28ff\u28ff\u28ff"
        "\u28ff\u28ff\u28ff\u28e6                  \n\u28b8\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff"
        "\u28ff\u2840                 \n \u28bb\u28ff\u28ff\u28ff\u28ff\u28ff\u28df\u28f5\u28e6\u2840               "
        "\n  \u2808\u2833\u28bf\u28fb\u28f5\u28ff\u28ff\u28ff\u28f7\u28c4              \n    \u2818\u28bf\u28ff\u28ff"
        "\u28ff\u28ff\u28ff\u28ff\u28f7\u28c4            \n      \u2839\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff"
        "\u28f7\u28e6\u28c0         \n       \u2808\u283b\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28f6"
        "\u28e4\u28e4\u28e4\u2840   \n         \u2808\u283b\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff"
        "\u28ff\u28ff\u28ff\u2846  \n           \u2808\u2819\u283f\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff"
        "\u28ff\u28ff  \n              \u2808\u2819\u283f\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u2847 \n"
        "               \u28e0\u28fe\u28f6\u28b9\u28ff\u28ff\u28ff\u28ff\u28ff\u28f7 \n              \u28f0\u28ff"
        "\u28ff\u284f\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u2847\n              \u28ff\u28ff\u28ff\u28b0\u28ff"
        "\u28ff\u28ff\u28ff\u28ff\u28ff\u28ff\u28f7\n              \u281b\u283f\u283f\u2838\u28ff\u28ff\u28ff\u28ff"
        "\u28ff\u28ff\u28ff\u284f\n                  \u2819\u283f\u28ff\u28ff\u28ff\u287f\u281f",
    'pipo3':
        "....... \u2584\u2588\u2593\u2591\u2591\u2591\u2591\u2591\u2591\u2593\u2588\u2584\n...."
        "\u2584\u2580\u2591\u2591\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\u2591\u2592"
        "\u258c\n.\u2590\u2591\u2591\u2591\u2591\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\u2591\u2591\u2591"
        "\u258c\n\u2590 \u2591\u2591\u2591\u2591\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\u2591\u2591\u2591"
        "\u2590\n\u2590 \u2592\u2591\u2591\u2591 \u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\u2591\u2592\u2592"
        "\u2590\n\u2590 \u2592\u2591\u2591\u2591\u2591\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\u2591\u2592"
        "\u2590\n..\u2580\u2584\u2592\u2592\u2592\u2592\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\u2584\u2580"
        "\n........ \u2580\u2580\u2580 \u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n.................\u2590"
        "\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n.................\u2590\u2591\u2591\u2591\u2591\u2591\u2591"
        "\u258c\n.................\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c\n.................\u2590\u2591"
        "\u2591\u2591\u2591\u2591\u2591\u258c\n.................\u2590\u2591\u2591\u2591\u2591\u2591\u2591\u258c"
        "\n................\u2590\u2584\u2580\u2580\u2580\u2580\u2580\u2584\u258c\n...............\u2590\u2592"
        "\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u258c\n...............\u2590\u2592\u2592\u2592\u2592\u2592"
        "\u2592\u2592\u2592\u258c\n................\u2590\u2592\u2592\u2592\u2592\u2592\u2592\u2592\u258c\n"
        "..................\u2580\u258c\u2592\u2580\u2592\u2590\u2580",
    'null': ''
}
RW_PATH, RESULT_PATH, TRACEBACK_PATH, PY_EXEC_FOLD, GA_FOLD = (
    'database/reply_wait.txt', 'database/result.txt', 'database/traceback.txt', 'database/py_exec', 'database/ga'
)
COMMANDS = {
    '?': {
        'alias': ['h', 'help', '?', 'commands', 'c'],
        'type': 2,
        'note': "see help menu",
        'group': "generic",
        'other': True
    },
    '?+': {
        'alias': ['h+', 'help+', '?+', 'commands+', 'c+'],
        'type': 1,
        'note': "see extra help info",
        'group': "generic",
    },
    'automatici': {
        'alias': ['auto'],
        'type': 2,
        'note': "\"uso i messaggi automatici perché..\"\n__{c?: char}__ : 'e' for english version",
        'group': "fast"
    },
    'delcmd': {
        'alias': [f'del{PREFIX_COMMAND}', f'd{PREFIX_COMMAND}'],
        'type': 2,
        'note': "run cmd and delete msg\nex.:`,del, eval p(1)`",
        'group': "service-cmd"
    },
    'delete': {
        'alias': ['del', 'd'],
        'type': 2,
        'note': "delete msg starting from reply or last before this\n"
                "__{n?: int = 1}__ : num of msgs to delete, max:100",
        'group': "service-cmd"
    },
    'eval': {
        'alias': ['eval', 'exec'],
        'type': 2,
        'note': "`eval h` / `exec ?` to see this help",
        'group': "service-cmd"
    },
    'eval reply': {
        'alias': ['reval', 'rexec'],
        'type': 2,
        'note': "`reval h` / `rexec ?` to see this help",
        'group': "service-cmd"
    },
    'eval file': {
        'alias': ['feval', 'fexec', 'fe'],
        'type': 2,
        'note': "`fe h` to see this help",
        'group': "service-cmd"
    },
    'gets': {
        'alias': ['get', 'g'],
        'type': 1,
        'note': "getchat or getreply",
        'group': "get"
    },
    'get msg id': {
        'alias': ['thisid', 'thisMsgId', 'MsgId'],
        'type': 2,
        'note': "edit text with his id\n"
                "__{n?: int = 1}__ : send n msg with id\nif have a reply it sends only the id of that",
        'group': "get",
        'other': True
    },
    'getall': {
        'alias': ['getAll', 'ga'],
        'type': 1,
        'note': f"print all vars of msg and chat on ga files, see `{PREFIX_COMMAND}h getall print`",
        'group': "get"
    },
    'getall print': {
        'alias': ['pga', 'printga'],
        'type': 1,
        'note': "print all ga files",
        'group': "print"
    },
    'getchat': {
        'alias': ['getchat', 'gc'],
        'type': 1,
        'note': "get basic info of chat",
        'group': "get"
    },
    'getchat reply': {
        'alias': ['getreply', 'getr'],
        'type': 1,
        'note': " = getchat, but of reply",
        'group': "get"
    },
    'getid': {
        'alias': ['getid', 'id'],
        'type': 1,
        'note': "get id of chat or replyed user",
        'group': "get"
    },
    'getme': {
        'alias': ['getme'],
        'type': 1,
        'note': "get User instance of myself",
        'group': "get"
    },
    'get reply waiting': {
        'alias': ['grw', 'gw'],
        'type': 1,
        'note': "get reply waiting list (terminal)",
        'group': "reply-wait"
    },
    'greetings': {
        'alias': ['0'],
        'type': 2,
        'note': "write \"buondì\\n come va?\"\n__{c?: char}__ : 'e' for english version",
        'group': "fast"
    },
    'moon': {
        'alias': ['moon', 'luna'],
        'type': 2,
        'note': "graphic moon UAU\n__{n: float = 0.1}__ : seconds between edits, min 0.1",
        'group': "special",
        'other': True
    },
    'null': {
        'alias': ['null', 'vuoto', 'void', '', 'spazio', 'space'],
        'type': 1,
        'note': "sends the text with empty space, if you reply a message it keeps it",
        'group': "special",
        'other': True
    },
    'offline': {
        'alias': ['offline', 'off'],
        'type': 2,
        'note': "set your status offline\n"
                "__{sec?: float = 4} {iter?: int = 5}__ : seconds and number of ripetition(if -1= always)",
        'group': "service-cmd"
    },
    'output': {
        'alias': ['output', 'out', 'po'],
        'type': 2,
        'note': f"print output files\nsee `{PREFIX_COMMAND}out h`",
        'group': "print"
    },
    'pic': {
        'alias': ['p', 'pic'],
        'type': 1,
        'note': "forward reply to pic topic",
        'group': "send to"
    },
    'ping': {
        'alias': ['ping'],
        'type': 1,
        'note': "ping in chat",
        'group': "service-cmd"
    },
    'pingt': {
        'alias': ['pingt'],
        'type': 1,
        'note': "ping in terminal",
        'group': "service-cmd"
    },
    'pipo': {
        'alias': ['pipo'],
        'type': 2,
        'note': "pipo : ascii art\n__{n?: int = rnd}__ : pipo choise= 0,1,2,3",
        'group': "special",
        'other': True
    },
    'print exec': {
        'alias': ['pr', 'pt'],
        'type': 1,
        'note': "print result or traceback (of exec)",
        'group': "print"
    },
    'remove': {
        'alias': ['r', 'remove'],
        'type': 2,
        'note': f"remove from rw list an user\nsee `{PREFIX_COMMAND}r h`",
        'group': "reply-wait"
    },
    'save': {
        'alias': ['save', 's'],
        'type': 1,
        'note': "forward reply to saved",
        'group': "send to"
    },
    'search': {
        'alias': ['search'],
        'type': 2,
        'note': "search for id or username",
        'group': "get"
    },
    'search reply': {
        'alias': ['rsearch'],
        'type': 1,
        'note': "search for id or username of reply",
        'group': "get"
    },
    'second profile': {
        'alias': ['2'],
        'type': 1,
        'note': "forward reply to second profile",
        'group': "send to"
    },
    'strikethrough': {
        'alias': ['strikethrough', 'done', 'v'],
        'type': 1,
        'note': "strikethrough the replyed message",
        'group': "fast"
    },
    'terminal': {
        'alias': ['t', 'terminal'],
        'type': 1,
        'note': "forward reply to terminal",
        'group': "send to"
    },
    'un attimo': {
        'alias': ['1'],
        'type': 2,
        'note': "\"Dammi un attimo\" + add to 'reply_waiting' list",
        'group': "fast"
    },
}
"""
    'version': {
        'alias': ['version'],
        'type': 1,
        'note': "edit msg with version and date of ubot",
        'group': "service-cmd",
        'other': True
    },
"""
""" '': {
        'alias': ['',' '],
        'type': 0,
        'note': "",
        'group': "generic",
        'other': True
    },
"""
HELP_PLUS_TEXT = (
    f"Il prefix è '`{PREFIX_COMMAND}`'\ni comandi '`{PREFIX_SEND_TO}`' sono \"send to\"\n"
    f"i comandi `{PREFIX_COMMAND}.` e `{PREFIX_SEND_TO}.` ignorano il comando (e cancellano il punto)\n\n"
    f"cos'è la lista \"reply waiting\" ?\n"
    "ogni tot tempo va a scrivere alle persone in lista che ancora non sei riuscito a dedicargli tempo\n\n"
    "come funziona la lista \"reply waiting\" ?\n"
    " - funziona solo nelle private\n"
    " - i tempi di attesa sono 1,8,24,36,48 ore. una volta raggiunto 48 ore, si stoppa\n"
    " - lo invia solo se l'ultimo messaggio non è tuo\n"
    " - come togliere una persona dalla lista? appena invii un messaggio a quella persona\n"
    f"     oppure comando `{PREFIX_COMMAND}r` / `{PREFIX_COMMAND}remove`\n"
    f" - per ottenere la lista: comando `{PREFIX_COMMAND}gw` / `{PREFIX_COMMAND}grw`\n\n\n"
    f"Others Commands:\n\n"
    f"Il prefix è `{MY_TAG} {PREFIX_COMMAND}`\n"
    "Richieste: una ogni 20 sec, esclusa esecuzione, tutte in coda (in teoria)"
)
