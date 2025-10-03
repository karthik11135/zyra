from helpers.repo.helpers import repo_find, repo_create, repo_store_branch
from cmds.add import add
from common.blob.blob_obj import GITBlob
from common.tag.tag_obj import GITTag
from common.tree.tree_obj import GITTree
from common.commit.commit_obj import GITCommit
from common.objects import GITObject
from helpers.objects.helpers import *
from cmds.checkout import tree_checkout
from helpers.refs.helpers import *
from cmds.log import log_graphiz
from cmds.tag import tag_create
from cmds.add import add
from cmds.rm import rm
from cmds.commit import *
from cmds.checkout import *
from stage.readwrite import index_read
from cmds.status import *
from termcolor import cprint

import sys
from datetime import datetime


def cmd_add(args):
    repo = repo_find()
    add(repo, args.path)


def cmd_checkout(args):
    repo = repo_find()
    sha = args.commit
    path = args.path

    if path == ".":
        cprint(
            "You cannot provide the current directory for checkout\nIf you want to go to an other branch use 'switch' command",
            "red",
        )
        return
    obj = GITObject.object_read(repo, object_find(repo, sha))
    if obj.obj_type == b"commit":
        obj = GITObject.object_read(repo, obj.kvlm[b"tree"].decode("ascii"))

    if os.path.exists(path):
        if not os.path.isdir(path):
            raise Exception("The provided path is not a directory")
        if os.listdir(path):
            pass
            # raise Exception("The given path already contains something")
    else:
        os.makedirs(path)

    print(obj)
    tree_checkout(repo, obj, os.path.realpath(path))


def cmd_init(args):
    if repo_create("."):
        repo_store_branch("master")
        cprint("zyra repository is succesfully initialised", "light_blue")



def cmd_cat_file(args):
    repo = repo_find()
    t = args.type
    obj_type = t.encode() if t else None
    obj = GITObject.object_read(repo, object_find(repo, args.sha, obj_type=obj_type))
    print(obj.obj_type)
    sys.stdout.buffer.write(obj.serialize())


def cmd_hash_obj(args):
    write = args.write
    path = args.path
    if write:
        repo = repo_find()
    else:
        repo = None

    with open(path, "rb") as f:
        data = f.read()
        obj = GITBlob(data)
        sha = GITObject.object_write(obj, repo)
        print(sha)


def cmd_log(args):
    repo = repo_find()

    print("Here are your diagraphiz logs")
    try:
        log_graphiz(repo, object_find(repo, args.commit), set())
        print("Logs ended here")
    except:
        cprint("You are supposed to provide the sha of a commit object only", "red")


def cmd_show_ref(args):
    repo = repo_find()
    ref_dict = ref_list(repo)
    print(ref_dict)
    show_ref(repo, ref_dict, prefix="refs")


def cmd_tag(args):
    repo = repo_find()

    if args.name:
        tag_create(
            repo, args.name, args.object, create_tag_object=args.create_tag_object
        )
    else:
        ref_dict = ref_list(repo)
        show_ref(repo, ref_dict, prefix="refs")


def cmd_rev_parse(args):
    if args.type:
        obj_type = args.type.encode()
    else:
        obj_type = None

    repo = repo_find()

    print(object_find(repo, args.name, obj_type=obj_type, follow=True))


def cmd_rm(args):
    repo = repo_find()
    nd = args.nd
    if nd:
        delete = False
    else:
        delete = True
    rm(repo, args.path, delete=delete)


def cmd_commit(args):
    repo = repo_find()
    index = index_read(repo)
    tree = tree_from_index(repo, index)
    commit = commit_create(
        repo,
        tree,
        object_find(repo, "HEAD"),
        gitconfig_user_get(gitconfig_read()),
        datetime.now(),
        args.message,
    )

    active_branch = branch_get_active(repo)
    if active_branch:
        with open(
            repo_file(repo, os.path.join("refs/heads/"), active_branch), "w"
        ) as f:
            f.write(commit + "\n")
    else:
        with open(repo_file(repo, "HEAD"), "w") as f:
            f.write("\n")


def cmd_status(args):
    repo = repo_find()
    index = index_read(repo)

    cmd_status_branch(repo)
    cmd_status_head_index(repo, index)
    cmd_status_index_worktree(repo, index)


def cmd_commits(args):
    repo = repo_find()
    my_dir = repo_dir(repo, "objects")
    my_shas = list()
    obj_dirs = list()
    i = 0
    for root, dirs, files in os.walk(my_dir):
        if dirs:
            obj_dirs = dirs
        if files:
            my_shas.append(obj_dirs[i] + files[0])
            i += 1

    for p in my_shas:
        obj = GITObject.object_read(repo, p)
        if obj.obj_type == b"commit":
            print(f"{p}: {obj.kvlm[None][:-1].decode()}")


def cmd_branch(args):
    repo = repo_find()
    head_file = repo_file(repo, "HEAD")
    print("branches:")
    with open(head_file, "r") as f:
        data = f.read()

    if data.startswith("ref:"):
        my_branch = data[16:-1]
        cprint(f" * {my_branch.strip()}", "green")
    else:
        my_branch = data[:-1]
        cprint(f" detached state: * {my_branch.strip()}", "green")

    branches_path = repo_dir(repo, "branches")
    for bs in os.listdir(branches_path):

        if bs == my_branch.strip():
            continue
        print("   " + bs)


def cmd_switch(args):
    branch_name = args.branch
    repo = repo_find()
    path = "."

    print(branch_name, path)

    branch_exists = False
    for filename in os.listdir(repo_dir(repo, "refs", "heads")):
        if filename == branch_name.strip():
            branch_exists = True
            break

    if not branch_exists:
        for filename in os.listdir(repo_file(repo, "branches")):
            if filename == branch_name.strip():
                branch_exists = True
                break

        if branch_exists:
            with open(repo_file(repo, "HEAD"), "w") as f:
                f.write(f"ref: refs/heads/{branch_name}\n")

            return
        

    if not branch_exists:
        cprint("First create a branch using the 'create-branch' command", "red")
        return

    branch_name = branch_name.strip()

    obj = GITObject.object_read(repo, object_find(repo, branch_name))
    if obj.obj_type == b"commit":
        obj = GITObject.object_read(repo, obj.kvlm[b"tree"].decode("ascii"))

    tree_checkout(repo, obj, os.path.realpath(path))

    with open(repo_file(repo, "HEAD"), "w") as f:
        f.write(f"ref: refs/heads/{branch_name}\n")


def cmd_create_branch(args):
    newbranch = args.branch
    repo = repo_find()
    with open(repo_file(repo, "HEAD"), "w") as f:
        f.write(f"ref: refs/heads/{newbranch}\n")
        cprint(f"Created a new branch {newbranch}", "green")

    repo_store_branch(newbranch)

def cmd_bcommits(args):
    repo = repo_find()
    with open(repo_file(repo, "HEAD"), "r") as f:
        branch = f.read()[16:-1]

    branches_folder = repo_dir(repo, "refs", "heads")
    branch_has_commit = False
    for filename in os.listdir(branches_folder):
        if branch == filename:
            branch_has_commit = True

    if not branch_has_commit:
        cprint("Your current branch does not have any commits")
        return

    with open(repo_file(repo, "refs", "heads", branch), "r") as f:
        sha = f.read()[:-1]

    obj = GITObject.object_read(repo, sha)
    cprint(f"{obj.kvlm[None].decode()[:-1]}: {sha}", "yellow")
    while b"parent" in obj.kvlm:
        parent_sha = obj.kvlm[b"parent"].decode()
        obj = GITObject.object_read(repo, parent_sha)
        cprint(f"{obj.kvlm[None].decode()[:-1]}: {parent_sha}", "yellow")
        
    print()
    cprint("Those were your commits in this branch", "cyan")