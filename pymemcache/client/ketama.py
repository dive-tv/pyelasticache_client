# -*- coding: utf-8 -*-
import hashlib

def ketama(data, h=0):

    m = hashlib.md5()
    if (type(data) is str):
        m.update(data.encode('utf-8'))
    else:
        m.update(data)
    b_key = m.digest()

    if (type(b_key[0]) is int):
        rv = ((b_key[3 + h * 4] & 0xFF) << 24) | ((b_key[2 + h * 4] & 0xFF) << 16) | ((b_key[1 + h * 4] & 0xFF) << 8) | (b_key[0 + h * 4] & 0xFF)
    else:
        rv = ((ord(b_key[3 + h * 4]) & 0xFF) << 24) | ((ord(b_key[2 + h * 4]) & 0xFF) << 16) | ((ord(b_key[1 + h * 4]) & 0xFF) << 8) | (ord(b_key[0 + h * 4]) & 0xFF)
        
    return rv & 0xFFFFFFFF