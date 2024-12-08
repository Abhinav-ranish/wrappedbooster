# Spotify Wrapped Booster

## Overview

Spotify Wrapped Booster is a tool designed to help users optimize their Spotify Wrapped playlist. The app ensures that the songs you want to feature are played continuously during inactive periods, helping you meet the necessary hours and song requirements.

---

## Features

- **Spotify Authentication**: Securely log in with Spotify to manage playback.
- **Background Playback**: Runs seamlessly in the background, auto-starting with your computer.
- **Custom Scheduling**: Play specific songs during inactive periods to boost your stats.
- **Machine Learning**: Optional feature to learn your Spotify usage patterns and optimize playback.
- **Minimal GUI**: Simple interface for setting preferences and tracking progress.
- **Data Storage**: Saves user preferences and tokens locally or in a database.

---

## Installation

### Prerequisites

- Python 3.8 or higher.
- Spotify Developer Account for API credentials.
- (Optional) MongoDB for database storage.

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/spotify-wrapped-booster.git
   cd spotify-wrapped-booster
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up Spotify API credentials:

   - Create a Spotify app at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
   - Add your client ID, secret, and redirect URI in `config.json`.

4. Run the backend server:
   ```bash
   python backend/server.py
   ```
5. Start the desktop app:
   ```bash
   python app/main.py
   ```

---

## Usage

1. Log in with your Spotify account through the app.
2. Configure playback settings and enable "Learn My Usage" for machine learning predictions.
3. Minimize the app to the system tray, where it will continue playback in the background.

---

## Development

### Backend

- Located in `backend/`.
- Handles Spotify OAuth2 and token management.

### Frontend

- Located in `app/`.
- Provides the user interface and playback scheduler.

### Machine Learning

- Training script available in `ml/`.

---

## Roadmap

1. Add support for cross-platform compatibility (Mac, Linux).
2. Expand ML capabilities for better predictions.
3. Introduce advanced analytics for playback statistics.

---

## Contributing

Feel free to fork the repository and submit pull requests. Contributions are welcome!

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.

```

Let me know if you want help implementing any of these sections or adding more details!
```
