
import pandas as pd
import numpy as np
import lightgbm as lgb
import xgboost as xgb # Import for the reference solution model
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Load the training dataset
train_df = pd.read_csv('./input/train.csv')

# --- Feature Engineering and Preprocessing ---

# Identify target and features
TARGET_COLUMN = 'median_house_value'
# Drop the target column from features
FEATURES = [col for col in train_df.columns if col != TARGET_COLUMN]

# Handle missing values in 'total_bedrooms'
# Calculate median from the training data to avoid data leakage
train_bedrooms_median = train_df['total_bedrooms'].median()

# Impute missing values in the training data
train_df['total_bedrooms'].fillna(train_bedrooms_median, inplace=True)

# Separate features (X) and target (y)
X = train_df[FEATURES]
y = train_df[TARGET_COLUMN]

# Split the training data into training and validation sets
# Using a fixed random_state for reproducibility
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# --- Model Training ---

# 1. LightGBM Model (from Base Solution)
lgbm_model = lgb.LGBMRegressor(
    objective='regression',
    metric='rmse',
    n_estimators=100,
    learning_rate=0.1,
    random_state=42,
    n_jobs=-1 # Use all available CPU cores
)
print("Training LightGBM model...")
lgbm_model.fit(X_train, y_train)
print("LightGBM model training complete.")

# 2. XGBoost Model (from Reference Solution)
xgb_model = xgb.XGBRegressor(
    objective='reg:squarederror', # Recommended objective for regression tasks
    eval_metric='rmse',          # Evaluation metric
    n_estimators=100,            # Number of boosting rounds
    learning_rate=0.1,           # Step size shrinkage
    random_state=42,             # For reproducibility
    n_jobs=-1                    # Use all available CPU cores
)
print("Training XGBoost model...")
xgb_model.fit(X_train, y_train)
print("XGBoost model training complete.")

# --- Model Prediction ---

# Make predictions on the validation set using LightGBM
y_pred_lgbm = lgbm_model.predict(X_val)

# Make predictions on the validation set using XGBoost
y_pred_xgb = xgb_model.predict(X_val)


# --- Ensembling ---
# Weighted average of predictions from both models, giving more weight to LightGBM
y_pred_ensemble = (0.6 * y_pred_lgbm + 0.4 * y_pred_xgb)


# --- Model Evaluation on Validation Set ---

# Evaluate the ensembled model using Root Mean Squared Error (RMSE)
rmse = np.sqrt(mean_squared_error(y_val, y_pred_ensemble))

# Print the validation performance in the specified format
print(f"Final Validation Performance: {rmse}")

