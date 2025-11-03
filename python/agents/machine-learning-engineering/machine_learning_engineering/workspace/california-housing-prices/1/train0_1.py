
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor

try:
    import lightgbm as lgb
except ImportError:
    print("LightGBM not found. Attempting to install...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "lightgbm"])
    import lightgbm as lgb
    print("LightGBM installed successfully.")


# Function to calculate Root Mean Squared Error
def rmse(y_true, y_pred):
    return np.sqrt(mean_squared_error(y_true, y_pred))

# Load data
# Ensure 'train.csv' and 'test.csv' are in a directory named 'input' relative to the script.
train_df = pd.read_csv("./input/train.csv")
test_df = pd.read_csv("./input/test.csv")

# --- Preprocessing ---

# 1. Impute missing values (from reference solution, applied before feature engineering)
# Only 'total_bedrooms' column has missing values in this dataset.
imputer = SimpleImputer(strategy='median')
train_df['total_bedrooms'] = imputer.fit_transform(train_df[['total_bedrooms']])
test_df['total_bedrooms'] = imputer.transform(test_df[['total_bedrooms']])

# 2. Feature Engineering (from base solution)
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

# 3. Scaling numerical features (from base solution)
# Identify numerical features for scaling. All columns are numerical after FE and imputation.
numerical_features = X.columns

scaler = StandardScaler()
X[numerical_features] = scaler.fit_transform(X[numerical_features])
X_test[numerical_features] = scaler.transform(X_test[numerical_features])

# --- Model Training and Ensembling ---

# K-Fold Cross Validation setup
kf = KFold(n_splits=5, shuffle=True, random_state=42)

# OOF and test predictions for LightGBM
oof_predictions_lgbm = np.zeros(X.shape[0])
test_predictions_lgbm = np.zeros(X_test.shape[0])
models_lgbm = []
validation_scores_lgbm = []

# OOF and test predictions for RandomForest
oof_predictions_rf = np.zeros(X.shape[0])
test_predictions_rf = np.zeros(X_test.shape[0])
models_rf = []
validation_scores_rf = []


for fold, (train_index, val_index) in enumerate(kf.split(X, y)):
    print(f"Fold {fold+1}")
    X_train, X_val = X.iloc[train_index], X.iloc[val_index]
    y_train, y_val = y.iloc[train_index], y.iloc[val_index]

    # --- LightGBM Model Training (from base solution) ---
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
        'seed': 42 + fold, # Vary seed per fold for diversity
        'boosting_type': 'gbdt',
    }

    lgbm_model = lgb.LGBMRegressor(**lgb_params)
    lgbm_model.fit(X_train, y_train,
                   eval_set=[(X_val, y_val)],
                   eval_metric='rmse',
                   callbacks=[lgb.early_stopping(50, verbose=False)])

    oof_predictions_lgbm[val_index] = lgbm_model.predict(X_val)
    fold_test_preds_lgbm = lgbm_model.predict(X_test)
    test_predictions_lgbm += fold_test_preds_lgbm / kf.n_splits

    fold_rmse_lgbm = rmse(y_val, oof_predictions_lgbm[val_index])
    validation_scores_lgbm.append(fold_rmse_lgbm)
    print(f"Fold {fold+1} LightGBM RMSE: {fold_rmse_lgbm}")
    models_lgbm.append(lgbm_model)


    # --- RandomForestRegressor Model Training (from reference solution) ---
    # Use different random_state for RandomForest to encourage diversity in ensemble
    rf_model = RandomForestRegressor(n_estimators=100, random_state=100 + fold, n_jobs=-1)
    rf_model.fit(X_train, y_train)

    oof_predictions_rf[val_index] = rf_model.predict(X_val)
    fold_test_preds_rf = rf_model.predict(X_test)
    test_predictions_rf += fold_test_preds_rf / kf.n_splits

    fold_rmse_rf = rmse(y_val, oof_predictions_rf[val_index])
    validation_scores_rf.append(fold_rmse_rf)
    print(f"Fold {fold+1} RandomForest RMSE: {fold_rmse_rf}")
    models_rf.append(rf_model)

# --- Ensembling Predictions ---
# Simple average ensembling for OOF predictions
oof_ensemble_predictions = (oof_predictions_lgbm + oof_predictions_rf) / 2
final_oof_rmse = rmse(y, oof_ensemble_predictions)

# Simple average ensembling for test predictions
final_test_predictions = (test_predictions_lgbm + test_predictions_rf) / 2

print(f"\nOverall OOF LightGBM RMSE: {rmse(y, oof_predictions_lgbm)}")
print(f"Overall OOF RandomForest RMSE: {rmse(y, oof_predictions_rf)}")
print(f"Overall OOF Ensemble RMSE: {final_oof_rmse}")

# Output the final validation performance
print(f"Final Validation Performance: {final_oof_rmse}")

# Create submission file
submission_df = pd.DataFrame({'median_house_value': final_test_predictions})
submission_df.to_csv("submission.csv", index=False)

print("Submission file created successfully!")

