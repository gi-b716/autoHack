import requests
import zipfile
import sys
import os

# mirror = "https://autoHack.netlify.app/"
mirror = "https://gi-b716.github.io/autoHack/"

lasted = requests.get("{0}/LASTED".format(mirror)).content

if os.path.exists("dataGenerator.py"):
	import dataGenerator
	metaObject = dataGenerator.Meta()
	if lasted == metaObject._version:
		print("autoHack is up to date.")
		sys.exit(0)
	if metaObject._version == "":
		print("Disabled update.")
		sys.exit(0)

res = input("Check new version: {0}\nUpdate? (y/[n]): ".format(lasted))
if res != 'y':
	sys.exit(0)

path = os.path.dirname(os.path.abspath(__file__))
files = os.listdir(".")

for file in files:
	os.remove(file)

lstFile = requests.get("{0}/meta/{1}.zip".format(mirror,lasted))
with open("{0}.zip".format(lasted), "w") as zf:
	zf.write(str(lstFile.content))

with zipfile.ZipFile("{0}.zip".format(lasted), "r") as z:
	z.extractall("{0}\\".format(path))

os.remove("{0}.zip".format(lasted))

if os.path.exists(".\\requirements"):
	os.chdir("requirements")
	os.system("pip install -r requirements.txt")
	os.chdir("..")
	os.removedirs("requirements")
