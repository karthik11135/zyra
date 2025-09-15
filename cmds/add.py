from cmds.rm import rm
import os
from stage.indexfile import GITIndexEntry
from stage.readwrite import index_read, index_write
from helpers.objects.helpers import object_hash

def add(repo, paths, delete=True, skip_missing=False):
    if paths[0] == ".":
        all_files = list()
        gitdir_prefix = repo.gitdir + os.path.sep
        for (root, _, files) in os.walk(repo.worktree, True):
            if root==repo.gitdir or root.startswith(gitdir_prefix):
                continue
            for f in files:
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, repo.worktree)
                all_files.append(rel_path)
                
        paths = all_files

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
