import os
from helpers.repo.helpers import repo_file
from stage.indexfile import GITIndex, GITIndexEntry
from math import ceil

def index_write(repo, index):
        with open(repo_file(repo, "index"), "wb") as f:
            f.write(b"DIRC")
            f.write(index.version.to_bytes(4, "big"))
            f.write(len(index.entries).to_bytes(4, "big"))

            idx = 0
            for e in index.entries:
                f.write(e.ctime[0].to_bytes(4, "big"))
                f.write(e.ctime[1].to_bytes(4, "big"))
                f.write(e.mtime[0].to_bytes(4, "big"))
                f.write(e.mtime[1].to_bytes(4, "big"))
                f.write(e.dev.to_bytes(4, "big"))
                f.write(e.ino.to_bytes(4, "big"))

                mode = (e.mode_type << 12) | e.mode_perms
                f.write(mode.to_bytes(4, "big"))
                f.write(e.uid.to_bytes(4, "big"))
                f.write(e.gid.to_bytes(4, "big"))

                f.write(e.fsize.to_bytes(4, "big"))
                f.write(int(e.sha, 16).to_bytes(20, "big"))
                flag_assume_valid = 0x1 << 15 if e.flag_assume_valid else 0
                name_bytes = e.name.encode("utf8")
                bytes_len = len(name_bytes)
                if bytes_len >= 0xFFF:
                    name_length = 0xFFF
                else:
                    name_length = bytes_len

                f.write((flag_assume_valid | e.flag_stage | name_length).to_bytes(2, "big"))

                f.write(name_bytes)
                f.write((0).to_bytes(1, "big"))

                idx += 62 + len(name_bytes) + 1
                if idx % 8 != 0:
                    pad = 8 - (idx % 8)
                    f.write((0).to_bytes(pad, "big"))
                    idx += pad

def index_read(repo):
    index_file = repo_file(repo, "index")

    if not os.path.exists(index_file):
        return GITIndex()

    with open(index_file, 'rb') as f:
        raw = f.read()

    header = raw[:12]
    signature = header[:4]
    assert signature == b"DIRC" # -> "DirCache"
    version = int.from_bytes(header[4:8], "big")
    assert version == 2, "wyag only supports index file version 2"
    count = int.from_bytes(header[8:12], "big")

    entries = list()

    content = raw[12:]
    idx = 0
    for i in range(0, count):
        ctime_s =  int.from_bytes(content[idx: idx+4], "big")
        ctime_ns = int.from_bytes(content[idx+4: idx+8], "big")
        mtime_s = int.from_bytes(content[idx+8: idx+12], "big")
        mtime_ns = int.from_bytes(content[idx+12: idx+16], "big")
        dev = int.from_bytes(content[idx+16: idx+20], "big")
        ino = int.from_bytes(content[idx+20: idx+24], "big")
        unused = int.from_bytes(content[idx+24: idx+26], "big")
        assert 0 == unused
        mode = int.from_bytes(content[idx+26: idx+28], "big")
        mode_type = mode >> 12
        assert mode_type in [0b1000, 0b1010, 0b1110]
        mode_perms = mode & 0b0000000111111111
        uid = int.from_bytes(content[idx+28: idx+32], "big")
        gid = int.from_bytes(content[idx+32: idx+36], "big")
        fsize = int.from_bytes(content[idx+36: idx+40], "big")
        sha = format(int.from_bytes(content[idx+40: idx+60], "big"), "040x")
        flags = int.from_bytes(content[idx+60: idx+62], "big")
        flag_assume_valid = (flags & 0b1000000000000000) != 0
        flag_extended = (flags & 0b0100000000000000) != 0
        assert not flag_extended
        flag_stage =  flags & 0b0011000000000000
        name_length = flags & 0b0000111111111111

        idx += 62

        if name_length < 0xFFF:
            assert content[idx + name_length] == 0x00
            raw_name = content[idx:idx+name_length]
            idx += name_length + 1
        else:
            print(f"Notice: Name is 0x{name_length:X} bytes long.")
            null_idx = content.find(b'\x00', idx + 0xFFF)
            raw_name = content[idx: null_idx]
            idx = null_idx + 1

        name = raw_name.decode("utf8")

        idx = 8 * ceil(idx / 8)

        entries.append(GITIndexEntry(ctime=(ctime_s, ctime_ns),
                                     mtime=(mtime_s,  mtime_ns),
                                     dev=dev,
                                     ino=ino,
                                     mode_type=mode_type,
                                     mode_perms=mode_perms,
                                     uid=uid,
                                     gid=gid,
                                     fsize=fsize,
                                     sha=sha,
                                     flag_assume_valid=flag_assume_valid,
                                     flag_stage=flag_stage,
                                     name=name))

    return GITIndex(version=version, entries=entries)
