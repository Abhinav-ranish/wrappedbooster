from PyQt5.QtWidgets import QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Window properties
        self.setWindowTitle("Spotify Wrapped Booster")
        self.setGeometry(100, 100, 400, 200)

        # Layout
        layout = QVBoxLayout()

        # Buttons and labels
        self.login_button = QPushButton("Login to Spotify")
        self.token_label = QLabel("Token Status: Not Logged In")
        self.token_label.setAlignment(Qt.AlignCenter)
        self.refresh_button = QPushButton("Refresh Tokens")
        self.refresh_button.setEnabled(False)  # Disable until logged in

        # Add widgets to layout
        layout.addWidget(self.token_label)
        layout.addWidget(self.login_button)
        layout.addWidget(self.refresh_button)

        # Set central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

