
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.impute import SimpleImputer
import os

# Define file paths
train_file = "./input/train.csv"
test_file = "./input/test.csv"

# Load the datasets
try:
    train_df = pd.read_csv(train_file)
    test_df = pd.read_csv(test_file)
except FileNotFoundError:
    raise FileNotFoundError(f"Ensure '{train_file}' and '{test_file}' exist in the './input' directory.")

# Separate target variable from features in training data
X = train_df.drop("median_house_value", axis=1)
y = train_df["median_house_value"]

# Identify numerical features for imputation
numerical_cols = X.select_dtypes(include=np.number).columns

# Impute missing values (e.g., for 'total_bedrooms')
# Use median strategy for numerical features, which is robust to outliers.
imputer = SimpleImputer(strategy='median')

# Fit imputer on training data and transform both training and test data.
# Reconstruct DataFrames to maintain column names and indices.
X_imputed = pd.DataFrame(imputer.fit_transform(X[numerical_cols]), columns=numerical_cols, index=X.index)
test_imputed = pd.DataFrame(imputer.transform(test_df[numerical_cols]), columns=numerical_cols, index=test_df.index)

# Split the training data into training and validation sets for local performance evaluation.
# 20% of the data is used for validation.
X_train, X_val, y_train, y_val = train_test_split(X_imputed, y, test_size=0.2, random_state=42)

# Initialize and train the RandomForestRegressor model.
# RandomForests are an ensemble learning method suitable for regression tasks.
# n_estimators=100 (number of trees in the forest) is a common starting point.
# random_state ensures reproducibility. n_jobs=-1 uses all available processor cores.
model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# Make predictions on the validation set to evaluate the model's performance.
val_predictions = model.predict(X_val)

# Calculate Root Mean Squared Error (RMSE) on the validation set.
# RMSE is a standard metric for regression tasks, penalizing larger errors more.
rmse = np.sqrt(mean_squared_error(y_val, val_predictions))

# Print the final validation performance as required by the task.
print(f"Final Validation Performance: {rmse}")

# Make predictions on the unseen test set.
test_predictions = model.predict(test_imputed)

# Print the submission output directly to stdout in the specified format.
# The format requires a header "median_house_value" followed by each prediction on a new line.
print("median_house_value")
for pred in test_predictions:
    print(pred)
