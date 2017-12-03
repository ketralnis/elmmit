from threading import RLock
import base64
import uuid


def to_base(q, alphabet):
    if q < 0:
        raise ValueError("must supply a positive integer")
    l = len(alphabet)
    converted = []
    while q != 0:
        q, r = divmod(q, l)
        converted.insert(0, alphabet[r])
    return "".join(converted) or '0'


def to36(q):
    return to_base(q, "0123456789abcdefghijklmnopqrstuvwxyz")


def uuid4_36():
    return to36(uuid.uuid4().int)


def enbase64(s):
    return base64.urlsafe_b64encode(s).rstrip('=')


def debase64(s):
    # add in any missing padding
    s += '=' * (4 - len(s) % 4)
    return base64.urlsafe_b64decode(s.encode('ascii'))


class LockBox(object):
    "Simple abstraction for mutable value locked by a recursive Lock"

    def __init__(self, value):
        self.lock = RLock()
        self.box = value

    def __enter__(self):
        self.lock.__enter__()
        return self.box

    def __exit__(self, *a):
        self.lock.__exit__(*a)

