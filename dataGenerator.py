import func_timeout
import random
import os

class Config:
    numberOfSamples = 10
    sourceFile = "source"
    stdFile = "std"
    dataFile = "hack"
    timeLimits = 1000 # ms
    exitWhenThereIsADiscrepancy = True
    waitTime = 3.0 # s
    ignoreSomeCharactersAtTheEnd = True
    saveWrongOutput = True

    # Program
    compileBeforeRun = False
    compileArgs = ""
    useFileIO = True
    useSameFileName = True
    freFileName = "plus"
    inputFileName = ""
    outputFileName = ""

    # Debug
    skipGenerate = False
    skipRun = False

globalConfig = Config()

class Data:
    def __init__(self, config:Config):
        self.config = config

    def getFileName(self, id):
        inputFileName = "{0}{1}.in".format(self.config.dataFile,str(id))
        ansFileName = "{0}{1}.ans".format(self.config.dataFile,str(id))
        freInputFileName = ""
        freOutputFileName = ""
        if self.config.useSameFileName==True:
            freInputFileName = "{0}.in".format(self.config.freFileName)
            freOutputFileName = "{0}.out".format(self.config.freFileName)
        else:
            freInputFileName = "{0}.in".format(self.config.inputFileName)
            freOutputFileName = "{0}.out".format(self.config.outputFileName)
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
        if self.config.useFileIO==False:
            os.system(".\\{0} < {1} > {2}".format(self.config.stdFile,freInputFileName,freOutputFileName))
        else:
            os.system(".\\{0}".format(self.config.stdFile))
        os.system("rename {0} {1}".format(freInputFileName,inputFileName))
        os.system("rename {0} {1}".format(freOutputFileName,ansFileName))

    @func_timeout.func_set_timeout(globalConfig.timeLimits/1000)
    def runCode(self, runCommand):
        os.system(runCommand)

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

        runCommand = ""
        if self.config.useFileIO==False:
            runCommand = ".\\{0} < {1} > {2}".format(self.config.sourceFile,freInputFileName,freOutputFileName)
        else:
            runCommand = ".\\{0}".format(self.config.sourceFile)

        try:
            self.runCode(runCommand)
        except func_timeout.exceptions.FunctionTimedOut:
            timeOutTag = True
            os.system("taskkill /F /IM {0}".format(self.config.sourceFile))
            os.system("cls")

        if timeOutTag==False:
            ansFile = open("{0}".format(ansFileName), "r")
            outputFile = open("{0}".format(freOutputFileName), "r")

            ans = ansFile.read()
            output = outputFile.read()

            if self.config.ignoreSomeCharactersAtTheEnd:
                ans = ans.rstrip("\n");
                output = output.rstrip("\n");
                anst = ans.splitlines();
                outputt = output.splitlines();
                if len(anst)==len(outputt):
                    result = 1
                    for i in range(len(anst)):
                        if anst[i].rstrip()!=outputt[i].rstrip():
                            result = 0
                            if self.config.saveWrongOutput==True:
                                os.system("copy .\\{0} .\\wrongOutput".format(freOutputFileName))
                                os.system("rename .\\wrongOutput\\{0} {1}{2}.out".format(freOutputFileName,self.config.dataFile,id))
                            break
                else:
                    if self.config.saveWrongOutput==True:
                        os.system("copy .\\{0} .\\wrongOutput".format(freOutputFileName))
                        os.system("rename .\\wrongOutput\\{0} {1}{2}.out".format(freOutputFileName,self.config.dataFile,id))
            else:
                if ans==output:
                    result = 1
                else:
                    if self.config.saveWrongOutput==True:
                        os.system("copy .\\{0} .\\wrongOutput".format(freOutputFileName))
                        os.system("rename .\\wrongOutput\\{0} {1}{2}.out".format(freOutputFileName,self.config.dataFile,id))

            ansFile.close()
            outputFile.close()

        os.system("rename {0} {1}".format(freInputFileName,inputFileName))
        os.system("del {0} /q".format(freOutputFileName))

        return [result,timeOutTag,self.config.timeLimits,ans,output]