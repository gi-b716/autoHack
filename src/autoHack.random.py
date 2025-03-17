import dataGenerator
import logging
import time
import sys
import os

config = dataGenerator.Config()
data = dataGenerator.Data(config)
utils = dataGenerator.Utils()

diffCount = 0

if not os.path.isdir(".autohack"):
    os.mkdir(".autohack")
    os.system("attrib +h .autohack")

# Init logger
os.system("mkdir .autohack\\logs\\random")
logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logFile = logging.FileHandler(".autohack\\logs\\random\\hackLog.random.{0}.log".format(time.strftime("%Y-%m-%d_%H-%M-%S",time.localtime(time.time()))))
logFile.setLevel(logging.DEBUG)
logFile.setFormatter(logFormatter)
logger.addHandler(logFile)
logger.info("Init logger")

# Init output
os.system("echo off")
os.system("cls")

if config.compileBeforeRun:
    print("Compile program(s)")
    logger.info("Compile program(s)")
    if not config.skipGenerate:
        os.system("{0}".format(config.compileCommands[1]))
    if not config.skipRun:
        os.system("{0}".format(config.compileCommands[0]))
    if config.useCustomChecker:
        os.system("{0}".format(config.compileCheckerCommands))
    if config.useInteractor:
        if not config.skipGenerate:
            os.system("{0}".format(config.compileCommandsExtra[1]))
        if not config.skipRun:
            os.system("{0}".format(config.compileCommandsExtra[0]))
        if config.useMiddleFile:
            os.system("{0}".format(config.compileCommandsExtra[2]))
    if config.compileCustomGenerator:
        os.system("{0}".format(config.compileGeneratorCommands))
    print("Compile done.")

if config.previewHackDataTime > 0 and not config.skipGenerate:
    print()
    utils.previewHackData()
    time.sleep(config.previewHackDataTime)
    logger.info("Preview hack data.")

# Generate hack data
if not config.skipGenerate:
    logger.info("Start generate hack data")
    os.system("rmdir /s/q hackData")
    os.system("md hackData")
    logger.info("Cleaning hack data history")
    for samplesId in range(config.numberOfSamples):
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
if not config.skipRun:
    logger.info("Start random hacking...")
    os.system("rmdir /s/q wrongOutput")
    if config.saveWrongOutput:
        os.system("md wrongOutput")
        logger.info("Cleaning wrong output history")
    for samplesId in range(config.numberOfSamples):
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

        if result[1]:
            logData = "Time Limit Exceeded! Exceed {0} ms".format(result[2])
            if config.useInteractor:
                logData = "Time Limit Exceeded on part {0}! Exceed {1} ms".format(result[9],result[2])
            print("{0}".format(logData))
            logger.warning("{0}".format(logData))
            time.sleep(config.waitTime)
            diffCount += 1

        elif result[5]!=0:
            logData = "Runtime Error! Exit code: {0}".format(result[5])
            if config.useInteractor:
                logData = "Runtime Error on part {0}! Exit code: {1}".format(result[9],result[5])
            print("{0}".format(logData))
            logger.warning("{0}".format(logData))
            time.sleep(config.waitTime)
            diffCount += 1

        elif result[6]:
            logData = "Memory Limit Exceeded! Exceed {0} MB".format(result[7])
            if config.useInteractor:
                logData = "Memory Limit Exceeded on part {0}! Exceed {1} MB".format(result[9],result[7])
            print("{0}".format(logData))
            logger.warning("{0}".format(logData))
            time.sleep(config.waitTime)
            diffCount += 1

        elif config.useCustomChecker and config.useTestlib:
            checkerResFile = open(".\\.autohack\\checkerResult","r")
            checkerRes = checkerResFile.read()
            checkerResFile.close()
            os.system("del .\\.autohack\\checkerResult /q")
            print("{0}".format(checkerRes))
            logger.debug("{0} Exit code: {1}.".format(checkerRes.replace("\n"," | "),result[8]))
            if result[0]==-1:
                print("Checker failed!")
                os.system("{0}".format(config.commandAtEnd))
                sys.exit(0)
            if result[0]!=1:
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
            os.system("{0}".format(config.commandAtEnd))
            sys.exit(0)

    logger.info("Catch {0} diff".format(diffCount))
else:
    logger.info("Skip judge")

logger.info("Done.")
os.system("{0}".format(config.commandAtEnd))
