import random
import os

class Config:
    numberOfSamples = 10
    sourceFile = "source.exe"
    stdFile = "std.exe"
    dataFile = "hack"
    freFileName = "plus"
    exitWhenThereIsADiscrepancy = True

class Data:
    def __init__(self, config:Config):
        self.config = config

    def getFileName(self, id):
        inputFileName = "{0}{1}.in".format(self.config.dataFile,str(id))
        ansFileName = "{0}{1}.ans".format(self.config.dataFile,str(id))
        freInputFileName = "{0}.in".format(self.config.freFileName)
        freOutputFileName = "{0}.out".format(self.config.freFileName)
        return [inputFileName,ansFileName,freInputFileName,freOutputFileName]

    def generateData(self, id):
        inputFileName = self.getFileName(id)[0]
        ansFileName = self.getFileName(id)[1]
        freInputFileName = self.getFileName(id)[2]
        freOutputFileName = self.getFileName(id)[3]

        with open(inputFileName, "w") as inputFile:
            a = random.randint(1,1000000000)
            b = random.randint(1,1000000000)
            inputFile.write("{0} {1}".format(a,b))
        
        os.system("rename {0} {1}".format(inputFileName,freInputFileName))
        os.system(".\{0}".format(self.config.stdFile))
        os.system("rename {0} {1}".format(freInputFileName,inputFileName))
        os.system("rename {0} {1}".format(freOutputFileName,ansFileName))

    def runHacking(self, id):
        inputFileName = self.getFileName(id)[0]
        ansFileName = self.getFileName(id)[1]
        freInputFileName = self.getFileName(id)[2]
        freOutputFileName = self.getFileName(id)[3]

        os.system("rename {0} {1}".format(inputFileName,freInputFileName))
        os.system(".\{0}".format(self.config.sourceFile))

        ansFile = open("{0}".format(ansFileName), "r")
        outputFile = open("{0}".format(freOutputFileName), "r")

        result = False
        ans = ansFile.read()
        output = outputFile.read()
        if ans==output:
            result = True
        
        ansFile.close()
        outputFile.close()
        os.system("rename {0} {1}".format(freInputFileName,inputFileName))
        os.system("del {0} /q".format(freOutputFileName))

        return [result,ans,output]