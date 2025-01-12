import dataGenerator
import logging
import time
import sys
import os

config = dataGenerator.Config()
data = dataGenerator.Data(config)
utils = dataGenerator.Utils()

globalCount = 0
diffCount = 0

if not os.path.isdir(".autohack"):
    os.mkdir(".autohack")
    os.system("attrib +h .autohack")

# Init logger
os.system(".autohack\\logs\\infinite")
logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logFile = logging.FileHandler(".autohack\\logs\\infinite\\hackLog.infinite.{0}.log".format(time.strftime("%Y-%m-%d_%H-%M-%S",time.localtime(time.time()))))
logFile.setLevel(logging.DEBUG)
logFile.setFormatter(logFormatter)
logger.addHandler(logFile)
logger.info("Init logger")

# Init output
os.system("echo off")
os.system("cls")

if config.compileBeforeRun==True:
    print("Compile program(s)")
    logger.info("Compile program(s)")
    os.system("{0}".format(config.compileCommands[0]))
    os.system("{0}".format(config.compileCommands[1]))
    if config.useCustomChecker: os.system("{0}".format(config.compileCheckerCommands))
    if config.useInteractor:
        os.system("{0}".format(config.compileCommandsExtra[1]))
        os.system("{0}".format(config.compileCommandsExtra[0]))
        if config.useMiddleFile: os.system("{0}".format(config.compileCommandsExtra[2]))
    if config.compileCustomGenerator: os.system("{0}".format(config.compileGeneratorCommands))
    print("Compile done.")

os.system("rmdir /s/q wrongOutput")
os.system("md wrongOutput")
os.system("rmdir /s/q hackData")
os.system("md hackData")
logger.info("Cleaning wrong output history")

if config.previewHackDataTime > 0 and not config.skipGenerate:
    utils.previewHackData()
    time.sleep(config.previewHackDataTime)
    logger.info("Preview hack data.")

while True:
    globalCount += 1
    os.system("cls")
    refer = data.getFileName(diffCount)
    print("Generating hack data {0}".format(globalCount))
    logger.info("Generating hack data {0}".format(globalCount))
    data.generateData(diffCount)
    os.system("cls")
    print("Judging data {0}".format(globalCount))
    logger.info("Judging data {0}".format(globalCount))
    result = data.runHacking(diffCount)

    if config.useCustomChecker and config.useTestlib:
        checkerResFile = open(".\\.autohack\\checkerResult","r")
        checkerRes = checkerResFile.read()
        checkerResFile.close()
        os.system("del .\\.autohack\\checkerResult /q")
        print("{0}".format(checkerRes))
        logger.debug("{0} Exit code: {1}.".format(checkerRes.replace("\n"," | "),result[8]))
        if result[0]==-1:
            os.system("move .\\{0} .\\hackData\\{0}".format(refer[0]))
            os.system("move .\\{0} .\\hackData\\{0}".format(refer[1]))
            os.system("cls")
            print("Checker failed!")
            os.system("{0}".format(config.commandAtEnd))
            sys.exit(0)
        if result[0]!=1:
            os.system("move .\\{0} .\\hackData\\{0}".format(refer[0]))
            os.system("move .\\{0} .\\hackData\\{0}".format(refer[1]))
            os.system("cls")
            time.sleep(config.waitTime)
            diffCount += 1

    elif result[1]==True:
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[0]))
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[1]))
        os.system("cls")
        logData = "Time Limit Exceeded! Exceed {0} ms".format(result[2])
        if config.useInteractor: logData="Time Limit Exceeded on part {0}! Exceed {1} ms".format(result[9],result[2])
        print("{0}".format(logData))
        logger.warning("{0}".format(logData))
        time.sleep(config.waitTime)
        diffCount += 1

    elif result[5]!=0:
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[0]))
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[1]))
        os.system("cls")
        logData = "Runtime Error! Exit code: {0}".format(result[5])
        if config.useInteractor: logData="Runtime Error on part {0}! Exit code: {1}".format(result[9],result[5])
        print("{0}".format(logData))
        logger.warning("{0}".format(logData))
        time.sleep(config.waitTime)
        diffCount += 1

    elif result[6]==True:
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[0]))
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[1]))
        os.system("cls")
        logData = "Memory Limit Exceeded! Exceed {0} MB".format(result[7])
        if config.useInteractor: logData="Memory Limit Exceeded on part {0}! Exceed {1} MB".format(result[9],result[7])
        print("{0}".format(logData))
        logger.warning("{0}".format(logData))
        time.sleep(config.waitTime)
        diffCount += 1

    elif result[0]==0:
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[0]))
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[1]))
        os.system("cls")
        print("Catch diff!\nAns:\n{0}\nOutput:\n{1}\n".format(utils.printData(result[3]),utils.printData(result[4])))
        logger.warning("Catch diff!")
        time.sleep(config.waitTime)
        diffCount += 1

    elif result[0]!=0 and result[0]!=1:
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[0]))
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[1]))
        os.system("cls")
        print("Checker failed! Exit code: {0}".format(result[0]))
        logger.error("Checker failed! Exit code: {0}".format(result[0]))
        os.system("{0}".format(config.commandAtEnd))
        sys.exit(0)

    else:
        os.system("del {0} /q".format(refer[0]))
        os.system("del {0} /q".format(refer[1]))
        os.system("cls")

    if diffCount == config.wrongLimits:
        os.system("{0}".format(config.commandAtEnd))
        sys.exit(0)

    if globalCount == config.numberOfSamples:
        os.system("{0}".format(config.commandAtEnd))
        sys.exit(0)
