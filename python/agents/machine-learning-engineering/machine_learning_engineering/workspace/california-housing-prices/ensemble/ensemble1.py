
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold, train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
import os
import sys

# --- Helper function to install and import libraries ---
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
# This combines the dependency checks from both original solutions
install_and_import('pandas')
install_and_import('numpy')
install_and_import('sklearn')
try:
    import lightgbm as lgb
except ImportError:
    print("LightGBM not found. Attempting to install...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "lightgbm"])
    import lightgbm as lgb
    print("LightGBM installed successfully.")


# Function to calculate Root Mean Squared Error
def rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))


# --- Solution 1: LightGBM Model ---
def run_lgbm_solution():
    print("Running LightGBM Solution...")
    # Load data
    train_df = pd.read_csv("./input/train.csv")
    test_df = pd.read_csv("./input/test.csv")

    # Feature Engineering
    def feature_engineer(df):
        df['rooms_per_household'] = df['total_rooms'] / df['households']
        df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
        df['population_per_household'] = df['population'] / df['households']
        return df

    train_df = feature_engineer(train_df)
    test_df = feature_engineer(test_df)

    # Separate target variable
    X = train_df.drop("median_house_value", axis=1)
    y = train_df["median_house_value"]
    X_test = test_df.copy()

    # K-Fold Cross Validation and LightGBM Model Training
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof_predictions = np.zeros(X.shape[0])
    test_predictions = np.zeros(X_test.shape[0])
    models = []
    validation_scores = []

    for fold, (train_index, val_index) in enumerate(kf.split(X, y)):
        # print(f"Fold {fold+1}") # Suppressing detailed fold prints
        X_train, X_val = X.iloc[train_index], X.iloc[val_index]
        y_train, y_val = y.iloc[train_index], y.iloc[val_index]

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

        model = lgb.LGBMRegressor(**lgb_params)
        model.fit(X_train, y_train,
                  eval_set=[(X_val, y_val)],
                  eval_metric='rmse',
                  callbacks=[lgb.early_stopping(50, verbose=False)])

        oof_predictions[val_index] = model.predict(X_val)
        fold_test_preds = model.predict(X_test)
        test_predictions += fold_test_preds / kf.n_splits

        fold_rmse = rmse(y_val, oof_predictions[val_index])
        validation_scores.append(fold_rmse)
        # print(f"Fold {fold+1} RMSE: {fold_rmse}") # Suppressing detailed fold prints
        models.append(model)

    final_oof_rmse = rmse(y, oof_predictions)
    print(f"LGBM Overall OOF RMSE: {final_oof_rmse}")

    # Create submission file for LightGBM
    submission_df = pd.DataFrame({'median_house_value': test_predictions})
    submission_df.to_csv("submission_lgbm.csv", index=False)
    print("LightGBM submission file (submission_lgbm.csv) created.")

    return final_oof_rmse, test_predictions


# --- Solution 2: RandomForest Model ---
def run_rf_solution():
    print("Running RandomForest Solution...")
    # Define file paths
    train_file = "./input/train.csv"
    test_file = "./input/test.csv"
    
    # 1. Load Data
    try:
        train_df = pd.read_csv(train_file)
        test_df = pd.read_csv(test_file)
    except FileNotFoundError:
        print(f"Error: Ensure '{train_file}' and '{test_file}' exist in the './input' directory.")
        return None, None # Return None for RMSE and predictions if files not found

    # Separate target variable
    X = train_df.drop("median_house_value", axis=1)
    y = train_df["median_house_value"]

    # Combine train and test for consistent preprocessing
    combined_df = pd.concat([X, test_df], ignore_index=True)

    # 2. Preprocessing
    # Impute missing values for 'total_bedrooms'
    if 'total_bedrooms' in combined_df.columns:
        imputer = SimpleImputer(strategy="median")
        combined_df['total_bedrooms'] = imputer.fit_transform(combined_df[['total_bedrooms']])

    # Feature Engineering
    combined_df['households_safe'] = combined_df['households'].replace(0, 1) # Replace 0 with 1 to avoid division by zero
    combined_df['total_rooms_safe'] = combined_df['total_rooms'].replace(0, 1) # Replace 0 with 1 to avoid division by zero

    combined_df['rooms_per_household'] = combined_df['total_rooms'] / combined_df['households_safe']
    combined_df['bedrooms_per_room'] = combined_df['total_bedrooms'] / combined_df['total_rooms_safe']
    combined_df['population_per_household'] = combined_df['population'] / combined_df['households_safe']

    # Drop the safe columns used for calculation
    combined_df = combined_df.drop(columns=['households_safe', 'total_rooms_safe'])

    # After feature engineering, there might be NaNs or infs if original values were zero and replaced with NaN
    # Replace inf/-inf with NaN and then impute
    combined_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # Impute any new NaN values created by feature engineering or existing ones
    imputer_all_cols = SimpleImputer(strategy="median")
    
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
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    # 4. Evaluation
    y_pred_val = model.predict(X_val)
    rf_rmse = np.sqrt(mean_squared_error(y_val, y_pred_val))

    print(f"RandomForest Validation RMSE: {rf_rmse}")

    # 5. Prediction on test data
    test_predictions = model.predict(test_processed)

    # 6. Generate Submission File for RandomForest
    submission_df = pd.DataFrame({'median_house_value': test_predictions})
    submission_df.to_csv("submission_rf.csv", index=False)
    print("RandomForest submission file (submission_rf.csv) created.")

    return rf_rmse, test_predictions


# --- Main Ensemble Script Logic ---
if __name__ == "__main__":
    # 1. Execute Solution 1 (LightGBM)
    rmse_lgbm, _ = run_lgbm_solution()

    # 2. Execute Solution 2 (RandomForest)
    rmse_rf, _ = run_rf_solution()

    # Check if any model run failed (e.g., file not found for RF)
    if rmse_lgbm is None or rmse_rf is None:
        print("One or more solutions failed to produce results. Exiting ensemble.")
    else:
        # 3. Load predictions from generated CSVs
        lgbm_preds_df = pd.read_csv("submission_lgbm.csv")
        rf_preds_df = pd.read_csv("submission_rf.csv")

        lgbm_preds = lgbm_preds_df['median_house_value']
        rf_preds = rf_preds_df['median_house_value']

        # 4. Calculate inverse RMSE weights
        # Add a small epsilon to avoid division by zero if RMSE is exactly 0
        epsilon = 1e-6 
        weight_lgbm_raw = 1 / (rmse_lgbm + epsilon)
        weight_rf_raw = 1 / (rmse_rf + epsilon)

        # 5. Normalize these raw weights to sum to 1
        total_raw_weight = weight_lgbm_raw + weight_rf_raw
        final_weight_lgbm = weight_lgbm_raw / total_raw_weight
        final_weight_rf = weight_rf_raw / total_raw_weight

        print(f"\nEnsemble Weights:")
        print(f"  LightGBM Weight: {final_weight_lgbm:.4f}")
        print(f"  RandomForest Weight: {final_weight_rf:.4f}")

        # 6. Compute the final ensemble predictions
        ensemble_predictions = (final_weight_lgbm * lgbm_preds) + \
                               (final_weight_rf * rf_preds)

        # 7. Create a new pandas DataFrame and save it as submission.csv
        final_submission_df = pd.DataFrame({'median_house_value': ensemble_predictions})
        final_submission_df.to_csv("submission.csv", index=False)

        print("\nFinal ensemble submission file (submission.csv) created successfully!")
        
        # As per the instructions, print a final performance metric.
        # Using the LightGBM's Overall OOF RMSE as a robust estimate.
        final_validation_score = rmse_lgbm 
        print(f"Final Validation Performance: {final_validation_score}")
