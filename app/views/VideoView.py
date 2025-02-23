import time
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSlider, QFileDialog, QHBoxLayout, QSizePolicy, QFrame, QProgressDialog, QMessageBox
from PySide6.QtGui import QImage, QPixmap, QIcon
from PySide6.QtCore import Qt, QThread, QUrl
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from controllers import VideoProcessor
from views.component import FilterListWidget, VideoPlayer, SettingWidget, ContentLabeling
from utils import Colors, Style, Icons

class VideoView(QWidget):
    '''PySide6를 이용한 비디오 재생 화면 구성 클래스'''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.video_processor = VideoProcessor()
        self.video_processor.encodingVideoPathEvent.connect(self.get_encoding_video)
        self.origin_video_path : str = None
        self.encoding_video_path : str = None
        self.initUI()

    def initUI(self):
        '''UI 초기화'''
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        self.video_player = VideoPlayer()
        self.video_player.setPlayVideo.connect(self.get_encoding_video)
        
        # 설정 위젯에 버튼 추가
        left_layout = self.initSettingButtons()
        
        layout.addWidget(self.video_player, 4)
        layout.addWidget(left_layout, 1)

        self.setLayout(layout)

    def initSettingButtons(self):
        '''설정 위젯에 버튼 추가'''
        frame = QWidget()
        frame.setStyleSheet(Style.frame_style)
        frame.setGraphicsEffect(Style.shadow(frame))
        frame.setMinimumWidth(200)
        
        setting_widget = SettingWidget()
        
        list_frame = ContentLabeling()
        list_frame.setLabel("필터 목록")
        list_frame.setStyleSheet(Style.frame_style)
        list_frame.setContentMargin(0,0,0,0)
        
        self.filter_list_widget = FilterListWidget()
        self.filter_list_widget.set_items_event(self.set_current_filter)
        list_frame.setContent(self.filter_list_widget)
        setting_widget.addWidget(list_frame)

        self.button1 = QPushButton("인코딩")
        self.button1.setFixedHeight(40)
        self.button1.setStyleSheet(Style.mini_button_style)
        self.button1.clicked.connect(self.do_video_encoding)
        self.button2 = QPushButton("다운로드")
        self.button2.setStyleSheet(Style.mini_button_style)
        self.button2.setFixedHeight(40)
        self.button2.clicked.connect(self.download_video)
        
        tool_button_frame = QWidget()
        tool_button_layout = QHBoxLayout()
        tool_button_layout.setAlignment(Qt.AlignLeft)
        
        button3 = QPushButton()
        button3.setIcon(QIcon(Icons.folder_open))
        button3.setStyleSheet(Style.mini_button_style)
        button3.clicked.connect(self.openFileDialog)
        button3.setFixedSize(50, 50)
        button3.setToolTip("파일탐색")
        
        button4 = QPushButton()
        button4.setIcon(QIcon(Icons.reload))
        button4.setStyleSheet(Style.mini_button_style)
        button4.clicked.connect(self.resetVideo)
        button4.setFixedSize(50, 50)
        button4.setToolTip("초기화")
        
        tool_button_layout.addWidget(button3)
        tool_button_layout.addWidget(button4)
        tool_button_frame.setLayout(tool_button_layout)

        setting_button_layout = QVBoxLayout()
        setting_button_frame = QWidget()
        setting_button_layout.setContentsMargins(15,0,15,5)
        setting_button_layout.addWidget(self.button1)
        setting_button_layout.addWidget(self.button2)
        setting_button_frame.setLayout(setting_button_layout)

        layout = QVBoxLayout()
        layout.addWidget(tool_button_frame)
        layout.addWidget(setting_widget)
        layout.addWidget(setting_button_frame)
        layout.setContentsMargins(5,5,5,5)
        frame.setLayout(layout)
        return frame
    
    def resetVideo(self):
        if self.origin_video_path:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
            msg.setText("작업 내용을 초기화 하시겠습니까?")
            msg.setWindowTitle("알림")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)

            result = msg.exec_()
            
            if result == QMessageBox.Yes:
                print("yes reset")
                self.encoding_video_path = None
                self.video_processor.temp_video_path = None
                self.video_processor.video_path = None
                self.video_processor.set_video(self.origin_video_path)
                self.video_processor.set_origin_video(self.origin_video_path)
                self.video_player.set_video(self.origin_video_path)
                self.video_player.start_video()
            elif result == QMessageBox.No:
                msg.close()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
            msg.setText("초기화 시킬 내용이 없습니다")
            msg.setWindowTitle("경고")
            msg.exec_()

        
    def openFileDialog(self):
        '''파일 대화상자를 통해 비디오 파일 선택'''
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(self, "Open Video File", "", "Video Files (*.mp4 *.avi *.mkv *.flv);;All Files (*)", options=options)
        if filePath:
            self.origin_video_path = filePath
            self.video_processor.set_origin_video(filePath)
            self.video_processor.is_complete = True
            self.play_video(filePath)

    def play_video(self, video_path):
        """영상 재생"""
        if self.video_processor.is_complete is True :
            self.video_processor.set_video(video_path)
            self.video_player.set_video(video_path)
            self.video_player.start_video()
        else :
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
            msg.setText("영상파일을 인식할 수 없습니다.")
            msg.setWindowTitle("경고")
            msg.exec_()

    def set_current_filter(self, index = None):
        """필터 옵션 선택"""
        if index == False:
            index = None

        self.video_processor.set_filter(index)

    def do_video_encoding(self):
        """비디오 인코딩"""
        #다이얼로그 구문 
        print("do_video_encoding")
        if self.filter_list_widget.seleted_filter is None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
            msg.setText("필터가 선택되지 않았습니다.")
            msg.setWindowTitle("경고")
            msg.exec_()
        elif self.origin_video_path:         
            self.video_processor.set_origin_video(self.origin_video_path)
            self.video_processor.is_complete = True
            self.video_player.set_video(self.origin_video_path)
            # self.video_processor.set_video(self.origin_video_path)

            self.video_player.stop_video()

            self.progress_dialog = QProgressDialog("Encoding", "Cancel", 0, 100)
            self.video_processor.progressChanged.connect(self.setProgress)
            self.progress_dialog.canceled.connect(self.cancelCounting) # 취소시

            self.video_processor.start()

            self.progress_dialog.exec_()
            
        else:
            # todo : 동영상이 선택 되지 않았음을 알려야 함
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
            msg.setText("동영상을 가져오지 못했습니다")
            msg.setWindowTitle("경고")
            msg.exec_()
        
    
    def setProgress(self, value):
        """작업 진행 상황 업데이트"""
        self.progress_dialog.setValue(value)

    def cancelCounting(self):
        """인코딩 취소시"""
        self.video_processor.encoding_cancel()
        self.encoding_video_path = self.origin_video_path
        self.play_video(self.origin_video_path)
        
    def get_encoding_video(self, video_path):
        """인코딩 후 영상 반환, 재생"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
        msg.setText("인코딩이 완료 되었습니다")
        msg.setWindowTitle("알림")
        msg.exec_()
        if self.video_processor.is_complete is True :
            self.encoding_video_path = video_path
            self.play_video(video_path)

    
    def download_video(self):
        """영상 다운로드"""
        try:
            self.video_processor.download_video()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("다운로드가 완료되었습니다")
            msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
            msg.setWindowTitle("알림")
            msg.exec_()
        except ValueError as e:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("인코딩 영상이 존재하지 않습니다")
            msg.setWindowFlags(msg.windowFlags() | Qt.WindowStaysOnTopHint)
            msg.setWindowTitle("경고")
            msg.exec_()
            
        
        
    def render(self):
        """페이지 refresh"""
        self.filter_list_widget.clear_seletecd()
        self.set_current_filter(None)
        
    def cleanup(self):
        self.set_current_filter(None)
        pass
        
