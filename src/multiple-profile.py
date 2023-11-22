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

TEMPLATEDIR = "./templates/"
STATICDIR = "./statics/"
SIMPLEPROF_TEMPLATEDIR = "./simple/"
COMPLETE_MENU = "menu.html"
COMPLETE_INDEX = "index.html"
COMPLETE_HOME = "home.html"
BOOTSTRAP_CSS = "bootstrap.css"
BOOTSTRAP_JS = "bootstrap.bundle.min.js"
EXT_CSV = ".CSV"
FILES_TO_COPY_AS_IS = [ BOOTSTRAP_CSS, BOOTSTRAP_JS, COMPLETE_INDEX ]

class Column:
	def __init__(self):
		self.name = ""
		self.tables = []
	def addTable(self, tableName):
		self.tables.append(tableName)

class Columns:
	def __init__(self):
		self.columns = []
	def add(self, name, tables):
		myCol = Column()
		self.columns.append()


class JinjaProfileItem:
	""" This class contains all the information needed for generating the HTML (Home & Index rendering)
	"""
	def __init__(self, filename, columns, rowcount):
		self.link = filename
		self.name = os.path.splitext(filename)[0]
		self.columns = columns
		self.columnsCount = len(columns)
		self.rowsCount = rowcount

class SimpleColumnProfile:
	""" This Class contains the brut profile data by column (per table)
	"""
	def __init__(self, name, distinct, missing, type, is_unique, freqDistrib):
		self.name = name
		self.distinct = distinct
		self.missing = missing
		self.type = type
		self.is_unique = is_unique
		self.freqDistrib = freqDistrib

class Options:
	""" This Class contains the options gathered from the Command line
	"""
	def __init__(self, directory, delimiter, encoding, destination):
		self.directory = directory
		self.delimiter = delimiter
		self.encoding = encoding
		self.__destimation__ = destination
	@property
	def destination(self): 
		return self.__destimation__ if len(self.__destimation__)>0 else self.directory

def getCLIArguments():
	""" Checks & Gather the command line parameters
	Returns:
		Options: options requested
	"""
	parser = argparse.ArgumentParser()
	parser.add_argument("-dir", help="Folder where the files in CSV format are stored", required=True)
	parser.add_argument("-sep", help="CSV column delimiter (comma by default)", required=False, default=",")
	parser.add_argument("-enc", help="Encoding (default UTF-8)", required=False, default="utf-8")
	parser.add_argument("-dest", help="Destination folder for the reports", required=False, default="")
	args = vars(parser.parse_args())
	return 	Options(args["dir"], args["sep"], args["enc"], args["dest"]) 

def getFreqDistribution(data):
	""" Get the word_counts value size (which can not exist depending on the column type)
	Args:
		data (json): Column informations from the profile
	Returns:
		str: return the number of different values (categorical)
	"""
	try:
		return len(data["word_counts"])
	except:
		return "N.A."

def buildCompleteProfile(files, options):
	""" Build the Profile of all the files in the folder
	Args:
		files (array): all the files to profile
		options (options): CLI options
	Returns:
		array: profile data
	"""
	profiles = []
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
			profiles.append(JinjaProfileItem(rptName, dsColumns, pdFile.shape[0]))
			fullRptName = options.destination + "/" + rptName
			profile.to_file(output_file=fullRptName)
	return profiles

def copyFromtemplate(options, templateFile, profiles):
	# Create the home.html page with the profiling basics infos
	templateContent = pathlib.Path(TEMPLATEDIR + templateFile).read_text()
	j2_template = Template(templateContent)
	htmlContent = j2_template.render(profiles=profiles, 
								  	sourcefolder=options.directory)
	with open(options.destination + "/" + templateFile, "w") as fileIndex:
		fileIndex.write(htmlContent)

def buildHTMLtructure(profiles, options):
	"""Create the HTML files accordingly by using JINJA2
	Args:
		links (array): profile data for all files
		options (Options): profile Options
	"""
	# Create the menu.html page with the profiled datasets pages
	copyFromtemplate(options, COMPLETE_MENU, profiles)
	# Create the home.html page with the profiling basics infos
	copyFromtemplate(options, COMPLETE_HOME, profiles)

def prepareHTML(options):
	""" Create the HTML structure. Copy the statics files / Create the html structure
	Args:
		destFolder (str): detination folder name
	"""
	try:
		# Create the destination directory if not exists
		#if (not os.path.isdir(options.destination)):
		#	os.makedirs(options.destination)
		# Copy the static files
		shutil.copytree(STATICDIR, options.destination)
	except:
		pass

if __name__ == "__main__":
	# get the options from the CLI
	options = getCLIArguments()
	# List all the fils in the source directory
	files = os.listdir(options.directory)
	prepareHTML(options)
	# Profile the Datasets
	profiles = buildCompleteProfile(files, options)
	# Create the menu.html page with the profiled datasets pages
	buildHTMLtructure(profiles, options)
