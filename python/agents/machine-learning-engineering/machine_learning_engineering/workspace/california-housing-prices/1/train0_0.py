
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Load the training dataset
train_df = pd.read_csv('./input/train.csv')

# --- Feature Engineering and Preprocessing ---

# Identify target and features
TARGET_COLUMN = 'median_house_value'
FEATURES = [col for col in train_df.columns if col != TARGET_COLUMN]

# Handle missing values in 'total_bedrooms'
# Calculate median from the training data to avoid data leakage
# This is a common practice for numerical features with missing values
train_bedrooms_median = train_df['total_bedrooms'].median()

# Impute missing values in the training data
train_df['total_bedrooms'].fillna(train_bedrooms_median, inplace=True)

# Separate features (X) and target (y)
X = train_df[FEATURES]
y = train_df[TARGET_COLUMN]

# Split the training data into training and validation sets
# Using a fixed random_state for reproducibility as requested for simple solutions
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# --- LightGBM Model Training ---

# Initialize the LightGBM Regressor model
# objective='regression' (or 'regression_l1' for MAE) for standard regression
# metric='rmse' specifies Root Mean Squared Error as the evaluation metric,
# which directly aligns with the competition metric.
# n_estimators: Number of boosting rounds. Default is often 100.
# learning_rate: Step size shrinkage to prevent overfitting. Default is often 0.1.
# random_state: For reproducibility.
model = lgb.LGBMRegressor(
    objective='regression',
    metric='rmse',
    n_estimators=100,
    learning_rate=0.1,
    random_state=42,
    n_jobs=-1 # Use all available CPU cores
)

# Train the model
model.fit(X_train, y_train)

# --- Model Evaluation on Validation Set ---

# Make predictions on the validation set
y_pred_val = model.predict(X_val)

# Evaluate the model using Root Mean Squared Error (RMSE)
rmse = np.sqrt(mean_squared_error(y_val, y_pred_val))

# Print the validation performance in the specified format
print(f"Final Validation Performance: {rmse}")
