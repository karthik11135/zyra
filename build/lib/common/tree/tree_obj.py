from common.objects import GITObject
from common.tree.tree_helper import tree_parse, tree_serialize

class GITTree(GITObject):
    obj_type = b'tree'

    def deserialize(self, data):
        self.items = tree_parse(data)
    
    def serialize(self):
        return tree_serialize(self)
    
    # old method
    # def __init__(self):
    #     self.items = list()
    
    def __init__(self, data=None):
        super().__init__(data)
        if not hasattr(self, 'items'):
            self.items = list()
