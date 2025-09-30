from common.objects import GITObject
from common.commit.commit_helper import kvlm_parse, kvlm_serialize

class GITCommit(GITObject):
    obj_type = b'commit'

    def deserialize(self, data):
        self.kvlm = kvlm_parse(data)

    def serialize(self):
        return kvlm_serialize(self.kvlm)
    
    # old method
    # def __init__(self):
    #     self.kvlm = dict()

    def __init__(self, data=None):
        super().__init__(data)   # calls GITObject.__init__(data)
        if not hasattr(self, 'kvlm'):
            self.kvlm = dict()