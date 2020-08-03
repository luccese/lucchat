import urllib.request
import os
from bs4 import BeautifulSoup
import zipfile
import psutil

def installTor():
	print("Wait, I'm downloading tor.zip")
	urllib.request.urlretrieve("https://torproject.org" + BeautifulSoup(urllib.request.urlopen('https://torproject.org/download/tor/').read(), 'html.parser').find("a", class_="downloadLink")["href"], filename="tor.zip")
	with zipfile.ZipFile("tor.zip", 'r') as zip_ref: zip_ref.extractall("TOR")
	print("Unziping...")
	with open("TOR\\Tor\\torrc", "a") as torrc: torrc.write("HiddenServiceDir " + os.getcwd() + "\nHiddenServicePort 5555 127.0.0.1:5555")
	print("torrc was created, tor installed.")
	os.remove('tor.zip')
	checkInstall()

def checkInstall():
	if os.path.isfile("TOR\\Tor\\torrc"):
		print("tor installed.")
		return True
	else:
		installTor()

def checkRunning():
	for p in psutil.process_iter(attrs=['pid', 'name']):
		if p.info['name'] == "tor.exe":
			print("Tor already running")
			return True

def runTor():
	print("Running tor.exe")
	os.popen("TOR\\Tor\\tor.exe")