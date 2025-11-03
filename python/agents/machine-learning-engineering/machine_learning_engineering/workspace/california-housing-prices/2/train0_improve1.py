
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.impute import SimpleImputer
import os
import sys

def install_and_import(package):
    """
    Installs a package if not found and then imports it.
    """
    try:
        __import__(package)
    except ImportError:
        print(f"Installing {package}...")
        try:
            # Use sys.executable to ensure pip corresponds to the current Python environment
            os.system(f"{sys.executable} -m pip install {package}")
            __import__(package)
            print(f"{package} installed successfully.")
        except Exception as e:
            print(f"Failed to install {package}: {e}")
            raise

# Ensure necessary libraries are installed
install_and_import('pandas')
install_and_import('numpy')
install_and_import('sklearn') # scikit-learn is imported as sklearn

def main():
    # Define file paths
    train_file = "./input/train.csv"
    test_file = "./input/test.csv"
    submission_file = "submission.csv"

    # 1. Load Data
    try:
        train_df = pd.read_csv(train_file)
        test_df = pd.read_csv(test_file)
    except FileNotFoundError:
        print(f"Error: Ensure '{train_file}' and '{test_file}' exist in the './input' directory.")
        return

    # Separate target variable
    X = train_df.drop("median_house_value", axis=1)
    y = train_df["median_house_value"]

    # Combine train and test for consistent preprocessing
    combined_df = pd.concat([X, test_df], ignore_index=True)

    # 2. Preprocessing
    # Impute missing values for 'total_bedrooms'
    # Ensure all columns exist before trying to impute
    if 'total_bedrooms' in combined_df.columns:
        imputer = SimpleImputer(strategy="median")
        combined_df['total_bedrooms'] = imputer.fit_transform(combined_df[['total_bedrooms']])


    # Feature Engineering (example features)
    # Avoid division by zero by adding a small epsilon or handling NaNs after creation
    combined_df['households_safe'] = combined_df['households'].replace(0, 1) # Replace 0 with 1 to avoid division by zero
    combined_df['total_rooms_safe'] = combined_df['total_rooms'].replace(0, 1) # Replace 0 with 1 to avoid division by zero
    # New: Add population_safe for rooms_per_person calculation
    combined_df['population_safe'] = combined_df['population'].replace(0, 1) # Replace 0 with 1 to avoid division by zero

    combined_df['rooms_per_household'] = combined_df['total_rooms'] / combined_df['households_safe']
    combined_df['bedrooms_per_room'] = combined_df['total_bedrooms'] / combined_df['total_rooms_safe']
    combined_df['population_per_household'] = combined_df['population'] / combined_df['households_safe']
    
    # Targeted, domain-specific interaction terms and transformations
    # 1. latitude * longitude for spatial relationships
    combined_df['latitude_longitude'] = combined_df['latitude'] * combined_df['longitude']
    
    # 2. median_income * rooms_per_household to capture quality of life
    combined_df['income_per_room_household'] = combined_df['median_income'] * combined_df['rooms_per_household']
    
    # 3. housing_median_age * median_income for value depreciation with income
    combined_df['age_income_interaction'] = combined_df['housing_median_age'] * combined_df['median_income']
    
    # 4. rooms_per_person to better represent living space density
    combined_df['rooms_per_person'] = combined_df['total_rooms'] / combined_df['population_safe']

    # Drop the safe columns used for calculation
    combined_df = combined_df.drop(columns=['households_safe', 'total_rooms_safe', 'population_safe'])

    # After feature engineering, there might be NaNs or infs if original values were zero and replaced with NaN
    # Replace inf/-inf with NaN and then impute
    combined_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # Impute any new NaN values created by feature engineering or existing ones
    # Re-initialize imputer to ensure it fits on the current state of combined_df
    imputer_all_cols = SimpleImputer(strategy="median")
    
    # Fit and transform only columns that might have NaNs
    for col in combined_df.columns:
        if combined_df[col].isnull().any():
            combined_df[col] = imputer_all_cols.fit_transform(combined_df[[col]])



    # Split back into processed train and test sets
    X_processed = combined_df.iloc[:len(X)]
    test_processed = combined_df.iloc[len(X):]

    # 3. Model Training
    # Split training data for validation
    X_train, X_val, y_train, y_val = train_test_split(X_processed, y, test_size=0.2, random_state=42)

    # Initialize and train the model
    # Using n_jobs=-1 to utilize all available CPU cores for faster training
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    # 4. Evaluation
    y_pred_val = model.predict(X_val)
    rmse = np.sqrt(mean_squared_error(y_val, y_pred_val))

    print(f"Final Validation Performance: {rmse}")

    # 5. Prediction on test data
    test_predictions = model.predict(test_processed)

    # 6. Generate Submission File
    submission_df = pd.DataFrame({'median_house_value': test_predictions})
    submission_df.to_csv(submission_file, index=False)

    print(f"Submission file '{submission_file}' created successfully.")

if __name__ == "__main__":
    main()
