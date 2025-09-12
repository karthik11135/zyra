
from common.objects import GITObject

def log_graphiz(repo, sha, seen):
    if sha in seen:
        return
    seen.add(sha)

    commitObj = GITObject.object_read(repo, sha)
    message = commitObj.kvlm[None].decode("utf8").strip()
    message = message.replace("\\", "\\\\")
    message = message.replace("\"", "\\\"")

    if "\n" in message: 
        message = message[:message.index("\n")]

    print(f"id: {sha[0:7]} | message: {message}")

    if not b'parent' in commitObj.kvlm:
        return

    parents = commitObj.kvlm[b'parent']

    if type(parents) != list:
        parents = [parents]

    for p in parents:
        p = p.decode("ascii")
        log_graphiz(repo, p, seen)
