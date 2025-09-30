import configparser
import os

class GITRepository(object):
    worktree = None
    conf = None
    gitdir = None

    def __init__(self, path, force=False):
        from helpers.repo.helpers import repo_file  # Lazy importing to avoid circular import conflicts
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
            raise Exception("No config path present")
        
        if not force:
            vers = int(self.conf.get("core", "repositoryformatversion"))
            if vers != 0:
                raise Exception("Version is unsupported")
