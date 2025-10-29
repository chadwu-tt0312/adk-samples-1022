
import pandas as pd
import numpy as np
import lightgbm as lgb
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression # For optimal weight determination
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
train_df = pd.read_csv("./input/train.csv")
test_df = pd.read_csv("./input/test.csv")

# --- Harmonized Feature Engineering (Step 1) ---
def create_features(df):
    # Avoid division by zero by replacing 0 with NaN for safety
    df['rooms_per_household'] = df['total_rooms'] / df['households'].replace(0, np.nan)
    df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms'].replace(0, np.nan)
    df['population_per_household'] = df['population'] / df['households'].replace(0, np.nan)
    return df

train_df = create_features(train_df)
test_df = create_features(test_df)

# Handle missing values: Impute 'total_bedrooms' and engineered features
# Calculate medians ONLY from the training data to prevent data leakage
median_total_bedrooms_train = train_df['total_bedrooms'].median()
train_df['total_bedrooms'].fillna(median_total_bedrooms_train, inplace=True)
test_df['total_bedrooms'].fillna(median_total_bedrooms_train, inplace=True)

engineered_features = ['rooms_per_household', 'bedrooms_per_room', 'population_per_household']
for col in engineered_features:
    median_val_for_col = train_df[col].median()
    train_df[col].fillna(median_val_for_col, inplace=True)
    test_df[col].fillna(median_val_for_col, inplace=True)

# Define features and target based on Solution 2 and engineered features
TARGET_COLUMN = 'median_house_value'
features = [
    'longitude', 'latitude', 'housing_median_age', 'total_rooms',
    'total_bedrooms', 'population', 'households', 'median_income',
    'rooms_per_household', 'bedrooms_per_room', 'population_per_household'
]

X_full_train = train_df[features]
y_full_train = train_df[TARGET_COLUMN]
X_test_submission = test_df[features]

# --- Single Train/Validation Split (Step 2) ---
X_train, X_val, y_train, y_val = train_test_split(X_full_train, y_full_train, test_size=0.2, random_state=42)

# --- Base Model Training and Prediction (Step 3) ---

# 1. LightGBM Model
lgbm_model = lgb.LGBMRegressor(
    objective='regression',
    metric='rmse',
    n_estimators=100,
    learning_rate=0.1,
    random_state=42,
    n_jobs=-1
)
print("Training LightGBM model...")
lgbm_model.fit(X_train, y_train)
print("LightGBM model training complete.")

# Predictions for LightGBM
y_val_lgbm_pred = lgbm_model.predict(X_val)
y_test_lgbm_pred = lgbm_model.predict(X_test_submission)

# 2. XGBoost Model
xgb_model = xgb.XGBRegressor(
    objective='reg:squarederror',
    eval_metric='rmse',
    n_estimators=100,
    learning_rate=0.1,
    random_state=42,
    n_jobs=-1
)
print("Training XGBoost model...")
xgb_model.fit(X_train, y_train)
print("XGBoost model training complete.")

# Predictions for XGBoost
y_val_xgb_pred = xgb_model.predict(X_val)
y_test_xgb_pred = xgb_model.predict(X_test_submission)

# 3. CatBoost Model
cat_model = CatBoostRegressor(loss_function='RMSE', random_seed=42, verbose=0)
print("Training CatBoost model...")
cat_model.fit(X_train, y_train)
print("CatBoost model training complete.")

# Predictions for CatBoost
y_val_cat_pred = cat_model.predict(X_val)
y_test_cat_pred = cat_model.predict(X_test_submission)


# --- Optimal Weight Determination (Step 4) ---
# Stack validation predictions to form the input for LinearRegression
X_val_preds = np.column_stack([y_val_lgbm_pred, y_val_xgb_pred, y_val_cat_pred])

# Train a LinearRegression model to find optimal weights
blender_model = LinearRegression(fit_intercept=True, positive=False) # positive=False if weights can be negative
blender_model.fit(X_val_preds, y_val)

# The coefficients are the learned weights
# print("Learned blending weights:", blender_model.coef_)
# print("Learned blending intercept:", blender_model.intercept_)

# --- Final Test Prediction (Step 5) ---
# Stack test predictions
X_test_preds = np.column_stack([y_test_lgbm_pred, y_test_xgb_pred, y_test_cat_pred])

# Apply the learned weights to the test predictions
final_test_predictions = blender_model.predict(X_test_preds)

# Ensure predictions are non-negative, as median house values cannot be negative
final_test_predictions[final_test_predictions < 0] = 0

# --- Evaluate Ensembled Model on Validation Set (for printing performance) ---
y_val_ensemble_pred = blender_model.predict(X_val_preds)
rmse_ensemble_val = np.sqrt(mean_squared_error(y_val, y_val_ensemble_pred))
print(f"Final Validation Performance: {rmse_ensemble_val}")

# --- Submission Output (Step 6) ---
print("median_house_value")
for val in final_test_predictions:
    print(f"{val}")

