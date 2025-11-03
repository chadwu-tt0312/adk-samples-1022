
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error

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

# Feature Engineering function
def feature_engineer(df):
    df['rooms_per_household'] = df['total_rooms'] / df['households']
    df['bedrooms_per_room'] = df['total_bedrooms'] / df['total_rooms']
    df['population_per_household'] = df['population'] / df['households']
    return df

# Main experiment function to run with different configurations
def run_experiment(name, use_feature_engineering, use_scaling):
    print(f"--- Running Experiment: {name} ---")

    # Load data
    train_df = pd.read_csv("./input/train.csv")

    # Feature Engineering
    if use_feature_engineering:
        train_df = feature_engineer(train_df)

    # Separate target variable
    X = train_df.drop("median_house_value", axis=1)
    y = train_df["median_house_value"]

    # Identify numerical features for scaling.
    numerical_features = X.columns

    # Scaling numerical features
    if use_scaling:
        scaler = StandardScaler()
        X[numerical_features] = scaler.fit_transform(X[numerical_features])

    # K-Fold Cross Validation and LightGBM Model Training
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    oof_predictions = np.zeros(X.shape[0])
    validation_scores = []

    for fold, (train_index, val_index) in enumerate(kf.split(X, y)):
        X_train, X_val = X.iloc[train_index], X.iloc[val_index]
        y_train, y_val = y.iloc[train_index], y.iloc[val_index]

        lgb_params = {
            'objective': 'regression_l1',
            'metric': 'rmse',
            'n_estimators': 1000,
            'learning_rate': 0.05,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 1,
            'lambda_l1': 0.1,
            'lambda_l2': 0.1,
            'num_leaves': 31,
            'verbose': -1,
            'n_jobs': -1,
            'seed': 42 + fold,
            'boosting_type': 'gbdt',
        }

        model = lgb.LGBMRegressor(**lgb_params)
        model.fit(X_train, y_train,
                  eval_set=[(X_val, y_val)],
                  eval_metric='rmse',
                  callbacks=[lgb.early_stopping(50, verbose=False)])

        oof_predictions[val_index] = model.predict(X_val)
        fold_rmse = rmse(y_val, oof_predictions[val_index])
        validation_scores.append(fold_rmse)

    final_oof_rmse = rmse(y, oof_predictions)
    print(f"Experiment '{name}' OOF RMSE: {final_oof_rmse}\n")
    return final_oof_rmse

# --- Ablation Study ---

results = {}

# 1. Base Case: Full Model (Feature Engineering + Scaling)
results['Full Model (FE + Scaling)'] = run_experiment('Full Model', use_feature_engineering=True, use_scaling=True)

# 2. Ablation: No Feature Engineering
results['No Feature Engineering'] = run_experiment('No Feature Engineering', use_feature_engineering=False, use_scaling=True)

# 3. Ablation: No Scaling
results['No Scaling'] = run_experiment('No Scaling', use_feature_engineering=True, use_scaling=False)

# 4. Ablation: No Feature Engineering & No Scaling
results['No Feature Engineering & No Scaling'] = run_experiment('No Feature Engineering & No Scaling', use_feature_engineering=False, use_scaling=False)


print("--- Ablation Study Results ---")
for name, score in results.items():
    print(f"{name}: {score:.4f}")

# Determine the most contributing part
base_rmse = results['Full Model (FE + Scaling)']
contribution = {}

# Calculate degradation when a component is removed
if 'No Feature Engineering' in results:
    degradation_fe = results['No Feature Engineering'] - base_rmse
    contribution['Feature Engineering'] = degradation_fe

if 'No Scaling' in results:
    degradation_scaling = results['No Scaling'] - base_rmse
    contribution['Standard Scaling'] = degradation_scaling

# Find the component whose removal caused the largest degradation (highest RMSE increase)
if contribution:
    most_contributing_part = max(contribution, key=contribution.get)
    print(f"\nThe part of the code that contributes the most to the overall performance is: {most_contributing_part} (removing it increased RMSE by {contribution[most_contributing_part]:.4f}).")
else:
    print("\nCould not determine the most contributing part due to missing ablation results.")

