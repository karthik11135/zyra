from common.objects import GITObject
import os

def tree_checkout(repo, tree, path):
    for item in tree.items:
        obj = GITObject.object_read(repo, item.sha)
        dest = os.path.join(path, item.path)

        if obj.obj_type == b'tree':
            os.makedirs(dest)
            tree_checkout(repo, obj, dest)
        elif obj.obj_type == b'blob':
            with open(dest, "wb") as f:
                f.write(obj.blobdata)
