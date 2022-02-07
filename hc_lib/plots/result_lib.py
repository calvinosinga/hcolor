
class ResultLibrary():

    def __init__(self, path):
        self.results = {}
        self.path = path
        return
    
    def addResults(self, result_containers):
        for r in result_containers:
            rt = r.getType()
            if rt in self.results:
                self.results[rt].append(r)
            else:
                self.results[rt] = [r]
        return
    