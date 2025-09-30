import hashlib
import os
import zlib
from helpers.repo.helpers import repo_file

# An object is stored in this manner: 
# b'{typeof object}{size} \x00{content}' (obj type: {blob, commit, tag, tree})
class GITObject(object):
    def __init__(self, data=None):
        if data != None:
            self.deserialize(data)
        else:
            self.init()

    def serialize(self, repo):
        pass

    def deserialize(self, repo):
        pass

    def init(self):
        pass

    #   Takes the type object(GitBlob, GitCommit etc) and optional repo (whether to write the contents of the file in the sha path or not) and returns the sha of the content. 
    @staticmethod
    def object_write(obj, repo=None):
        # Forming metadata -> head space size content
        data = obj.serialize() # this gives the content of the object in the format of a b string
        head = obj.obj_type
        str_len = str(len(data)).encode()
        space = b' '
        zero_bin = b'\x00'

        final_str = head + space + str_len  + zero_bin + data
        
        sha = hashlib.sha1(final_str).hexdigest()

        if not repo:
            return sha

        path = repo_file(repo, "objects", sha[0:2], sha[2:], mkdir=True)

        print(path)

        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(zlib.compress(final_str))
        
        return sha


    # takes the sha and returns the class according to the type of object. 
    @staticmethod
    def object_read(repo, sha):
        path = repo_file(repo, "objects", sha[0:2], sha[2:])

        if not os.path.isfile(path):
            raise Exception("No object exists here")
        
        with open(path, "rb") as f:
            decomp_str = zlib.decompress(f.read())
            # b'blob{size} \x00{content}' -> format of storage. 
            x = decomp_str.find(b' ')

            obj_type = decomp_str[0:x]
            y = decomp_str.find(b'\x00', x)

            content = decomp_str[y+1:]

            from common.blob.blob_obj import GITBlob
            from common.tag.tag_obj import GITTag
            from common.tree.tree_obj import GITTree
            from common.commit.commit_obj import GITCommit
            match obj_type:
                case b'commit': c=GITCommit
                case b'tree'  : c=GITTree
                case b'tag'   : c=GITTag
                case b'blob'  : c=GITBlob
                case _:
                    raise Exception("I dont know what object this is")
            
            return c(decomp_str[y+1:])
        

