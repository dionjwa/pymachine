#! /usr/bin/env python

"""
Time Machine like functionality using rsync and Python.

This script is called on the server/backup host.

Cleans and repairs a backup folder.  
If the 'current' symlink is broken, it repairs it.
If there are no backup folders, it creates an empty one with yesterdays
date and points the 'current' symlink to it.
"""

import os
import sys
import time
import datetime
import shutil
import string

def printHelpAndExit():
	print "Usage:"
	print "  pymachine <local source folder> <local or remote destination> [rsync excludes file]"
	sys.exit(1)
	
def main(*arguments):
	if len(arguments) == 0:
		printHelpAndExit()
		
	if arguments[0] == "clean":
		if len(arguments) < 2:
			print "'pymachine clean' requires a local folder as the argument"
		else:
			commandClean(arguments[1])
	elif arguments[0] == "--help":
		printHelpAndExit()
	else:
		if len(arguments) < 2:
			print "pymachine requires a source and destination"
			sys.exit(1)
		source = arguments[0]
		dest = arguments[1]
		rsyncExcludes = arguments[2] if len(arguments) >= 3 else None
		commandBackup(source, dest, rsyncExcludes)
	
def commandBackup(source, destination, rsyncExcludes=None):
	print "commandBackup source=" + source + ",  destination=" + destination + ", rsyncExcludes=" + str(rsyncExcludes)
	print "Clean up the destination folder: " + destination
	
	#If the destination is remote, copy this script to the /tmp folder
	if destination.find(":") > -1:
		command = "scp " + os.path.abspath(__file__) + " " + destination.split(":")[0] + ":" + os.path.join("/tmp", os.path.basename(__file__))
		print command
		os.system(command)
	
	commandClean(destination)	
	# #Clean, maybe remotely
	# if destination.find(":") > -1:
	# 	command = "ssh " + destination.split(":")[0] + " '/tmp/" + os.path.basename(__file__) + " clean " + destination.split(":")[1] + "'"
	# 	os.system(command)
	# else:
	# 	commandClean(destination)
		
	date = datetime.datetime.now()
	commandSync(source, destination, date, rsyncExcludes)
	commandClean(destination)

def commandClean(folder):
	#If the destination is remote, copy this script to the /tmp folder
	# if folder.find(":") > -1:
	# 	command = "scp " + os.path.abspath(__file__) + " " + folder.split(":")[0] + ":" + os.path.join("/tmp", os.path.basename(__file__))
	# 	print command
	# 	os.system(command)
		
	#Clean, maybe remotely
	if folder.find(":") > -1:
		command = "ssh " + folder.split(":")[0] + " '/tmp/" + os.path.basename(__file__) + " clean " + folder.split(":")[1] + "'"
		os.system(command)
	else:
		commandCleanInternal(folder)
	
def commandCleanInternal(folder):
	os.system('mkdir -p ' + folder)
	os.chdir(folder)
	
	#Check for healthy 'current' symlink
	foldersInBackupDir = os.listdir(os.getcwd())
	backupFolders = [f for f in os.listdir(os.getcwd()) if filterForBackupFolders(f)]
	
	toDelete = filterOldBackups(backupFolders)
	for oldFolder in toDelete:
		print "Deleting backup folder \n\t",  os.path.join(os.getcwd(), oldFolder)
		shutil.rmtree(oldFolder)
	
	#If the current cymlink isinstance broken, remove it
	if foldersInBackupDir.count('current') > 0:
		print 'Removing symlink current'
		os.unlink('current')
		
	#Reset the symlink
	backupFolders.sort()
	empty_folder_placeholder = 'empty'
	if len(backupFolders) == 0:
		pass
		# backupFolders.append( 'back-delete' )
		if os.path.exists(empty_folder_placeholder):
			shutil.rmtree(empty_folder_placeholder)
		os.mkdir(empty_folder_placeholder)
		print 'Creating symlink current->', empty_folder_placeholder
		os.symlink(empty_folder_placeholder, 'current')
	else:
		print 'Creating symlink current->', backupFolders[-1]
		os.symlink(backupFolders[-1], 'current')
		
		if os.path.exists(empty_folder_placeholder):
			shutil.rmtree(empty_folder_placeholder)

def commandSync(source, destination, date=None, rsyncexcludes=None):
	date = date if date else datetime.date.today()
	dateFolder = convertDateToBackupFolder(date)
	formatArgs = '--exclude-from="' + rsyncexcludes + '"' if rsyncexcludes else ""
	linkDestination = destination if len(destination.split(":")) == 1 else destination.split(":")[1]
	command = 'rsync -az ' + formatArgs + ' --link-dest="' + linkDestination + '/current" ' + source + '/ ' + destination + '/' + dateFolder + "/"
	print command
	os.system(command)

def commandPostSync(backupFolder, date):
	
	if destination.find(":") > -1:
		command = "ssh " + destination.split(":")[0] + " '/tmp/" + os.path.basename(__file__) + " clean " + destination.split(":")[1] + "'"
		os.system(command)
	else:
		commandClean(destination)
	
	os.chdir(backupFolder)
	if foldersInBackupDir.count('current') > 0:
		print "Unlinking " + os.path.join(backupFolder, 'current')
		os.unlink('current')
	print "Linking current->" + convertDateToBackupFolder(date) 
	os.symlink(convertDateToBackupFolder(date), 'current')
	
def convertDateToBackupFolder(date=None):
	date = date if date else datetime.datetime.now()
	return date.strftime("backup-%Y-%m-%d_%H-%M-%S")

def convertBackupFolderToDate( folder ):#{{{ 

	childFolder = os.path.basename(folder)
	childFolder = childFolder.replace("backup-", "").replace("back-", "")
	datetimetokens = childFolder.split("_")
	datetokens = datetimetokens[0].split("-")
	timetokens = datetimetokens[1].split("-")
	
	year = int(datetokens[0])
	month = int(datetokens[1])
	day = int(datetokens[2])
	hour = int(timetokens[0])
	minute = int(timetokens[1])
	second = int(timetokens[2])
	
	return datetime.datetime(year, month, day, hour, minute, second)
 #}}}
   
def filterForBackupFolders( testFolder ):#{{{ 

	return testFolder.find('back-') > -1 or testFolder.find('backup-') > -1 #or testFolder.find( 'delete' ) > -1 
#}}}

def last_day_of_month(date):#{{{ 

	if date.month == 12:
		return date.replace(day=31)
	return date.replace(month=date.month+1, day=1) - datetime.timedelta(days=1)
#}}}

def filterOldBackups( backupdirs ):#{{{ 

	#Start by assuming all backup folders will be kept
	folder2Delete = dict([(f,False) for f in backupdirs])
	time2Folder = dict([(convertBackupFolderToDate(f), f) for f in backupdirs])
	
	times = time2Folder.keys()
	times.sort()
	times.reverse()
	
	now = datetime.datetime.now()
	
	
	#Only one backup per month, if older than a three months
	threeMonthsWeekAgo = now  - datetime.timedelta(90)
	currentMonthStart = None
	currentMonthEnd = None

	for time in times: 
		
		#Ignore if we are already deleted
		if folder2Delete[ time2Folder[time] ]:
			continue
			
		if time < threeMonthsWeekAgo:#Only check folders more than three months old
			folder = time2Folder[time]
			
			if currentMonthStart != None and time >= currentMonthStart and time <= currentMonthEnd:
				print "deleting because too many on month ", time
				folder2Delete[ folder ] = True
			else:
				currentMonthStart = datetime.datetime(time.year, time.month, 1)
				print 'currentMonthStart=', time
				print last_day_of_month(currentMonthStart)
				currentMonthEnd = datetime.datetime(currentMonthStart.year, currentMonthStart.month, last_day_of_month(currentMonthStart).day) 
				


	#Only one backup per week, if older than a week
	oneWeekAgo = now  - datetime.timedelta(7 + now.weekday())
	currentWeekStart = None
	currentWeekEnd = None

	for time in times: 
		
		#Ignore if we are already deleted
		if folder2Delete[ time2Folder[time] ]:
			continue
			
		if time < oneWeekAgo:#Only check folders more than a whole week old
			folder = time2Folder[time]
			
			if currentWeekStart != None and time >= currentWeekStart and time <= currentWeekEnd:
				folder2Delete[ folder ] = True
			else:
				currentWeekStart = datetime.datetime(time.year, time.month, time.day) - datetime.timedelta(time.weekday())
				currentWeekEnd = datetime.datetime(currentWeekStart.year, currentWeekStart.month, currentWeekStart.day) + datetime.timedelta(6)

	
	
	oneDayAgo = now  - datetime.timedelta(1)
	dayInTime = None 
	#Only one backup per day, if older than a day
	for time in times: 
		
		#Ignore if we are already deleted
		if folder2Delete[ time2Folder[time] ]:
			continue
		
		if time < oneDayAgo:#Make sure we are older than a day
			folder = time2Folder[time]
			
			coarseDay = datetime.datetime( time.year, time.month, time.day )
			
			if not dayInTime or coarseDay != dayInTime:
				dayInTime = coarseDay
			else:#It's the same day, delete
				folder2Delete[ folder ] = True
			
	
	


				
	# for time in times: 
	#	 print time, '\t\t', folder2Delete[time2Folder[time]], '\t', time.weekday()
	
	return [ f for f in backupdirs if folder2Delete[f] ]
   #}}}
 
def isSymlinkOk( path ) :#{{{ 

	try:
		os.stat(path)
		return 1
	except:
		print 'path %s does not exist or is a broken symlink' % path
		return 0 #}}}

	
if __name__ == '__main__':
	# f = convertDateToBackupFolder()
	# print f
	# print convertBackupFolderToDate(f)
	print "sys.argv=" + str(sys.argv)
	main(*sys.argv[1:])
	# print os.path.abspath(__file__)
	# print os.path.basename( __file__)
	# commandBackup('/Users/dion/tmp/testy', '/tmp/backup')
	
	
	
