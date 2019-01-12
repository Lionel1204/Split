import os
import sys
import cv2
from OSSManager import OSSManager
import Utils
from configparser import ConfigParser
from LoggingHelper import Logger
import shutil
import json

_logger = Logger()

def mainProcess(exId):
  manifest = {}
  idPath = exId
  if exId != 'example':
    idPath = Utils.genMD5(exId)
  tempPath, remotePath, videoFilesArr = downloadVideos(idPath)

  for vf in videoFilesArr:
    count = splitVideo(tempPath, vf)
    manifest[vf.split('.')[0]] = count - 1

  manifest["id"] = exId
  maniPath = createManifest(idPath, manifest, tempPath)
  uploadImages(idPath, tempPath, remotePath)
  uploadManifest(idPath, maniPath, remotePath)
  cleanTemp(tempPath)

def createManifest(userId, manifest, tempPath):
  filename = '{0}.json'.format(userId)
  maniPath = os.path.join(tempPath, filename)
  with open(maniPath, 'w') as jsonfile:
    json.dump(manifest, jsonfile)
  return maniPath

def uploadManifest(userId, maniPath, ossPath):
  om = OSSManager()
  filename = '{0}.json'.format(userId)
  uploadPath = os.path.join(ossPath, userId, filename)
  om.uploadFile(uploadPath, maniPath)

def cleanTemp(path):
  if os.path.exists(path):
    shutil.rmtree(path)

def downloadVideos(idPath):
  om = OSSManager()

  ossPath, localPath, videoFiles = getVideoInfo()
  if not os.path.exists( localPath):
    os.makedirs(localPath)

  tempPath = os.path.join(localPath, idPath)
  remotePath = os.path.join(ossPath, idPath)
  if not os.path.exists(tempPath):
    os.makedirs(tempPath)

  videoFilesArr = videoFiles.split(',')
  for vf in videoFilesArr:
    tempFilePath = os.path.join(tempPath, vf)
    remoteFilePath = os.path.join(remotePath, vf)

    if not os.path.isfile(tempFilePath):
      om.downloadFile(remoteFilePath, tempFilePath)
      _logger.logger.info("Download File from {0} to {1}".format(remotePath, tempPath))

  return tempPath, remotePath, videoFilesArr

def uploadImages(userId, tempPath, ossPath):
  om = OSSManager()
  uploadPath = os.path.join(ossPath, userId)

  for (dirpath, dirnames, filenames) in os.walk(tempPath):
    for file in filenames:
      if ".jpg" in file:
        uploadFilePath = os.path.join(uploadPath, file)
        localFilePath = os.path.join(tempPath, file)
        om.uploadFile(uploadFilePath, localFilePath)

def getVideoInfo():
  config = ConfigParser()
  config.read('./config.ini')
  localPath = config.get('LOCAL', 'temp.path')
  ossPath = config.get('OSS', 'video.path')
  videoFiles = config.get('OSS', 'video.name')
  return ossPath, localPath, videoFiles

def splitVideo(path, fileName):
  videoPath = os.path.join(path, fileName)
  vidcap = cv2.VideoCapture(videoPath)
  success, image = vidcap.read()
  count = 0
  while success:
    success, image = vidcap.read()
    frameName = "{0}_{1}.jpg".format(fileName.split('.')[0], count)
    cv2.imwrite(os.path.join(path, frameName), image)  # save frame as JPEG file
    if cv2.waitKey(10) == 27:
      break
    count += 1

  return count

if __name__ == "__main__":
  if len(sys.argv) == 2:
    exId = sys.argv[1]
    mainProcess(exId)
