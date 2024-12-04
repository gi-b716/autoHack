import subprocess
import threading
import requests
import psutil
import random
import sys
import os

class Config:
    numberOfSamples = 10
    sourceFile = "source"
    stdFile = "std"
    timeLimits = 1000 # ms
    memoryLimits = 1024 # MB
    waitTime = 3.0 # s
    ignoreSomeCharactersAtTheEnd = True
    saveWrongOutput = True
    previewHackDataTime = 0.0 # s
    wrongLimits = -1

    # Program
    compileBeforeRun = True
    compileCommands = ["g++ $(name).cpp -o $(name) -Wl,--stack=$(mem)", ""] # $(name) will be automatically replaced with the source program name
    runningCommands = [".\\$(name)", ""]
    useFileIO = False

    # Checker
    checkerFile = ""
    compileCheckerCommands = "g++ $(cname).cpp -o $(cname)"
    runningCheckerCommands =  ".\\$(cname) $(i) $(o) $(a)"
    useTestlib = True

    # File
    dataFileName = (("hack","in"),("hack","ans"))
    fileName = (("plus","in"),("plus","out"))
    wrongOutputFileName = ("plus","out")

    # Debug
    skipGenerate = False
    skipRun = False

    def __init__(self):
        if self.compileCommands[1] == "":
            self.compileCommands[1] = self.compileCommands[0]
        if self.runningCommands[1] == "":
            self.runningCommands[1] = self.runningCommands[0]
        self.compileCommands[0] = self.compileCommands[0].replace("$(mem)", str(self.memoryLimits*1024*1024))
        self.compileCommands[1] = self.compileCommands[1].replace("$(mem)", str(self.memoryLimits*1024*1024))

class Utils:
    def __init__(self):
        self.memoryOut = False

    def memoryMonitor(self, pid, memoryLimits):
        psutilProcess = psutil.Process(pid)
        while True:
            try:
                if psutilProcess.memory_info().vms > memoryLimits:
                    self.memoryOut = True
                    os.system("taskkill /F /PID {0}".format(pid))
                    return
            except:
                return

    def run(self, *popenargs, timeout=None, memoryLimits, **kwargs):
        with subprocess.Popen(*popenargs, **kwargs) as process:
            monitor = threading.Thread(target=self.memoryMonitor, args=(process.pid, memoryLimits, ))
            monitor.start()
            try:
                process.communicate(None, timeout=timeout)
            except:
                process.kill()
                raise
            retcode = process.poll()
        if self.memoryOut == True:
            retcode = 0
        return retcode

    def getLastedTestlib(self):
        testlibRepoApi = "https://api.github.com/repos/MikeMirzayanov/testlib/releases/latest"
        response = requests.get("{0}".format(testlibRepoApi))
        lasted = response.json()["tag_name"]
        downloadUrl = "https://github.com/MikeMirzayanov/testlib/releases/download/{0}/testlib.h".format(lasted)
        print("Download testlib {0}".format(lasted))
        testlib = requests.get("{0}".format(downloadUrl))
        with open("testlib.h", "w") as testlibFile:
            testlibFile.write(str(testlib.content, "utf-8"))
        res = input("Download testlib-{0}.zip? (y/[n]): ".format(lasted))
        if res != 'y':
            return
        downloadUrl = "https://github.com/MikeMirzayanov/testlib/releases/download/{0}/testlib-{0}.zip".format(lasted)
        zipFile = requests.get("{0}".format(downloadUrl))
        with open("testlib-{0}.zip".format(lasted), "wb") as zf:
            zf.write(zipFile.content)

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
            os.system("{0} < {1} > {2}".format(self.config.runningCommands[1].replace("$(name)",self.config.stdFile),freInputFileName,freOutputFileName))
        else:
            os.system("{0}".format(self.config.runningCommands[1].replace("$(name)",self.config.stdFile)))
        os.system("rename {0} {1}".format(freInputFileName,inputFileName))
        os.system("rename {0} {1}".format(freOutputFileName,ansFileName))

    def runHacking(self, id):
        inputFileName = self.getFileName(id)[0]
        ansFileName = self.getFileName(id)[1]
        freInputFileName = self.getFileName(id)[2]
        freOutputFileName = self.getFileName(id)[3]

        timeOutTag = False
        memoryOutTag = False
        exitCode = 0
        checkerExitCode = 0
        result = 0
        ans = None
        output = None

        os.system("rename {0} {1}".format(inputFileName,freInputFileName))

        utilsObject = Utils()
        runCommand = "{0}".format(self.config.runningCommands[0].replace("$(name)",self.config.sourceFile))
        if self.config.useFileIO==False:
            inputFilePipe = open("{0}".format(freInputFileName), "r")
            outputFilePipe = open("{0}".format(freOutputFileName), "w")
            try:
                self.runCodeResult = utilsObject.run("{0}".format(runCommand),stdin=inputFilePipe,stdout=outputFilePipe,timeout=self.config.timeLimits/1000,memoryLimits=self.config.memoryLimits*1024*1024)
            except subprocess.TimeoutExpired:
                timeOutTag = True
            inputFilePipe.close()
            outputFilePipe.close()
            if not timeOutTag:
                exitCode = self.runCodeResult
                memoryOutTag = utilsObject.memoryOut

        else:
            try:
                self.runCodeResult = utilsObject.run("{0}".format(runCommand),timeout=self.config.timeLimits/1000,memoryLimits=self.config.memoryLimits*1024*1024)
            except subprocess.TimeoutExpired:
                timeOutTag = True
            if not timeOutTag:
                exitCode = self.runCodeResult
                memoryOutTag = utilsObject.memoryOut

        if timeOutTag==False and exitCode==0 and memoryOutTag==False:
            ansFile = open("{0}".format(ansFileName), "r")
            outputFile = open("{0}".format(freOutputFileName), "r")
            ans = ansFile.read()
            output = outputFile.read()

            if self.config.checkerFile != "" and self.config.useTestlib:
                runCheckerCommand = "{0} checkerResult".format(self.config.runningCheckerCommands.replace("$(cname)",self.config.checkerFile).replace("$(i)",freInputFileName).replace("$(a)",ansFileName).replace("$(o)",freOutputFileName))
                checkerExitCode = os.system("{0}".format(runCheckerCommand))
                if checkerExitCode == 0:
                    result = 1
                elif checkerExitCode == 3:
                    result = -1
                    os.system("copy .\\{0} .\\wrongOutput".format(freOutputFileName))
                    os.system("rename .\\wrongOutput\\{0} {1}{2}.{3}".format(freOutputFileName,self.config.wrongOutputFileName[0],id,self.config.wrongOutputFileName[1]))
                else:
                    result = 0
                    os.system("copy .\\{0} .\\wrongOutput".format(freOutputFileName))
                    os.system("rename .\\wrongOutput\\{0} {1}{2}.{3}".format(freOutputFileName,self.config.wrongOutputFileName[0],id,self.config.wrongOutputFileName[1]))

            elif self.config.checkerFile != "":
                runCheckerCommand = self.config.runningCheckerCommands.replace("$(cname)",self.config.checkerFile).replace("$(i)",freInputFileName).replace("$(a)",ansFileName).replace("$(o)",freOutputFileName)
                result = os.system("{0}".format(runCheckerCommand))
                if result != 1:
                    os.system("copy .\\{0} .\\wrongOutput".format(freOutputFileName))
                    os.system("rename .\\wrongOutput\\{0} {1}{2}.{3}".format(freOutputFileName,self.config.wrongOutputFileName[0],id,self.config.wrongOutputFileName[1]))

            else:
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

        return [result,timeOutTag,self.config.timeLimits,ans,output,exitCode,memoryOutTag,self.config.memoryLimits,checkerExitCode]

class Test:
    def __init__(self):
        pass

    """Preview hack data"""
    def previewHackData(self):
        configObj = Config()
        dataObj = Data(configObj)
        dataObj.generateData(-1)
        refer = dataObj.getFileName(-1)

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
        self.configObj = Config()
        # self.pythonRunningCommand = input("Please enter the command you used to run the Python file (leave it blank to auto-fill with \"python\"): ")
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
        if mode == "infinite":
            os.system("{0} autoHack.infinite.py".format(self.pythonRunningCommand))
        elif mode == "random":
            os.system("{0} autoHack.random.py".format(self.pythonRunningCommand))

    def testPage(self):
        testObject = Test()

        sendBackInformation = input("""autoHack (GUI version) - Run test
1. Run all tests
2. Run previewHackData

b. Return to the main screen
q. Exit
Enter a number to execute: """)
        print()

        if sendBackInformation == '1':
            print("Test 1/1: previewHackData\n")
            if self.configObj.compileBeforeRun == True:
                os.system("{0}".format(self.configObj.compileCommands[1].replace("$(name)",self.configObj.stdFile)))
            testObject.previewHackData()
            print()
        elif sendBackInformation == '2':
            print("Test: previewHackData\n")
            if self.configObj.compileBeforeRun == True:
                os.system("{0}".format(self.configObj.compileCommands[1].replace("$(name)",self.configObj.stdFile)))
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
4. Download testlib
5. Run test

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
            utilsObject = Utils()
            utilsObject.getLastedTestlib()
        elif sendBackInformation == '5':
            self.testPage()
        elif sendBackInformation == 'q':
            sys.exit(0)

        self.mainPage()

class Meta:
    _version = "6.2.1"


if __name__ == "__main__":
    guiObject = GUI()
    guiObject.mainPage()
