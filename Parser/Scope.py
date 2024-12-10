class Escopo():

    def __init__(self, index, pai):
        self.index = index
        self.pai = pai
        self.aberto = True
        self.varList = []
    def __str__(self):
        return "Index: %s\n Pai: %s\n Aberto:%s\n" % (str(self.index),str(self.pai),str(self.aberto))
    def fechar(self):
        self.aberto = False