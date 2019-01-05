import hashlib

def genMD5(str):
    return hashlib.md5(str.encode('utf8')).hexdigest()