import re

mask = re.compile(r'^:?(?P<nick>[^!]+)!(?P<user>[^@]+)@(?P<host>.+)$')

def parsemask(hostmask):
    ''' [:]nick!user@host '''
    res = mask.search(hostmask)
    if res is None:
        return {u'nick': None, u'host': None, u'user': None}
    return res.groupdict()

def parseirc(data):
    ''' parse all the things '''
    msg = data['raw'].split(u' ')
    parsed = {
        'prefix': None,   # always a hostmask?
        'nick': None,
        'user': None,
        'host': None,
        'cmd': None,
        'src': None,
        'to': None,
        'msg': None,
        'private': None,
        'admin': None,
    }
    if msg[0].startswith(':'):
        parsed['prefix'], msg = msg[0][1:], msg[1:]
        parsed.update(parsemask(parsed['prefix']))
        parsed['admin'] = True if parsed['nick'] in data['admins'] else False
    parsed['cmd'], msg = msg[0], msg[1:]
    if parsed['cmd'] == 'MODE':
        parsed['to'], msg = msg[0], u' '.join(msg[1:])
    elif parsed['cmd'] == 'JOIN':
        parsed['to'], msg = msg[0][1:], None
    elif parsed['cmd'] == 'PART':
        parsed['to'], msg = msg[0], None
    elif parsed['cmd'] in ('PRIVMSG', 'NOTICE'):
        parsed['to'], msg = msg[0], u' '.join(msg[1:])[1:].strip()
        parsed['private'] = True if parsed['to'] == data['nick'] else False
        parsed['src'] = parsed['nick'] if parsed['private'] else parsed['to']
    else:
        msg = u' '.join(msg)
    parsed['msg'] = msg
    data['parsed'] = parsed
    return data
