from hicc_library.fields_dev.field import Field

class Hisubhalo(Field):
    def __init__(self, simname, snapshot, axis, resolution, verbose):
        
        super().__init__('hisubhalo', simname, snapshot, axis, resolution, verbose)
        
        return