import requests
import zipfile
import sys
import os

if "-help" in sys.argv or "-h" in sys.argv:
	print("""autoHack Automatic Upgrade Module Help

-help / -h: Display this help message
-dev: Receive updates for dev versions
-force: Force update to the latest version of the selected channel
-debug: Show debug message""")
	sys.exit(0)

mirrorList = ["https://autohack.netlify.app/", "https://gi-b716.github.io/autoHack/", "https://autohack.pages.dev/"]
pingTime = []

if os.path.exists("dataGenerator.py"):
	import dataGenerator
	metaObject = dataGenerator.Meta()
	if metaObject._version == "":
		print("Disabled update.")
		sys.exit(0)

lasted = None
debugTag = False
channal = "LASTED"

if "-dev" in sys.argv:
	channal = "DEV"

if "-debug" in sys.argv:
	debugTag = True

print("Searching for the fastest image source.")

for mirrorID in range(len(mirrorList)):
	res = None
	mirror = mirrorList[mirrorID]
	try:
		res = requests.get("{0}/{1}".format(mirror,channal), timeout=5)
		lasted = str(res.content, "utf-8")
	except:
		pingTime.append(1000000.0)
		if debugTag: print("> \"{0}\": Time Out! <".format(mirror), file=sys.stderr)
	else:
		pingTime.append(res.elapsed.total_seconds())
		if debugTag: print("> \"{0}\": {1}s <".format(mirror, res.elapsed.total_seconds()), file=sys.stderr)
	print("Searching for the fastest image source. ({0}/{1})".format(mirrorID+1,len(mirrorList)))

if lasted == None:
	print("\nCheck your network connection!")
	sys.exit(-1)

if os.path.exists("dataGenerator.py"):
	import dataGenerator
	metaObject = dataGenerator.Meta()
	if lasted == metaObject._version and "-force" not in sys.argv:
		print("\nautoHack is up to date.")
		sys.exit(0)

res = input("\nCheck new version: {0}\nUpdate? (y/[n]): ".format(lasted))
if res != 'y':
	sys.exit(0)

path = os.path.dirname(os.path.abspath(__file__))
files = os.listdir(".")

mirror = mirrorList[pingTime.index(min(pingTime))]
if debugTag: print("> Mirror: \"{0}\" <".format(mirror), file=sys.stderr)

lstFile = requests.get("{0}/meta/{1}.zip".format(mirror,lasted))

for file in files:
	if os.path.isdir(file):
		os.system("rmdir /s/q {0}".format(file))
	else:
		os.system("del {0}".format(file))

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
