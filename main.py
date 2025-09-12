from argparsing import argparser
import sys
from cmds.commands import *

def main(argvs=sys.argv[1:]):
    args = argparser.parse_args(argvs)

    print("hey there from wyag!! \n")

    match args.command:
        case "add" : cmd_add(args)
        case "checkout" : cmd_checkout(args)
        case "init": cmd_init(args)
        case "cat-file": cmd_cat_file(args)
        case "hash-object": cmd_hash_obj(args)
        case "log": cmd_log(args)
        case "show-ref": cmd_show_ref(args)
        case "tag": cmd_tag(args)
        case "rev-parse": cmd_rev_parse(args)
        case "status": cmd_status(args)
        case "rm": cmd_rm(args)
        case "commit": cmd_commit(args)
