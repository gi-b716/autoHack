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

if config.compileBeforeRun==True:
    print("Compile program(s)")
    logger.info("Compile program(s)")
    if config.skipGenerate==False:
        os.system("g++ {0}.cpp -o {0} {1}".format(config.stdFile,config.compileArgs))
    if config.skipRun==False:
        os.system("g++ {0}.cpp -o {0} {1}".format(config.sourceFile,config.compileArgs))
    print("Compile done.")

os.system("rmdir /s/q wrongOutput")
os.system("md wrongOutput")
logger.info("Cleaning wrong output history")

while True:
    os.system("cls")
    refer = data.getFileName(diffCount)
    print("Generating hack data.")
    logger.info("Generating hack data.")
    data.generateData(diffCount)
    os.system("cls")
    print("Judging")
    logger.info("Judging.")
    result = data.runHacking(diffCount)

    if result[1]==True:
        os.system("move .\\{0} .\\wrongOutput\\{0}".format(refer[0]))
        os.system("move .\\{0} .\\wrongOutput\\{0}".format(refer[1]))
        os.system("cls")
        print("Time Limit Exceeded!")
        logger.warning("Time Limit Exceeded! Exceed {0} ms".format(result[2]))
        time.sleep(config.waitTime)
        diffCount += 1

    elif result[0]==0:
        os.system("move .\\{0} .\\wrongOutput\\{0}".format(refer[0]))
        os.system("move .\\{0} .\\wrongOutput\\{0}".format(refer[1]))
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