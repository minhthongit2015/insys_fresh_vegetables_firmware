# coding=utf-8
import http.client as httplib
import urllib
import base64
import json
import datetime

class BaseAPI:
  def __init__(self, method='post', path='', params={}, body='', headers={}):
    self.method = method
    self.path = path
    self.params = params
    self.paramsStr = "?"+urllib.parse.urlencode(params)
    self.headers = headers
    self.body = body

class InSysServices:
  """
  Lớp cơ bản hỗ trợ điều khiển luồng API
  """

  _server = ''
  _headers = { }

  def __init__(self, server=''):
    self.setServer(server)
    self.lastNetwork = True

  def setServer(self, server):
    self._server = server

  def _defaultHandler(self, res):
    res = res.read()
    try:
      parsed = json.loads(res.decode('utf-8'))
      print(json.dumps(parsed.decode('utf-8'), sort_keys=True, indent=2))
    except:
      print(res)
      raise

  def request(self, api, callback=None, keepalive=False):
    # Gắn header mặc định vào với header của api
    headers = self._headers
    for header in api.headers: headers[header] = api.headers[header]
    try:
      conn = httplib.HTTPSConnection(self._server)
      conn.request(api.method, api.path + api.paramsStr, api.body, headers)
    except Exception as err:
      if self.lastNetwork:
        print(">> Network error at: {}\r\n{}".format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S'), str(err)))
        self.lastNetwork = False
      return err

    if not self.lastNetwork:
      print(">> Network is online at: {}".format(datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')))
      self.lastNetwork = True

    res = conn.getresponse()
    if callback != None: callback(res, api)
    # else: self._defaultHandler(res)

    if not keepalive: conn.close()
      
    return conn

  ###############
  # Some Helper #
  ###############
  def attachFile(self, api, filePath='', fileRawData='', fileUrl=''):
    api.headers['Content-Type'] = 'application/octet-stream'
    api.headers['Content-Disposition'] = 'attachment; filename=payload.jpg'
    if filePath != '':
      try:
        with open(filePath, 'rb') as f: api.body = f.read()
      except Exception as err:
        print(err)
    elif fileRawData != '':
      api.body = fileRawData
    elif fileUrl != '':
      api.body = '{"url": {}'.format(urllib.parse.urlencode(fileUrl))

  def parseParams(self, params):
    return urllib.parse.urlencode(params)

  def paramsToJSON(self, params):
    return json.dumps(params)

  def parseResult(self, responseBytes):
    return json.loads(responseBytes.decode('utf-8'))