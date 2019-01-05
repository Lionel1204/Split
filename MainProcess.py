import os
import sys
import cv2
from OSSManager import OSSManager
import Utils
from configparser import ConfigParser
from LoggingHelper import Logger

_logger = Logger()

def mainProcess(exId):
  idPath = Utils.genMD5(exId)
  tempPath, remotePath, videoFilesArr = downloadVideos(idPath)
  for vf in videoFilesArr:
    splitVideo(tempPath, vf)


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
    frameName = "frame_%d_%d.jpg".format(fileName.split('.')[0], count)
    cv2.imwrite(frameName, image)  # save frame as JPEG file
    if cv2.waitKey(10) == 27:
      break
    count += 1


if __name__ == "__main__":
  if len(sys.argv) == 2:
    exId = sys.argv[1]
    mainProcess(exId)