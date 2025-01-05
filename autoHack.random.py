import dataGenerator
import hashlib
import logging
import time
import sys
import os

config = dataGenerator.Config()
data = dataGenerator.Data(config)
utils = dataGenerator.Utils()

diffCount = 0
generateStart = 0
runStart = 0
clearTag = False

# Init logger
logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
logFile = logging.FileHandler("hackLog.random.log")
logFile.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logFile.setFormatter(logFormatter)
logger.addHandler(logFile)
logger.info("Init logger")

# Init output
os.system("echo off")
os.system("cls")

if not os.path.isdir(".autohack"):
    os.mkdir(".autohack")
    os.system("attrib +h .autohack")

if config.compileBeforeRun==True:
    print("Compile program(s)")
    logger.info("Compile program(s)")
    if config.skipGenerate==False: os.system("{0}".format(config.compileCommands[1]))
    if config.skipRun==False: os.system("{0}".format(config.compileCommands[0]))
    if config.useCustomChecker: os.system("{0}".format(config.compileCheckerCommands))
    if config.useInteractor:
        if config.skipGenerate==False: os.system("{0}".format(config.compileCommandsExtra[1]))
        if config.skipRun==False: os.system("{0}".format(config.compileCommandsExtra[0]))
        if config.useMiddleFile: os.system("{0}".format(config.compileCommandsExtra[2]))
    print("Compile done.")

md5Obj = hashlib.md5()
with open("dataGenerator.py", "rb") as fileObj:
    while True:
        fileData = fileObj.read(4096)
        if not fileData:
            break
        md5Obj.update(fileData)
md5Result = md5Obj.hexdigest()

if os.path.exists(".\\.autohack\\keep"):
    keepFile = open(".\\.autohack\\keep", "r")
    keepFileContent = keepFile.readlines()
    keepFile.close()
    os.remove(".\\.autohack\\keep")
    if md5Result == keepFileContent[0].strip():
        askRes = input("Detected unfinished tasks, do you want to restore them? (y/[n]): ")
        if askRes == "y":
            if keepFileContent[-2].strip() == "g":
                generateStart = int(keepFileContent[-1].strip())
                clearTag = True
            if keepFileContent[-2].strip() == "r":
                runStart = int(keepFileContent[-1].strip())
                config.skipGenerate = True

if config.previewHackDataTime > 0 and not config.skipGenerate:
    utils.previewHackData()
    time.sleep(config.previewHackDataTime)
    logger.info("Preview hack data.")

keepFileObj = open(".\\.autohack\\keep", "w")
keepFileObj.write("{0}\n".format(md5Result))

# Generate hack data
if config.skipGenerate==False:
    logger.info("Start generate hack data")
    if not clearTag:
        os.system("rmdir /s/q hackData")
        os.system("md hackData")
        logger.info("Cleaning hack data history")
    for samplesId in range(generateStart, config.numberOfSamples):
        keepFileObj.write("g\n{0}\n".format(samplesId))
        refer = data.getFileName(samplesId)
        data.generateData(samplesId)
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[0]))
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[1]))
        os.system("cls")
        print("Generating hack data: {0} | {1}/{2}".format((samplesId+1)/config.numberOfSamples, samplesId+1, config.numberOfSamples))
        logger.info("Generating hack data: {0} | {1}/{2}".format((samplesId+1)/config.numberOfSamples, samplesId+1, config.numberOfSamples))
else:
    logger.info("Skip generate")

# Start random hacking
if config.skipRun==False: # TODO
    logger.info("Start random hacking...")
    os.system("rmdir /s/q wrongOutput")
    if config.saveWrongOutput==True:
        os.system("md wrongOutput")
        logger.info("Cleaning wrong output history")
    for samplesId in range(runStart, config.numberOfSamples):
        keepFileObj.write("r\n{0}\n".format(samplesId))
        refer = data.getFileName(samplesId)
        os.system("move .\\hackData\\{0} .\\{0}".format(refer[0]))
        os.system("move .\\hackData\\{0} .\\{0}".format(refer[1]))
        os.system("cls")
        print("Judging: {0} | {1}/{2}".format((samplesId+1)/config.numberOfSamples, samplesId+1, config.numberOfSamples))
        logger.info("Judging: {0} | {1}/{2}".format((samplesId+1)/config.numberOfSamples, samplesId+1, config.numberOfSamples))
        result = data.runHacking(samplesId)
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[0]))
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[1]))
        os.system("cls")

        if config.useCustomChecker and config.useTestlib:
            checkerResFile = open("checkerResult","r")
            checkerRes = checkerResFile.read()
            checkerResFile.close()
            os.system("del checkerResult /q")
            print("{0}".format(checkerRes))
            logger.debug("{0} Exit code: {1}.".format(checkerRes.replace("\n"," | "),result[8]))
            if result[0]==-1:
                print("Checker failed!")
                os.system("{0}".format(config.commandAtEnd))
                sys.exit(0)
            if result[0]!=1:
                time.sleep(config.waitTime)
                diffCount += 1

        elif result[1]==True:
            print("Time Limit Exceeded!")
            logger.warning("Time Limit Exceeded! Exceed {0} ms".format(result[2]))
            time.sleep(config.waitTime)
            diffCount += 1

        elif result[5]!=0:
            print("Runtime Error! Exit code: {0}".format(result[5]))
            logger.warning("Runtime Error! Exit code: {0}".format(result[5]))
            time.sleep(config.waitTime)
            diffCount += 1

        elif result[6]==True:
            print("Memory Limit Exceeded!")
            logger.warning("Memory Limit Exceeded! Exceed {0} MB".format(result[7]))
            time.sleep(config.waitTime)
            diffCount += 1

        elif result[0]==0:
            print("Catch diff on data {0}!\nAns:\n{1}\nOutput:\n{2}\n".format(samplesId,utils.printData(result[3]),utils.printData(result[4])))
            logger.warning("Catch diff! See {0} and {1}".format(refer[0],refer[1]))
            time.sleep(config.waitTime)
            diffCount += 1

        elif result[0]!=0 and result[0]!=1:
            print("Checker failed! Exit code: {0}".format(result[0]))
            logger.error("Checker failed! Exit code: {0}".format(result[0]))
            os.system("{0}".format(config.commandAtEnd))
            sys.exit(0)

        if diffCount == config.wrongLimits:
            keepFileObj.close()
            os.remove(".\\.autohack\\keep")
            os.system("{0}".format(config.commandAtEnd))
            sys.exit(0)

    logger.info("Catch {0} diff".format(diffCount))
else:
    logger.info("Skip judge")

logger.info("Done.")
keepFileObj.close()
os.remove(".\\.autohack\\keep")
os.system("{0}".format(config.commandAtEnd))