import time
import requests
import sqlite3
from threading import Thread
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import os

dotenv_path = Path(__file__).parent.parent / ".user"  # Adjust for relative paths
load_dotenv(dotenv_path)

class ActivityMonitor:
    def __init__(self, db_path="activity_log.db", check_interval=600):
        """
        Monitor Spotify playback activity and log it periodically.
        
        Args:
            db_path (str): Path to the SQLite database file.
            check_interval (int): Interval in seconds to check playback status (default 10 minutes).
        """
        self.db_path = db_path
        self.check_interval = check_interval
        self.running = False

        # Initialize database
        self._initialize_db()

    def _initialize_db(self):
        """Create the database table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playback_activity (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                status TEXT,
                song_name TEXT,
                artist_name TEXT
            )
        """)
        conn.commit()
        conn.close()

    def _get_playback_status(self):
        """Fetch the current playback status from Spotify."""
        access_token = os.getenv("ACCESS_TOKEN")
        if not access_token:
            raise Exception("Access token not found. Please log in.")

        headers = {"Authorization": f"Bearer {access_token}"}
        url = "https://api.spotify.com/v1/me/player/currently-playing"

        response = requests.get(url, headers=headers)
        if response.status_code == 204:  # No content (no playback)
            return None
        response.raise_for_status()

        data = response.json()
        is_playing = data.get("is_playing", False)
        song_name = data["item"]["name"]
        artist_name = ", ".join(artist["name"] for artist in data["item"]["artists"])

        return {
            "is_playing": is_playing,
            "song_name": song_name,
            "artist_name": artist_name,
        }

    def _log_activity(self, status, song_name=None, artist_name=None):
        """Log playback activity in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO playback_activity (status, song_name, artist_name)
            VALUES (?, ?, ?)
        """, (status, song_name, artist_name))
        conn.commit()
        conn.close()

    def _monitor(self):
        """Continuously monitor and log playback activity."""
        while self.running:
            try:
                playback = self._get_playback_status()
                if playback:
                    status = "playing" if playback["is_playing"] else "paused"
                    self._log_activity(status, playback["song_name"], playback["artist_name"])
                    print(f"Logged: {status} - {playback['song_name']} by {playback['artist_name']}")
                else:
                    self._log_activity("no_playback")
                    print("Logged: No playback detected.")
            except Exception as e:
                print(f"Error during monitoring: {e}")

            time.sleep(self.check_interval)

    def start(self):
        """Start the playback activity monitor."""
        if not self.running:
            self.running = True
            self.thread = Thread(target=self._monitor, daemon=True)
            self.thread.start()
            print("Activity monitor started.")

    def stop(self):
        """Stop the playback activity monitor."""
        self.running = False
        self.thread.join()
        print("Activity monitor stopped.")
