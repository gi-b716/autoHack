import sys
import os

directoryPath = os.path.dirname(os.path.abspath(__file__))
argvL = sys.argv
argvLen = len(argvL)
cwd = os.getcwd()

try:
	import func_timeout
except:
	os.chdir("{0}\\requirements".format(directoryPath))
	os.system("pip install -r requirements.txt")

if argvLen == 1:
	newCwd = "{0}\\Hack".format(cwd)
	os.chdir("{0}".format(cwd))
	os.system("mkdir Hack")
	os.chdir("{0}".format(newCwd))
	os.system("copy {0}\\autoHack.infinite.py {1}".format(directoryPath,newCwd))
	os.system("copy {0}\\autoHack.random.py {1}".format(directoryPath,newCwd))
	os.system("copy {0}\\dataGenerator.py {1}".format(directoryPath,newCwd))
	os.system("cls")

elif argvLen == 2:
	newCwd = "{0}\\Hack-{1}".format(cwd,argvL[1])
	os.chdir("{0}".format(cwd))
	os.system("mkdir Hack-{0}".format(argvL[1]))
	os.chdir("{0}".format(newCwd))
	os.system("copy {0}\\autoHack.infinite.py {1}".format(directoryPath,newCwd))
	os.system("copy {0}\\autoHack.random.py {1}".format(directoryPath,newCwd))
	os.system("copy {0}\\dataGenerator.py {1}".format(directoryPath,newCwd))
	os.system("cls")