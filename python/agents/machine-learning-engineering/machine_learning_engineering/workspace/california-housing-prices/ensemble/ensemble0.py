
import pandas as pd
import numpy as np
import lightgbm as lgb
import xgboost as xgb
from sklearn.model_selection import KFold
from sklearn.metrics import mean_squared_error
from sklearn.linear_model import LinearRegression
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

# Load Data
train_df = pd.read_csv("./input/train.csv")
test_df = pd.read_csv("./input/test.csv")

# --- Harmonized Feature Engineering ---

# 1. Handle missing 'total_bedrooms' with median from training data
median_total_bedrooms_train = train_df['total_bedrooms'].median()
train_df['total_bedrooms'].fillna(median_total_bedrooms_train, inplace=True)
test_df['total_bedrooms'].fillna(median_total_bedrooms_train, inplace=True)

# 2. Engineered features from Solution 2
def create_additional_features(df):
    df['rooms_per_household'] = df['total_rooms'] / df['households'].replace(0, np.nan)
    df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms'].replace(0, np.nan)
    df['population_per_household'] = df['population'] / df['households'].replace(0, np.nan)
    return df

train_df = create_additional_features(train_df)
test_df = create_additional_features(test_df)

# Impute missing values for engineered features using medians from training data
engineered_features = ['rooms_per_household', 'bedrooms_per_room', 'population_per_household']
for col in engineered_features:
    median_val_for_col = train_df[col].median()
    train_df[col].fillna(median_val_for_col, inplace=True)
    test_df[col].fillna(median_val_for_col, inplace=True)

# 3. One-hot encode 'ocean_proximity' if it exists
# Combine train and test for consistent one-hot encoding, dropping the target column from train_df
combined_df = pd.concat([train_df.drop('median_house_value', axis=1), test_df], ignore_index=True)

has_ocean_proximity = False
if 'ocean_proximity' in combined_df.columns:
    print("One-hot encoding 'ocean_proximity'...")
    combined_df = pd.get_dummies(combined_df, columns=['ocean_proximity'], drop_first=False)
    has_ocean_proximity = True
else:
    print("'ocean_proximity' column not found in data, skipping one-hot encoding.")

# Separate back into processed train and test sets
train_df_processed = combined_df.iloc[:len(train_df)].copy()
test_df_processed = combined_df.iloc[len(train_df):].copy()

# Add target back to train_df_processed
train_df_processed['median_house_value'] = train_df['median_house_value']

# Define final features and target
TARGET_COLUMN = 'median_house_value'
# List all numerical features and the newly created one-hot encoded features
final_features = [
    'longitude', 'latitude', 'housing_median_age', 'total_rooms',
    'total_bedrooms', 'population', 'households', 'median_income',
    'rooms_per_household', 'bedrooms_per_room', 'population_per_household'
]

# Add one-hot encoded 'ocean_proximity' columns if they were created
if has_ocean_proximity:
    for col in train_df_processed.columns:
        if 'ocean_proximity_' in col:
            final_features.append(col)

# Ensure all final_features exist in the processed dataframes and remove target if it's accidentally in
final_features = [f for f in final_features if f in train_df_processed.columns and f != TARGET_COLUMN]

X_full_train = train_df_processed[final_features]
y_full_train = train_df_processed[TARGET_COLUMN]
X_test_submission = test_df_processed[final_features]

# --- Cross-Validation for Base Models and OOF Predictions ---

N_SPLITS = 5 # K-Fold Cross-Validation splits

kf = KFold(n_splits=N_SPLITS, shuffle=True, random_state=42)

# Initialize arrays to store Out-Of-Fold (OOF) predictions for meta-model training
oof_preds_lgbm = np.zeros(len(X_full_train))
oof_preds_xgb = np.zeros(len(X_full_train))
oof_preds_cat = np.zeros(len(X_full_train))

# Initialize arrays to store test predictions from each fold, to be averaged later
test_preds_lgbm_folds = np.zeros((N_SPLITS, len(X_test_submission)))
test_preds_xgb_folds = np.zeros((N_SPLITS, len(X_test_submission)))
test_preds_cat_folds = np.zeros((N_SPLITS, len(X_test_submission)))

print("Starting K-Fold Cross-Validation...")
for fold, (train_idx, val_idx) in enumerate(kf.split(X_full_train, y_full_train)):
    print(f"--- Fold {fold+1}/{N_SPLITS} ---")

    X_train_fold, X_val_fold = X_full_train.iloc[train_idx], X_full_train.iloc[val_idx]
    y_train_fold, y_val_fold = y_full_train.iloc[train_idx], y_full_train.iloc[val_idx]

    # LightGBM Model
    lgbm_model = lgb.LGBMRegressor(
        objective='regression', metric='rmse', n_estimators=100, learning_rate=0.1, random_state=42, n_jobs=-1
    )
    lgbm_model.fit(X_train_fold, y_train_fold)
    oof_preds_lgbm[val_idx] = lgbm_model.predict(X_val_fold)
    test_preds_lgbm_folds[fold, :] = lgbm_model.predict(X_test_submission)

    # XGBoost Model
    xgb_model = xgb.XGBRegressor(
        objective='reg:squarederror', eval_metric='rmse', n_estimators=100, learning_rate=0.1, random_state=42, n_jobs=-1
    )
    xgb_model.fit(X_train_fold, y_train_fold)
    oof_preds_xgb[val_idx] = xgb_model.predict(X_val_fold)
    test_preds_xgb_folds[fold, :] = xgb_model.predict(X_test_submission)

    # CatBoost Model
    cat_model = CatBoostRegressor(loss_function='RMSE', random_seed=42, verbose=0, n_estimators=100)
    cat_model.fit(X_train_fold, y_train_fold)
    oof_preds_cat[val_idx] = cat_model.predict(X_val_fold)
    test_preds_cat_folds[fold, :] = cat_model.predict(X_test_submission)

print("K-Fold Cross-Validation complete.")

# Average test predictions across all folds for each base model
test_pred_lgbm_avg = np.mean(test_preds_lgbm_folds, axis=0)
test_pred_xgb_avg = np.mean(test_preds_xgb_folds, axis=0)
test_pred_cat_avg = np.mean(test_preds_cat_folds, axis=0)

# --- Meta-Model Training ---

# Create a new dataset for the meta-model using OOF predictions as features
X_meta = pd.DataFrame({
    'lgbm_oof': oof_preds_lgbm,
    'xgb_oof': oof_preds_xgb,
    'cat_oof': oof_preds_cat
})
y_meta = y_full_train

# Train a simple Linear Regression meta-model
meta_model = LinearRegression()
print("Training meta-model...")
meta_model.fit(X_meta, y_meta)
print("Meta-model training complete.")

# --- Final Validation Performance ---
# Evaluate the meta-model's performance on its training data (OOF predictions)
y_pred_meta_oof = meta_model.predict(X_meta)
rmse_meta_oof = np.sqrt(mean_squared_error(y_meta, y_pred_meta_oof))
print(f"Final Validation Performance: {rmse_meta_oof}")

# --- Final Test Predictions ---

# Create meta-test features using the averaged test predictions from base models
X_meta_test = pd.DataFrame({
    'lgbm_oof': test_pred_lgbm_avg,
    'xgb_oof': test_pred_xgb_avg,
    'cat_oof': test_pred_cat_avg
})

# Generate final ensembled predictions for the test set
final_test_predictions = meta_model.predict(X_meta_test)

# Ensure predictions are non-negative
final_test_predictions[final_test_predictions < 0] = 0

# --- Submission Output ---
# Print the header as required by the submission format
print("median_house_value")
# Print each prediction on a new line
for val in final_test_predictions:
    print(f"{val}")
