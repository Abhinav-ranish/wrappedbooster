import sys
from PyQt5.QtWidgets import QApplication
from ui import MainWindow
from api_client import get_login_url, refresh_tokens
from PyQt5.QtCore import QThread, pyqtSignal
import webbrowser
import websocket
import time
from threading import Thread
from dotenv import load_dotenv
from pathlib import Path
import os
from plyer import notification

# Load environment variables
dotenv_path = Path(__file__).parent.parent / ".user"
load_dotenv(dotenv_path)

class WebSocketClient(QThread):
    reload_signal = pyqtSignal(str)  # Signal to notify the GUI of updates

    def run(self):
        """Run the WebSocket listener in a thread."""
        def on_message(ws, message):
            if message == "reload_env":
                # Reload environment variables and emit the new access token
                load_dotenv(dotenv_path)
                access_token = os.getenv("ACCESS_TOKEN")
                print(f"New access token received: {access_token}")
                self.reload_signal.emit(access_token)
            
                # Send desktop notification
                notification.notify(
                    title="Spotify Booster",
                    message="Access token updated successfully!",
                    app_name="Spotify Booster"
                )

        while True:
            try:
                ws_url = "ws://localhost:8000/ws"  # WebSocket server URL
                ws = websocket.WebSocketApp(ws_url, on_message=on_message)
                ws.run_forever()
            except Exception as e:
                print(f"WebSocket error: {e}. Retrying in 5 seconds...")
                time.sleep(5)

class LoginThread(QThread):
    login_complete = pyqtSignal(str)

    def run(self):
        try:
            login_url = get_login_url()
            webbrowser.open(login_url)
            self.login_complete.emit("Login initiated! Please complete the process in your browser.")
        except Exception as e:
            self.login_complete.emit(f"Error: {str(e)}")

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = MainWindow()

        # Connect buttons
        self.window.login_button.clicked.connect(self.login_to_spotify)
        self.window.refresh_button.clicked.connect(self.refresh_tokens)

        # WebSocket Client
        self.websocket_client = WebSocketClient()
        self.websocket_client.reload_signal.connect(self.update_access_token)
        self.websocket_client.start()

    def login_to_spotify(self):
        self.window.token_label.setText("Opening browser for login...")
        self.login_thread = LoginThread()
        self.login_thread.login_complete.connect(self.update_login_status)
        self.login_thread.start()

    def update_login_status(self, message):
        self.window.token_label.setText(message)
        if "Login initiated" in message:
            self.window.refresh_button.setEnabled(True)

    def refresh_tokens(self):
        try:
            self.window.token_label.setText("Refreshing tokens...")
            tokens = refresh_tokens()
            self.window.token_label.setText("Tokens refreshed successfully!")

            # Send desktop notification
            notification.notify(
                title="Spotify Booster",
                message="Tokens refreshed successfully!",
                app_name="Spotify Booster"
            )

        except Exception as e:
            self.window.token_label.setText(f"Error refreshing tokens: {str(e)}")
            notification.notify(
                title="Spotify Booster",
                message=f"Error refreshing tokens: {str(e)}",
                app_name="Spotify Booster"
            )


    def update_access_token(self, token):
        """Update the GUI with the new access token."""
        self.window.token_label.setText("Token Status: Logged In")
        # Notify the user
        notification.notify(
            title="Spotify Booster",
            message="Access token updated in the GUI!",
            app_name="Spotify Booster"
        )

    def run(self):
        self.window.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app = AppController()
    app.run()
