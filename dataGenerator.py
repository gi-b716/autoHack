import subprocess
import threading
import requests
import zipfile
import psutil
import random
import time
import sys
import os

class Config:
    numberOfSamples = 10
    globalArgs = {"sourceFile": "source", "stdFile": "std"}
    timeLimits = 1000 # ms
    memoryLimits = 1024 # MB
    waitTime = 3.0 # s
    ignoreSomeCharactersAtTheEnd = True
    saveWrongOutput = True
    previewHackDataTime = 0.0 # s
    wrongLimits = -1

    # Program
    compileBeforeRun = True
    commandsArgs = {"mem": str(memoryLimits*1024*1024)}
    compileCommands = ["g++ $(sourceFile).cpp -o $(sourceFile) -Wl,--stack=$(mem)", "g++ $(stdFile).cpp -o $(stdFile) -Wl,--stack=$(mem)"] # source / std
    runningCommands = [".\\$(sourceFile)", ".\\$(stdFile)"]
    useFileIO = False

    # Checker
    useCustomChecker = False
    checkerFileArgs = {"checkerFile": ""}
    compileCheckerCommands = "g++ $(checkerFile).cpp -o $(checkerFile)"
    runningCheckerCommands =  ".\\$(checkerFile) $[input] $[output] $[ans]"
    useTestlib = True

    # File
    dataFileName = (("hack","in"),("hack","ans"))
    fileName = (("plus","in"),("plus","out"))
    wrongOutputFileName = ("plus","out")

    # Debug
    skipGenerate = False
    skipRun = False
    commandAtEnd = ""
    dataOutputLimits = 200

    def __init__(self):
        utilsObj = Utils()

        if self.compileCommands[1] == "":
            self.compileCommands[1] = self.compileCommands[0]
        if self.runningCommands[1] == "":
            self.runningCommands[1] = self.runningCommands[0]

        compileFormat = self.globalArgs.copy()
        compileFormat.update(self.commandsArgs)
        self.compileCommands[0] = utilsObj.formatCommand(self.compileCommands[0], compileFormat)
        self.compileCommands[1] = utilsObj.formatCommand(self.compileCommands[1], compileFormat)
        self.runningCommands[0] = utilsObj.formatCommand(self.runningCommands[0], compileFormat)
        self.runningCommands[1] = utilsObj.formatCommand(self.runningCommands[1], compileFormat)

        if self.useCustomChecker:
            checkerFormat = self.globalArgs.copy()
            checkerFormat.update(self.checkerFileArgs)
            self.compileCheckerCommands = utilsObj.formatCommand(self.compileCheckerCommands, checkerFormat)
            self.runningCheckerCommands = utilsObj.formatCommand(self.runningCheckerCommands, checkerFormat)

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

    def formatCommand(self, command:str, fillList:dict):
        for key, value in fillList.items():
            command = command.replace("$({0})".format(key), "{0}".format(value))
        return command

    def printData(self, data):
        configObj = Config()
        if len(data) <= configObj.dataOutputLimits or configObj.dataOutputLimits < 0:
            return data
        else:
            return data[:configObj.dataOutputLimits] + "..."

    def previewHackData(self):
        configObj = Config()
        dataObj = Data(configObj)
        dataObj.generateData(-1)
        refer = dataObj.getFileName(-1)

        print("Input:")
        with open(refer[0],"r") as inputFile:
            print("{0}".format(self.printData(inputFile.read())))
        print("\nAns:")
        with open(refer[1],"r") as ansFile:
            print("{0}".format(self.printData(ansFile.read())))

        os.system("del {0} /q".format(refer[0]))
        os.system("del {0} /q".format(refer[1]))

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
            os.system("{0} < {1} > {2}".format(self.config.runningCommands[1],freInputFileName,freOutputFileName))
        else:
            os.system("{0}".format(self.config.runningCommands[1]))
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
        runCommand = "{0}".format(self.config.runningCommands[0])
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

            if self.config.useCustomChecker and self.config.useTestlib:
                runCheckerCommand = "{0} checkerResult".format(self.config.runningCheckerCommands.replace("$[input]",freInputFileName).replace("$[ans]",ansFileName).replace("$[output]",freOutputFileName))
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

            elif self.config.useCustomChecker:
                runCheckerCommand = self.config.runningCheckerCommands.replace("$[input]",freInputFileName).replace("$[ans]",ansFileName).replace("$[output]",freOutputFileName)
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

class Tools:
    class dataSet:
        def __init__(self):
            self.dataSetList = []

        def refresh(self):
            if not os.path.isdir(".autohack\\dataset"):
                os.mkdir(".autohack\\dataset")
                self.dataSetList = []
                return
            self.dataSetList = os.listdir(".autohack\\dataset")

        def create(self):
            self.refresh()
            note = "\\/:*?\"<>|"
            while "\\" in note or "/" in note or ":" in note or "*" in note or "?" in note or "\"" in note or "<" in note or ">" in note or "|" in note:
                note = input("Please enter a note: ")
            zipFileName = str(time.time())
            if note != "":
                zipFileName = zipFileName + "-" + note
            if os.path.isdir("hackData"):
                zipFileObj = zipfile.ZipFile(".\\hackData.zip", "w", zipfile.ZIP_DEFLATED)
                fileList = os.listdir(".\\hackData")
                for file in fileList:
                    zipFileObj.write(".\\hackData\\{0}".format(file))
                zipFileObj.close()
            if os.path.isdir("wrongOutput"):
                zipFileObj = zipfile.ZipFile(".\\wrongOutput.zip", "w", zipfile.ZIP_DEFLATED)
                fileList = os.listdir(".\\wrongOutput")
                for file in fileList:
                    zipFileObj.write(".\\wrongOutput\\{0}".format(file))
                zipFileObj.close()
            zipFileObj = zipfile.ZipFile(".\\{0}.zip".format(zipFileName), "w", zipfile.ZIP_DEFLATED)
            if os.path.exists("hackData.zip"):
                zipFileObj.write(".\\hackData.zip")
            if os.path.exists("wrongOutput.zip"):
                zipFileObj.write(".\\wrongOutput.zip")
            zipFileObj.close()
            os.system("move {0}.zip .\\.autohack\\dataset".format(zipFileName))
            os.system("del hackData.zip")
            os.system("del wrongOutput.zip")

        def switch(self, id):
            self.refresh()
            os.system("rmdir /s/q hackData")
            os.system("rmdir /s/q wrongOutput")
            os.system("copy .\\.autohack\\dataset\\{0}".format(self.dataSetList[id]))
            with zipfile.ZipFile("{0}".format(self.dataSetList[id]), "r") as zipFileObj:
                zipFileObj.extractall(".")
            if os.path.exists("hackData.zip"):
                with zipfile.ZipFile("hackData.zip", "r") as zipFileObj:
                    zipFileObj.extractall(".")
            if os.path.exists("wrongOutput.zip"):
                with zipfile.ZipFile("wrongOutput.zip", "r") as zipFileObj:
                    zipFileObj.extractall(".")
            os.remove("{0}".format(self.dataSetList[id]))
            os.system("del hackData.zip")
            os.system("del wrongOutput.zip")

        def delete(self, id):
            os.system("del .\\.autohack\\dataset\\{0}".format(self.dataSetList[id]))

class GUI:
    def __init__(self):
        self.configObj = Config()
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
            os.system("python {1}".format(directory+"\\_create.py"))
        else:
            os.system("python {1} {2}".format(directory+"\\_create.py",instanceName))
        os.chdir("{0}".format(directory))

    def viewDataSet(self):
        toolsObj = Tools()
        dataSetObj = toolsObj.dataSet()
        dataSetObj.refresh()
        for dataId in range(len(dataSetObj.dataSetList)):
            data = dataSetObj.dataSetList[dataId]
            dataName = data[:-4].split("-")
            print("{0}. {1}".format(dataId, time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(float(dataName[0])))), end="")
            if len(dataName) == 2:
                print(" | {0}".format(dataName[1]))
            else:
                print()
        sendBackInformation = input("\nc. Create\nq. Exit\nEnter a number to execute: ")
        print()
        try:
            sendBackInformation = int(sendBackInformation)
        except:
            if sendBackInformation == "c":
                dataSetObj.create()
            elif sendBackInformation == "q":
                return
            else:
                self.viewDataSet()
        else:
            if sendBackInformation < len(dataSetObj.dataSetList):
                choiceRes = input("s. Switch\nd. Delete\nEnter a number to execute: ")
                print()
                if choiceRes == "s":
                    dataSetObj.switch(sendBackInformation)
                elif choiceRes == "d":
                    dataSetObj.delete(sendBackInformation)
                else:
                    self.viewDataSet()
            else:
                self.viewDataSet()

    def mainPage(self):
        sendBackInformation = input("""autoHack (GUI version) v{0}
1. Create a new instance using _create.py
2. Run autoHack.infinite.py
3. Run autoHack.random.py
4. Preview hack data
5. Download testlib
6. View dataset

q. Exit
Enter a number to execute: """.format(Meta._version))
        print()

        if sendBackInformation == '1':
            self.createInstancePage()
        elif sendBackInformation == '2':
            os.system("python autoHack.infinite.py")
        elif sendBackInformation == '3':
            os.system("python autoHack.random.py")
        elif sendBackInformation == '4':
            utilsObject = Utils()
            utilsObject.previewHackData()
        elif sendBackInformation == '5':
            utilsObject = Utils()
            utilsObject.getLastedTestlib()
        elif sendBackInformation == '6':
            self.viewDataSet()
        elif sendBackInformation == 'q':
            sys.exit(0)

        self.mainPage()

class Meta:
    _version = "8.0.0-dev1"


if __name__ == "__main__":
    if not os.path.isdir(".autohack"):
        os.mkdir(".autohack")
        os.system("attrib +h .autohack")
    guiObject = GUI()
    guiObject.mainPage()
