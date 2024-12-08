import sys
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt5.QtGui import QIcon
from ui import MainWindow
from api_client import get_login_url, refresh_tokens
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from datetime import datetime, timedelta
from api_client import start_playback, pause_playback, stop_playback
import webbrowser
import websocket
import time
from threading import Thread
from dotenv import load_dotenv
from pathlib import Path
import os
from plyer import notification
import json

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

        # System Tray Integration
        self.tray_icon = QSystemTrayIcon(QIcon("icon.png"), self.app)  # Use your app's icon here
        self.tray_icon.setToolTip("Spotify Booster")

        # Preferences
        self.preferences_file = "user_preferences.json"
        self.load_preferences()

        self.window.add_song_button.clicked.connect(self.add_song)
        self.window.save_preferences_button.clicked.connect(self.save_preferences)

        # Tray Menu
        self.tray_menu = QMenu()
        self.show_action = self.tray_menu.addAction("Show App")
        self.exit_action = self.tray_menu.addAction("Exit")

        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.show_action.triggered.connect(self.show_app)
        self.exit_action.triggered.connect(self.exit_app)

        self.tray_icon.show()


        self.token_expiry_timer = QTimer()
        self.token_expiry_timer.timeout.connect(self.update_token_expiry)
        self.token_expiry_timer.start(1000)  # Update every second

        self.refresh_threshold = timedelta(minutes=5)

        # Connect playback controls
        self.window.play_button.clicked.connect(self.play_song)
        self.window.pause_button.clicked.connect(self.pause_song)
        self.window.stop_button.clicked.connect(self.stop_playback)

    def login_to_spotify(self):
        self.window.token_label.setText("Opening browser for login...")
        self.login_thread = LoginThread()
        self.login_thread.login_complete.connect(self.update_login_status)
        self.login_thread.start()

    def update_login_status(self, message):
        self.window.token_label.setText(message)
        if "Login initiated" in message:
            self.window.refresh_button.setEnabled(True)
    
    def on_tray_icon_activated(self, reason):
        """Handle tray icon click events."""
        if reason == QSystemTrayIcon.Trigger:  # Single click
            self.show_app()

    def show_app(self):
        """Restore the app window."""
        self.window.showNormal()
        self.window.activateWindow()

    def exit_app(self):
        """Exit the application."""
        self.websocket_client.terminate()
        self.app.quit()

    def refresh_tokens(self):
        try:
            self.window.token_label.setText("Refreshing tokens...")
            tokens = refresh_tokens()
            self.window.token_label.setText("Tokens refreshed successfully!")

            # Send desktop notification
            notification.notify(
                title="Spotify Booster",
                message="Tokens refreshed successfully!",
                app_name="Spotify Booster",
                timeout=3
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

    
    def update_token_expiry(self):
        """Update the token expiry label dynamically and refresh tokens if needed."""
        try:
            expires_in = os.getenv("EXPIRES_IN")
            if expires_in:
                token_expiry_time = datetime.now() + timedelta(seconds=int(expires_in))
                time_remaining = token_expiry_time - datetime.now()

                # if time_remaining.total_seconds() > 0:
                #     print(f"Token Expires In: {str(time_remaining).split('.')[0]}")
                # else:
                #     print("Token Expired")
                
                # Auto-refresh token if within the threshold
                if time_remaining <= self.refresh_threshold:
                    self.auto_refresh_tokens()
            else:
                self.window.token_label.setText("Token Expiry Unknown")
        except Exception as e:
            print(f"Error updating token expiry: {e}")

    def auto_refresh_tokens(self):
        """Automatically refresh the token before it expires."""
        try:
            print("Token is nearing expiry. Refreshing tokens...")
            tokens = refresh_tokens()  # Call the API client to refresh tokens
            load_dotenv(dotenv_path)  # Reload updated tokens
            access_token = os.getenv("ACCESS_TOKEN")

            # Update GUI and send a notification
            self.update_access_token(access_token)
            notification.notify(
                title="Spotify Booster",
                message="Token auto-refreshed successfully!",
                app_name="Spotify Booster"
            )
        except Exception as e:
            print(f"Error auto-refreshing tokens: {e}")
            notification.notify(
                title="Spotify Booster",
                message=f"Error auto-refreshing tokens: {str(e)}",
                app_name="Spotify Booster"
            )

    def load_preferences(self):
        """Load user preferences from a JSON file."""
        try:
            with open(self.preferences_file, "r") as f:
                preferences = json.load(f)
                self.window.song_list.addItems(preferences.get("songs", []))
        except FileNotFoundError:
            print("Preferences file not found. Creating a new one.")
        except Exception as e:
            print(f"Error loading preferences: {e}")

    def add_song(self):
        """Add a song to the preferences list."""
        song = self.window.song_input.text().strip()
        if song:
            self.window.song_list.addItem(song)
            self.window.song_input.clear()
            notification.notify(
                title="Spotify Booster",
                message=f"Added song: {song}",
                app_name="Spotify Booster"
            )

    def save_preferences(self):
        """Save user preferences to a JSON file."""
        try:
            songs = [self.window.song_list.item(i).text() for i in range(self.window.song_list.count())]
            preferences = {"songs": songs}

            with open(self.preferences_file, "w") as f:
                json.dump(preferences, f, indent=4)

            notification.notify(
                title="Spotify Booster",
                message="Preferences saved successfully!",
                app_name="Spotify Booster"
            )
        except Exception as e:
            print(f"Error saving preferences: {e}")
            notification.notify(
                title="Spotify Booster",
                message=f"Error saving preferences: {str(e)}",
                app_name="Spotify Booster"
            )

    
    def play_song(self):
        """Start playback on Spotify."""
        try:
            # Example URI for testing; replace with user-selected song if needed
            example_song_uri = "spotify:track:2plbrEY59IikOBgBGLjaoe"
            # https://open.spotify.com/track/2plbrEY59IikOBgBGLjaoe?si=73e7f6a50f7c43da spotify:track:2plbrEY59IikOBgBGLjaoe  spotify.com/track/ 2plbrEY59IikOBgBGLjaoe  ?si=73e7f6a50f7c43da
            start_playback(example_song_uri)
            self.window.token_label.setText("Playing song...")
            notification.notify(
                title="Spotify Booster",
                message="Playback started successfully!",
                app_name="Spotify Booster",
                timeout=2
            )
        except Exception as e:
            self.window.token_label.setText(f"Error playing song: {str(e)}")
            notification.notify(
                title="Spotify Booster",
                message=f"Error playing song: {str(e)}",
                app_name="Spotify Booster"
            )

    def pause_song(self):
        """Pause playback on Spotify."""
        try:
            pause_playback()
            self.window.token_label.setText("Playback paused.")
        except Exception as e:
            print(f"Error pausing playback: {str(e)}")


    def stop_playback(self):
        """Stop playback on Spotify."""
        try:
            stop_playback()
            self.window.token_label.setText("Playback stopped.")
        except Exception as e:
            print(f"Error stopping playback: {str(e)}")


    def run(self):
        self.window.show()
        sys.exit(self.app.exec_())
    
    

if __name__ == "__main__":
    app = AppController()
    app.run()
