import dataGenerator
import logging
import time
import sys
import os

config = dataGenerator.Config()
data = dataGenerator.Data(config)
test = dataGenerator.Test()

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
    if config.skipGenerate==False:
        os.system("{0}".format(config.compileCommands.replace("$(name)",config.stdFile)))
    if config.skipRun==False:
        os.system("{0}".format(config.compileCommands.replace("$(name)",config.sourceFile)))
    print("Compile done.")

if config.previewHackDataTime > 0 and not config.skipGenerate:
    test.previewHackData()
    time.sleep(config.previewHackDataTime)
    logger.info("Preview hack data.")

# Generate hack data
if config.skipGenerate==False:
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
if config.skipRun==False:
    logger.info("Start random hacking...")
    os.system("rmdir /s/q wrongOutput")
    if config.saveWrongOutput==True:
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

        if result[1]==True:
            print("Time Limit Exceeded on data {0}!".format(samplesId))
            logger.warning("Time Limit Exceeded! On {0} and {1}, exceed {2} ms".format(refer[0],refer[1],result[2]))
            time.sleep(config.waitTime)
            diffCount += 1

        elif result[5]!=0:
            print("Runtime Error! Exit code: {0}".format(result[5]))
            logger.warning("Runtime Error! Exit code: {0}".format(result[5]))
            time.sleep(config.waitTime)
            diffCount += 1

        elif result[6]==True:
            print("Memory Limit Exceeded on data {0}!".format(samplesId))
            logger.warning("Memory Limit Exceeded! On {0} and {1}, exceed {2} MB".format(refer[0],refer[1],result[7]))
            time.sleep(config.waitTime)
            diffCount += 1

        elif result[0]==0:
            print("Catch diff on data {0}!\nAns:\n{1}\nOutput:\n{2}\n".format(samplesId,result[3],result[4]))
            logger.warning("Catch diff! See {0} and {1}".format(refer[0],refer[1]))
            time.sleep(config.waitTime)
            diffCount += 1

        if diffCount == config.wrongLimits:
            sys.exit(0)
    logger.info("Catch {0} diff".format(diffCount))
else:
    logger.info("Skip judge")

logger.info("Done.")