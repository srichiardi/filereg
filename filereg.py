import re
from os import listdir
from os.path import isfile, join
import csv
from datetime import datetime


class FileReg:
    
    def __init__(self):
        
        self.extractDict = {}
        self.regexDict = {
                          'Bank_Name' : { re.compile() : re.compile() },
                          'Bank_SortCode' : { re.compile() : re.compile() },
                          'Bank_Acct_Nr' : { re.compile() : re.compile() },
                          'Bank_SwiftBic' : { re.compile() : re.compile() },
                          'Bank_IBAN' : { re.compile() : re.compile() },
                          'Bank_Beneficiary' : { re.compile() : re.compile() },
                          'Phone_Nr' : { re.compile() : re.compile() },
                          'Fax_Nr' : { re.compile() : re.compile() },
                          'Email_From' : { re.compile() : re.compile() },
                          'Email_To' : { re.compile() : re.compile() },
                          'Email' : { re.compile() : re.compile() }
                          }
        
        
    def loadRegexes(self, regList):
        ''' adding custom regexes to default '''

        for line in regList:
            title, key, value = line.split(':::')
            self.regexDict[title] = ( re.compile(key) , re.compile(value) )
            
    
    def extract(self, folderPath):
        
        folderPath = folderPath.replace("\\","/")
        filesList = [ join(folderPath,f) for f in listdir(folderPath) if isfile(join(folderPath,f)) ]
        failLimit = 6
        
        for f in filesList:
            currFile = open(f, 'r', newline='')
            
            # loop settings
            hdrSet = False
            self.extractDict[f] = { key : [] for key in self.regexDict.keys() }
            
            # assuming only one key, value or key-value pair per line, more values on same line will be lost
            for line in currFile:
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
                        # add only if unique values, avoid duplicates
                        if value not in self.extractDict[f][hdr]:
                            self.extractDict[f][hdr].extend(value)
                        failCount = 0 # reset failcount after each positive match
                    else:
                        failCount += 1 # increase failcount after each negative match
                else:
                    hdrSet = False # stop looking for header value after too many failcounts
            
            currFile.close()

    
    def exportToCsv(self,folderPath):
        pass
    
    