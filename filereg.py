import re
from os import listdir
from os.path import isfile, join
import csv
from datetime import datetime


class FileReg:
    
    def __init__(self):
        
        self.extractDict = {}
        self.regexDict = {}
        
        
    def loadRegexes(self, regList):

        for line in regList:
            title, key, value = line.split(':::')
            self.regexDict[title] = ( re.compile(key) , re.compile(value) )
            
    
    def extract(self, folderPath):
        
        folderPath = folderPath.replace("\\","/")
        filesList = [ join(folderPath,f) for f in listdir(folderPath) if isfile(join(folderPath,f)) ]
        failLimit = 6
        
        for f in filesList:
            currFile = open(f, 'r', newline='')
            
            allLines = []
            
            # move file in a list
            for line in currFile:
                allLines.append(line)
            
            currFile.close()
            
            # loop settings
            hdrSet = False
            self.extractDict[f] = { key : [] for key in self.regexDict.keys() }
            
            # extraction loop (assumption: no more than one value per line)
            for line in allLines:
            
                # find header, but skip this step if header already exists
                for regType in self.regexDict.keys():
                    if self.regexDict[regType][0].match(line):
                        hdr = regType
                        hdrSet = True
                        failCount = 0
                        break
                    
                if hdrSet and failCount < failLimit:
                    if self.regexDict[hdr][1].match(line):
                        value = self.regexDict[hdr][1].match(line).group()
                        self.extractDict[f][hdr].extend(value)
                        failCount = 0 # reset failcount after each positive match
                    else:
                        failCount += 1 # increase failcount after each negative match
                else:
                    hdrSet = False # stop looking for header value after too many failcounts

    
    def exportToCsv(self,folderPath):
        pass
    
    