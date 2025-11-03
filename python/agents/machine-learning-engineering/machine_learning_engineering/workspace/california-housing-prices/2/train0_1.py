
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
        # Use sys.executable to ensure pip corresponds to the current Python environment
        os.system(f"{sys.executable} -m pip install {package}")
        __import__(package)
        print(f"{package} installed successfully.")

# Ensure necessary libraries are installed
install_and_import('pandas')
install_and_import('numpy')
install_and_import('sklearn') # scikit-learn is imported as sklearn

def apply_feature_engineering(df):
    """
    Applies feature engineering steps to the DataFrame.
    """
    df_copy = df.copy()

    # Avoid division by zero by replacing 0 with 1 for 'households' and 'total_rooms'
    # These 'safe' columns are temporary and dropped later.
    df_copy['households_safe'] = df_copy['households'].replace(0, 1)
    df_copy['total_rooms_safe'] = df_copy['total_rooms'].replace(0, 1)

    df_copy['rooms_per_household'] = df_copy['total_rooms'] / df_copy['households_safe']
    df_copy['bedrooms_per_room'] = df_copy['total_bedrooms'] / df_copy['total_rooms_safe']
    df_copy['population_per_household'] = df_copy['population'] / df_copy['households_safe']

    # Drop the temporary safe columns
    df_copy = df_copy.drop(columns=['households_safe', 'total_rooms_safe'])

    # Replace any infinite values (which might result from division) with NaN
    df_copy.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    return df_copy

def main():
    # Define file paths
    train_file = "./input/train.csv"
    test_file = "./input/test.csv"
    submission_file = "submission.csv"

    # 1. Load Data
    # Assuming files exist in the specified path as per competition setup
    train_df = pd.read_csv(train_file)
    test_df = pd.read_csv(test_file)

    # Separate target variable
    X = train_df.drop("median_house_value", axis=1)
    y = train_df["median_house_value"]

    # Identify numerical features (all features in this dataset are numerical)
    numerical_features = X.select_dtypes(include=np.number).columns.tolist()

    # 2. Preprocessing
    # Initial Imputation for existing missing values (e.g., total_bedrooms)
    # Fit imputer on training data (X) and transform both X and test_df
    imputer_initial = SimpleImputer(strategy="median")

    X_imputed = pd.DataFrame(imputer_initial.fit_transform(X[numerical_features]),
                             columns=numerical_features, index=X.index)
    test_imputed = pd.DataFrame(imputer_initial.transform(test_df[numerical_features]),
                                columns=numerical_features, index=test_df.index)

    # Apply Feature Engineering
    X_fe = apply_feature_engineering(X_imputed)
    test_fe = apply_feature_engineering(test_imputed)

    # Post-Feature Engineering Imputation for any NaNs introduced by FE
    # Fit imputer on engineered training data (X_fe) and transform both X_fe and test_fe
    imputer_post_fe = SimpleImputer(strategy="median")

    X_processed = pd.DataFrame(imputer_post_fe.fit_transform(X_fe),
                               columns=X_fe.columns, index=X_fe.index)
    test_processed = pd.DataFrame(imputer_post_fe.transform(test_fe),
                                  columns=test_fe.columns, index=test_fe.index)

    # 3. Model Training
    # Split training data for validation
    X_train, X_val, y_train, y_val = train_test_split(X_processed, y, test_size=0.2, random_state=42)

    # Initialize and train Model 1 (RandomForestRegressor from base solution)
    model_1 = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model_1.fit(X_train, y_train)
    val_preds_1 = model_1.predict(X_val)
    test_preds_1 = model_1.predict(test_processed)

    # Initialize and train Model 2 (Additional RandomForestRegressor, following reference solution type)
    # Using slightly different parameters for diversity in ensembling
    model_2 = RandomForestRegressor(n_estimators=150, random_state=43, n_jobs=-1, max_depth=10)
    model_2.fit(X_train, y_train)
    val_preds_2 = model_2.predict(X_val)
    test_preds_2 = model_2.predict(test_processed)

    # 4. Ensembling and Evaluation
    # Simple averaging ensemble
    y_pred_val_ensemble = (val_preds_1 + val_preds_2) / 2
    
    rmse = np.sqrt(mean_squared_error(y_val, y_pred_val_ensemble))
    print(f"Final Validation Performance: {rmse}")

    # 5. Prediction on test data using the ensemble
    test_predictions_ensemble = (test_preds_1 + test_preds_2) / 2

    # 6. Generate Submission File
    submission_df = pd.DataFrame({'median_house_value': test_predictions_ensemble})
    submission_df.to_csv(submission_file, index=False)

    print(f"Submission file '{submission_file}' created successfully.")

if __name__ == "__main__":
    main()
