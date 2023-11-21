__author__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

from ydata_profiling import ProfileReport
import argparse
import os
import pandas as pd
from jinja2 import Template
import pathlib
import shutil
import json

COMPLETEPROF_TEMPLATEDIR = "./complete/"
SIMPLEPROF_TEMPLATEDIR = "./simple/"
COMPLETE_MENU = "menu.html"
COMPLETE_INDEX = "index.html"
COMPLETE_HOME = "home.html"
BOOTSTRAP_CSS = "bootstrap.css"
BOOTSTRAP_JS = "bootstrap.bundle.min.js"
EXT_CSV = ".CSV"

class JinjaProfileItem:
	def __init__(self, filename, columns, rowcount):
		self.link = filename
		self.name = os.path.splitext(filename)[0]
		self.columns = columns
		self.columnsCount = len(columns)
		self.rowsCount = rowcount

class SimpleColumnProfile:
	def __init__(self, name, distinct, missing, type, is_unique, freqDistrib):
		self.name = name
		self.distinct = distinct
		self.missing = missing
		self.type = type
		self.is_unique = is_unique
		self.freqDistrib = freqDistrib

class Options:
	def __init__(self, directory, delimiter, encoding, destination):
		self.directory = directory
		self.delimiter = delimiter
		self.encoding = encoding
		self.__destimation__ = destination
	@property
	def destination(self): 
		return self.__destimation__ if len(self.__destimation__)>0 else self.directory

def getCLIArguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("-dir", help="Folder where the files in CSV format are stored", required=True)
	parser.add_argument("-sep", help="CSV column delimiter (comma by default)", required=False, default=",")
	parser.add_argument("-enc", help="Encoding (default UTF-8)", required=False, default="utf-8")
	parser.add_argument("-dest", help="Destination folder for the reports", required=False, default="")
	args = vars(parser.parse_args())
	return 	Options(args["dir"], args["sep"], args["enc"], args["dest"]) 

def getFreqDistribution(data):
	try:
		return len(data["word_counts"])
	except:
		return "N.A."

def buildCompleteProfile(files, options):
	links = [] 
	# Create the destination directory if not exists
	if (not os.path.isdir(options.destination)):
		os.makedirs(options.destination)
	# Profile the Datasets
	for file in files:
		filename, dotext = os.path.splitext(file)
		if (dotext.upper() == EXT_CSV):
			rptName = filename + ".html"
			# Read the CSV file
			pdFile = pd.read_csv(options.directory + "/" + file, 
								encoding=options.encoding, 
								on_bad_lines='warn', 
								delimiter=options.delimiter)
			# Profile the dataset
			profile = ProfileReport(pdFile, 
						   sort="ascending", 
						   correlations=None, 
						   interactions=None)
			# Get the basics from the profiling
			details = json.loads(profile.json)["variables"]
			dsColumns = []
			for col in details:
				freqDistrib = getFreqDistribution(details[col])
				sProf = SimpleColumnProfile(col, 
								details[col]["n_distinct"], 
								details[col]["n_missing"],
								details[col]["type"],
								details[col]["is_unique"],
								freqDistrib)
				dsColumns.append(sProf)
			links.append(JinjaProfileItem(rptName, dsColumns, pdFile.shape[0]))
			fullRptName = options.destination + "/" + rptName
			profile.to_file(output_file=fullRptName)
	return links

def buildHTMLtructure(links, destinationFolder):
	# Create the menu.html page with the profiled datasets pages
	templateContent = pathlib.Path(COMPLETEPROF_TEMPLATEDIR + COMPLETE_MENU).read_text()
	j2_template = Template(templateContent)
	htmlContent = j2_template.render(links=links)
	with open(destinationFolder + "/" + COMPLETE_MENU, "w") as fileIndex:
		fileIndex.write(htmlContent)
	# Create the home.html page with the profiling basics infos
	templateContent = pathlib.Path(COMPLETEPROF_TEMPLATEDIR + COMPLETE_HOME).read_text()
	j2_template = Template(templateContent)
	htmlContent = j2_template.render(links=links)
	with open(destinationFolder + "/" + COMPLETE_HOME, "w") as fileIndex:
		fileIndex.write(htmlContent)
	# Copy the index html files (basic copy)
	shutil.copy(COMPLETEPROF_TEMPLATEDIR + BOOTSTRAP_CSS, destinationFolder)
	shutil.copy(COMPLETEPROF_TEMPLATEDIR + BOOTSTRAP_JS, destinationFolder)
	shutil.copy(COMPLETEPROF_TEMPLATEDIR + COMPLETE_INDEX, destinationFolder)

if __name__ == "__main__":
	# get the options from the CLI
	options = getCLIArguments()
	# List all the fils in the source directory
	files = os.listdir(options.directory)
	# Profile the Datasets
	links = buildCompleteProfile(files, options)
	# Create the menu.html page with the profiled datasets pages
	buildHTMLtructure(links, options.destination)
