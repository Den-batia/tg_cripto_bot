import decimal


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


def is_string_a_number(s):
    return s.replace('.', '', 1).isdigit()


def prettify_number(n):
    if n > 1_000_000:
        n = str(round(n/1_000_000, 2))
        prefix = 'M'
    elif n > 1_000:
        n = str(round(n/1_000, 2))
        prefix = 'K'
    else:
        n = str(n)
        prefix = ''

    if '.' in n:
        n = n.rstrip('0')
        if n[-1] == '.':
            n = n[:-1]

    return f'{n}{prefix}'


def round_down(value, decimals=8):
    with decimal.localcontext() as ctx:
        d = decimal.Decimal(value)
        ctx.rounding = decimal.ROUND_DOWN
        return round(d, decimals)
