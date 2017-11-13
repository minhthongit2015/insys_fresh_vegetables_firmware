# coding=utf-8
"""
![logo](https://raw.githubusercontent.com/megahertz/electron-simple-updater/master/logo.png)
# electron-simple-updater
[![Build Status](https://travis-ci.org/megahertz/electron-simple-updater.svg?branch=master)](https://travis-ci.org/megahertz/electron-simple-updater)
[![npm version](https://badge.fury.io/js/electron-simple-updater.svg)](https://badge.fury.io/js/electron-simple-updater)

## Description

This module allows to automatically update your application. You only
need to install this module and write two lines of code! To publish
your updates you just need a simple file hosting, it does not require
a dedicated server.

Supported OS: 
 - Mac, ([Squirrel.Mac](https://github.com/Squirrel/Squirrel.Mac))
 - Windows ([Squirrel.Windows](https://github.com/Squirrel/Squirrel.Windows))
 - Linux (for [AppImage](http://appimage.org/) format)

## Differences between electron-simple-updater and built-in autoUpdater

* Actually, autoUpdater is used inside.
* Linux support.
* It handles Squirrel.Windows install/update command line arguments.
* It doesn't require a dedicated release server.
* You need only 2 lines of code to make it work.

## Installation

Install with [npm](https://npmjs.org/package/electron-simple-updater):

    npm install --save electron-simple-updater

## Usage

### Publish a new release
1. Insert a link to a hosting where you will store updates.json to main.js. 
You can find a sample of updates.json in the [the example](example)

    ```js
    // Just place this code at the entry point of your application:
    const updater = require('electron-simple-updater');
    updater.init('https://raw.githubusercontent.com/megahertz/electron-simple-updater/master/example/updates.json');
    ```
    You can set this link in package.json:updater.url instead of init() argument.

2. Build your release using electron-builder or another tool.
Note: Your application must be signed for automatic updates on macOS.
This is a requirement of Squirrel.Mac.

3. Upload your release with update.json to a hosting. You can 
do it [manually](example/updates.json) or use
[electron-simple-publisher](https://github.com/megahertz/electron-simple-publisher)
to simplify this process. Note: Squirrel.Mac requires a properly prepared `release.json` file. A release in the property `url` must be zipped .app file.

4. That's it!

    Now your application will check for updates on start and download it 
    automatically if an update is available. After app is restarted a new
    version will be loaded. But you can customize it to ask a user if he
    would like to install updates. See [the example](example) for details.
    
## API

### Options
You can set options when calling init() method or in package.json:updater
section.

Name                | Default                 | Description
--------------------|-------------------------|------------
autoDownload        | true                    | Automatically download an update when it is found in updates.json
build               | {platform}-{arch}       | Build type, like 'linux-x64' or 'win32-ia32'
channel             | 'prod'                  | An application which is built for channel like 'beta' will receive updates only from this channel
checkUpdateOnStart  | true                    | Check for updates immediately when init() is called
disabled            | false                   | Disable update feature. This option is set to true automatically for applications built for Mac App Store or Windows Store
logger              | console                 | You can pass [electron-log](https://github.com/megahertz/electron-log), [winston](https://github.com/winstonjs/winston) or another logger with the following interface: { info(), warn() }. Set it to false if you would like to disable a logging feature 
version             | app.getVersion()        | Current app version. In most cases, you should not pass this options manually, it is read by electron from version at package.json
url*                | undefined               | The only required parameter. This is a URL to [updates.json](https://github.com/megahertz/electron-simple-updater/blob/master/example/updates.json) file
    
### Method
    
#### init(options)
Initialize a package. By default it finish the process if is run by
Squirrel.Windows installer.

#### setFeedURL(url) *deprecated*
Sets the url and initialize the electron-simple-updater. Instead of
built-in auto-updater init(), this method receives a URL to updates.json.   
    
#### getFeedURL() *deprecated*
Return the current updates.json URL.

#### checkForUpdates() 
Asks the server whether there is an update. url must be set before this
call. Instead of built-in auto-updater, this method does not start
downloading if autoDownload options is set to false.
    
#### downloadUpdate()
Start downloading update manually. You can use this method if
autoDownload option is set to false
    
#### quitAndInstall()
Restarts the app and installs the update after it has been downloaded.
It should only be called after update-downloaded has been emitted.

#### setOptions(name, value)
Set one or a few options. Pass an object as the name for multiple set.
   
### Properties (read only)
These properties are mapped to options 

 * **build** 
 * **channel**
 * **version**
 * **buildId** - this string contains a build, a channel and version
    
### Events
**meta** object of some events is a data from updates.json
   
#### error(err)
Emitted when there is an error while updating.

#### checking-for-update 
Emitted when start downloading update.json file.

#### update-available(meta)
Emitted when there is an available update.

#### update-not-available
Emitted when there is no available update.

#### update-downloading(meta)
Emitted when star downloading an update.

#### update-downloaded(meta)
Emitted when an update has been downloaded.

#### squirrel-win-installer(event)
Emitted when the app is run by Squirrel.Windows when installing. The
SimpleUpdater creates/removes shortcuts and finishes the process by
default.

 * **event.preventDefault** - set to true if you would like to
 customize this action
 * **event.squirrelAction** - squirrel-install, squirrel-updated,
 squirrel-uninstall, squirrel-obsolete
    
## Related
 - [electron-builder](https://github.com/electron-userland/electron-builder) -
 A complete solution to package and build an Electron app. Also it contains
 alternative implementation of update package.
 - [electron-simple-publisher](https://github.com/megahertz/electron-simple-publisher) -
 Simple way to publish releases for electron-simple-updater
    
    
## License

Licensed under MIT.

Logo was designed by [prolko](https://www.behance.net/prolko) base on the
original [electron](https://github.com/electron/electron) logo.
"""

try: import RPi.GPIO as GPIO
except: import core.RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def clean():
  GPIO.cleanup()

class Pin():
  def __init__(self, pin, isOutput=True, default=True, reverse=False, eventDetect=False, emitter=False): # Setup GPIO Pin for output by default
    self.pin = int(pin)
    self.default = self._verifyState(default)
    self.isOutput = self._verifyState(isOutput)
    self.oldState = self.state = self._verifyState(default)
    self.reverse = reverse
    self.setup(pin, isOutput, default)
    self.eventDetect = eventDetect
    self.emitter = emitter

  def setup(self, pin=-1, isOutput=False, default=True):
    if pin < 0:
      print("> Warn: GPIO pin must set to an positive integer.")
      return
    self.oldState = self.state = self.default
    if isOutput:
      GPIO.setup(pin, GPIO.OUT)
      GPIO.output(pin, GPIO.HIGH if default^self.reverse else GPIO.LOW)
    else:
      GPIO.setup(pin, GPIO.IN)

  def reset(self):
    self.setup(self.pin, self.isOutput, self.default)
  
  def onchange(self, eventDetect, phase=0):
    print("Setup onchange event on pin {} (phase: {})".format(self.pin, phase))
    if self.isOutput:
      self.eventDetect = eventDetect
    else:
      if phase == 1: event = GPIO.RISING
      elif phase == -1: event = GPIO.FALLING
      else: event = GPIO.BOTH
      GPIO.add_event_detect(self.pin, event, callback=eventDetect)

  def high(self): # set pin to high
    return self.turn(True)
  def on(self):
    return self.high()
  
  def low(self): # set pin to low
    return self.turn(False)
  def off(self):
    return self.low()

  def set(self, state):
    newState = self._verifyState(state)
    if self.state^newState:
      self.oldState = self.state
      self.state = newState
      GPIO.output(self.pin, GPIO.HIGH if self.state^self.reverse else GPIO.LOW)
      if self.eventDetect: self.eventDetect(self)
      return True
    return False
  def turn(self, state):
    return self.set(state)

  def toggle(self):
    self.oldState = self.state
    self.state = not self.state
    GPIO.output(self.pin, GPIO.HIGH if self.state^self.reverse else GPIO.LOW)
    if self.eventDetect: self.eventDetect(self)

  @property
  def value(self):
    return self.read()
  def read(self):
    return GPIO.input(self.pin)

  def _verifyState(self, state, default=False):
    try: state = int(state)
    except: return None
    return bool(state)

class ListPin():
  def __init__(self, pinList, isOut=[True], default=[True], reverse=[False], eventDetect=[False], emitter=[False]):
    self.size = len(pinList)
    self.pinList = pinList
    self.isOut = (isOut*self.size)[:self.size]
    self.default = (default*self.size)[:self.size]
    self.reverse = (reverse*self.size)[:self.size]
    self.eventDetect = (eventDetect*self.size)[:self.size]
    self.emitter = (emitter*self.size)[:self.size]
    self.pins = []
    for (pin, out, deft, rev, event, emit) in zip(self.pinList, self.isOut, self.default, self.reverse, self.eventDetect, self.emitter):
      self.pins.append(Pin(pin, out, deft, rev, event, emit))

  def setEventDetect(self, eventDetect=[False]):
    self.eventDetect = (eventDetect*self.size)[:self.size]
    for (pin, event) in zip(self.pins, self.eventDetect):
      pin.eventDetect = event