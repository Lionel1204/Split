import os
import oss2
import subprocess
from configparser import ConfigParser
from itertools import islice
from oss2.models import PartInfo
from oss2 import determine_part_size
import json

class OSSManager(object):

  _bucket = {}
  _config = {}
  _endpoint = {}
  _videoPath = ""

  def __init__(self):

    self._config = ConfigParser()
    self._config.read('config.ini')
    self._endpoint = self._config.get('OSS', 'endpoint')
    self._bucketName = self._config.get('OSS', 'bucket.name')
    self._videoPath = self._config.get('OSS', 'video.path')
    credFile = self._config.get('CRED', 'file.name')

    with open(credFile, 'r') as f:
      cred = json.load(f)
      auth = oss2.Auth(cred['AK'], cred['SK'])
      self._bucket = oss2.Bucket(auth, self._endpoint, self._bucketName)

  def getVideoPath(self):
      return self._videoPath

  def listFiles(self, path=''):
      fileKeys = []
      currentMarker = ''
      while True:
        listObjects = oss2.ObjectIterator(self._bucket, prefix=path, marker=currentMarker, max_keys=100)
        for obj in listObjects:
            if not obj.key.endswith('/'):
                fileKeys.append(obj.key)
        currentMarker = listObjects.next_marker
        if not currentMarker:
            break

      return fileKeys

  def downloadFile(self, path, localPath):
      oss2.resumable_download(self._bucket, path, localPath,
                              store=oss2.ResumableDownloadStore(root='./tmp'),
                              multiget_threshold=20 * 1024 * 1024,
                              part_size=10 * 1024 * 1024,
                              num_threads=3)

  def uploadFile(self, path, localPath):
    oss2.resumable_upload(self._bucket, path, localPath,
                          store=oss2.ResumableDownloadStore(root='./tmp'),
                          multipart_threshold=20 * 1024 * 1024,
                          part_size=10 * 1024 * 1024,
                          num_threads=3)

  def cleanDirs(self, key):
      return ""

