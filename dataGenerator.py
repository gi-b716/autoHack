import func_timeout
import subprocess
import random
import time
import sys
import os

class Config:
    numberOfSamples = 10
    sourceFile = "source"
    stdFile = "std"
    timeLimits = 1000 # ms
    exitWhenThereIsADiscrepancy = True
    waitTime = 3.0 # s
    ignoreSomeCharactersAtTheEnd = True
    saveWrongOutput = True
    previewHackDataTime = 0.0 # s

    # Program
    compileBeforeRun = False
    compileCommands = "g++ $(name).cpp -o $(name)" # $(name) will be automatically replaced with the source program name
    runningCommands = ".\\$(name)"
    useFileIO = False

    # File
    dataFileName = (("hack","in"),("hack","ans"))
    fileName = (("plus","in"),("plus","out"))
    wrongOutputFileName = ("plus","out")

    # Debug
    skipGenerate = False
    skipRun = False

    # Infinite
    wrongLimits = 1

class Data:
    def __init__(self, config:Config):
        self.config = config

    def getFileName(self, id):
        inputFileName = "{0}{1}.{2}".format(self.config.dataFileName[0][0],id,self.config.dataFileName[0][1])
        ansFileName = "{0}{1}.{2}".format(self.config.dataFileName[1][0],id,self.config.dataFileName[1][1])
        freInputFileName = "{0}.{1}".format(self.config.fileName[0][0],self.config.fileName[0][1])
        freOutputFileName = "{0}.{1}".format(self.config.fileName[1][0],self.config.fileName[1][1])
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
            os.system("{0} < {1} > {2}".format(self.config.runningCommands.replace("$(name)",self.config.stdFile),freInputFileName,freOutputFileName))
        else:
            os.system("{0}".format(self.config.runningCommands.replace("$(name)",self.config.stdFile)))
        os.system("rename {0} {1}".format(freInputFileName,inputFileName))
        os.system("rename {0} {1}".format(freOutputFileName,ansFileName))

    @func_timeout.func_set_timeout(Config.timeLimits/1000)
    def runCode(self, runCommand):
        self.runCodeResult = subprocess.Popen("{0}".format(runCommand))
        self.runCodeResult.wait()

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
            runCommand = "{0} < {1} > {2}".format(self.config.runningCommands.replace("$(name)",self.config.sourceFile),freInputFileName,freOutputFileName)
        else:
            runCommand = "{0}".format(self.config.runningCommands.replace("$(name)",self.config.sourceFile))

        try:
            self.runCode(runCommand)
        except func_timeout.exceptions.FunctionTimedOut:
            timeOutTag = True
            os.system("taskkill /F /PID {0}".format(self.runCodeResult.pid))
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
                                os.system("rename .\\wrongOutput\\{0} {1}{2}.{3}".format(freOutputFileName,self.config.wrongOutputFileName[0],id,self.config.wrongOutputFileName[1]))
                            break
                else:
                    if self.config.saveWrongOutput==True:
                        os.system("copy .\\{0} .\\wrongOutput".format(freOutputFileName))
                        os.system("rename .\\wrongOutput\\{0} {1}{2}.{3}".format(freOutputFileName,self.config.wrongOutputFileName[0],id,self.config.wrongOutputFileName[1]))
            else:
                if ans==output:
                    result = 1
                else:
                    if self.config.saveWrongOutput==True:
                        os.system("copy .\\{0} .\\wrongOutput".format(freOutputFileName))
                        os.system("rename .\\wrongOutput\\{0} {1}{2}.{3}".format(freOutputFileName,self.config.wrongOutputFileName[0],id,self.config.wrongOutputFileName[1]))

            ansFile.close()
            outputFile.close()

        os.system("rename {0} {1}".format(freInputFileName,inputFileName))
        os.system("del {0} /q".format(freOutputFileName))

        return [result,timeOutTag,self.config.timeLimits,ans,output]

class Test:
    def __init__(self):
        # TLEErrorDetection
        self.testFileName = "TLEErrorDetection.cpp"
        self.defaultContent = """int main(){
}"""
        self.compileCommands = "g++ TLEErrorDetection.cpp -o TLEErrorDetection"
        self.runningCommands = ".\\TLEErrorDetection"

    """Due to technical reasons, the time used by autoHack to detect TLE includes the time spent using function calls to evaluate the program. This test can help measure this error."""
    def TLEErrorDetection(self):
        print("Writing in progress.")
        with open("{0}".format(self.testFileName),"w") as testFile:
            testFile.write("{0}".format(self.defaultContent))

        print("Compiling.")
        os.system("{0}".format(self.compileCommands))

        print("During testing.")
        startTime = time.time()
        subprocess.Popen("{0}".format(self.runningCommands))
        endTime = time.time()

        print("Start: {0}\nEnd: {1}\nError: {2}".format(startTime, endTime, endTime-startTime))

    """Preview hack data"""
    def previewHackData(self):
        configObj = Config()
        dataObj = Data(configObj)
        dataObj.generateData(0)
        refer = dataObj.getFileName(0)

        print("Input:")
        with open(refer[0],"r") as inputFile:
            print("{0}".format(inputFile.read()))
        print("\nAns:")
        with open(refer[1],"r") as ansFile:
            print("{0}".format(ansFile.read()))

        os.system("del {0} /q".format(refer[0]))
        os.system("del {0} /q".format(refer[1]))

class GUI:
    def __init__(self):
        self.pythonRunningCommand = input("Please enter the command you used to run the Python file (leave it blank to auto-fill with \"python\"): ")
        if self.pythonRunningCommand == "":
            self.pythonRunningCommand = "python"
        os.system("echo off")
        os.system("cls")
        print("autoHack (GUI version) is launched.\n")

    def createInstancePage(self):
        if not os.path.exists("_create.py"):
            print("autoHack is already running in an instance!\n")
            return

        directory = os.path.dirname(os.path.abspath(__file__))
        instanceDirectory = input("Enter the instance storage directory: ")
        print()
        instanceName = input("Enter the instance name: ")
        print()

        os.chdir("{0}".format(instanceDirectory))
        if instanceName == "":
            os.system("{0} {1}".format(self.pythonRunningCommand,directory+"\\_create.py"))
        else:
            os.system("{0} {1} {2}".format(self.pythonRunningCommand,directory+"\\_create.py",instanceName))
        os.chdir("{0}".format(directory))

    def runningAutohack(self, mode):
        directory = os.path.dirname(os.path.abspath(__file__))
        if mode == "infinite":
            os.system("{0} autoHack.infinite.py".format(self.pythonRunningCommand))
        elif mode == "random":
            os.system("{0} autoHack.random.py".format(self.pythonRunningCommand))

    def testPage(self):
        testObject = Test()

        sendBackInformation = input("""autoHack (GUI version) - Run test
1. Run all tests
2. Run TLEErrorDetection
3. Run previewHackData

b. Return to the main screen
q. Exit
Enter a number to execute: """)
        print()

        if sendBackInformation == '1':
            print("Test 1/2: TLEErrorDetection\n")
            testObject.TLEErrorDetection()
            print("\nTest 2/2: previewHackData\n")
            testObject.previewHackData()
            print()
        elif sendBackInformation == '2':
            print("Test: TLEErrorDetection\n")
            testObject.TLEErrorDetection()
            print()
        elif sendBackInformation == '3':
            print("Test: previewHackData\n")
            testObject.previewHackData()
            print()
        elif sendBackInformation == 'b':
            return
        elif sendBackInformation == 'q':
            sys.exit(0)

        self.testPage()

    def mainPage(self):
        sendBackInformation = input("""autoHack (GUI version)
1. Create a new instance using _create.py
2. Run autoHack.infinite.py
3. Run autoHack.random.py
4. Run test

q. Exit
Enter a number to execute: """)
        print()

        if sendBackInformation == '1':
            self.createInstancePage()
        elif sendBackInformation == '2':
            self.runningAutohack("infinite")
        elif sendBackInformation == '3':
            self.runningAutohack("random")
        elif sendBackInformation == '4':
            self.testPage()
        elif sendBackInformation == 'q':
            sys.exit(0)

        self.mainPage()


if __name__ == "__main__":
    guiObject = GUI()
    guiObject.mainPage()
