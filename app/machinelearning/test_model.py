import joblib
import pandas as pd

# Path to the saved model
MODEL_PATH = "saved_models/activity_model.pkl"

def test_model():
    """Test the trained model with sample data."""
    # Load the trained model and label encoder
    model, label_encoder = joblib.load(MODEL_PATH)

    # Sample data for testing
    sample_data = pd.DataFrame({
        "hour": [9, 14, 21],
        "day_of_week": [0, 4, 6],  # Monday, Friday, Sunday
        "is_weekend": [0, 0, 1]
    })

    # Make predictions
    predictions = model.predict(sample_data)
    decoded_predictions = label_encoder.inverse_transform(predictions)

    # Display results
    for i, prediction in enumerate(decoded_predictions):
        print(f"Sample {i + 1}: Predicted Status - {prediction}")

if __name__ == "__main__":
    test_model()
