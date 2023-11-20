__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

from ydata_profiling import ProfileReport
import argparse
from pathlib import Path
import os
import pandas as pd
import chardet

def getSourceFolder():
	parser = argparse.ArgumentParser()
	parser.add_argument("-dir", help="Folder where the files in CSV format are stored", required=True)
	args = vars(parser.parse_args())
	return args["dir"]

if __name__ == "__main__":
	links = []
	sourceFolder = getSourceFolder()
	allFiles = os.listdir(sourceFolder)

	# Profile the Datasets
	for file in allFiles:
		filename, dotextension = os.path.splitext(file)
		if (dotextension.upper() == ".CSV"):
			reportfileName = filename + ".html"
			links.append(reportfileName)
			src = sourceFolder + "/" + file
			#with open(src, 'rb') as f:
			#	result = chardet.detect(f.readline())
			pdFile = pd.read_csv(src, encoding='utf-8', on_bad_lines='warn', delimiter=";")
			prof = ProfileReport(pdFile, 
								correlations=None,
								interactions=None)
			prof.to_file(output_file=sourceFolder + "/" + reportfileName)

	# Create the index.html page
	indexContent = "<frameset cols='20%,80%'>"
	indexContent += "<frame src='menu.html' />"
	indexContent += "<frame name=profile src='{}' />".format(links[0])
	indexContent += "</frameset>"
	with open(sourceFolder + "/" + "index.html", "w") as fileIndex:
		fileIndex.write(indexContent)

	# Create the menu page
	menuContent = "<html><head></head><body><H2>Datasets Profiles</H2>"
	menuContent += "<ul>"
	for item in links:
		menuContent += "<li><A href='{}' target=profile>{}</A></li>".format(item, item)
	menuContent += "<ul></body></html>"
	with open(sourceFolder + "/" + "menu.html", "w") as fileIndex:
		fileIndex.write(menuContent)