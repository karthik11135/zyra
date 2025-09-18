import os
from helpers.repo.helpers import repo_file, repo_dir

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

def ref_create(repo, path, sha):
    with open(repo_file(repo, "refs", path), 'w') as f:
        f.write(sha + "\n")