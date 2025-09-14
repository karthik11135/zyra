from argparsing import argparser
import configparser
from datetime import datetime
import grp, pwd
from fnmatch import fnmatch
import hashlib
from math import ceil
import os, re
import zlib
import sys

# helpers folder
def repo_path(repo, *path):
    """Compute path under repo's gitdir."""
    return os.path.join(repo.gitdir, *path)

def repo_file(repo, *path, mkdir=False):
    if repo_dir(repo, *path[:-1], mkdir=mkdir):
        return repo_path(repo, *path)

def repo_dir(repo, *path, mkdir=False):
    """Same as repo_path, but mkdir *path if absent if mkdir."""

    path = repo_path(repo, *path)

    if os.path.exists(path):
        if (os.path.isdir(path)):
            return path
        else:
            raise Exception(f"Not a directory {path}")

    if mkdir:
        os.makedirs(path)
        return path
    else:
        return None


class GITRepository(object):
    worktree = None
    conf = None
    gitdir = None

    def __init__(self, path, force=False):
        self.worktree = path
        self.gitdir = os.path.join(path, '.git')

        if not (force or os.path.isdir(self.gitdir)):
            raise Exception(".git doesnt exist")

        # Reading configuration file in the .git repository
        self.conf = configparser.ConfigParser()
        cf = repo_file(self, "config")

        if cf:
            self.conf.read([cf])
        elif not force:
            raise Exception("No config path")
        
        if not force:
            vers = int(self.conf.get("core", "repositoryformatversion"))
            if vers != 0:
                raise Exception("Unsupported version")


# cmd folder
def repo_create(path):
    repo = GITRepository(path, True)

    if os.path.exists(repo.worktree):
        if not os.path.isdir(repo.worktree):
            raise Exception("Path is not a directory")
        if os.path.exists(repo.gitdir):
            raise Exception(".git already exists")
    else :
        os.makedirs(repo.worktree)
    
    repo_dir(repo, "branches", mkdir=True)
    repo_dir(repo, "objects", mkdir=True)
    repo_dir(repo, "refs", "tags", mkdir=True)
    repo_dir(repo, "refs", "heads", mkdir=True)

    with open(repo_file(repo, "description"), "w") as f:
        f.write("Unnamed repository yo; edit this file to name the repo")
    
    with open(repo_file(repo, "config"), "w") as f:
        ret = configparser.ConfigParser()
        ret.add_section("core")
        ret.set("core", "repositoryformatversion", "0")
        ret.set("core", "filemode", "false")
        ret.set("core", "bare", "false")
        ret.write(f)

    with open(repo_file(repo, "HEAD"), 'w') as f:
        f.write("ref: refs/heads/master\n")

    return repo


# helpers
def repo_find(path=".", required=True):
    path = os.path.realpath(path)
    if os.path.isdir(os.path.join(path, ".git")):
        return GITRepository(path)
    
    parent = os.path.realpath(os.path.join(path, ".."))
    if parent == path:
        if required:
            raise Exception("No git directory.")
        else:
            return None
    
    return repo_find(parent, required)


# converts the commit raw string (ig its binary only) into dictionary
def kvlm_parse(raw, start=0, dct=None):
    if not dct:
        dct = dict()

    spc = raw.find(b' ', start)
    nl = raw.find(b'\n', start)

    if (spc < 0) or (nl < spc):
        assert nl == start
        dct[None] = raw[start+1:]
        return dct

    key = raw[start:spc]

    end = start
    while True:
        end = raw.find(b'\n', end+1)
        if raw[end+1] != ord(' '): break

    value = raw[spc+1:end].replace(b'\n ', b'\n')

    if key in dct:
        if type(dct[key]) == list:
            dct[key].append(value)
        else:
            dct[key] = [dct[key], value]
    else:
        dct[key]=value

    return kvlm_parse(raw, start=end+1, dct=dct)


# converts the commit dictionary into raw string
def kvlm_serialize(kvlm):
    ret = b''

    # Output fields
    for k in kvlm.keys():
        # Skip the message itself
        if k == None: continue
        val = kvlm[k]

        # Normalize to a list
        if type(val) != list:
            val = [ val ]

        print(k)
        # print(k_encode)

        for v in val:
            ret += k + b' ' + (v.replace(b'\n', b'\n ')) + b'\n'

    # Append message
    ret += b'\n' + kvlm[None]

    return ret


class GITObject(object):
    def __init__(self, data=None):
        if data != None:
            self.deserialize(data)
        else:
            self.init()

    def serialize(self, repo):
        pass

    def deserialize(self, repo):
        pass

    def init(self):
        pass


#   Takes the type object(GitBlob, GitCommit etc) and optional repo (whether to write the contents of the file in the sha path or not) and returns the sha of the content. 
    @staticmethod
    def object_write(obj, repo=None):
        # Forming metadata -> head space size content
        data = obj.serialize()
        head = obj.obj_type
        str_len = str(len(data)).encode()
        space = b' '
        zero_bin = b'\x00'

        print(data)
        print(head)
        print(str_len)
        print(space)
        print(zero_bin)

        final_str = head + space + str_len  + zero_bin + data
        
        sha = hashlib.sha1(final_str).hexdigest()

        if not repo:
            return sha

        path = repo_file(repo, "objects", sha[0:2], sha[2:], mkdir=True)

        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(zlib.compress(final_str))
        
        return sha


    # takes the sha and returns the class according to the type of object. 
    @staticmethod
    def object_read(repo, sha):
        path = repo_file(repo, "objects", sha[0:2], sha[2:])

        if not os.path.isfile(path):
            raise Exception("No object exists here")
        
        with open(path, "rb") as f:
            decomp_str = zlib.decompress(f.read())
            # b'blobsize \x00content' -> format of storage. 
            x = decomp_str.find(b' ')

            obj_type = decomp_str[0:x]
            y = decomp_str.find(b'\x00', x)

            content = decomp_str[y+1:]

            match obj_type:
                case b'commit': c=GITCommit
                case b'tree'  : c=GITTree
                case b'tag'   : c=GITTag
                case b'blob'  : c=GITBlob
                case _:
                    raise Exception("I dont know what object this is")
            
            return c(decomp_str[y+1:])

class GITTreeLeaf(object):
    def __init__(self, mode, path, sha):
        self.mode = mode
        self.path = path
        self.sha = sha


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

# helpers
def object_hash(fd, fmt, repo=None):
    """ Hash object, writing it to repo if provided."""
    data = fd.read()

    match fmt:
        case b'commit' : obj=GITCommit(data)
        case b'tree'   : obj=GITTree(data)
        case b'tag'    : obj=GITTag(data)
        case b'blob'   : obj=GITBlob(data)
        case _: raise Exception(f"Unknown type {fmt}!")

    return GITObject.object_write(obj, repo)

        
class GITBlob(GITObject):
    obj_type = b'blob'

    def serialize(self):
        return self.blobdata
    
    def deserialize(self, data):
        self.blobdata = data
    
class GITCommit(GITObject):
    obj_type = b'commit'

    def deserialize(self, data):
        self.kvlm = kvlm_parse(data)

    def serialize(self):
        return kvlm_serialize(self.kvlm)
    
    # old method
    # def __init__(self):
    #     self.kvlm = dict()

    def __init__(self, data=None):
        super().__init__(data)   # calls GITObject.__init__(data)
        if not hasattr(self, 'kvlm'):
            self.kvlm = dict()


class GITTag(GITCommit):
    obj_type = b'tag'

class GITTree(GITObject):
    obj_type = b'tree'

    def deserialize(self, data):
        self.items = tree_parse(data)
    
    def serialize(self):
        return tree_serialize(self)
    
    # old method
    # def __init__(self):
    #     self.items = list()
    
    def __init__(self, data=None):
        super().__init__(data)
        if not hasattr(self, 'items'):
            self.items = list()

# helpers
def object_resolve(repo, name):
    candidates = list()
    hashRE = re.compile(r"^[0-9A-Fa-f]{4,40}$")

    if not name.strip():
        return None

    if name == "HEAD":

        return [ ref_resolve(repo, "HEAD") ]

    if hashRE.match(name):
        name = name.lower()
        prefix = name[0:2]
        path = repo_dir(repo, "objects", prefix, mkdir=False)
        if path:
            rem = name[2:]
            for f in os.listdir(path):
                if f.startswith(rem):
                    candidates.append(prefix + f)


    as_tag = ref_resolve(repo, "refs/tags/" + name)
    if as_tag: 
        candidates.append(as_tag)

    as_branch = ref_resolve(repo, "refs/heads/" + name)
    if as_branch:
        candidates.append(as_branch)

    as_remote_branch = ref_resolve(repo, "refs/remotes/" + name)
    if as_remote_branch:
        candidates.append(as_remote_branch)

    return candidates

# helpers
def object_find(repo, name, obj_type=None, follow=True):
    sha = object_resolve(repo, name)

    if not sha:
        raise Exception(f"No such reference {name}.")

    if len(sha) > 1:
        raise Exception("Ambiguous reference {name}: Candidates are:\n - {'\n - '.join(sha)}.")
    

    sha = sha[0]

    if not sha:
        return None

    if not obj_type:
        return sha
    
    while True:
        obj = GITObject.object_read(repo, sha)


        if obj.obj_type == obj_type:
            return sha
        
        if not follow:
            return None
        
        if obj.obj_type == b'tag':
            sha = obj.kvlm[b'object'].decode("ascii")
        elif obj.obj_type == b'commit' and obj_type == b'tree':
            sha = obj.kvlm[b'tree'].decode("ascii")
        else:
            return None


# common
def cmd_cat_file(args):
    t = args.type
    repo = repo_find()
    obj = GITObject.object_read(repo, object_find(repo, args.sha, obj_type=t.encode()))
    sys.stdout.buffer.write(obj.serialize())


# common
def cmd_hash_obj(args):
    t = args.type.encode()
    write = args.write
    path = args.path

    if write :
        repo = repo_find()
    else:
        repo = None

    with(path, "rb") as f:
        data = f.read()
        
        match t:
            case b'blob': obj = GITBlob(data)
            case b'commit': obj = GITCommit(data)
            case b'tag': obj = GITTag(data)
            case b'tree': obj = GITTree(data)
            case _: raise Exception("Unknown type provided!")
        
        sha = GITObject.object_write(obj, repo)
            
# separate file
def cmd_log(args):
    repo = repo_find()

    print("Here are your diagraphiz logs")

    log_graphiz(repo, object_find(repo, args.commit), set())

    print("Logs ended here")


def log_graphiz(repo, sha, seen):
    if sha in seen:
        return
    seen.add(sha)

    commitObj = GITObject.object_read(repo, sha)
    message = commitObj.kvlm[None].decode("utf8").strip()
    message = message.replace("\\", "\\\\")
    message = message.replace("\"", "\\\"")

    if "\n" in message: 
        message = message[:message.index("\n")]

    print(f"id: {sha[0:7]} | message: {message}")

    if not b'parent' in commitObj.kvlm:
        return

    parents = commitObj.kvlm[b'parent']

    if type(parents) != list:
        parents = [parents]

    for p in parents:
        p = p.decode("ascii")
        log_graphiz(repo, p, seen)

def tree_checkout(repo, tree, path):
    for item in tree.items:
        obj = GITObject.object_read(repo, item.sha)
        dest = os.path.join(path, item.path)

        if obj.obj_type == b'tree':
            os.makedirs(dest)
            tree_checkout(repo, obj, dest)
        elif obj.obj_type == b'blob':
            with open(dest, "wb") as f:
                f.write(obj.blobdata)

def ref_resolve(repo, ref):

    path = repo_file(repo, ref)
    if not os.path.isfile(path):
        return None
    
    with open(path, "r") as f:
        data = f.read()[:-1]

    if data.startswith("ref: "):
        return ref_resolve(repo, data[5:])
    else:
        return data
    
def ref_list(repo, path=None):
    if not path:
        path = repo_dir(repo, "refs")

    ret = dict()

    for f in sorted(os.listdir(path)):
        can = os.path.join(path, f)

        if os.path.isdir(can):
            ret[f] = ref_list(repo, can)
        else :
            ret[f] = ref_resolve(repo, can)

    return ret

def show_ref(repo, refs, with_hash=True, prefix=""):
    if prefix:
        prefix = prefix + '/'
    for k, v in refs.items():
        if type(v) == str and with_hash:
            print (f"{v} {prefix}{k}")
        elif type(v) == str:
            print (f"{prefix}{k}")
        else:
            show_ref(repo, v, with_hash=with_hash, prefix=f"{prefix}{k}")

# goes with cmd
def branch_get_active(repo):
    with open(repo_file(repo, "HEAD"), "r") as f:
        head = f.read()

    if head.startswith("ref: refs/heads/"):
        return(head[16:-1])
    else:
        return False


def ref_create(repo, path, sha):
    with open(repo_file(repo, "/refs" + path), 'w') as f:
        f.write(sha + "\n")

def tag_create(repo, name, ref, create_tag_object=False):
    sha = object_find(repo, ref)

    if create_tag_object:
        tag = GITTag()
        tag.kvlm = dict()
        tag.kvlm[b'object'] = sha.encode()
        tag.kvlm[b'type'] = b'commit'
        tag.kvlm[b'tag'] = name.encode()
        tag.kvlm[b'tagger'] = b'Wyag <wyag@example.com>'
        tag.kvlm[None] = b"A tag generated by wyag, which won't let you customize the message!\n"
        tag_sha = GITObject.object_write(tag, repo)
        ref_create(repo, "tags/" + name, tag_sha)
    else:
        ref_create(repo, "/tags"+name, sha)


# Index file : header(DIRC + format version number + number of entries) and entries
class GITIndexEntry(object):
    def __init__(self, ctime=None, mtime=None, dev=None, ino=None,
                 mode_type=None, mode_perms=None, uid=None, gid=None,
                 fsize=None, sha=None, flag_assume_valid=None,
                 flag_stage=None, name=None):
        
        self.ctime = ctime
        self.mtime = mtime
        self.dev = dev
        self.ino = ino
        self.mode_type = mode_type
        self.mode_perms = mode_perms
        self.uid = uid
        self.gid = gid
        self.fsize = fsize
        self.sha = sha
        self.flag_assume_valid = flag_assume_valid
        self.flag_stage = flag_stage
        self.name = name

class GITIndex(object):
    entries = []
    version = None

    def __init__(self, version=2, entries=None):
        if not entries:
            entries = list()
        self.version = version
        self.entries = entries

def index_write(repo, index):
        with open(repo_file(repo, "index"), "wb") as f:
            f.write(b"DIRC")
            f.write(index.version.to_bytes(4, "big"))
            f.write(len(index.entries).to_bytes(4, "big"))

            idx = 0
            for e in index.entries:
                f.write(e.ctime[0].to_bytes(4, "big"))
                f.write(e.ctime[1].to_bytes(4, "big"))
                f.write(e.mtime[0].to_bytes(4, "big"))
                f.write(e.mtime[1].to_bytes(4, "big"))
                f.write(e.dev.to_bytes(4, "big"))
                f.write(e.ino.to_bytes(4, "big"))

                mode = (e.mode_type << 12) | e.mode_perms
                f.write(mode.to_bytes(4, "big"))
                f.write(e.uid.to_bytes(4, "big"))
                f.write(e.gid.to_bytes(4, "big"))

                f.write(e.fsize.to_bytes(4, "big"))
                f.write(int(e.sha, 16).to_bytes(20, "big"))
                flag_assume_valid = 0x1 << 15 if e.flag_assume_valid else 0
                name_bytes = e.name.encode("utf8")
                bytes_len = len(name_bytes)
                if bytes_len >= 0xFFF:
                    name_length = 0xFFF
                else:
                    name_length = bytes_len

                f.write((flag_assume_valid | e.flag_stage | name_length).to_bytes(2, "big"))

                f.write(name_bytes)
                f.write((0).to_bytes(1, "big"))

                idx += 62 + len(name_bytes) + 1
                if idx % 8 != 0:
                    pad = 8 - (idx % 8)
                    f.write((0).to_bytes(pad, "big"))
                    idx += pad

def index_read(repo):
    index_file = repo_file(repo, "index")

    # New repositories have no index!
    if not os.path.exists(index_file):
        return GITIndex()

    with open(index_file, 'rb') as f:
        raw = f.read()

    header = raw[:12]
    signature = header[:4]
    assert signature == b"DIRC" # Stands for "DirCache"
    version = int.from_bytes(header[4:8], "big")
    assert version == 2, "wyag only supports index file version 2"
    count = int.from_bytes(header[8:12], "big")

    entries = list()

    content = raw[12:]
    idx = 0
    for i in range(0, count):
        # Read creation time, as a unix timestamp (seconds since
        # 1970-01-01 00:00:00, the "epoch")
        ctime_s =  int.from_bytes(content[idx: idx+4], "big")
        # Read creation time, as nanoseconds after that timestamps,
        # for extra precision.
        ctime_ns = int.from_bytes(content[idx+4: idx+8], "big")
        # Same for modification time: first seconds from epoch.
        mtime_s = int.from_bytes(content[idx+8: idx+12], "big")
        # Then extra nanoseconds
        mtime_ns = int.from_bytes(content[idx+12: idx+16], "big")
        # Device ID
        dev = int.from_bytes(content[idx+16: idx+20], "big")
        # Inode
        ino = int.from_bytes(content[idx+20: idx+24], "big")
        # Ignored.
        unused = int.from_bytes(content[idx+24: idx+26], "big")
        assert 0 == unused
        mode = int.from_bytes(content[idx+26: idx+28], "big")
        mode_type = mode >> 12
        assert mode_type in [0b1000, 0b1010, 0b1110]
        mode_perms = mode & 0b0000000111111111
        # User ID
        uid = int.from_bytes(content[idx+28: idx+32], "big")
        # Group ID
        gid = int.from_bytes(content[idx+32: idx+36], "big")
        # Size
        fsize = int.from_bytes(content[idx+36: idx+40], "big")
        # SHA (object ID).  We'll store it as a lowercase hex string
        # for consistency.
        sha = format(int.from_bytes(content[idx+40: idx+60], "big"), "040x")
        # Flags we're going to ignore
        flags = int.from_bytes(content[idx+60: idx+62], "big")
        # Parse flags
        flag_assume_valid = (flags & 0b1000000000000000) != 0
        flag_extended = (flags & 0b0100000000000000) != 0
        assert not flag_extended
        flag_stage =  flags & 0b0011000000000000
        # Length of the name.  This is stored on 12 bits, some max
        # value is 0xFFF, 4095.  Since names can occasionally go
        # beyond that length, git treats 0xFFF as meaning at least
        # 0xFFF, and looks for the final 0x00 to find the end of the
        # name --- at a small, and probably very rare, performance
        # cost.
        name_length = flags & 0b0000111111111111

        # We've read 62 bytes so far.
        idx += 62

        if name_length < 0xFFF:
            assert content[idx + name_length] == 0x00
            raw_name = content[idx:idx+name_length]
            idx += name_length + 1
        else:
            print(f"Notice: Name is 0x{name_length:X} bytes long.")
            # This probably wasn't tested enough.  It works with a
            # path of exactly 0xFFF bytes.  Any extra bytes broke
            # something between git, my shell and my filesystem.
            null_idx = content.find(b'\x00', idx + 0xFFF)
            raw_name = content[idx: null_idx]
            idx = null_idx + 1

        # Just parse the name as utf8.
        name = raw_name.decode("utf8")

        # Data is padded on multiples of eight bytes for pointer
        # alignment, so we skip as many bytes as we need for the next
        # read to start at the right position.

        idx = 8 * ceil(idx / 8)

        # And we add this entry to our list.
        entries.append(GITIndexEntry(ctime=(ctime_s, ctime_ns),
                                     mtime=(mtime_s,  mtime_ns),
                                     dev=dev,
                                     ino=ino,
                                     mode_type=mode_type,
                                     mode_perms=mode_perms,
                                     uid=uid,
                                     gid=gid,
                                     fsize=fsize,
                                     sha=sha,
                                     flag_assume_valid=flag_assume_valid,
                                     flag_stage=flag_stage,
                                     name=name))

    return GITIndex(version=version, entries=entries)

def tree_to_dict(repo, ref, prefix=""):
    ret = dict()
    tree_sha = object_find(repo, ref, obj_type=b"tree")

    if not tree_sha:
        return ret

    tree = GITObject.object_read(repo, tree_sha)

    for leaf in tree.items:
        full_path = os.path.join(prefix, leaf.path)
        is_subtree = leaf.mode.startswith(b'04')
        if is_subtree:
            ret.update(tree_to_dict(repo, leaf.sha, full_path))
        else:
            ret[full_path] = leaf.sha
    return ret

# separate file
def rm(repo, paths, delete=True, skip_missing=False):
    index = index_read(repo)

    worktree = repo.worktree + os.sep

    abspaths = set()

    for path in paths:
        abspath = os.path.abspath(path)
        if abspath.startswith(worktree):
            abspaths.add(abspath)
        else:
            raise Exception(f"Cannot remove paths outside of worktree: {paths}")

    kept_entries = list()
    remove = list()

    for e in index.entries:
        full_path = os.path.join(repo.worktree, e.name)

        if full_path in abspaths:
            remove.append(full_path)
            abspaths.remove(full_path)
        else:
            kept_entries.append(e) 

    if len(abspaths) > 0 and not skip_missing:
        raise Exception(f"Cannot remove paths not in the index: {abspaths}")

    if delete:
        for path in remove:
            os.unlink(path)

    index.entries = kept_entries
    index_write(repo, index)

# separate file
def add(repo, paths, delete=True, skip_missing=False):
    rm(repo, paths, delete=False, skip_missing=True)
    worktree = repo.worktree + os.sep

    cleanpaths = set()
    for path in paths:
        p = os.path.abspath(path)
        relpath = os.path.relpath(p, repo.worktree)
        if not (p.startswith(worktree) and os.path.isfile(p)):
            raise Exception(f"Not a file, or outside the worktree: {paths}")

        cleanpaths.add((p, relpath))

    index = index_read(repo)



    for (abspath, relpath) in cleanpaths:
        with open(abspath, "rb") as f:
            sha = object_hash(f, b"blob", repo)
            stat = os.stat(abspath)
            ctime_s = int(stat.st_ctime)
            ctime_ns = stat.st_ctime_ns % 10**9
            mtime_s = int(stat.st_mtime)
            mtime_ns = stat.st_mtime_ns % 10**9

            entry = GITIndexEntry(ctime=(ctime_s, ctime_ns), mtime=(mtime_s, mtime_ns), dev=stat.st_dev, ino=stat.st_ino,
                                  mode_type=0b1000, mode_perms=0o644, uid=stat.st_uid, gid=stat.st_gid,
                                  fsize=stat.st_size, sha=sha, flag_assume_valid=False,
                                  flag_stage=False, name=relpath)
            index.entries.append(entry)

    index_write(repo, index)


def gitconfig_user_get(config):
    if "user" in config:
        if "name" in config["user"] and "email" in config["user"]:
            return f"{config['user']['name']} <{config['user']['email']}>"
    return None

def gitconfig_read():
    xdg_config_home = os.environ["XDG_CONFIG_HOME"] if "XDG_CONFIG_HOME" in os.environ else "~/.config"
    configfiles = [
        os.path.expanduser(os.path.join(xdg_config_home, "git/config")),
        os.path.expanduser("~/.gitconfig")
    ]

    config = configparser.ConfigParser()
    config.read(configfiles)
    return config

def tree_from_index(repo, index):
    contents = dict()
    contents[""] = list()

    for entry in index.entries:
        dirname = os.path.dirname(entry.name)
        key = dirname 
        while key != "":
            if not key in contents:
                contents[key] = list()
            key = os.path.dirname(key)
        contents[dirname].append(entry)      

    sorted_paths = sorted(contents.keys(), key=len, reverse=True)  
    sha = None

    for path in sorted_paths:
        tree = GITTree()
        for entry in contents[path]:
            if isinstance(entry, GITIndexEntry):
                leaf_mode = f"{entry.mode_type:02o}{entry.mode_perms:04o}".encode("ascii")
                leaf = GITTreeLeaf(mode = leaf_mode, path=os.path.basename(entry.name), sha=entry.sha)
            else: 
                leaf = GITTreeLeaf(mode = b"040000", path=entry[0], sha=entry[1])
            tree.items.append(leaf)
        sha = GITObject.object_write(tree, repo)

        parent = os.path.dirname(path)
        base = os.path.basename(path) 
        contents[parent].append((base, sha))
    
    return sha

# separate file
def commit_create(repo, tree, parent, author, timestamp, message):
    commit = GITCommit()

    commit.kvlm[b"tree"] = tree.encode("ascii")
    if parent:
        commit.kvlm[b"parent"] = parent.encode("ascii")

    message = message.strip() + "\n"
    offset = int(timestamp.astimezone().utcoffset().total_seconds())
    hours = offset // 3600
    minutes = (offset % 3600) // 60
    tz = "{}{:02}{:02}".format("+" if offset > 0 else "-", hours, minutes)

    author = author + timestamp.strftime(" %s ") + tz
    commit.kvlm[b"author"] = author.encode("utf8")
    commit.kvlm[b"committer"] = author.encode("utf8")
    commit.kvlm[None] = message.encode("utf8")

    return GITObject.object_write(commit, repo)

# separate file
def cmd_status_branch(repo):
    with open(repo_file(repo, "HEAD"), "r") as f:
        head = f.read()
    
    if head.startswith("ref: refs/heads/"):
        print("On branch ", head[16:-1])
        print()
    else:
        print(f"Currently in detached mode : {object_find(repo, "HEAD")}")

def cmd_status_head_index(repo, index):
    # staging area is index
    print("Changes staged for commit")
    head = tree_to_dict(repo, "HEAD")
    for entry in index.entries:
        if entry.name in head:
            if head[entry.name] != entry.sha:
                print("modified: ", entry.name)
            del head[entry.name]
        else:
            print("added: ", entry.name)

    for entry in head.keys():
        print("deleted: ", entry)

    print()

def cmd_status_index_worktree(repo, index):
    print("Changes not staged for commit:")

    gitdir_prefix = repo.gitdir + os.path.sep

    all_files = list()

    for (root, _, files) in os.walk(repo.worktree, True):
        if root==repo.gitdir or root.startswith(gitdir_prefix):
            continue
        for f in files:
            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, repo.worktree)
            all_files.append(rel_path)

    for entry in index.entries:
        full_path = os.path.join(repo.worktree, entry.name)
        if not os.path.exists(full_path):
            print("  deleted: ", entry.name)
        else:
            stat = os.stat(full_path)

            ctime_ns = entry.ctime[0] * 10**9 + entry.ctime[1]
            mtime_ns = entry.mtime[0] * 10**9 + entry.mtime[1]
            if (stat.st_ctime_ns != ctime_ns) or (stat.st_mtime_ns != mtime_ns):
                with open(full_path, "rb") as fd:
                    new_sha = object_hash(fd, b"blob", None)
                    same = entry.sha == new_sha
                    if not same:
                        print(" modified:", entry.name)

        if entry.name in all_files:
            all_files.remove(entry.name)

    print()
    print("Untracked files:")

    for f in all_files:
        print(" ", f)

def cmd_status(args):
    repo = repo_find()
    index = index_read(repo)

    cmd_status_branch(repo)
    cmd_status_head_index(repo, index)
    cmd_status_index_worktree(repo, index)

def cmd_init(args):
    repo_create(args.path)

def cmd_show_ref(args):
    repo = repo_find()
    ref_dict = ref_list(repo)
    show_ref(repo, ref_dict, prefix="refs")

def cmd_tag(args):
    repo = repo_find()

    if args.name:
        tag_create(repo, args.name, args.object, create_tag_object=args.create_tag_object)
    else:
        ref_dict = ref_list(repo)
        show_ref(repo, ref_dict, prefix="refs")

def cmd_rev_parse(args):
    if args.type:
        obj_type = args.type.encode()
    else:
        obj_type = None

    repo = repo_find()

    print(object_find(repo, obj_type))

def cmd_rm(args):
    repo = repo_find()
    rm(repo, args.path)

def cmd_add(args):
    repo = repo_find()
    add(repo, args.path)

def cmd_commit(args):
    repo = repo_find()
    index = index_read(repo)
    tree = tree_from_index(repo, index)
    commit = commit_create(repo, tree, object_find(repo, "HEAD"), gitconfig_user_get(gitconfig_read()), datetime.now(), args.message)

    active_branch = branch_get_active(repo)
    if active_branch:
        with open(repo_file(repo, os.path.join("refs/heads/"), active_branch), "w") as f:
            f.write(commit + "\n")
    else:
        with open(repo_file(repo, "HEAD"), "w") as f:
            f.write("\n")

def main(argvs=sys.argv[1:]):
    args = argparser.parse_args(argvs)

    print("hey there from wyag!! \n")

    match args.command:
        case "add" : cmd_add(args)
        case "checkout" : cmd_checkout(args)
        case "init": cmd_init(args)
        case "cat-file": cmd_cat_file(args)
        case "hash-object": cmd_hash_obj(args)
        case "log": cmd_log(args)
        case "show-ref": cmd_show_ref(args)
        case "tag": cmd_tag(args)
        case "rev-parse": cmd_rev_parse(args)
        case "status": cmd_status(args)
        case "rm": cmd_rm(args)
        case "commit": cmd_commit(args)

def cmd_checkout(args):
    repo = repo_find()
    sha = args.commit
    path = args.path

    obj = GITObject.object_read(repo, object_find(repo, sha))


    if obj.obj_type == b'commit':
        obj = GITObject.object_read(repo, obj.kvlm[b'tree'].decode("ascii"))

    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception("The provided path is not a directory")
        if os.listdir(path):
            raise Exception("The given path already contains something")
    else:
        os.makedirs(path)

    tree_checkout(repo, obj, os.path.realpath(path))
