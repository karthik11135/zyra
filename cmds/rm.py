import os
from stage.readwrite import index_read, index_write

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
