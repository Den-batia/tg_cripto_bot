def get_ref_code(msg):
    splited = msg.text.split()
    ref_code = None
    if len(splited) > 1:
        ref_code = splited[1]
    return ref_code


async def get_ref_link(ref_code):
    from ..settings import bot
    bot = await bot.get_me()
    return f't.me/{bot.username}?start={ref_code}'


def get_chunks(lst, n):
    res = []
    for i in range(0, len(lst), n):
        res.append(lst[i:i + n])
    return res
