import argparse

argparser = argparse.ArgumentParser(description="The Git Learning Parser")
argsubparser = argparser.add_subparsers(dest="command", title="Commands")
argsubparser.required = True

# Initializes an empty git repository
init_parser = argsubparser.add_parser("init")
init_parser.add_argument("path")


# Prints out the content inside that hash file (sha file -> .git/objects/2a/as5272fs82dg)
# The internal function that calls this returns object that is type of the sha. (blob, commit etc). So when .serialize() it'll print.
catfile_parser = argsubparser.add_parser("cat-file")
catfile_parser.add_argument(
    "--obj-type", metavar="type", dest="type", choices=["blob", "commit", "tag", "tree"]
)
catfile_parser.add_argument("sha")


# Given a file it'll make it binary string in a proper format, compresses it stores in the sha path of that binary format (given -w option). It prints the sha hash object.
hashobject_parser = argsubparser.add_parser("hash-object")
hashobject_parser.add_argument(
    "-w",
    dest="write",
    action="store_true",
    help="Actually write the object into database",
)
hashobject_parser.add_argument("path")

# Takes the sha of a commit object and prints its contents
log_parser = argsubparser.add_parser("log", help="Display history of given commit")
log_parser.add_argument("commit", default="HEAD")


checkout_parser = argsubparser.add_parser("checkout")
checkout_parser.add_argument("commit", help="The commit or tree to checkout.")
checkout_parser.add_argument("path", help="The Empty directory to check on")

showref_parser = argsubparser.add_parser("show-ref", help="List references")

tag_parser = argsubparser.add_parser("tag", help="List and create tags")
tag_parser.add_argument(
    "-a",
    dest="create_tag_object",
    action="store_true",
    help="Whether to create a tag object",
)
tag_parser.add_argument("name", nargs="?", help="The new tag's name")
tag_parser.add_argument(
    "object", default="HEAD", nargs="?", help="The object the new tag will point to"
)

rev_parser = argsubparser.add_parser("rev-parse", help="Converts name to hash")
rev_parser.add_argument(
    "--wyag-type", dest="type", choices=["blob", "commit", "tag", "tree"]
)
rev_parser.add_argument("name")


# git status command
# On branch master

# Changes to be committed: (comparision of index file with HEAD (previous commit and staging area))

# Changes not staged for commit: (comparisin with staging area (index file) and working tree(workdir))

# Untracked files: (comparision of index file with HEAD (previous commit and staging area))
status_parser = argsubparser.add_parser("status", help="Print the status of the game")


rm_parser = argsubparser.add_parser("rm", help="Remove paths from the staging area")
rm_parser.add_argument("-n", dest="nd", action="store_true", help="unstage")
rm_parser.add_argument("path", nargs="+", help="Paths to remove")


add_parser = argsubparser.add_parser("add", help="Adding files to staging area")
add_parser.add_argument("path", nargs="+", help="Paths going to staging area")


commit_parser = argsubparser.add_parser("commit", help="Finally commit it goddammit")
commit_parser.add_argument(
    "-m",
    metavar="message",
    dest="message",
    help="Message to associate with this commit",
)

commits_parser = argsubparser.add_parser("all-commits", help="Display all the commits")

branch_parser = argsubparser.add_parser("branch", help="Look at your current branch")
