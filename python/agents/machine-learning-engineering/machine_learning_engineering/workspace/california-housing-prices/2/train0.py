
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import subprocess
import sys

# Attempt to import CatBoostRegressor, if not found, install it.
try:
    from catboost import CatBoostRegressor
except ImportError:
    print("CatBoost not found. Installing catboost...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "catboost"])
    from catboost import CatBoostRegressor
    print("CatBoost installed successfully.")


# --- Load Data ---
# All input data is stored in "./input" directory
train_df = pd.read_csv("./input/train.csv")
test_df = pd.read_csv("./input/test.csv")

# --- Feature Engineering ---
def create_features(df):
    # Avoid division by zero by replacing 0 with a small epsilon or the median/mean in the denominator
    # For this dataset, 'households' and 'total_rooms' are generally positive, but checking is good practice.
    # Let's ensure denominators are not zero before division
    df['rooms_per_household'] = df['total_rooms'] / df['households'].replace(0, np.nan)
    df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms'].replace(0, np.nan)
    df['population_per_household'] = df['population'] / df['households'].replace(0, np.nan)
    return df

train_df = create_features(train_df)
test_df = create_features(test_df)

# --- Handle Missing Values ---
# Impute missing 'total_bedrooms' with the median from the training set to prevent data leakage
median_total_bedrooms_train = train_df['total_bedrooms'].median()
train_df['total_bedrooms'].fillna(median_total_bedrooms_train, inplace=True)
test_df['total_bedrooms'].fillna(median_total_bedrooms_train, inplace=True)

# Impute missing values for engineered features.
# Use median from training data for both train and test sets to prevent data leakage.
engineered_features = ['rooms_per_household', 'bedrooms_per_room', 'population_per_household']
for col in engineered_features:
    # Calculate median only from the training data
    median_val_for_col = train_df[col].median()
    train_df[col].fillna(median_val_for_col, inplace=True)
    test_df[col].fillna(median_val_for_col, inplace=True)

# --- Define Features and Target ---
features = [
    'longitude', 'latitude', 'housing_median_age', 'total_rooms',
    'total_bedrooms', 'population', 'households', 'median_income',
    'rooms_per_household', 'bedrooms_per_room', 'population_per_household'
]
target = 'median_house_value'

X_full_train = train_df[features]
y_full_train = train_df[target]
X_test_submission = test_df[features]

# --- Model Training and Validation ---
# Split the full training data into training and validation sets for evaluating performance.
# This hold-out set ensures we get an unbiased estimate of the model's performance on unseen data.
X_train, X_val, y_train, y_val = train_test_split(X_full_train, y_full_train, test_size=0.2, random_state=42)

# Initialize CatBoost Regressor
# loss_function='RMSE' is chosen to directly optimize for the competition's evaluation metric.
# random_seed ensures reproducibility. verbose=0 suppresses training output for cleaner execution.
cat_model = CatBoostRegressor(loss_function='RMSE', random_seed=42, verbose=0)

# Train the model on the training split (80% of train.csv)
cat_model.fit(X_train, y_train)

# Make predictions on the validation set (20% of train.csv)
y_val_pred = cat_model.predict(X_val)

# Evaluate the model using Root Mean Squared Error (RMSE)
rmse_val = np.sqrt(mean_squared_error(y_val, y_val_pred))
print(f"Final Validation Performance: {rmse_val}")

# --- Retrain on full training data for final predictions ---
# It is common practice to retrain the model on the entire training dataset
# (X_full_train, y_full_train) after validating performance, to leverage all available data for the final model.
final_cat_model = CatBoostRegressor(loss_function='RMSE', random_seed=42, verbose=0)
final_cat_model.fit(X_full_train, y_full_train)

# --- Make Predictions on Test Set ---
test_predictions = final_cat_model.predict(X_test_submission)

# Ensure predictions are non-negative, as median house values cannot be negative
test_predictions[test_predictions < 0] = 0

# --- Submission Format ---
# Print the header as required by the submission format
print("median_house_value")
# Print each prediction on a new line
for val in test_predictions:
    print(f"{val}")
