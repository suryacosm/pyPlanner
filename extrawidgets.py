import time
from PyQt4 import QtGui, QtCore
from globalsettings import PROGRAM_NAME

class SystemTray(QtGui.QSystemTrayIcon):
    '''
    A simple system tray with support for .gif icons
    '''
    
    clicked = QtCore.pyqtSignal()
    
    def __init__(self, icon=None, *args, **kwargs):   
        self.gif = None
        
        if not icon:
            icon = QtGui.QIcon(QtGui.qApp.style().standardPixmap(QtGui.QStyle.SP_FileIcon))
        
        super(SystemTray, self).__init__(icon, *args, **kwargs)    
        self.setToolTip(PROGRAM_NAME)
          
        self.menu = QtGui.QMenu()
        self.showAction = self.menu.addAction("Show")
        self.menu.addSeparator()
        self.exitAction = self.menu.addAction("Exit")
        self.setContextMenu(self.menu)

    def setIcon(self, icon):
        self.gif = None
        super(SystemTray, self).setIcon(icon)
         
    def show(self):
        if self.gif: self.gif.start()
        super(SystemTray, self).show()

    def hide(self): 
        if self.gif: self.gif.stop()        
        super(SystemTray, self).hide()
            
    def SetGifIcon(self,iconPath):
        self.gif = QtGui.QMovie(iconPath);
        self.gif.frameChanged.connect(self._onChangeImage)
        if self.gif.isValid(): self._onChangeImage()   
        
    def _onChangeImage(self):
        super(SystemTray, self).setIcon( QtGui.QIcon(self.gif.currentPixmap()) )

class ExtraDateTimeEdit(QtGui.QDateTimeEdit):
    '''
    Able to tick like a clock
    Stops ticking when it is edited/foused 
    '''
    def __init__(self, *args, **kwargs):
        super(ExtraDateTimeEdit,self).__init__(*args, **kwargs)  
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.UpdateClock)
        self.dirty = False
        #self.timer.start(1000) #Uncomment for ticking clocks
        
        self.UpdateClock()
    
    def UpdateClock(self):
        if not self.hasFocus() and not self.dirty:
            self.setDateTime(QtCore.QDateTime.currentDateTime() )
        else:
            self.dirty = True

class ExtraLCDDisplay(QtGui.QLCDNumber):
    '''
    A simple ticking QLCD display 
    Does not display "AM" or "PM" (Only support for numbers and limited letters)
    A custom widget might prove more useful for displaying AM/PM
    '''
    def __init__(self,*args, **kwargs):
        super(ExtraLCDDisplay,self).__init__(*args, **kwargs)
        self.setDigitCount(8)
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.UpdateDisplay)
        self.timer.start(1000)

        self.UpdateDisplay()
         
    def UpdateDisplay(self):
        self.display(time.strftime("%I:%M:%S"))

class ExtraPictureLabel(QtGui.QLabel):
    '''
    Double clickable
    Added a keep aspect ratio feature 
        Enables perservation of aspect ratio when resizing or setting the option
        Does not interfere with other options such as SetScaledContents
        Fixed an issue where QT may not center the picture after resizing horizontally (Qt.KeepAspectRatio)
    '''
    
    doubleClicked = QtCore.pyqtSignal()
     
    def __init__(self, *args, **kwargs):
        super(ExtraPictureLabel, self).__init__(*args, **kwargs)
        self._keep = False
        self._pix = None
        self._morphedPix = None

        self.installEventFilter(self)
        
    def setPixmap(self, pixmap):
        self._pix = self._morphedPix = pixmap
        if self._keep: 
            self._morphedPix = self._scaledPix()
        super(ExtraPictureLabel, self).setPixmap( self._pix )
    
    def paintEvent(self, event):
        if not self._keep:
            super(ExtraPictureLabel, self).paintEvent(event)
        else:
            self._paintAspectRatioPixmap()

    def setScaledContents(self, scale):
        if scale: 
            self.setKeepAspectRatio(False)
        super(ExtraPictureLabel, self).setScaledContents(scale)

    def setKeepAspectRatio(self,keep):
        self._keep = keep
        if self._keep:
            self._morphedPix = self._scaledPix() 
            self.setScaledContents(False)
            
    def resizeEvent(self, event):
        if self._keep: 
            self._morphedPix = self._scaledPix() 
        super(ExtraPictureLabel, self).resizeEvent(event)

    def eventFilter(self, widget, event):
        if event.type() == QtCore.QEvent.MouseButtonDblClick:
            self.doubleClicked.emit()
        return super(ExtraPictureLabel, self).eventFilter(widget, event)
    
    def _scaledPix(self):
        if not self._pix: 
            return None
        return self._pix.scaled(self.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

    def _paintAspectRatioPixmap(self):
        if self._morphedPix.isNull(): return
  
        x = (self.width() - self._morphedPix.width() ) /2
        y = (self.height() - self._morphedPix.height() ) /2
        
        paint = QtGui.QPainter(self)
        paint.drawPixmap(x, y, self._morphedPix) 

class ExtraSplashScreen(QtGui.QSplashScreen):
    '''
    A splashscreen that emits hide and show signals
    
    Useful for easier cleanup on the main widget 
    (where we keep a cache so that splash screens that
    do not need a parent are displayed correctly)
    And for running logic when it appears on the screen, 
    such as playing music files
    
    Press Esc to close, when in focus (better to close 
    from main widget or higher)
    '''
    
    completed = QtCore.pyqtSignal()
    shown = QtCore.pyqtSignal()
    hidden = QtCore.pyqtSignal()
        
    def __init__(self,*args,**kwargs):
        super(ExtraSplashScreen,self).__init__(*args,**kwargs)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            print "Hiding Splash Screen"
            self.hide()
            
    def hideEvent(self, event):
        self.hidden.emit()
        super(ExtraSplashScreen,self).hideEvent(event)
    
    def showEvent(self, event):
        event.accept()
        #Signals are not sent in the show event when starting up a widget
        #So instead it is deferred until after the showEvent completes
        QtCore.QTimer.singleShot(0, self.shown.emit) 
        super(ExtraSplashScreen,self).showEvent(event)
    
    def closeEvent(self,event):
        self.completed.emit()
        super(ExtraSplashScreen,self).closeEvent(event)
       


