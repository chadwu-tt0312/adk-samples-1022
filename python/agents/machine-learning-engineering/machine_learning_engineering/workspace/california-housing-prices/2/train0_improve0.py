
import os
import sys

# Function to install a package if not found and then import it implicitly
def install_and_import(package_name, import_name=None):
    """
    Installs a package if not found and then imports it.
    Args:
        package_name (str): The name of the package to install via pip (e.g., 'scikit-learn').
        import_name (str, optional): The name to use for importing the package (e.g., 'sklearn').
                                     If None, package_name is used for import.
    """
    if import_name is None:
        import_name = package_name

    try:
        # Try to import first to check if it's already available
        __import__(import_name)
    except ImportError:
        print(f"Installing {package_name}...")
        try:
            # Use sys.executable to ensure pip corresponds to the current Python environment
            os.system(f"{sys.executable} -m pip install {package_name}")
            __import__(import_name) # Import after installation
            print(f"{package_name} installed successfully.")
        except Exception as e:
            print(f"Failed to install {package_name}: {e}")
            raise

# Ensure necessary libraries are installed before importing them
install_and_import('pandas')
install_and_import('numpy')
install_and_import('scikit-learn', 'sklearn') # scikit-learn is the package name, sklearn is the import name

# Now, import the libraries and modules explicitly at the top level
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import PolynomialFeatures

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
        # .fit_transform expects a 2D array, hence combined_df[['total_bedrooms']]
        combined_df['total_bedrooms'] = imputer.fit_transform(combined_df[['total_bedrooms']])

    # Feature Engineering (example features)
    # Avoid division by zero by adding a small epsilon or handling NaNs after creation
    combined_df['households_safe'] = combined_df['households'].replace(0, 1) # Replace 0 with 1 to avoid division by zero
    combined_df['total_rooms_safe'] = combined_df['total_rooms'].replace(0, 1) # Replace 0 with 1 to avoid division by zero

    combined_df['rooms_per_household'] = combined_df['total_rooms'] / combined_df['households_safe']
    combined_df['bedrooms_per_room'] = combined_df['total_bedrooms'] / combined_df['total_rooms_safe']
    combined_df['population_per_household'] = combined_df['population'] / combined_df['households_safe']

    # Drop the safe columns used for calculation
    combined_df = combined_df.drop(columns=['households_safe', 'total_rooms_safe'])

    # --- Introduce Polynomial and Interaction Features ---
    # Identify key numerical features for polynomial transformation and interaction terms.
    # Selecting original numerical features and the newly created ratio features.
    numerical_features_for_poly = [
        'housing_median_age', 'total_rooms', 'total_bedrooms', 'population', 'households', 'median_income',
        'rooms_per_household', 'bedrooms_per_room', 'population_per_household',
        'longitude', 'latitude'
    ]

    # Filter to ensure only existing columns are selected from the combined_df
    existing_numerical_features_for_poly = [
        col for col in numerical_features_for_poly if col in combined_df.columns
    ]

    if existing_numerical_features_for_poly:
        # Initialize PolynomialFeatures to generate polynomial terms up to degree 2 and all pairwise interaction terms.
        # include_bias=False prevents adding a column of all ones, which is usually not desired for feature sets.
        poly = PolynomialFeatures(degree=2, include_bias=False)
        
        # Apply polynomial transformations to the selected numerical columns
        poly_features_array = poly.fit_transform(combined_df[existing_numerical_features_for_poly])
        
        # Get the names for the newly created polynomial features
        # For sklearn versions < 1.0, use poly.get_feature_names(existing_numerical_features_for_poly)
        # For sklearn versions >= 1.0, use poly.get_feature_names_out(existing_numerical_features_for_poly)
        # Using get_feature_names_out for broader compatibility with modern sklearn
        poly_feature_names = poly.get_feature_names_out(existing_numerical_features_for_poly)
        
        # Convert the array of new features into a DataFrame, preserving the original index
        poly_df = pd.DataFrame(poly_features_array, columns=poly_feature_names, index=combined_df.index)
        
        # Add a prefix to new columns to distinguish them from original features and avoid name clashes
        poly_df.columns = ['poly_' + col for col in poly_df.columns]
        
        # Concatenate the new polynomial features DataFrame with the existing combined_df
        combined_df = pd.concat([combined_df, poly_df], axis=1)

    # After feature engineering, there might be NaNs or infs if original values were zero or new features
    # resulted in undefined values (e.g., division by zero leading to inf before imputation).
    # Replace infinite values with NaN for proper imputation.
    combined_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # Impute any NaN values that might exist or were created during feature engineering.
    # Re-initialize imputer to ensure it fits on the current state of combined_df, especially for new features.
    imputer_all_cols = SimpleImputer(strategy="median")
    
    # Identify all columns that currently contain NaN values
    cols_with_nan = combined_df.columns[combined_df.isnull().any()].tolist()

    # Apply imputation only to the identified columns with NaNs
    if cols_with_nan:
        # When fitting and transforming, ensure only numerical columns are passed
        # and that the output replaces the correct columns.
        combined_df[cols_with_nan] = imputer_all_cols.fit_transform(combined_df[cols_with_nan])


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
