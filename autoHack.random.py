import dataGenerator
import logging
import time
import sys
import os

config = dataGenerator.Config()
data = dataGenerator.Data(config)

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

# Generate hack data
logger.info("Start generate hack data")
os.system("rmdir /s/q hackData")
os.system("md hackData")
logger.info("Cleaning hack data history")
for samplesId in range(config.numberOfSamples):
    refer = data.getFileName(samplesId)
    data.generateData(samplesId)
    os.system("move .\{0} .\hackData\{0}".format(refer[0]))
    os.system("move .\{0} .\hackData\{0}".format(refer[1]))
    os.system("cls")
    print("Generating hack data: {0} | {1}/{2}".format((samplesId+1)/config.numberOfSamples, samplesId+1, config.numberOfSamples))
    logger.info("Generating hack data: {0} | {1}/{2}".format((samplesId+1)/config.numberOfSamples, samplesId+1, config.numberOfSamples))

# Start random hacking
logger.info("Start random hacking...")
for samplesId in range(config.numberOfSamples):
    refer = data.getFileName(samplesId)
    os.system("move .\hackData\{0} .\{0}".format(refer[0]))
    os.system("move .\hackData\{0} .\{0}".format(refer[1]))
    os.system("cls")
    result = data.runHacking(samplesId)
    print("Judging: {0} | {1}/{2}".format((samplesId+1)/config.numberOfSamples, samplesId+1, config.numberOfSamples))
    logger.info("Judging: {0} | {1}/{2}".format((samplesId+1)/config.numberOfSamples, samplesId+1, config.numberOfSamples))
    if result[0]==False:
        print("ans: ")
        print(result[1])
        print("output: ")
        print(result[2])
        logger.warning("Catch diff! See {0} and {1}".format(refer[0],refer[1]))
        time.sleep(7)
        if config.exitWhenThereIsADiscrepancy:
            os.system("move .\{0} .\hackData\{0}".format(refer[0])) 
            os.system("move .\{0} .\hackData\{0}".format(refer[1]))
            sys.exit()
        diffCount += 1
    os.system("move .\{0} .\hackData\{0}".format(refer[0]))
    os.system("move .\{0} .\hackData\{0}".format(refer[1]))
logger.info("Catch {0} diff".format(diffCount))
logger.info("Done.")