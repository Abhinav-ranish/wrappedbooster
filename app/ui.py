from PyQt5.QtWidgets import QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QTabWidget, QDateTimeEdit, QHBoxLayout, QListWidget, QLineEdit
from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window properties
        self.setWindowTitle("Spotify Booster")
        self.setGeometry(100, 100, 600, 400)
        self.setWindowIcon(QIcon("icon.png"))

        # Main layout with tabs
        self.tabs = QTabWidget()

        # Tab 1: Playback Status
        self.playback_tab = QWidget()
        self.playback_layout = QVBoxLayout()

        self.token_label = QLabel("Token Status: Not Logged In")
        self.playback_layout.addWidget(self.token_label)
        self.token_label.setAlignment(Qt.AlignCenter)

        self.login_button = QPushButton("Login to Spotify")
        self.playback_layout.addWidget(self.login_button)

        self.refresh_button = QPushButton("Refresh Tokens")
        self.refresh_button.setEnabled(False)
        self.playback_layout.addWidget(self.refresh_button)

        # Playback Controls
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.stop_button = QPushButton("Stop")

        self.playback_layout.addWidget(self.play_button)
        self.playback_layout.addWidget(self.pause_button)
        self.playback_layout.addWidget(self.stop_button)

        self.playback_tab.setLayout(self.playback_layout)
        self.tabs.addTab(self.playback_tab, "Playback Status")

        # Tab 2: User Preferences
        self.preferences_tab = QWidget()
        self.preferences_layout = QVBoxLayout()

        self.song_list_label = QLabel("Top Songs for Boosting:")
        self.preferences_layout.addWidget(self.song_list_label)

        self.song_list = QListWidget()
        self.preferences_layout.addWidget(self.song_list)

        self.add_song_layout = QHBoxLayout()
        self.song_input = QLineEdit()
        self.song_input.setPlaceholderText("Enter song name or URL")
        self.add_song_layout.addWidget(self.song_input)

        self.add_song_button = QPushButton("Add Song")
        self.add_song_layout.addWidget(self.add_song_button)
        self.preferences_layout.addLayout(self.add_song_layout)

        self.save_preferences_button = QPushButton("Save Preferences")
        self.preferences_layout.addWidget(self.save_preferences_button)

        self.preferences_tab.setLayout(self.preferences_layout)
        self.tabs.addTab(self.preferences_tab, "User Preferences")

        # Tab 3: Playback Scheduler
        self.scheduler_tab = QWidget()
        self.scheduler_layout = QVBoxLayout()

        self.scheduler_label = QLabel("Set Playback Schedule:")
        self.scheduler_layout.addWidget(self.scheduler_label)

        # Start time picker
        self.start_time_picker = QDateTimeEdit()
        self.start_time_picker.setDateTime(QDateTime.currentDateTime())
        self.scheduler_layout.addWidget(QLabel("Start Time:"))
        self.scheduler_layout.addWidget(self.start_time_picker)

        # End time picker
        self.end_time_picker = QDateTimeEdit()
        self.end_time_picker.setDateTime(QDateTime.currentDateTime().addSecs(3600))  # Default +1 hour
        self.scheduler_layout.addWidget(QLabel("End Time:"))
        self.scheduler_layout.addWidget(self.end_time_picker)

        # Save schedule button
        self.save_schedule_button = QPushButton("Save Schedule")
        self.scheduler_layout.addWidget(self.save_schedule_button)

        self.scheduler_tab.setLayout(self.scheduler_layout)
        self.tabs.addTab(self.scheduler_tab, "Playback Scheduler")

        # Tab 2: Machine Learning
        self.ml_tab = QWidget()
        self.ml_layout = QVBoxLayout()

        self.start_training_button = QPushButton("Start Training")
        self.ml_layout.addWidget(self.start_training_button)

        self.create_model_button = QPushButton("Create Model")
        self.ml_layout.addWidget(self.create_model_button)

        self.ml_tab.setLayout(self.ml_layout)
        self.tabs.addTab(self.ml_tab, "Machine Learning")

        # Tab 3: Prediction
        self.prediction_tab = QWidget()
        self.prediction_layout = QVBoxLayout()

        self.start_prediction_button = QPushButton("Start Prediction")
        self.prediction_layout.addWidget(self.start_prediction_button)
        # Chart area
        self.chart_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        self.prediction_layout.addWidget(self.chart_canvas)

        self.prediction_tab.setLayout(self.prediction_layout)
        self.tabs.addTab(self.prediction_tab, "Prediction")

        # Set central widget
        self.setCentralWidget(self.tabs)
