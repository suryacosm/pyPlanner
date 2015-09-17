from PyQt4 import QtGui,QtCore
from globalsettings import AUTHOR_NAME, PROGRAM_NAME
from extrawidgets import ExtraPictureLabel, ExtraDateTimeEdit

class GoalWidget(QtGui.QFrame):
    '''
    A widget that stores information that is used to create goals
    It is to be contained within the main widget and meant to be
    created and re-created, for re-useability
    '''
    
    removeClicked = QtCore.pyqtSignal(object)
    startClicked = QtCore.pyqtSignal(object)
    
    def __init__(self, parent=None, *args,**kwargs):
        super(GoalWidget,self).__init__(None, *args,**kwargs)
        
        self.lastDirectoryAudio = None
        self.lastDirectory = None
        self._loadSettings()
        
        self.setFrameShape(QtGui.QFrame.StyledPanel)
        self.setFrameShadow(QtGui.QFrame.Plain)
        self.setLayout( QtGui.QHBoxLayout() )
        
        self.setFixedHeight(165)
        self.setMinimumWidth(350)
                
        ### Goal Icon ###
        pix = QtGui.QPixmap("No_Image_Available.png")
        
        self.goalIconLabel = ExtraPictureLabel()
        self.goalIconLabel.setKeepAspectRatio(True)
        self.goalIconLabel.setFixedSize(150, 150)
        self.goalIconLabel.setPixmap(pix)
        
        self.goalIconLabel.doubleClicked.connect(self._selectImage)
        
        ### Button Layout
        self.minimizeButton = QtGui.QPushButton("Hide")
        self.startButton = QtGui.QPushButton("Start")
        self.removeButton = QtGui.QPushButton("Remove")
        self.saveButton = QtGui.QPushButton("Save")
        
        self.removeButton.clicked.connect( lambda : self.removeClicked.emit(self) )
        self.startButton.clicked.connect(lambda : self.startClicked.emit(self) )
        
        buttonsLayout = QtGui.QHBoxLayout()
        buttonsLayout.addItem(QtGui.QSpacerItem(1,1,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding))
        buttonsLayout.addWidget(self.removeButton)
        buttonsLayout.addWidget(self.minimizeButton)
        buttonsLayout.addWidget(self.saveButton)
        buttonsLayout.addWidget(self.startButton)
            
        ### Title Bar ###
        self.titleBar = QtGui.QLineEdit()
        self.titleBar.setPlaceholderText("Enter Title Here")
        
        ### Date Widget
        self.dateLayout = QtGui.QHBoxLayout()
        
        self.dateTimeEdit = ExtraDateTimeEdit()
        self.dateTimeEdit.setCalendarPopup(True)
        self.dateTimeEdit.setDateTime(self._currentDateTime() )
        
        self.dateLayout.addWidget(self.dateTimeEdit)
         
        ### Select Image Widget
        self.selectImageLayout = QtGui.QHBoxLayout()
        
        self.selectImageEdit = QtGui.QLineEdit()
        self.selectImageEdit.setText("Select Image")
        self.selectImageEdit.setReadOnly(True)
        
        self.selectImageEdit.setStyleSheet(r"""
        color: #808080;
        background-color: #D2D2D2;
        border: 1px solid #757575;
        border-radius: 3px;
        """)
        
        self.selectImageButton = QtGui.QPushButton("Browse")
        self.selectImageButton.clicked.connect(self._selectImage)
         
        self.selectImageLayout.addWidget(self.selectImageEdit)
        self.selectImageLayout.addWidget(self.selectImageButton)

        ### Select Audio Widget
        self.selectAudioLayout = QtGui.QHBoxLayout()
        
        self.selectAudioEdit = QtGui.QLineEdit()
        self.selectAudioEdit.setReadOnly(True)
        self.selectAudioEdit.setText("mp3/avi audio")
        
        self.selectAudioEdit.setReadOnly(True)
        self.selectAudioEdit.setStyleSheet(r"""
        color: #808080;
        background-color: #D2D2D2;
        border: 1px solid #757575;
        border-radius: 3px;
        """)
        
        self.selectAudioButton = QtGui.QPushButton("Browse Audio")
        self.selectAudioButton.clicked.connect(self._selectAudio)
        
        self.selectAudioLayout.addWidget(self.selectAudioEdit)
        self.selectAudioLayout.addWidget(self.selectAudioButton)
        
        ### Add Widgets ###
        goalRightLayout = QtGui.QVBoxLayout() 
        goalRightLayout.addLayout( buttonsLayout )
        goalRightLayout.addWidget(self.titleBar)
        goalRightLayout.addLayout(self.dateLayout)
        goalRightLayout.addLayout(self.selectImageLayout)
        goalRightLayout.addLayout(self.selectAudioLayout)
        goalRightLayout.addItem( QtGui.QSpacerItem(1,1,QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding) )
 
        self.layout().addWidget(self.goalIconLabel)
        self.layout().addLayout(goalRightLayout)
    
    def _loadSettings(self):
        self.settings = QtCore.QSettings( AUTHOR_NAME, PROGRAM_NAME)
        self.lastDirectory = self.settings.value("LastDirectory", QtCore.QString() ).toString()
        self.lastDirectoryAudio = self.settings.value("AudioLastDirectory", QtCore.QString() ).toString()
            
    def _selectImage(self):
        fileName = str(QtGui.QFileDialog.getOpenFileName(self,"Select an Image",self.lastDirectory,"Image Files (*.png *.jpg *.bmp *.tif);"))
        #Only continue when there's a selection
        if fileName == "": 
            return
        
        directory = fileName.split('/')
        directory.pop()
        self.lastDirectory = "/".join(directory)+"/" 

        self.settings.setValue("LastDirectory", QtCore.QVariant(QtCore.QString(self.lastDirectory)) )        
        self.selectImageEdit.setText(fileName)
        
        pixmap = QtGui.QPixmap(fileName)
        self.goalIconLabel.setPixmap( pixmap )

    def _selectAudio(self):
        fileName = unicode(QtGui.QFileDialog.getOpenFileName(self,"Select Audio",self.lastDirectoryAudio,"Audio Files (*.mp3 *.avi *.wav);;"))    
        if fileName == "": return
        
        directory = fileName.split('/')
        directory.pop()
        self.lastDirectoryAudio = "/".join(directory)+"/" 
        
        self.settings.setValue("AudioLastDirectory", QtCore.QVariant(QtCore.QString(self.lastDirectoryAudio)) )        
        self.selectAudioEdit.setText(fileName)
        
    def _currentDateTime(self):
        return QtCore.QDateTime.currentDateTime()
    
class GoalListWidgetPart(QtGui.QFrame):
    '''
    A widget that acts as a part of a list widget, although it is a list view widget
    Represents goal threads that are currently running on the main widget
    Is used to keep track of running threads and to stop them as well
    '''
    
    removeClicked = QtCore.pyqtSignal(object)
    
    def __init__(self,):   
        super(GoalListWidgetPart, self).__init__()

        self.setMinimumWidth(200)
        self.setFrameShape(QtGui.QFrame.StyledPanel)

        self.hlayout = QtGui.QHBoxLayout()
        self.hlayout.setContentsMargins(10, 1, 1, 1)
        self.setLayout(self.hlayout)
        
        self.removeButton = QtGui.QPushButton("Remove")
        self.removeButton.clicked.connect( lambda : self.removeClicked.emit(self) )
        
        self.titleLabel = QtGui.QLabel("")
        
        self.dateTimeEdit = QtGui.QDateTimeEdit()
        self.dateTimeEdit.setDateTime(QtCore.QDateTime.currentDateTime() )
        self.dateTimeEdit.setReadOnly(True)
        
        self.hlayout.addWidget(self.titleLabel)
        self.hlayout.addItem(QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum) )
        self.hlayout.addWidget(self.dateTimeEdit)
        self.hlayout.addWidget(self.removeButton)