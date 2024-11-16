import requests
import zipfile
import sys
import os

mirrorList = [["https://autohack.netlify.app/", "autohack.netlify.app"], ["https://gi-b716.github.io/autoHack/", "gi-b716.github.io"]]

if os.path.exists("dataGenerator.py"):
	import dataGenerator
	metaObject = dataGenerator.Meta()
	if metaObject._version == "":
		print("Disabled update.")
		sys.exit(0)

for i in range(len(mirrorList)):
	print("{0}. {1}".format(i, mirrorList[i][0]))
	os.system("ping {0} -n 2 -w 500".format(mirrorList[i][1]))
	print()

mirror = mirrorList[int(input("Set mirror: "))][0]

os.system("cls")

lasted = str(requests.get("{0}/LASTED".format(mirror)).content, "utf-8")

if os.path.exists("dataGenerator.py"):
	import dataGenerator
	metaObject = dataGenerator.Meta()
	if lasted == metaObject._version:
		print("autoHack is up to date.")
		sys.exit(0)

res = input("Check new version: {0}\nUpdate? (y/[n]): ".format(lasted))
if res != 'y':
	sys.exit(0)

path = os.path.dirname(os.path.abspath(__file__))
files = os.listdir(".")

for file in files:
	if os.path.isdir(file):
		os.system("rmdir /s/q {0}".format(file))
	else:
		os.system("del {0}".format(file))

lstFile = requests.get("{0}/meta/{1}.zip".format(mirror,lasted))
with open("{0}.zip".format(lasted), "wb") as zf:
	zf.write(lstFile.content)

with zipfile.ZipFile("{0}.zip".format(lasted), "r") as z:
	z.extractall("{0}\\".format(path))

os.remove("{0}.zip".format(lasted))

if os.path.exists(".\\requirements"):
	os.chdir("requirements")
	os.system("pip install -r requirements.txt")
	os.chdir("..")
	os.system("rmdir /s/q requirements")
