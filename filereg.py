import re
from os import listdir
from os.path import isfile, join
import csv
from datetime import datetime


class FileReg:
    
    def __init__(self):
        
        self.extractDict = {}
        self.regexDict = {
                          'Bank_Name' : ( re.compile(r'', re.IGNORECASE),
                                          re.compile(r'', re.IGNORECASE) ),
                          'Bank_SortCode' : ( re.compile(r'', re.IGNORECASE),
                                              re.compile(r'', re.IGNORECASE) ),
                          'Bank_Acct_Nr' : ( re.compile(r'', re.IGNORECASE),
                                             re.compile(r'', re.IGNORECASE) ),
                          'Bank_SwiftBic' : ( re.compile(r'', re.IGNORECASE),
                                              re.compile(r'', re.IGNORECASE) ),
                          'Bank_IBAN' : ( re.compile(r'', re.IGNORECASE),
                                          re.compile(r'', re.IGNORECASE) ),
                          'Bank_Beneficiary' : ( re.compile(r'', re.IGNORECASE),
                                                 re.compile(r'', re.IGNORECASE) ),
                          'Phone_Nr' : ( re.compile(r'(\btel\b|\bphone\b|\btelephone\b)', re.IGNORECASE),
                                         re.compile(r'(\+|00)? ?\d{2,3} ?(\(0\))? ?[\d -.]{8,16}\d', re.IGNORECASE) ),
                          'Fax_Nr' : ( re.compile(r'\bfax\b', re.IGNORECASE),
                                       re.compile(r'(\+|00)? ?\d{2,3} ?(\(0\))? ?[\d -.]{8,16}\d', re.IGNORECASE) ),
                          'Email_From' : ( re.compile(r'', re.IGNORECASE),
                                           re.compile(r'', re.IGNORECASE) ),
                          'Email_To' : ( re.compile(r'', re.IGNORECASE),
                                         re.compile(r'', re.IGNORECASE) ),
                          'Email' : ( re.compile(r'', re.IGNORECASE),
                                      re.compile(r'', re.IGNORECASE) )
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
        fileCount = 0
        fileTot = len(filesList)
        complThresh = step = 25
        
        for f in filesList:
            
            fileCount += 1
            
            currFile = open(f, 'r', newline='')
            
            # loop settings
            hdrSet = False
            self.extractDict[f] = { key : [] for key in self.regexDict.keys() }
            
            # assuming only one key, value or key-value pair per line, more values on same line will be lost
            for line in currFile:
                # find header, but skip this step if header already exists
                for regType in self.regexDict.keys():
                    if self.regexDict[regType][0].search(line):
                        hdr = regType
                        hdrSet = True
                        failCount = 0
                        break
                    
                if hdrSet and failCount < failLimit:
                    if self.regexDict[hdr][1].findall(line):
                        values = self.regexDict[hdr][1].findall(line)
                        # add only if unique values, avoid duplicates
                        for value in values:
                            if value not in self.extractDict[f][hdr]:
                                self.extractDict[f][hdr].extend(value)
                        failCount = 0 # reset failcount after each positive match
                    else:
                        failCount += 1 # increase failcount after each negative match
                else:
                    hdrSet = False # stop looking for header value after too many failcounts
            
            currFile.close()
            
            fsp = fileCount / fileTot * 100
            
            if fsp >= complThresh:
                print("Completed scanning {:.2%} files".format(fsp))
                complThresh += step
            
        print("Scanned {} files. Found {:.2%} possible matching terms.".format(fileTot))

    
    def printResults(self):
        
        for fileID in self.extractDict.keys():
            print(fileID)
            for hdr in self.extractDict[fileID].keys():
                print("{}: {}".format(hdr, self.extractDict[fileID][hdr]))
                
            print("")
    
    
    def exportToCsv(self,folderPath):
        
        csvHeaders = ['file']
        csvHeaders.extend(self.regexDict.keys())
        folderPath = folderPath.replace("\\","/")
        fileName = folderPath + "/filereg_%s.csv" % datetime.now().strftime("%Y%m%d_%H-%M-%S")
        csvFileToWrite = open(fileName, 'a', newline='')
        
        csvWriter = csv.DictWriter(csvFileToWrite, csvHeaders, restval='', delimiter=',',
                                   extrasaction='ignore', dialect='excel', quotechar='"')
        csvWriter.writeheader()
        
        for f in self.extractDict.keys():
            
            nextField = True
            
            while nextField == True:
                
                nextField = False
                tempDict = { csvHeaders[0] : f }
                
                for key in self.extractDict[f].keys():
                    
                    try:
                        value = self.extractDict[f][key].pop()
                        nextField = True
                    except IndexError:
                        value = ''
                    finally:
                        tempDict[key] = value
                        
                # write tempDict to csv file
                if nextField:
                    csvWriter.writerow(tempDict)
                    
        # close csv file
        csvFileToWrite.close()
        print('Export completed. Data saved in {}.'.format(fileName))


import filereg


def main():
    
    folderPath = input("Enter the path: ")
    regextractor = filereg.FileReg()
    
    regextractor.extract(folderPath)
    
    regextractor.printResults()
    