class GITTreeLeaf(object):
    def __init__(self, mode, path, sha):
        self.mode = mode
        self.path = path
        self.sha = sha

def tree_parse(raw):
    pos = 0
    total = len(raw)
    ret = []
    while pos < total:
        pos, data = tree_parse_one(raw, pos)
        ret.append(data)
    return ret

def tree_leaf_sort_key(leaf):
    if leaf.mode.startswith(b"10"):
        return leaf.path
    else:
        return leaf.path + "/"

def tree_serialize(obj):
    obj.items.sort(key=tree_leaf_sort_key)

    ret = b""

    for o in obj.items:
        ret += o.mode
        ret += b" "
        ret += o.path.encode("utf8")
        ret += b"\x00"
        sha = int(o.sha, 16)
        ret += sha.to_bytes(20, byteorder="big")
    
    return ret

def tree_parse_one(raw, start = 0):
    x = raw.find(b' ', start)
    assert x-start == 5 or x-start == 6
    mode = raw[start:x]

    if len(mode) == 5:
        mode += b"0"

    y = raw.find(b'\x00', x)
    path = raw[x+1: y]

    raw_sha = int.from_bytes(raw[y+1: y+21], "big")
    sha = format(raw_sha, "040x")
    return y + 21, GITTreeLeaf(mode, path.decode("utf8"), sha)
