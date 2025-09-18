import re
import os
from common.blob.blob_obj import GITBlob
from common.tag.tag_obj import GITTag
from common.tree.tree_obj import GITTree
from common.commit.commit_obj import GITCommit
from common.objects import GITObject
from helpers.repo.helpers import repo_dir
from helpers.refs.helpers import ref_resolve


def object_hash(fd, fmt, repo=None):
    data = fd.read()

    match fmt:
        case b'commit' : obj=GITCommit(data)
        case b'tree'   : obj=GITTree(data)
        case b'tag'    : obj=GITTag(data)
        case b'blob'   : obj=GITBlob(data)
        case _: raise Exception(f"Unknown type {fmt}!")

    return GITObject.object_write(obj, repo)

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


def object_find(repo, name, obj_type=None, follow=True):
    sha = object_resolve(repo, name)

    if not sha:
        raise Exception(f"No such reference {name}.")

    if len(sha) > 1:
        raise Exception("That's weird")
    

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
