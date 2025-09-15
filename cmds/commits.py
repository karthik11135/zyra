from helpers.repo.helpers import repo_file, repo_dir, repo_find
import os

def cmd_commits(args):
    repo = repo_find()
    my_dir = repo_dir(repo, "objects")
    for root, dirs, files in os.walk(my_dir):
        for filename in files:
            print(os.path.join(root, filename))
