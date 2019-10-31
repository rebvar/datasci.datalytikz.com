#Abstract class for Chromosome structure for GIS

class  IChrm:
    
    def getFitness(self):
        raise NotImplementedError("Not Implemented")

    def SetTrSet(self,value):
        raise NotImplementedError("Not Implemented")