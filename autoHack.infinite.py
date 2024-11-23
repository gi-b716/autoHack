import dataGenerator
import logging
import time
import sys
import os

config = dataGenerator.Config()
data = dataGenerator.Data(config)
test = dataGenerator.Test()

globalCount = 0
diffCount = 0

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

if config.compileBeforeRun==True:
    print("Compile program(s)")
    logger.info("Compile program(s)")
    os.system("{0}".format(config.compileCommands[1].replace("$(name)",config.stdFile)))
    os.system("{0}".format(config.compileCommands[0].replace("$(name)",config.sourceFile)))
    if config.checkerFile != "":
        os.system("{0}".format(config.compileCheckerCommands.replace("$(cname)",config.checkerFile)))
    print("Compile done.")

os.system("rmdir /s/q wrongOutput")
os.system("md wrongOutput")
os.system("rmdir /s/q hackData")
os.system("md hackData")
logger.info("Cleaning wrong output history")

if config.previewHackDataTime > 0 and not config.skipGenerate:
    test.previewHackData()
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

    if config.checkerFile != "" and config.useTestlib:
        checkerResFile = open("checkerResult","r")
        checkerRes = checkerResFile.read()
        checkerResFile.close()
        os.system("del checkerResult /q")
        print("{0}".format(checkerRes))
        logger.debug("{0} Exit code: {1}.".format(checkerRes.replace("\n"," | "),result[8]))
        if result[0]==-1:
            os.system("move .\\{0} .\\hackData\\{0}".format(refer[0]))
            os.system("move .\\{0} .\\hackData\\{0}".format(refer[1]))
            print("Checker failed!")
            sys.exit(0)
        if result[0]!=1:
            os.system("move .\\{0} .\\hackData\\{0}".format(refer[0]))
            os.system("move .\\{0} .\\hackData\\{0}".format(refer[1]))
            time.sleep(config.waitTime)
            diffCount += 1

    elif result[1]==True:
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[0]))
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[1]))
        os.system("cls")
        print("Time Limit Exceeded!")
        logger.warning("Time Limit Exceeded! Exceed {0} ms".format(result[2]))
        time.sleep(config.waitTime)
        diffCount += 1

    elif result[5]!=0:
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[0]))
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[1]))
        os.system("cls")
        print("Runtime Error! Exit code: {0}".format(result[5]))
        logger.warning("Runtime Error! Exit code: {0}".format(result[5]))
        time.sleep(config.waitTime)
        diffCount += 1

    elif result[6]==True:
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[0]))
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[1]))
        os.system("cls")
        print("Memory Limit Exceeded!")
        logger.warning("Memory Limit Exceeded! Exceed {0} MB".format(result[7]))
        time.sleep(config.waitTime)
        diffCount += 1

    elif result[0]==0:
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[0]))
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[1]))
        os.system("cls")
        print("Catch diff!")
        logger.warning("Catch diff!")
        time.sleep(config.waitTime)
        diffCount += 1

    elif result[0]!=0 and result[0]!=1:
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[0]))
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[1]))
        print("Checker failed! Exit code: {0}".format(result[0]))
        logger.error("Checker failed! Exit code: {0}".format(result[0]))
        sys.exit(0)

    else:
        os.system("del {0} /q".format(refer[0]))
        os.system("del {0} /q".format(refer[1]))
        os.system("cls")

    if diffCount == config.wrongLimits:
        sys.exit()

    if globalCount == config.numberOfSamples:
        sys.exit()