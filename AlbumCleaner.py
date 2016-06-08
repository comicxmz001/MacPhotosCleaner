import os
import time
import filecmp
import random
from collections import deque
import exifread

class albumCleaner(object):
	"""
		The albumCleaner is a easy to use tool, 
		that can process duplicated files, when you mess your Photos (Mac) library up with duplicated imports

		TODO: 	1. processMov()
				2. When processing images, keep the one with an earlier modified data.
	"""
	def __init__(self, dirname = ''):
		"""
			By default, the program should be placed at the root folder of the photo album
		"""
		self._rootDir = os.getcwd()
		self._undefinedDir = os.path.join(self._rootDir,'undefined')
		if not os.path.exists(self._undefinedDir):
			os.mkdir(self._undefinedDir)
		self._log = {} # saves original names and new names, incase we need to process mov files
		print "The root folder is \'{}\'".format(self._rootDir)
		self.cleanDuplicates(os.path.join(self._rootDir,'08'))
		self.saveLog()

	def log(self, oldName, newName):
		"""
			log the rename records
		"""
		self._log[oldName] = newName

	def saveLog(self):
		"""
			save log file to ./log.txt
		"""
		f = open('./log.txt','w')
		for element in self._log:
			f.write('{} => {}\n'.format(element,self._log[element]))
		f.close()

	def cleanDuplicates(self, dirname,singleDir = True):
		"""
			go through each directory, clean up the duplicated images.
		"""
		if singleDir:
			# only process the given dir
			self.processDir(dirname)
		else:
			dirList = deque(self.getSubDirectoryList(dirname))
			while dirList:
				tmpdir = dirList.popleft()
				self.processDir(tmpdir)
				for subdir in self.getSubDirectoryList(tmpdir):
					dirList.append(subdir)

	def getSubDirectoryList(self, dirname = './'):
		"""
			return a list of lvl1 subdirectories
		"""
		dirs = set()
		directoryList = os.walk(dirname)
		for directory in directoryList:
			if isinstance(directory[0], str):
				dirs.add(directory[0])
		return list(dirs)


	def processDir(self,dirname):
		"""
			process all relevant files under this directory
		"""
		print "Currently processing \'{}\'".format(dirname)
		self._fileList = set()
		movList = []
		for file in os.listdir(dirname):
			file = os.path.join(dirname,file)
			if file.upper().endswith('.MOV'):
				movList.append(file)
			if file.upper().endswith('.JPG'):
				self.processJPG(dirname,file)
		# print self._fileList
	
	def processMov(self):
		"""
			method to process MOV files for live photo. 
			The name of mov shoud match the name of static photo.
			E.g. IMG_001.JPG & IMG_001.MOV
		"""
		pass

	def processJPG(self, dirname, filename):
		"""
			Remove duplicated JPG files, and log the changes
		"""
		print "Processing {}".format(filename)
		tags = self.readEXIF(filename)
		ext = filename[-4:].upper()
		if 'EXIF DateTimeOriginal' in tags:
			filename_new = str(tags['EXIF DateTimeOriginal'])
		else:
			# move to undefined folder
			filename_new = os.path.join(self._undefinedDir, os.path.basename(filename))
			os.rename(filename, filename_new)
			print "{} is moved to {}".format(filename, self._undefinedDir)
			return 

		filename_new = 'IMG_' + filename_new.replace(':','').replace(' ','_')
		filename_new = os.path.join(dirname,filename_new) # covnert to abs path

		# process duplicated file
		print self._fileList, filename_new+ext
		if filename_new + ext in self._fileList:
			print "Potential duplicates " + filename_new+ext
			if filecmp.cmp(filename_new + ext, filename):
				# deleted duplicated file
				os.remove(filename)
				print filename + ' is deleted!'
			else:
				# TODO: if two images have same exif date, then they are same photo,
				# 		keep the one with small os.getmtime() -- the older one.

				count = 1
				# add a new name
				while filename_new + '_' + str(count) + ext in self._fileList:
					count += 1
				# print ('newname = ' + filename_new + '_' + str(count))
				filename_new = filename_new + '_' + str(count) + ext
				self._fileList.add(filename_new)
				self.log(filename,filename_new)
				os.rename(filename,filename_new)
		else:	
			filename_new = filename_new + ext
			self._fileList.add(filename_new)
			self.log(filename, filename_new)
			print "{}=>{}".format(filename, filename_new)
			os.rename(filename, filename_new)

	def readEXIF(self, filename):
		"""
			use exifread module to read EXIF data of the given image file.
		"""
		f = open(filename,'r')
		tags = exifread.process_file(f,details=False)
		f.close()
		return tags

start_time = time.time()
ac = albumCleaner()
print("--- %s seconds ---" % (time.time() - start_time))