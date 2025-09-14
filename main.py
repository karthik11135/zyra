from argparsing import argparser
import sys
from cmds.commands import *
from termcolor import cprint
from stream import *

def main(argvs=sys.argv[1:]):
    args = argparser.parse_args(argvs)

    cprint(f"zyra rolling...", (196, 251, 174), "on_black", ["bold", "blink"])
    print("\033[38;5;81m")

    match args.command:
        case "add": #
            cmd_add(args)
        case "checkout":
            cmd_checkout(args)
        case "init": # done
            cmd_init(args)
        case "cat-file": # done
            cmd_cat_file(args) 
        case "hash-object": # done
            cmd_hash_obj(args)
        case "log": # done
            cmd_log(args)
        case "show-ref": # done
            cmd_show_ref(args)
        case "tag":
            cmd_tag(args)
        case "rev-parse":
            cmd_rev_parse(args)
        case "status":
            cmd_status(args)
        case "rm":
            cmd_rm(args)
        case "commit":
            cmd_commit(args)
