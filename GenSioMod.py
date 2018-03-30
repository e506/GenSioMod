import os
import subprocess
import re
import ctypes
import time
import binascii
import shutil
import fileinput
import uuid
import zipfile
import configparser
from stat import *

class NewConfigParser(configparser.ConfigParser):

  def optionxform(self, optionstr):
      return optionstr

def ConfFileTextAlign(Path):

  MaxStrLength = 0
  TempLenght = 0
  Buffer = []
  TmpStrSplit = []

  config = NewConfigParser(configparser.ConfigParser())
  config.read(Path)
  for line in config.sections():
    Section = line
    for line2 in config[Section]:
      TempLenght = len(line2)
      if TempLenght > MaxStrLength:
        MaxStrLength = TempLenght

  MaxStrLength += 2

  with open(Path, "r") as f:
    for line in f:
      StrLengthCount = 0
      TmpStrSplit.clear()
      NewStr = ""
      if ":" in line:
        TmpStrSplit = line.split()
        for line2 in TmpStrSplit:
          StrLengthCount += len(line2)
          if line2 == ":":
            NewStr += " " * (MaxStrLength - StrLengthCount) + " " + line2 + " "
          else:
            NewStr += line2
        Buffer.append(NewStr)

      else:
        Buffer.append(line)

  f2 = open(Path, 'w')
  for line in Buffer:
    if ":" in line:
      f2.write("  " + line + "\n")
    else:
      f2.write(line)

def getEnvironment(ConfigPath):
  CurrentSetting = {}
  defaultSetting = {
  "Paths"    : {
                     "SioSrcRootPath"  : "F:/SioCode/5.X/Trunk/"
                 },
  "FileName" : {
                     "FileName"        : "SioMod"
                 }
  }

  if os.path.exists(ConfigPath):
    config = NewConfigParser(configparser.ConfigParser())
    config.read(ConfigPath)
    for Section in config.sections():
      for Index in config.options(Section):
        CurrentSetting[Index] = config[Section][Index]
  else:
    f = open(ConfigPath, "w")
    for line in defaultSetting:
      f.write("[" + line + "]" + "\n")
      for line2 in defaultSetting[line]:
         f.write("  " + line2 + " : " + defaultSetting[line][line2] + "\n")
      f.write("\n")
    f.close()
    for Section in defaultSetting:
      for Index in defaultSetting[Section]:
        CurrentSetting[Index] = defaultSetting[Section][Index]
    ConfFileTextAlign(ConfigPath)

  return CurrentSetting

def GetFileList(Regex):
  # This function will get destination file by regular expression
  Buffer = []

  regex = re.compile (Regex)
  for line in os.listdir("."):
    if regex.search(line):
      Buffer.append(str(line))
  return Buffer

def RecursiveDumpFilePath(TopPath, Buffer):

  for file in os.listdir(TopPath):
    path = os.path.join(TopPath, file)
    mode = os.stat(path)[ST_MODE]
    # Check file is folder
    if S_ISDIR(mode):
      RecursiveDumpFilePath(path, Buffer)
    # Check file is file
    elif S_ISREG(mode):
     if not path.endswith(".uni"):
        Buffer.append(path)
    # unrecognize file type
    else:
      print("Error!\n")

def main():

  AllFilePath       = []

  env = getEnvironment("GenSioMod.conf")
  SioList = GetFileList ("^Sio.*Pkg$")

  if not os.path.exists(env["FileName"]):
    os.mkdir(env["FileName"])
    os.mkdir(env["FileName"] + "/Org")
    os.mkdir(env["FileName"] + "/Mod")

  for name in SioList:
    RecursiveDumpFilePath(name, AllFilePath)
    if os.path.exists(env["FileName"] + "/Org"):
      shutil.copytree(env["SioSrcRootPath"] + name, env["FileName"] + "/Org/" + name)
    if os.path.exists(env["FileName"] + "/Mod"):
      shutil.copytree(name, env["FileName"] + "/Mod/" + name)

  AllFilePath.clear()
  ZipFileName = env["FileName"] + ".zip"
  RecursiveDumpFilePath(env["FileName"], AllFilePath)
  with zipfile.ZipFile (ZipFileName, 'w') as myzip:
    for line in AllFilePath:
      myzip.write(line)
  if os.path.exists (ZipFileName):
    if os.path.exists (env["FileName"]):
      shutil.rmtree (env["FileName"])

if __name__ == "__main__":
  main()
