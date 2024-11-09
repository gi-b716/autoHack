import dataGenerator
import logging
import time
import sys
import os

config = dataGenerator.Config()
data = dataGenerator.Data(config)

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
    os.system("{0}".format(config.compileCommands.replace("$(name)",config.stdFile)))
    os.system("{0}".format(config.compileCommands.replace("$(name)",config.sourceFile)))
    print("Compile done.")

os.system("rmdir /s/q wrongOutput")
os.system("md wrongOutput")
os.system("rmdir /s/q hackData")
os.system("md hackData")
logger.info("Cleaning wrong output history")

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

    if result[1]==True:
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[0]))
        os.system("move .\\{0} .\\hackData\\{0}".format(refer[1]))
        os.system("cls")
        print("Time Limit Exceeded!")
        logger.warning("Time Limit Exceeded! Exceed {0} ms".format(result[2]))
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

    else:
        os.system("del {0} /q".format(refer[0]))
        os.system("del {0} /q".format(refer[1]))
        os.system("cls")

    if diffCount == config.wrongLimits:
        sys.exit()

    if globalCount == config.numberOfSamples:
        sys.exit()