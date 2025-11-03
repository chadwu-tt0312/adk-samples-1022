
import pandas as pd
import numpy as np
import os
import sys
from sklearn.metrics import mean_squared_error

# --- Common functions ---
# Function to calculate Root Mean Squared Error (used by both solutions and for final evaluation)
def calculate_rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))

# Ensure 'input' directory exists for data loading.
# This check is crucial for the script to run correctly in a new environment.
if not os.path.exists("./input"):
    print("Error: The './input' directory does not exist.")
    print("Please ensure 'train.csv' and 'test.csv' are placed inside a directory named 'input' relative to the script.")
    sys.exit(1) # Exit if data directory is missing


# --- Solution 1 Code Block (LightGBM) ---
print("--- Running Solution 1 (LightGBM) ---")

# Solution 1: LightGBM specific imports and install logic
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler # This import is in original but not used. Keeping it as is.
try:
    import lightgbm as lgb
except ImportError:
    print("LightGBM not found. Attempting to install...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "lightgbm"])
    import lightgbm as lgb
    print("LightGBM installed successfully.")


# Load data
train_df_s1 = pd.read_csv("./input/train.csv")
test_df_s1 = pd.read_csv("./input/test.csv")

# Feature Engineering
def feature_engineer_s1(df):
    df['rooms_per_household'] = df['total_rooms'] / df['households']
    df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
    df['population_per_household'] = df['population'] / df['households']
    return df

train_df_s1 = feature_engineer_s1(train_df_s1)
test_df_s1 = feature_engineer_s1(test_df_s1)

# Separate target variable
X_s1 = train_df_s1.drop("median_house_value", axis=1)
y_s1 = train_df_s1["median_house_value"]
X_test_s1 = test_df_s1.copy()

# K-Fold Cross Validation and LightGBM Model Training
kf = KFold(n_splits=5, shuffle=True, random_state=42)
oof_predictions_s1 = np.zeros(X_s1.shape[0])
test_predictions_s1 = np.zeros(X_test_s1.shape[0])
validation_scores_s1 = []

for fold, (train_index, val_index) in enumerate(kf.split(X_s1, y_s1)):
    print(f"LGBM Fold {fold+1}")
    X_train_s1, X_val_s1 = X_s1.iloc[train_index], X_s1.iloc[val_index]
    y_train_s1, y_val_s1 = y_s1.iloc[train_index], y_s1.iloc[val_index]

    lgb_params = {
        'objective': 'regression_l1', # MAE objective often robust to outliers
        'metric': 'rmse',
        'n_estimators': 1000,
        'learning_rate': 0.05,
        'feature_fraction': 0.8,
        'bagging_fraction': 0.8,
        'bagging_freq': 1,
        'lambda_l1': 0.1,
        'lambda_l2': 0.1,
        'num_leaves': 31,
        'verbose': -1, # Suppress verbose output
        'n_jobs': -1, # Use all available cores
        'seed': 42 + fold,
        'boosting_type': 'gbdt',
    }

    model_s1 = lgb.LGBMRegressor(**lgb_params)
    model_s1.fit(X_train_s1, y_train_s1,
              eval_set=[(X_val_s1, y_val_s1)],
              eval_metric='rmse',
              callbacks=[lgb.early_stopping(50, verbose=False)]) # Use callbacks for early stopping

    oof_predictions_s1[val_index] = model_s1.predict(X_val_s1)
    fold_test_preds_s1 = model_s1.predict(X_test_s1)
    test_predictions_s1 += fold_test_preds_s1 / kf.n_splits

    fold_rmse_s1 = calculate_rmse(y_val_s1, oof_predictions_s1[val_index])
    validation_scores_s1.append(fold_rmse_s1)
    print(f"LGBM Fold {fold+1} RMSE: {fold_rmse_s1}")

final_oof_rmse_s1 = calculate_rmse(y_s1, oof_predictions_s1)
print(f"LGBM Overall OOF RMSE: {final_oof_rmse_s1}")

# Create submission file for Solution 1 and rename as per ensemble plan
submission_df_s1 = pd.DataFrame({'median_house_value': test_predictions_s1})
submission_df_s1.to_csv("submission.csv", index=False) # Original file name
os.rename("submission.csv", "submission_lgbm.csv")
print("Solution 1 submission file created and renamed to submission_lgbm.csv")


# --- Solution 2 Code Block (RandomForest) ---
print("\n--- Running Solution 2 (RandomForest) ---")

# Solution 2: RandomForest specific imports and install logic
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer

# Function to install and import packages for Solution 2
def install_and_import_s2(package):
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
install_and_import_s2('pandas') # Already imported by common block, but good to keep as per original
install_and_import_s2('numpy')  # Already imported
install_and_import_s2('sklearn') # scikit-learn is imported as sklearn

# Define file paths (using hardcoded paths as per original)
train_file_s2 = "./input/train.csv"
test_file_s2 = "./input/test.csv"

# 1. Load Data
train_df_s2 = pd.read_csv(train_file_s2)
test_df_s2 = pd.read_csv(test_file_s2)

# Separate target variable
X_s2 = train_df_s2.drop("median_house_value", axis=1)
y_s2 = train_df_s2["median_house_value"]

# Combine train and test for consistent preprocessing
combined_df_s2 = pd.concat([X_s2, test_df_s2], ignore_index=True)

# 2. Preprocessing
# Impute missing values for 'total_bedrooms'
if 'total_bedrooms' in combined_df_s2.columns:
    imputer_s2 = SimpleImputer(strategy="median")
    combined_df_s2['total_bedrooms'] = imputer_s2.fit_transform(combined_df_s2[['total_bedrooms']])

# Feature Engineering (example features)
# Avoid division by zero by adding a small epsilon or handling NaNs after creation
combined_df_s2['households_safe'] = combined_df_s2['households'].replace(0, 1) # Replace 0 with 1 to avoid division by zero
combined_df_s2['total_rooms_safe'] = combined_df_s2['total_rooms'].replace(0, 1) # Replace 0 with 1 to avoid division by zero

combined_df_s2['rooms_per_household'] = combined_df_s2['total_rooms'] / combined_df_s2['households_safe']
combined_df_s2['bedrooms_per_room'] = combined_df_s2['total_bedrooms'] / combined_df_s2['total_rooms_safe']
combined_df_s2['population_per_household'] = combined_df_s2['population'] / combined_df_s2['households_safe']

# Drop the safe columns used for calculation
combined_df_s2 = combined_df_s2.drop(columns=['households_safe', 'total_rooms_safe'])

# After feature engineering, there might be NaNs or infs if original values were zero and replaced with NaN
# Replace inf/-inf with NaN and then impute
combined_df_s2.replace([np.inf, -np.inf], np.nan, inplace=True)
    
# Impute any new NaN values created by feature engineering or existing ones
imputer_all_cols_s2 = SimpleImputer(strategy="median")
    
# Fit and transform only columns that might have NaNs
for col in combined_df_s2.columns:
    if combined_df_s2[col].isnull().any():
        combined_df_s2[col] = imputer_all_cols_s2.fit_transform(combined_df_s2[[col]])


# Split back into processed train and test sets
X_processed_s2 = combined_df_s2.iloc[:len(X_s2)]
test_processed_s2 = combined_df_s2.iloc[len(X_s2):]

# 3. Model Training
# Split training data for validation
X_train_s2, X_val_s2, y_train_s2, y_val_s2 = train_test_split(X_processed_s2, y_s2, test_size=0.2, random_state=42)

# Initialize and train the model
model_s2 = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model_s2.fit(X_train_s2, y_train_s2)

# 4. Evaluation
y_pred_val_s2 = model_s2.predict(X_val_s2)
rmse_s2 = calculate_rmse(y_val_s2, y_pred_val_s2)

print(f"RandomForest Final Validation Performance: {rmse_s2}")

# 5. Prediction on test data
test_predictions_s2 = model_s2.predict(test_processed_s2)

# 6. Generate Submission File for Solution 2 and rename as per ensemble plan
submission_df_s2 = pd.DataFrame({'median_house_value': test_predictions_s2})
submission_df_s2.to_csv("submission.csv", index=False) # Original file name
os.rename("submission.csv", "submission_rf.csv")
print("Solution 2 submission file created and renamed to submission_rf.csv")


# --- Ensemble Script Block ---
print("\n--- Running Ensemble Script ---")

# Load submission files
try:
    lgbm_submission = pd.read_csv("submission_lgbm.csv")
    rf_submission = pd.read_csv("submission_rf.csv")
except FileNotFoundError as e:
    print(f"Error loading submission files for ensemble: {e}")
    sys.exit(1)

# Extract predictions
lgbm_preds = lgbm_submission['median_house_value']
rf_preds = rf_submission['median_house_value']

# Calculate ensemble predictions (simple average)
ensemble_predictions_test = (lgbm_preds + rf_preds) / 2

# Create final submission DataFrame
final_submission_df = pd.DataFrame({'median_house_value': ensemble_predictions_test})

# Save final ensemble submission
final_submission_df.to_csv("submission.csv", index=False)
print("Ensemble submission file 'submission.csv' created successfully.")

# Calculate and print final validation performance for the ensemble
# As per the instructions and constraints, we average the reported validation scores
# from the individual models to provide a final metric for the combined script.
ensemble_final_validation_score = (final_oof_rmse_s1 + rmse_s2) / 2
print(f"Final Validation Performance: {ensemble_final_validation_score}")

# Clean up intermediate submission files (optional, but good practice)
if os.path.exists("submission_lgbm.csv"):
    os.remove("submission_lgbm.csv")
if os.path.exists("submission_rf.csv"):
    os.remove("submission_rf.csv")
print("Intermediate submission files (submission_lgbm.csv, submission_rf.csv) removed.")
