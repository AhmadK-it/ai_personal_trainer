import random

import joblib
import pandas as pd

# Load the saved pipeline
loaded_pipeline = joblib.load('trained_pipeline.pkl')

# Helper functions
def calculate_bmi(height_cm, weight_kg):
    height_m = height_cm / 100  # Convert height to meters
    bmi = weight_kg / (height_m ** 2)  # Calculate BMI
    return bmi

def categorize_bmi(bmi):
    if bmi < 18.5:
        return 'Underweight'
    elif 18.5 <= bmi < 24.9:
        return 'Normal Weight'
    elif bmi >= 25:
        return 'Overweight'

def process_json_input(json_input):
    age = json_input["age"]
    weight = json_input["weight"]
    height = json_input["height"]
    weakness_points = json_input.get("weakness_points", "No pain")
    experience_level = json_input["experience_level"]
    
    # Calculate BMI and categorize it
    bmi_value = calculate_bmi(height, weight)
    bmi_category = categorize_bmi(bmi_value)
    
    # Prepare the data in the expected format
    data_dict = {
        "Age": [age],
        "BMI Category": [bmi_category],
        "Training Experience": [experience_level],
        "Pain 1": [weakness_points.split(",")[0] if weakness_points else "No pain"],
        "Pain 2": [weakness_points.split(",")[1] if "," in weakness_points else "No pain"]
    }
    
    # Convert to DataFrame
    df = pd.DataFrame(data_dict)
    
    return df

# Example JSON input
json_input = {
    "age": 46,
    "weight": 90,
    "height": 180,
    "weakness_points": "Shoulder,Knee",
    "experience_level": "BEGINNER"
}

# Process the JSON input to create a DataFrame
input_df = process_json_input(json_input)

# Use the loaded pipeline to make predictions
predictions = loaded_pipeline.predict(input_df)



def predict():
    return random.randint(1,9)