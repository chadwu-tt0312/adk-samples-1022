
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

# Load data
# Ensure 'train.csv' and 'test.csv' are in a directory named 'input' relative to the script.
train_df = pd.read_csv("./input/train.csv")
test_df = pd.read_csv("./input/test.csv")

# Feature Engineering
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






# K-Fold Cross Validation and LightGBM Model Training
kf = KFold(n_splits=5, shuffle=True, random_state=42)
oof_predictions = np.zeros(X.shape[0])
test_predictions = np.zeros(X_test.shape[0])
models = []
validation_scores = []

for fold, (train_index, val_index) in enumerate(kf.split(X, y)):
    print(f"Fold {fold+1}")
    X_train, X_val = X.iloc[train_index], X.iloc[val_index]
    y_train, y_val = y.iloc[train_index], y.iloc[val_index]

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
        'seed': 42 + fold,
        'boosting_type': 'gbdt',
    }

    model = lgb.LGBMRegressor(**lgb_params)
    model.fit(X_train, y_train,
              eval_set=[(X_val, y_val)],
              eval_metric='rmse',
              callbacks=[lgb.early_stopping(50, verbose=False)]) # Use callbacks for early stopping

    oof_predictions[val_index] = model.predict(X_val)
    fold_test_preds = model.predict(X_test)
    test_predictions += fold_test_preds / kf.n_splits

    fold_rmse = rmse(y_val, oof_predictions[val_index])
    validation_scores.append(fold_rmse)
    print(f"Fold {fold+1} RMSE: {fold_rmse}")
    models.append(model)

final_oof_rmse = rmse(y, oof_predictions)
print(f"Overall OOF RMSE: {final_oof_rmse}")
print(f"Final Validation Performance: {final_oof_rmse}") # Required output format

# Create submission file
submission_df = pd.DataFrame({'median_house_value': test_predictions})
submission_df.to_csv("submission.csv", index=False)

print("Submission file created successfully!")
