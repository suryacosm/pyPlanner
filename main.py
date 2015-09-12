#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, os, time, shutil
from PyQt4 import QtGui,QtCore,QtNetwork
from PyQt4.phonon import Phonon

from qtsingleapplication import QtSingleApplication
from extrawidgets import SystemTray, ExtraLCDDisplay, ExtraSplashScreen
from goalwidgets import GoalWidget, GoalListWidgetPart
from globalsettings import PROGRAM_NAME, REGISTRY_PATH, generateID

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
os.chdir(CURRENT_PATH)

class MasterControl(QtGui.QWidget):
        
    def CreateTray(self):
        #self.setWindowFlags(QtCore.Qt.Tool)
        if self.tray is not None: return
        
        iconImage = QtGui.QPixmap("No_Image_Available.png")
        icon = None
        if not iconImage.isNull():
            icon = QtGui.QIcon(iconImage)
            
        self.tray = SystemTray(icon)
        self.tray.exitAction.triggered.connect(self.close)
        self.tray.showAction.triggered.connect(self._putOnTop)
        self.tray.activated.connect(self._handleShowTray)
        #self.tray.show()

    def HandleShow(self):
        #Check for minimized Start
        try:
            if sys.argv[1] == "-mini":
                print "SYS.ARGV[1]:",sys.argv[1]
                print "Minimized Start"
                self.hide()
                self.tray.show()
                self.tray.showMessage(PROGRAM_NAME,"Started Minimized",QtGui.QSystemTrayIcon.Information,10000)
            else:
                print "SYS.ARGV[1]:",sys.argv[1]
                self.show()
                self.tray.hide()
        except Exception as e:
            #print "NO SYS.ARGV[1]:",
            #print type(e), e
            self.show()
            self.tray.hide()

    def LoadRegistrySettings(self):
        self.registrySettings = QtCore.QSettings(REGISTRY_PATH, QtCore.QSettings.NativeFormat)
        print "Boot on Windows Startup:",self.registrySettings.contains("Boot_"+PROGRAM_NAME)
        self.registryCheckbox.setChecked( self.registrySettings.contains("Boot_"+PROGRAM_NAME) )
        self.registryCheckbox.stateChanged.connect(self._registryCheckboxChecked)

    def _handleShowTray(self, reason):
        if reason == QtGui.QSystemTrayIcon.Context:
            self.tray.contextMenu().show()
        else:
            self._putOnTop()
    
    def _putOnTop(self):
        #Does not work well
        #self.raise_()
        self.show()
        
        #For Windows OS
        self.setWindowState(self.windowState() & ~QtCore.Qt.WindowMinimized | QtCore.Qt.WindowActive)
        self.activateWindow()
    
    def _registryCheckboxChecked(self,state):
        if state == QtCore.Qt.Checked:
            self.registrySettings.setValue("Boot_"+PROGRAM_NAME, '"' + sys.argv[0] + '"' + " -mini")
        else:
            self.registrySettings.remove("Boot_"+PROGRAM_NAME)
            
    def __init__(self, parent=None):   
        super(MasterControl, self).__init__(parent)
        self.tray = None
        self.CreateTray()

        #---- Styling Stuff ----#
        self.resize(1000, 500)
        self.center()

        self.HandleShow()
            
        self.mainLayout = QtGui.QGridLayout()
        self.setLayout(self.mainLayout)
        #-----------------------#
        
     
        #----- Buttons Container ---------#    
        self.topWidget = QtGui.QWidget()
        self.topWidget.setLayout(QtGui.QHBoxLayout() )
    
        self.addGoalWidgetButton = QtGui.QPushButton("Add Goal Widget")
        self.addGoalWidgetButton.clicked.connect(self.AppendGoalWidget)
        
        self.registryCheckbox = QtGui.QCheckBox("Boot on Windows Start")
        
        '''
        note = ""
        count = 1
        for arg in sys.argv:
            note += "(" + str(count) + ")" + arg + " "
            count += 1
        self.quickNote = QtGui.QLabel(note)
        '''
        
        self.topWidget.layout().addWidget( self.addGoalWidgetButton )
        self.topWidget.layout().addWidget( ExtraLCDDisplay() )
        self.topWidget.layout().addWidget( self.registryCheckbox )
        #self.topWidget.layout().addWidget(self.quickNote)
        self.topWidget.layout().addItem(QtGui.QSpacerItem( 1, 1, QtGui.QSizePolicy.Expanding) )
        #----- End of Button Container ---#
        
        
        #------------------- Main Area --------------------#
        
        #---- Goal Widget Area ------#
        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setLayout( QtGui.QVBoxLayout() )
        self.scrollArea.setWidgetResizable(True)
        #self.scrollArea.setMaximumWidth(500)
        
        #Buffer area, to make the main widget appear on top always
        self.scrollAreaBuffer = QtGui.QWidget()
        self.scrollAreaBuffer.setLayout( QtGui.QVBoxLayout() )
        
        #Main Goal Widget Container
        self.scrollAreaWidget = QtGui.QWidget()
        self.scrollAreaWidget.setLayout( QtGui.QVBoxLayout() )
        
        self.scrollAreaBuffer.layout().addWidget(self.scrollAreaWidget)
        self.scrollAreaBuffer.layout().addItem( QtGui.QSpacerItem(1,2000,QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding) ) 
        
        #Set widget to scroll area
        self.scrollArea.setWidget(self.scrollAreaBuffer)
        #---- End of Goal Widget Area ----#
        
        #---- List Widget Area (Running Goals) ----#
        
        self.goalListWidgetScroll = QtGui.QScrollArea()
        self.goalListWidgetScroll.setWidgetResizable(True)
        #self.goalListWidgetScroll.setMaximumWidth(200)
        
        #Buffer area
        self.goalListWidgetBuffer = QtGui.QWidget()
        goalListBufferLayout = QtGui.QVBoxLayout() 
        goalListBufferLayout.setSpacing(0)
        goalListBufferLayout.setMargin(0)
        self.goalListWidgetBuffer.setLayout(goalListBufferLayout)
        
        #List Widget
        self.goalListWidget = QtGui.QWidget() #QtGui.QListWidget()
        self.goalListWidgetLayout = QtGui.QVBoxLayout()
        self.goalListWidgetLayout.setSpacing(0)
        self.goalListWidgetLayout.setMargin(0)
        self.goalListWidget.setLayout(self.goalListWidgetLayout)
        
        
        self.goalListWidgetBuffer.layout().addWidget(self.goalListWidget)
        self.goalListWidgetBuffer.layout().addItem(QtGui.QSpacerItem(1, 2000, QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding))

        self.goalListWidgetScroll.setWidget(self.goalListWidgetBuffer)

        #--------- End of List Widget Area ------------#
        self.bottomWidget = QtGui.QWidget()
        self.bottomWidget.setLayout(QtGui.QHBoxLayout() )
        
        self.bottomWidget.layout().addWidget(self.scrollArea)
        self.bottomWidget.layout().addWidget(self.goalListWidgetScroll)
        #-------- End of Main Area --------------------#
        
        
        #Add everything to main widget
        self.mainLayout.addWidget(self.topWidget,0,0)
        self.mainLayout.addWidget(self.bottomWidget,1,0)
        
        
        #Cache needed or else splash screens will display properly
        self.splashes = []
        
        #For saving information on startup
        self.goalWidgets = []
        self.runningGoals = []
        
        #Cache needed or else threads just stop running immiediately 
        self.qthreads = []
        self.qobjects = []
    
        #Periodically save widget info
        #QtCore.QTimer.singleShot(120000, self.SaveWidgets)
        
        #Delay load until main widgets appear first
        QtCore.QTimer.singleShot(0, self._load)

    def _load(self):
        self.LoadRegistrySettings()
        self.LoadWidgets()
        self.LoadRunningGoals()
    
    def AppendGoalWidget(self):
        gw = GoalWidget(None)
        gw.removeClicked.connect(self.RemoveGoalWidget)
        gw.startButton.clicked.connect(lambda : self.StartCreatingGoal(gw) )
        gw.saveButton.clicked.connect(self.SaveWidgets)
        
        self.scrollAreaWidget.layout().addWidget(gw)
        self.goalWidgets.append(gw)

    def RemoveGoalWidget(self, gw):
        print "Removing gw"
        #Save the widget here
        gw.removeClicked.disconnect()
        gw.deleteLater()
        
        self.goalWidgets.remove(gw)
        self.scrollAreaWidget.layout().removeWidget(gw)
        #self.SaveWidgets()
              
    def StartCreatingGoal(self, gw):
        now = self._currentDateTime()
        dt = now.msecsTo( gw.dateTimeEdit.dateTime() )
        if dt < 0: dt = 0

        imagePath = gw.selectImageEdit.text()
        if imagePath == "" : imagePath = QtCore.QString("No_Image_Available.png")
        title = gw.titleBar.text()
        if title == "": title = QtCore.QString("(NO NAME)")
        mp3Path = gw.selectAudioEdit.text()
        
        goal = Goal(dt, now, imagePath, mp3Path, title, dt)
        self.runningGoals.append(goal)
    
        gwp = self.CreateGoalWidgetPart(goal)
        self.AddGoalThread(goal, gwp)
        #gwp.removeButton.clicked.connect(lambda : self.RemoveGoalWidget(gwp, goal, qobject) )
        
        print "Started Goal:", title, now.toString(), "DELTA(ms):", dt,"\n"
        self.SaveRunningGoals()
        
    def CreateGoalWidgetPart(self, goal):
        gwp = GoalListWidgetPart()
        gwp.titleLabel.setText(goal.title)
        
        gwp.dateTimeEdit.setDateTime( goal.registeredTime.addMSecs(goal.initialSeconds) )
        #gwp.removeButton.clicked.connect(lambda : self.RemoveGoalWidgetPart(gwp,goal) )
        self.goalListWidgetLayout.addWidget( gwp )
        return gwp
    
    def RemoveGoalWidgetPart(self, gwp, goal=None):
        #self.listWidgets.remove(gwp)
        #qobject.StopRunning()
        if goal:
            try:
                self.runningGoals.remove(goal)
                self.SaveRunningGoals()
            except Exception as e:
                print type(e),e
                
        self.goalListWidgetLayout.removeWidget(gwp)
        gwp.deleteLater()
        
    def AddGoalThread(self,goal, gwp):
        qthread = QtCore.QThread()
        qobject = GoalLogic(goal.seconds)
        qobject.moveToThread(qthread)                                       
        
        
        qobject.completed.connect(lambda : self.RunGoal(goal, gwp) )#, qobject, qthread) )
        qobject.completed.connect(qthread.quit)
        qobject.stopped.connect(qthread.quit)
        
        qthread.started.connect(qobject.run)
        qthread.finished.connect( lambda : self._cleanupQThreads( qthread, qobject) )

        gwp.removeButton.clicked.connect( lambda : qobject.StopRunning() )
        gwp.removeButton.clicked.connect( lambda : self.RemoveGoalWidgetPart(gwp,goal) )
        
        self.qthreads.append(qthread)
        self.qobjects.append(qobject)
        
        qthread.start()  
                
    def RunGoal(self, goal, gwp):
        print "Running Goal"

        message = "Goal: "+str(goal.title)+"\nFinished: "+str( self._currentDateTime().toString() )+"\nStarted: "+str(goal.registeredTime.toString())+"\nDT: "+str(goal.seconds)+" milliseconds"
        print message,"\n"
        #QtGui.QMessageBox.warning(None, "Timer Complete: "+goal.title, message)
                
        #print goal.imagePath
        if goal.imagePath != "":
            splashPix = QtGui.QPixmap(goal.imagePath)
        else:
            splashPix = QtGui.QPixmap("No_Image_Available.png")
            
        if splashPix.isNull(): 
            print "Null pix, avoiding creating a splashscreen"
        else:
            splash = ExtraSplashScreen(splashPix, QtCore.Qt.WindowStaysOnTopHint)
            splash.setMask( splashPix.mask() )
            splash.show()
            
            if goal.mp3Path != "":
                mediaSource = Phonon.MediaSource(goal.mp3Path)
                mediaObject = Phonon.MediaObject(self)
                audioOutput = Phonon.AudioOutput(Phonon.MusicCategory, self)
                Phonon.createPath(mediaObject, audioOutput)
                mediaObject.setCurrentSource(mediaSource)
           
                splash.shown.connect(mediaObject.play)
                splash.hidden.connect(mediaObject.stop)
            
            self.splashes.append(splash)
            splash.hidden.connect(lambda : self._cleanupSplashScreen(splash) )
            
        self.RemoveGoalWidgetPart(gwp, goal)
        
        #self.runningGoals.remove(goal)
        #self.SaveRunningGoals()
               
    def SaveRunningGoals(self):
        #Save File, cleanup
        #print "Saving running Goals"
        file = QtCore.QFile("goals.bin")
        file.open(QtCore.QIODevice.WriteOnly)
        stream = QtCore.QDataStream(file)
        
        for goal in self.runningGoals:
            stream << QtCore.QString(str(goal.seconds))
            stream << goal.registeredTime
            stream << goal.imagePath
            stream << goal.mp3Path
            stream << goal.title
            stream << QtCore.QString(str(goal.initialSeconds))
        
        file.close()

    def LoadRunningGoals(self):
        #Load Goals
        file = QtCore.QFile("goals.bin")
        file.open(QtCore.QIODevice.ReadOnly)
        stream = QtCore.QDataStream(file)

        while not stream.atEnd():
            timeToGoal = QtCore.QString()
            registeredTime = QtCore.QDateTime()
            imagePath = QtCore.QString()
            mp3Path = QtCore.QString()
            title = QtCore.QString()
            initialSeconds = QtCore.QString()
            
            stream >> timeToGoal #timeToGoal = stream.readInt64()
            stream >> registeredTime
            stream >> imagePath
            stream >> mp3Path
            stream >> title
            stream >> initialSeconds

            timeToGoal = int(timeToGoal)
            initialSeconds = int(initialSeconds)
            self.runningGoals.append( Goal(timeToGoal, registeredTime, imagePath, mp3Path, title, initialSeconds) )
        
        file.close()   
        
        #print "Time now:",self._currentDateTime().toString(),"\n"
        for goal in self.runningGoals:
            now = self._currentDateTime()
            
            
            print "\nReloaded a goal:", goal.title
            print "Started:", goal.registeredTime.toString()
            print "Ending :", goal.registeredTime.addMSecs(goal.seconds).toString(),"\n"
           
            passedTime = now.msecsTo(goal.registeredTime)
            goal.seconds += passedTime
            if goal.seconds < 0: goal.seconds = 0
            
            gwp = self.CreateGoalWidgetPart(goal)
            self.AddGoalThread(goal, gwp) 
        print "Goals Loaded"
        
    def SaveWidgets(self):
        #Save File, cleanup
        file = None
        success = False
        
        for i in range(0,3):
            if not success:
                try:
                    file = QtCore.QFile("widgets.bin")
                    if not file.open(QtCore.QIODevice.WriteOnly):
                        raise IOError("Failed to open widgets.bin")
                    
                    stream = QtCore.QDataStream(file)
                    
                    for gw in self.goalWidgets:
                        stream << gw.titleBar.text()
                        stream << gw.selectAudioEdit.text()
                        stream << gw.selectImageEdit.text()
                        
                        #print "SAVEWIDGETS():",gw.lastDirectoryAudio, gw.lastDirectory
                        stream << QtCore.QString(gw.lastDirectory)
                        stream << QtCore.QString(gw.lastDirectoryAudio)
                    
                    success = True
                except Exception as e:
                    print type(e), e
                    continue
                finally:
                    if file is not None:
                        file.close()
                break
           
        if success:
            print "Widgets saved."
            if os.path.exists("widgets.bin"):
                shutil.copy2("widgets.bin","widgets.bin.bkp")
        else:
            print "Failed to copy over data."
            if os.path.exists("widgets.bin.bkp"):
                print "Restoring from backup."
        
                shutil.copy2("widgets.bin.bkp","widgets.bin")

    def LoadWidgets(self):
        file = QtCore.QFile("widgets.bin")
        file.open(QtCore.QIODevice.ReadOnly)
        stream = QtCore.QDataStream(file)
        
        while not stream.atEnd():
            titleText = QtCore.QString()
            audioPathText = QtCore.QString()
            imagePathText = QtCore.QString()
            lastDirectory = QtCore.QString()
            lastDirectoryAudio = QtCore.QString()  
 
            stream >> titleText
            stream >> audioPathText
            stream >> imagePathText
            stream >> lastDirectory
            stream >> lastDirectoryAudio
            
            if imagePathText == "Select Image":
                imagePathText = "No_Image_Available.png"

            if audioPathText == "mp3/avi audio":
                audioPathText = ""
                        
            #Load general settings
            gw = GoalWidget(None)
            gw.removeClicked.connect(self.RemoveGoalWidget)
            gw.startClicked.connect(self.StartCreatingGoal)
            gw.saveButton.clicked.connect(self.SaveWidgets)
        
            self.scrollAreaWidget.layout().addWidget(gw)
            self.goalWidgets.append(gw)
             
            #Load specific settings
            gw.titleBar.setText(titleText)
            gw.selectAudioEdit.setText(audioPathText)
            gw.selectImageEdit.setText(imagePathText)   
            
            pix = QtGui.QPixmap(imagePathText)
            gw.goalIconLabel.setPixmap( pix )
            #gw.goalIconLabel.setOriginalPixmap( pix )
            
            #print "LOADWIDGETS():", gw.lastDirectoryAudio, gw.lastDirectory
            
            #if not lastDirectory.isEmpty():#lastDirectory != "":
            gw.lastDirectory = lastDirectory
            #if lastDirectoryAudio != None:
            gw.lastDirectoryAudio = lastDirectoryAudio   
        
        file.close()
        print "Widgets Loaded"
    
    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            for splash in self.splashes:
                splash.hide()
            
    def changeEvent(self, event):
        super(MasterControl,self).changeEvent(event)
        
        if event.type() == QtCore.QEvent.WindowStateChange:
            if event.oldState() != QtCore.Qt.WindowMinimized and self.isMinimized():
                #Defer until after minizmization (allows hiding from taskbar)
                QtCore.QTimer.singleShot(200, self.hide)
                event.ignore()

    def showEvent(self,event):
        if self.tray: 
            self.tray.hide()

        '''
        if True and self.hidden:
            self.setWindowFlags(QtCore.Qt.Window)
            self.hidden = False
        #event.accept()   
        self.show()
        '''
        
        
    def hideEvent(self,event):
        if self.tray:
            self.tray.show()
        
        '''
        self.hide()
        if True:
            self.hidden = True
            self.setWindowFlags(QtCore.Qt.ToolTip)
        '''
        
    def closeEvent(self,event):
        super(MasterControl,self).closeEvent(event)
        self.tray = None
        #self.SaveOnExit()

    def SaveOnExit(self):
        try:
            print "Closing and saving widgets"#"Stopping queue relay thread"
            print "Goal Widgets",len(self.goalWidgets),"Splash Screens",len(self.splashes),
            print "QThreads",len(self.qthreads),"QObjects",len(self.qobjects),"Running Goals",len(self.runningGoals)
            self.SaveWidgets()
            
            print sys.argv[0]
        except Exception as e:
            print type(e),e
        
        try:
            if self.registryCheckbox.isChecked():
                self.registrySettings.setValue("Boot_"+PROGRAM_NAME, '"' + sys.argv[0] + '"' + " -mini")
            else:
                self.registrySettings.remove("Boot_"+PROGRAM_NAME)
        except Exception as e:
            print type(e),e
            
        #time.sleep(3)
        
        '''
        self.runningGoals = None
        self.goalWidgets = None
        self.splashes = None
        self.qobjects = None
        self.qthreads = None
        '''

    def _cleanupQThreads(self, qthread, qobject):
        print "Cleaning up qthreads"
        self.qthreads.remove(qthread)
        self.qobjects.remove(qobject)

    def _cleanupSplashScreen(self, splash):
        #print "Cleaning up splash screen"
        splash.finish(None)
        self.splashes.remove(splash)
        
    def _currentDateTime(self):
        return QtCore.QDateTime.currentDateTime()

class GoalLogic(QtCore.QObject):
    '''
    Meant to run on qthread, this qobject runs the goal logic 
    Goal logic is simply waiting until time has passed before 
    notifying the main widget that the goal action should be run
    
    Alternatively, this can also be run directly on a sub-classed qthread.
    However QT prefers that we use qobjects and move them to qthreads because
    of how it handles event loops. For this simple logic, either one works
    '''
    stopped = QtCore.pyqtSignal()
    completed = QtCore.pyqtSignal()
    MSEC = 30000#5000

    def __init__(self, duration, *args, **kwargs):
        super(GoalLogic,self).__init__(*args,**kwargs)
        self.duration = duration
        self.isMSec = True
        self._stop = False
    
    def StopRunning(self):
        self._stop = True
        self.stopped.emit()
        print "StopRunning() qthread/qobject"
    
    def _wasStopped(self):
        if self._stop:
            #self.stopped.emit()
            return True
        return False
    
    def run(self):

        if self.isMSec:
            #Cycle through large numbers, every MSEC seconds
            while self.duration > self.MSEC:
                time.sleep(self.MSEC/1000.0)
                self.duration -= self.MSEC
                if self._wasStopped(): return

            time.sleep(self.duration / 1000.0)
            if self._wasStopped(): return
        else:
            raise NotImplementedError( "Not implemented qthread/qobject" )            
                
        self.completed.emit()
 
class Goal(object):
    def __init__(self, seconds, currentTime, imagePath="", mp3Path="", title="", initialSeconds=0, gwp=None):
        self.seconds = seconds
        self.registeredTime = currentTime
        self.imagePath = imagePath
        self.mp3Path = mp3Path
        self.title = title
        self.initialSeconds = initialSeconds
        self.gwp = gwp
                  
if __name__ == '__main__':
    print "\nPROG_ID:",generateID(),'\n'
    ID = generateID()
    
    #Replace with QtGui.QApplication() for no singleton
    app = QtSingleApplication(ID, sys.argv)
    if app.isRunning(): 

        saveSocket = QtNetwork.QLocalSocket()
        saveSocket.connectToServer(ID + '-2')
        saving = saveSocket.waitForConnected()
        
        if saving:
            QtGui.QMessageBox.critical(None, PROGRAM_NAME+" - Still Saving", "Application is still saving. Wait until it has completed.")
            print "Already running, exiting"
            sys.exit(0)
        else:
            QtGui.QMessageBox.critical(None, PROGRAM_NAME, "Application is still running. Closing.")
            print "Already running, exiting"
            sys.exit(0)

    control = MasterControl(None)
    app.exec_()
    
    #Used to display a different messagebox when saving 
    saveIndicatorServer = QtNetwork.QLocalServer()
    saveIndicatorServer.listen(ID + '-2')
    print "Save Server Up"                 
    
    #Ended app event loop before saving for responsiveness
    control.SaveOnExit()
    saveIndicatorServer.close()
    print "Save Server Down"
    