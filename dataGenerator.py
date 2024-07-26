import func_timeout
import random
import os

class Config:
    numberOfSamples = 10
    sourceFile = "source.exe"
    stdFile = "std.exe"
    dataFile = "hack"
    freFileName = "plus"
    timeLimits = 1000 # ms
    exitWhenThereIsADiscrepancy = True

globalConfig = Config()

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

    @func_timeout.func_set_timeout(globalConfig.timeLimits/1000)
    def runCode(self):
        os.system(".\{0}".format(self.config.sourceFile))

    def runHacking(self, id):
        inputFileName = self.getFileName(id)[0]
        ansFileName = self.getFileName(id)[1]
        freInputFileName = self.getFileName(id)[2]
        freOutputFileName = self.getFileName(id)[3]

        timeOutTag = False
        result = 0
        ans = None
        output = None

        os.system("rename {0} {1}".format(inputFileName,freInputFileName))

        try:
            self.runCode()
        except func_timeout.exceptions.FunctionTimedOut:
            timeOutTag = True
            os.system("taskkill /F /IM {0}".format(self.config.sourceFile))
            os.system("cls")

        if(timeOutTag==False):
            ansFile = open("{0}".format(ansFileName), "r")
            outputFile = open("{0}".format(freOutputFileName), "r")

            ans = ansFile.read()
            output = outputFile.read()
            if ans==output:
                result = 1
            
            ansFile.close()
            outputFile.close()
        
        os.system("rename {0} {1}".format(freInputFileName,inputFileName))
        os.system("del {0} /q".format(freOutputFileName))

        return [result,timeOutTag,self.config.timeLimits,ans,output]