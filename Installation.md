# Installation Guide for Spotify Wrapped Booster

Follow these steps to set up and run the Spotify Wrapped Booster on your system.

---

## Prerequisites

- Python 3.8 or higher.
- A Spotify Developer Account to create API credentials.

---

## Step-by-Step Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/abhinav-ranish/wrappedbot.git
cd wrappedbot
```

### Step 2: Install Dependencies

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

### Step 3: Set Up Spotify API Credentials

1. Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Create a new application.
3. Add your `Client ID`, `Client Secret`, and `Redirect URI` in a `config.json` file:

   Example `config.json`:

   ```json
   {
       "SPOTIFY_CLIENT_ID": "your_client_id_here",
       "SPOTIFY_CLIENT_SECRET": "your_client_secret_here",
       "SPOTIFY_REDIRECT_URI": "http://localhost:8000/callback"
   }
   ```

### Step 4: Run the Backend Server

```bash
cd backend
uvicorn server:app --reload
```

Ensure the server is running to handle Spotify authentication and API requests.

### Step 5: Start the Desktop App

```bash
python app/app_controller.py
```

The GUI application will launch, allowing you to log in and configure playback.

---

## Common Issues and Troubleshooting

### Missing Dependencies

If a dependency is missing, try installing it individually:

```bash
pip install <package_name>
```

### Spotify API Error

Ensure your `config.json` is correct and the `Redirect URI` matches what is registered in the Spotify Developer Dashboard.

---

## Need Help?

For support, open an issue in the [GitHub repository](https://github.com/abhinav-ranish/wrappedbot/issues).
```

