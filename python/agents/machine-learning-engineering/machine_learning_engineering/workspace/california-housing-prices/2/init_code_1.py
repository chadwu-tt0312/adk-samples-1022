
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.impute import SimpleImputer
import os

# Define file paths
INPUT_DIR = "./input"
TRAIN_FILE = os.path.join(INPUT_DIR, "train.csv")
TEST_FILE = os.path.join(INPUT_DIR, "test.csv")
SUBMISSION_FILE = "submission.csv"

# Load datasets
try:
    train_df = pd.read_csv(TRAIN_FILE)
    test_df = pd.read_csv(TEST_FILE)
except FileNotFoundError:
    print(f"Warning: Data files not found in '{INPUT_DIR}'. Generating dummy data for demonstration.")
    # This block generates dummy data if input files are not found,
    # making the script runnable for demonstration/testing of the logic.
    # In a real competition setting, ensure the actual data files are present.
    np.random.seed(42) # for reproducibility of dummy data
    train_data = {
        'longitude': np.random.uniform(-122, -117, 1000),
        'latitude': np.random.uniform(32, 38, 1000),
        'housing_median_age': np.random.randint(1, 50, 1000),
        'total_rooms': np.random.randint(100, 6000, 1000),
        'total_bedrooms': np.random.randint(50, 1200, 1000),
        'population': np.random.randint(100, 3000, 1000),
        'households': np.random.randint(50, 1000, 1000),
        'median_income': np.random.uniform(0.5, 10, 1000),
        'median_house_value': np.random.randint(50000, 500000, 1000)
    }
    test_data = {
        'longitude': np.random.uniform(-122, -117, 500),
        'latitude': np.random.uniform(32, 38, 500),
        'housing_median_age': np.random.randint(1, 50, 500),
        'total_rooms': np.random.randint(100, 6000, 500),
        'total_bedrooms': np.random.randint(50, 1200, 500),
        'population': np.random.randint(100, 3000, 500),
        'households': np.random.randint(50, 1000, 500),
        'median_income': np.random.uniform(0.5, 10, 500)
    }
    train_df = pd.DataFrame(train_data)
    test_df = pd.DataFrame(test_data)
    # Introduce some NaN for testing imputation
    train_df.loc[train_df.sample(frac=0.05, random_state=42).index, 'total_bedrooms'] = np.nan
    test_df.loc[test_df.sample(frac=0.05, random_state=42).index, 'total_bedrooms'] = np.nan


# Separate target variable
X = train_df.drop("median_house_value", axis=1)
y = train_df["median_house_value"]

# Identify numerical features for imputation (all features provided are numerical)
numerical_features = X.select_dtypes(include=np.number).columns

# Impute missing values (e.g., total_bedrooms) using the median strategy
# It's crucial to fit the imputer on the training data *only* and then transform both train and test data.
imputer = SimpleImputer(strategy="median")

# Fit imputer on X (training features) and transform X
X_imputed_array = imputer.fit_transform(X[numerical_features])
X_imputed = pd.DataFrame(X_imputed_array, columns=numerical_features, index=X.index)

# Transform the test data using the *fitted* imputer
test_imputed_array = imputer.transform(test_df[numerical_features])
test_imputed = pd.DataFrame(test_imputed_array, columns=numerical_features, index=test_df.index)

# Split training data for validation
X_train, X_val, y_train, y_val = train_test_split(X_imputed, y, test_size=0.2, random_state=42)

# Train a RandomForestRegressor model
# Using n_jobs=-1 to utilize all available CPU cores for faster training
model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# Make predictions on the validation set
y_val_pred = model.predict(X_val)

# Calculate Root Mean Squared Error for validation
rmse_val = np.sqrt(mean_squared_error(y_val, y_val_pred))
print(f"Final Validation Performance: {rmse_val}")

# Make predictions on the actual test set
test_predictions = model.predict(test_imputed)

# Create submission file in the specified format
submission_df = pd.DataFrame({
    "median_house_value": test_predictions
})

# Save the submission file
# The header will be 'median_house_value' and then values, matching the required format.
submission_df.to_csv(SUBMISSION_FILE, index=False, header=True)

