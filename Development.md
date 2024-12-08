# Development Plan: Spotify Wrapped Booster

## Overview

The Spotify Wrapped Booster app is designed to optimize your Spotify Wrapped by intelligently managing playback to meet specific song and hour requirements. It runs seamlessly in the background, with a machine learning component to predict user activity and playback behavior.

---

## Project Components

### 1. Backend Server

- **Purpose**: Manage Spotify authentication and provide APIs for user data and token refresh.
- **Technology**: Python (FastAPI/Flask) or Node.js.
- **Key Features**:
  - OAuth2 integration with Spotify.
  - API endpoints for:
    - Fetching user data.
    - Refreshing tokens.
  - JSON or MongoDB storage for user tokens and settings.

### 2. Frontend/Desktop App

- **Purpose**: User interface for preferences, status, and scheduling.
- **Technology Options**:
  - **Desktop**: Python (PyQt/Tkinter) or Java (JavaFX).
  - **Web**: ReactJS or HTML/CSS + Flask/FastAPI for backend APIs.
- **Key Features**:
  - Minimal GUI with settings and playback tracking.
  - System tray support for Windows (runs in background).
  - Auto-start on boot.

### 3. Background Scheduler

- **Purpose**: Manage song playback and ensure background operation.
- **Technology**: Python `schedule` library or `threading`.
- **Key Features**:
  - Automates playback when user is inactive.
  - Integrates with machine learning model to predict user activity.

### 4. Machine Learning Model

- **Purpose**: Predict user activity for smarter playback scheduling.
- **Technology**: Python (scikit-learn, TensorFlow, or PyTorch).
- **Key Features**:
  - Train a model on user activity data (login/logout times).
  - Dynamically adjust playback schedule based on predictions.

### 5. Database

- **Purpose**: Store user preferences, playback logs, and credentials.
- **Technology Options**:
  - JSON file for local desktop storage.
  - MongoDB for web-based scalability.
- **Key Features**:
  - Save user tokens and preferences.
  - Track playback hours and song statistics.

---

## **Development Phases**

### **Phase 1: Backend Development**
- **Objective**: Set up a robust backend to handle Spotify authentication and token management.
1. Set up Spotify authentication using OAuth2.
2. Create APIs to:
   - Fetch user data.
   - Refresh tokens.
3. Test token handling and storage with a sample JSON or MongoDB setup.

---

### **Phase 2: Frontend/Desktop App**

#### **Phase 2a: Basic Functionality**
- **Objective**: Establish basic GUI functionality and WebSocket integration.
1. Build a basic GUI to display user preferences and playback status.
2. Integrate WebSocket to receive real-time updates from the backend.
3. Add desktop notifications for events (e.g., token refresh, updates).

#### **Phase 2b: Enhanced GUI and System Tray**
- **Objective**: Enhance the desktop app for better usability.
1. Add system tray integration for Windows:
   - Run app in the background.
   - Add tray icon for quick controls (e.g., pause/resume playback).
2. Extend GUI to show:
   - Playback status.
   - Token expiry time.
3. Include options for user preferences:
   - Set top songs for boosting.
   - Enable/disable specific features.

---

### **Phase 3: Playback Scheduler**
- **Objective**: Implement a playback mechanism to meet Spotify Wrapped goals.
1. Implement a background playback mechanism using threading or scheduling.
2. Allow users to set schedules for automatic playback.
3. Ensure playback runs seamlessly without interrupting user activities.

---

### **Phase 4: Machine Learning Integration**

#### **Phase 4a: Data Collection**
1. Collect user activity data (e.g., login/logout times, playback history).
2. Store data securely in a local database (e.g., SQLite) or MongoDB.

#### **Phase 4b: Model Development**
1. Use collected data to train a time-series model (e.g., using `scikit-learn` or `tensorflow`).
2. Predict activity patterns (e.g., when the user is likely to interact with Spotify).

#### **Phase 4c: Integration**
1. Integrate predictions into the playback scheduler.
2. Add a "Learning Mode" option in the GUI for users to enable/disable predictions.

---

### **Phase 5: Testing and Deployment**

1. **Testing**:
   - End-to-end workflow:
     - User authentication.
     - Playback scheduling.
     - Machine learning predictions.
   - Cross-platform testing (Windows, macOS, Linux if applicable).

2. **Deployment**:
   - Package the desktop app using tools like PyInstaller or Electron.
   - Create an installer for easy distribution.

---

## Tools and Libraries

### Backend

- Spotify API Library: `spotipy` (Python).
- Web Framework: FastAPI or Flask.

### Frontend/Desktop

- GUI: PyQt/Tkinter (Python) or JavaFX (Java).
- Web Option: ReactJS + REST API integration.

### Scheduler

- Python `schedule` or `threading`.

### Machine Learning

- Libraries: scikit-learn, TensorFlow (if needed).

### Database

- JSON (`json` module in Python) or MongoDB (`pymongo`).

---

## Deployment

- Package the app using PyInstaller (for Python).
- Enable auto-start on boot via Windows Registry or Startup Folder.
- Encrypt stored credentials for user privacy.

---
