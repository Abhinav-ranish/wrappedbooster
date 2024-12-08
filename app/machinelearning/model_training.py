import sqlite3
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import lightgbm as lgb
from sklearn.metrics import classification_report
import joblib

# Database and model paths
DATABASE_PATH = "activity_log.db"
MODEL_PATH = "saved_models/activity_model.pkl"

# Step 1: Load and Prepare Data
def load_and_prepare_data():
    """Load data from the database and prepare features."""
    # Connect to SQLite database
    conn = sqlite3.connect(DATABASE_PATH)
    df = pd.read_sql_query("SELECT * FROM playback_activity", conn)
    conn.close()

    # Parse timestamps and extract features
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour  # Hour of the day
    df['day_of_week'] = df['timestamp'].dt.dayofweek  # Day of the week
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)  # Weekend flag

    # Encode 'status' as the target variable
    label_encoder = LabelEncoder()
    df['status_encoded'] = label_encoder.fit_transform(df['status'])

    # Define features and target
    X = df[['hour', 'day_of_week', 'is_weekend']]
    y = df['status_encoded']

    # Split into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    return X_train, X_test, y_train, y_test, label_encoder

# Step 2: Train and Evaluate the Model
def train_and_evaluate_model(X_train, X_test, y_train, y_test):
    """Train a LightGBM model and evaluate its performance."""
    print("Training the model...")
    model = lgb.LGBMClassifier(random_state=42)
    model.fit(X_train, y_train)

    # Make predictions
    y_pred = model.predict(X_test)

    # Evaluate performance
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    return model

# Step 3: Save the Model
def save_model(model, label_encoder, model_path=MODEL_PATH):
    """Save the trained model and label encoder to a file."""
    joblib.dump((model, label_encoder), model_path)
    print(f"Model and label encoder saved to {model_path}.")

# Step 4: Load the Model (if needed later)
def load_model(model_path=MODEL_PATH):
    """Load a trained model and label encoder."""
    return joblib.load(model_path)

# Main Workflow
def main():
    # Load and prepare data
    print("Loading and preparing data...")
    X_train, X_test, y_train, y_test, label_encoder = load_and_prepare_data()

    # Train and evaluate the model
    model = train_and_evaluate_model(X_train, X_test, y_train, y_test)

    # Save the model
    print("Saving the trained model...")
    save_model(model, label_encoder)

if __name__ == "__main__":
    main()
