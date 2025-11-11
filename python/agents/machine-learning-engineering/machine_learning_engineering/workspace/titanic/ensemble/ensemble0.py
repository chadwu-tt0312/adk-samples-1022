
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
import lightgbm as lgb
from sklearn.metrics import accuracy_score
import numpy as np
import os

# --- Common Data Loading and Initial Split ---
# Load the dataset from the specified directory
df_train_raw_full = pd.read_csv('./input/train.csv')

# Define features (X) and target (y) for the initial split
X_raw_data = df_train_raw_full.drop('Survived', axis=1)
y_raw_target = df_train_raw_full['Survived']

# Perform a single train_test_split on the raw data
# This ensures that both solutions' internal validation sets will be identical.
X_train_split, X_val_split, y_train_split, y_val_split = train_test_split(
    X_raw_data, y_raw_target, test_size=0.2, random_state=42
)

# --- Function encapsulating Solution 1's logic for validation probabilities ---
def get_solution1_ensemble_proba(X_train_df, X_val_df, y_train_series):
    # Make copies to avoid modifying the original split dataframes for other solution
    df_train_s1 = X_train_df.copy()
    df_val_s1 = X_val_df.copy()

    # --- Preprocessing specific to Solution 1 ---
    # Drop columns that are not useful or have too many missing values
    df_train_s1 = df_train_s1.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1)
    df_val_s1 = df_val_s1.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1)

    # Handle missing 'Age' values with median imputation (calculated on training data)
    age_median_s1 = df_train_s1['Age'].median()
    df_train_s1['Age'].fillna(age_median_s1, inplace=True)
    df_val_s1['Age'].fillna(age_median_s1, inplace=True)

    # Handle missing 'Embarked' values with the most frequent value (mode, calculated on training data)
    embarked_mode_s1 = df_train_s1['Embarked'].mode()[0]
    df_train_s1['Embarked'].fillna(embarked_mode_s1, inplace=True)
    df_val_s1['Embarked'].fillna(embarked_mode_s1, inplace=True)

    # Convert 'Sex' and 'Embarked' categorical features to numerical using Label Encoding
    le_sex = LabelEncoder()
    df_train_s1['Sex'] = le_sex.fit_transform(df_train_s1['Sex'])
    df_val_s1['Sex'] = le_sex.transform(df_val_s1['Sex']) # Use fitted encoder

    le_embarked = LabelEncoder()
    df_train_s1['Embarked'] = le_embarked.fit_transform(df_train_s1['Embarked'])
    df_val_s1['Embarked'] = le_embarked.transform(df_val_s1['Embarked']) # Use fitted encoder

    # --- Model Training ---
    # Train the XGBoost Classifier
    xgb_model = XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)
    xgb_model.fit(df_train_s1, y_train_series)

    # Train the LightGBM Classifier
    lgb_model = lgb.LGBMClassifier(objective='binary', metric='binary_logloss', random_state=42)
    lgb_model.fit(df_train_s1, y_train_series)

    # --- Prediction and Ensembling for validation set ---
    # Get prediction probabilities from both models
    xgb_preds_proba = xgb_model.predict_proba(df_val_s1)[:, 1] # Probability of the positive class
    lgb_preds_proba = lgb_model.predict_proba(df_val_s1)[:, 1] # Probability of the positive class

    # Simple ensemble: average the predicted probabilities
    ensembled_preds_proba_s1 = (xgb_preds_proba + lgb_preds_proba) / 2
    
    return ensembled_preds_proba_s1

# --- Function encapsulating Solution 2's logic for validation probabilities ---
def get_solution2_proba(X_train_df, X_val_df, y_train_series):
    # Combine training and validation data for consistent preprocessing (similar to Solution 2's 'all_data' approach)
    combined_s2 = pd.concat([X_train_df, X_val_df], ignore_index=True)

    # --- Preprocessing specific to Solution 2 ---
    # Drop irrelevant columns
    combined_s2.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1, inplace=True)

    # Fill missing 'Age' with median (calculated on the combined data)
    age_median_s2 = combined_s2['Age'].median()
    combined_s2['Age'].fillna(age_median_s2, inplace=True)

    # Fill missing 'Fare' with median (calculated on the combined data)
    fare_median_s2 = combined_s2['Fare'].median()
    combined_s2['Fare'].fillna(fare_median_s2, inplace=True)

    # Fill missing 'Embarked' with mode (calculated on the combined data)
    embarked_mode_s2 = combined_s2['Embarked'].mode()[0]
    combined_s2['Embarked'].fillna(embarked_mode_s2, inplace=True)

    # Encode categorical features
    le = LabelEncoder()
    combined_s2['Sex'] = le.fit_transform(combined_s2['Sex'])
    
    # One-hot encode 'Embarked' and 'Pclass'
    combined_s2 = pd.get_dummies(combined_s2, columns=['Embarked', 'Pclass'], drop_first=True)

    # Split back into processed training and validation sets
    X_train_processed_s2 = combined_s2.iloc[:len(X_train_df)]
    X_val_processed_s2 = combined_s2.iloc[len(X_train_df):]
    
    # Initialize and train XGBoost Classifier
    model_s2 = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    model_s2.fit(X_train_processed_s2, y_train_series)

    # Make probabilistic predictions on the validation set (Step 3)
    y_pred_proba_val_s2 = model_s2.predict_proba(X_val_processed_s2)[:, 1]
    
    return y_pred_proba_val_s2

# --- Execute functions to get probabilities from each solution ---
# Get probabilities from Solution 1 (Step 2)
solution1_preds_proba = get_solution1_ensemble_proba(X_train_split, X_val_split, y_train_split)

# Get probabilities from Solution 2 (Step 3)
solution2_preds_proba = get_solution2_proba(X_train_split, X_val_split, y_train_split)

# --- Combine Probabilities using Simple Averaging (Step 4) ---
final_combined_probabilities = (solution1_preds_proba + solution2_preds_proba) / 2

# --- Convert to Binary Predictions (Step 5) ---
ensembled_y_pred = (final_combined_probabilities >= 0.5).astype(int)

# --- Evaluate Ensembled Performance (Step 6) ---
accuracy = accuracy_score(y_val_split, ensembled_y_pred)

# Print the final validation performance
print(f"Final Validation Performance: {accuracy:.4f}")
