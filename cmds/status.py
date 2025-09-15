import os
from helpers.repo.helpers import repo_file
from helpers.objects.helpers import object_hash, object_find
from helpers.objects.helpers import tree_to_dict
from termcolor import cprint

def cmd_status_branch(repo):
    with open(repo_file(repo, "HEAD"), "r") as f:
        head = f.read()
    
    if head.startswith("ref: refs/heads/"):
        cprint(f"On branch {head[16:-1]}", "blue")
        print()
    else:
        print(f"Currently in detached mode : {object_find(repo, "HEAD")}")

def cmd_status_head_index(repo, index):
    # staging area is index
    cprint("Changes staged for commit:", "blue")
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
    cprint("Changes not staged for commit:", "blue")

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
    cprint("Untracked files:", "blue")

    for f in all_files:
        print(" ", f)
