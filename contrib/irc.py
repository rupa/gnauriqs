import re

spaces = re.compile(r'\s\s+', re.U)
mask = re.compile(r'^:?(?P<nick>[^!]+)!(?P<user>[^@]+)@(?P<host>.+)$')

def cram(s, width=420):
    '''
    Get rid of whitespace, and also make sure things don't get truncated.
    '''
    i, s = 0, spaces.sub(' ', s).replace('\n', ' ')
    while i < len(s):
        yield s[i:i + width]
        i += width

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
        'channel': None,

        'src': None,
        'to': None,
        'msg': None,

        'private': None,
        'admin': None,
    }
    if msg[0].startswith(':'):
        parsed['prefix'], msg = msg[0][1:], msg[1:]
        # this sets nick, host, and user
        parsed.update(parsemask(parsed['prefix']))
        parsed['admin'] = True if parsed['nick'] in data['admins'] else False
    parsed['cmd'], msg = msg[0], msg[1:]
    if parsed['cmd'] == 'MODE':
        parsed['to'], msg = msg[0], u' '.join(msg[1:])
    elif parsed['cmd'] == 'JOIN':
        parsed['to'], msg = msg[0][1:], None
        parsed['channel'] = parsed['to']
    elif parsed['cmd'] == 'PART':
        parsed['to'], msg = msg[0], None
        parsed['channel'] = parsed['to']
    elif parsed['cmd'] == 'KICK':
        #17 :mataglap!~lindsay@cloak-19AE7D2B.io KICK #idiots-club gnauriqs :mataglap
        parsed.update({
            'channel': msg[0],
            'to': msg[1],
            'src': msg[2][1:],
        })
    elif parsed['cmd'] in ('PRIVMSG', 'NOTICE'):
        parsed['to'], msg = msg[0], u' '.join(msg[1:])[1:].strip()
        parsed['private'] = True if parsed['to'] == data['nick'] else False
        parsed['src'] = parsed['nick'] if parsed['private'] else parsed['to']
    else:
        msg = u' '.join(msg)
    parsed['msg'] = msg
    data['parsed'] = parsed
    return data
