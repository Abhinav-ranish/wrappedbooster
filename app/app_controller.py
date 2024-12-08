import sys
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt5.QtGui import QIcon
from ui import MainWindow
import pandas as pd
from api_client import get_login_url, refresh_tokens
from machinelearning.model_training import train_and_evaluate_model, load_and_prepare_data, save_model
from PyQt5.QtCore import QThread, pyqtSignal, QTimer
from datetime import datetime, timedelta
from api_client import start_playback, pause_playback, validate_access_token
import webbrowser
import websocket
import time
from threading import Thread
from dotenv import load_dotenv
import joblib
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
                    app_name="Spotify Booster",
                    app_icon="icon.ico",
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

        # Check and refresh tokens at startup
        self.check_and_refresh_tokens()

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

        # Scheduler
        self.schedule_file = "playback_schedule.json"
        self.load_schedule()
        self.window.save_schedule_button.clicked.connect(self.save_schedule)

        # Start scheduler thread
        self.scheduler_thread = Thread(target=self.run_scheduler, daemon=True)
        self.scheduler_thread.start()
        self.is_playing = False  # Tracks if playback is running

         # Connect Machine Learning buttons
        self.window.start_training_button.clicked.connect(self.start_training)
        self.window.create_model_button.clicked.connect(self.create_model)

        # Connect Prediction button
        self.window.start_prediction_button.clicked.connect(self.start_prediction)

        # Load trained model (initially None)
        self.model = None
        self.label_encoder = None
        
    def check_and_refresh_tokens(self):
        """Check and refresh tokens at startup."""
        try:
            load_dotenv(dotenv_path)  # Reload the .user file
            access_token = os.getenv("ACCESS_TOKEN")
            if not access_token:
                print("No valid login found. Please log in.")
                return

            # Attempt to refresh tokens
            refresh_tokens()
            print("Tokens refreshed successfully.")
        except Exception as e:
            print(f"Error refreshing tokens: {e}")


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
                app_icon="icon.ico",
                timeout=3
            )

        except Exception as e:
            self.window.token_label.setText(f"Error refreshing tokens: {str(e)}")
            notification.notify(
                title="Spotify Booster",
                message=f"Error refreshing tokens: {str(e)}",
                app_icon="icon.ico",
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
                app_icon="icon.ico",
                app_name="Spotify Booster"
            )
        except Exception as e:
            print(f"Error auto-refreshing tokens: {e}")
            notification.notify(
                title="Spotify Booster",
                message=f"Error auto-refreshing tokens: {str(e)}",
                app_name="Spotify Booster",
                app_icon="icon.ico",
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
                app_name="Spotify Booster",
                app_icon="icon.ico",
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
                app_name="Spotify Booster",
                app_icon="icon.ico",
            )
        except Exception as e:
            print(f"Error saving preferences: {e}")
            notification.notify(
                title="Spotify Booster",
                message=f"Error saving preferences: {str(e)}",
                app_name="Spotify Booster",
                app_icon="icon.ico",
            )

    def start_training(self):
        """Start the training process for the model."""
        try:
            QMessageBox.information(self.window, "Training", "Training has started!")
            X_train, X_test, y_train, y_test, label_encoder = load_and_prepare_data()
            self.model = train_and_evaluate_model(X_train, X_test, y_train, y_test)
            self.label_encoder = label_encoder
            QMessageBox.information(self.window, "Training", "Training completed!")
        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Error during training: {e}")

    def create_model(self):
        """Create and save the trained model."""
        try:
            if self.model and self.label_encoder:
                save_model(self.model, self.label_encoder)
                QMessageBox.information(self.window, "Model Saved", "The model has been saved successfully!")
            else:
                QMessageBox.warning(self.window, "Warning", "No trained model found. Train the model first.")
        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Error saving the model: {e}")

    def start_prediction(self):
        """Load the model and display playback prediction chart."""
        try:
            # Load model
            self.model, self.label_encoder = joblib.load("machinelearning/saved_models/activity_model.pkl")
            QMessageBox.information(self.window, "Prediction", "Model loaded successfully!")

            # Generate predictions
            now = pd.Timestamp.now()
            future = pd.date_range(start=now, periods=24, freq='H')  # Next 24 hours
            sample_data = pd.DataFrame({
                "hour": future.hour,
                "day_of_week": future.dayofweek,
                "is_weekend": (future.dayofweek >= 5).astype(int)
            })

            predictions = self.model.predict(sample_data)
            decoded_predictions = self.label_encoder.inverse_transform(predictions)

            # Plot chart
            ax = self.window.chart_canvas.figure.add_subplot(111)
            ax.clear()
            ax.plot(future, decoded_predictions, label="Predicted Status")
            ax.set_title("Playback Predictions")
            ax.set_xlabel("Time")
            ax.set_ylabel("Status")
            ax.legend()
            self.window.chart_canvas.draw()
        except Exception as e:
            QMessageBox.critical(self.window, "Error", f"Error during prediction: {e}")


    
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
                app_name="Spotify Booster",
                app_icon="icon.ico",
            )

    def pause_song(self):
        """Pause playback on Spotify."""
        try:
            pause_playback()
            self.window.token_label.setText("Playback paused.")
        except Exception as e:
            print(f"Error pausing playback: {str(e)}")

    def load_schedule(self):
        """Load the playback schedule from a JSON file."""
        try:
            with open(self.schedule_file, "r") as f:
                schedule = json.load(f)
                self.start_time = datetime.fromisoformat(schedule.get("start_time"))
                self.end_time = datetime.fromisoformat(schedule.get("end_time"))
        except (FileNotFoundError, ValueError):
            print("No valid schedule found.")
            self.start_time = None
            self.end_time = None

    def save_schedule(self):
        """Save the playback schedule to a JSON file."""
        try:
            start_time = self.window.start_time_picker.dateTime().toPyDateTime()
            end_time = self.window.end_time_picker.dateTime().toPyDateTime()

            if end_time <= start_time:
                self.window.scheduler_label.setText("End time must be after start time.")
                return

            schedule = {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            }

            with open(self.schedule_file, "w") as f:
                json.dump(schedule, f, indent=4)

            self.start_time = start_time
            self.end_time = end_time
            self.window.scheduler_label.setText("Schedule saved successfully!")

            notification.notify(
                title="Spotify Booster",
                message="Playback schedule saved!",
                app_name="Spotify Booster",
                app_icon="icon.ico",
            )
        except Exception as e:
            print(f"Error saving schedule: {e}")
            self.window.scheduler_label.setText("Error saving schedule.")

    def run_scheduler(self):
        """Continuously check if it's time to start or stop playback."""
        while True:
            try:
                now = datetime.now()
                if self.start_time and self.end_time:
                    if self.start_time <= now <= self.end_time:
                        if not self.is_playing:
                            self.start_playback_if_not_running()
                    elif now > self.end_time:
                        self.stop_playback()
                time.sleep(120)  # Check every 30 seconds to avoid spamming
            except Exception as e:
                print(f"Scheduler error: {e}")



    def start_playback_if_not_running(self):
        """Start playback if it's not already running."""
        try:
            if self.is_playing:
                print("Playback is already running. Skipping API call.")
                return

            if not validate_access_token():
                print("Access token invalid or expired. Login required.")
                return

            try:
                start_playback()  # Attempt to start playback
                self.is_playing = True  # Set playback state
                self.schedule_recheck()  # Schedule a recheck for later

                notification.notify(
                    title="Spotify Booster",
                    message="Scheduled playback started!",
                    app_name="Spotify Booster",
                    app_icon="icon.ico",
                )
            except Exception as e:
                print(f"Error starting playback: {e}")
        except Exception as e:
            print(f"Error during playback handling: {e}")



    def schedule_recheck(self):
        """Schedule a recheck to validate playback after a certain period."""
        Thread(target=self.recheck_playback_status, daemon=True).start()

    def recheck_playback_status(self):
        """Recheck playback status after 30 minutes."""
        time.sleep(1800)  # Wait 30 minutes
        print("Rechecking playback status...")
        try:
            if validate_access_token():
                self.is_playing = False  # Reset state to trigger revalidation
            else:
                print("Access token expired during playback. Login required.")
        except Exception as e:
            print(f"Error rechecking playback: {e}")

    def stop_playback(self):
        """Stop playback if the schedule ends."""
        try:
            # pause_playback()  # Pause instead of stopping
            self.start_time = None
            self.end_time = None  # Clear the schedule after stopping playback
            notification.notify(
                title="Spotify Booster",
                message="Scheduled playback stopped!",
                app_name="Spotify Booster",
                app_icon="icon.ico",
            )
        except Exception as e:
            print(f"Error stopping playback: {e}")

    def run(self):
        self.window.show()
        sys.exit(self.app.exec_())
    
    

if __name__ == "__main__":
    app = AppController()
    app.run()
