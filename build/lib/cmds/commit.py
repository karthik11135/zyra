from helpers.repo.helpers import repo_file
from common.objects import GITObject
from common.commit.commit_obj import GITCommit
from common.tree.tree_obj import GITTree
from common.tree.tree_helper import GITTreeLeaf
from stage.indexfile import GITIndexEntry

import configparser
import os

def branch_get_active(repo):
    with open(repo_file(repo, "HEAD"), "r") as f:
        head = f.read()

    if head.startswith("ref: refs/heads/"):
        return(head[16:-1])
    else:
        return False
    
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