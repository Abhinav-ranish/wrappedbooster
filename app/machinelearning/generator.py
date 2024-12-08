import sqlite3
import pandas as pd # type: ignore
from datetime import datetime, timedelta
import random

DATABASE_PATH = "activity_log.db"

def generate_sample_data(num_entries=1000):
    """Generate synthetic playback activity data."""
    start_time = datetime.now() - timedelta(days=30)  # Start 30 days ago
    statuses = ["playing", "paused", "no_playback"]
    sample_data = []

    for _ in range(num_entries):
        timestamp = start_time + timedelta(minutes=random.randint(1, 1440))  # Random minute
        status = random.choice(statuses)
        song_name = f"Song {random.randint(1, 100)}" if status == "playing" else None
        artist_name = f"Artist {random.randint(1, 50)}" if status == "playing" else None
        sample_data.append((timestamp, status, song_name, artist_name))

    # Insert into database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO playback_activity (timestamp, status, song_name, artist_name)
        VALUES (?, ?, ?, ?)
    """, sample_data)
    conn.commit()
    conn.close()
    print(f"Generated {num_entries} sample entries in {DATABASE_PATH}.")

if __name__ == "__main__":
    generate_sample_data()
