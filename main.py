from argparsing import argparser
import sys
from cmds.commands import *
from termcolor import cprint
import random

colors = [
    ["on_light_cyan"],
    ["on_red"],
    ["on_green"],
    ["on_yellow"],
    ["on_blue"],
    ["on_magenta"],
    ["on_cyan"],
    ["on_white"],
    ["on_light_grey"],
    ["on_dark_grey"],
    ["on_light_red"],
    ["on_light_green"],
    ["on_light_yellow"],
    ["on_light_blue"],
    ["on_light_magenta"],
]


def main(argvs=sys.argv[1:]):
    args = argparser.parse_args(argvs)

    cprint(f"zyra rolling...", (196, 251, 174), random.choice(colors)[0], ["bold", "blink"])

    match args.command:
        case "commit":
            cmd_commit(args)
        case "all-commits":
            cmd_commits(args)
        case "branch":
            cmd_branch(args)
        case "switch":
            cmd_switch(args)
        case "create-branch":
            cmd_create_branch(args)
        case "b-commits":
            cmd_bcommits(args)
        case "add":
            cmd_add(args)
        case "checkout":
            cmd_checkout(args)
        case "init":
            cmd_init(args)
        case "cat-file":
            cmd_cat_file(args)
        case "hash-object":
            cmd_hash_obj(args)
        case "log":
            cmd_log(args)
        case "show-ref":
            cmd_show_ref(args)
        case "tag":
            cmd_tag(args)
        case "rev-parse":
            cmd_rev_parse(args)
        case "status":
            cmd_status(args)
        case "rm":
            cmd_rm(args)
