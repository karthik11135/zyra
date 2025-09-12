from common.objects import GITObject

class GITBlob(GITObject):
    obj_type = b'blob'

    def serialize(self):
        return self.blobdata
    
    def deserialize(self, data):
        self.blobdata = data

