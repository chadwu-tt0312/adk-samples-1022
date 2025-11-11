
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
import lightgbm as lgb
from sklearn.metrics import accuracy_score

# --- Standardized Data Loading and Initial Split ---
# Load the raw dataset
raw_df = pd.read_csv('./input/train.csv')

# Define target
y_raw_target = raw_df['Survived']

# Define features (before any solution-specific preprocessing)
# Keep original columns for now, they will be dropped/processed within functions
X_raw_data = raw_df.drop('Survived', axis=1)

# Standardize the validation data generation
X_train_split_raw, X_val_split_raw, y_train_split, y_val_split = train_test_split(
    X_raw_data, y_raw_target, test_size=0.2, random_state=42
)

# --- Solution 1 Function Definition ---
def get_solution1_ensemble_proba(X_train, y_train, X_val):
    """
    Applies preprocessing and trains models from Python Solution 1,
    then returns ensembled probabilities for the validation set.
    """
    # Make copies to avoid modifying original splits
    df_train_s1 = X_train.copy()
    df_val_s1 = X_val.copy()

    # Preprocessing consistent with Solution 1
    # Drop columns
    df_train_s1 = df_train_s1.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1)
    df_val_s1 = df_val_s1.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1)

    # Handle missing 'Age' values with median imputation (from training data)
    age_median_s1 = df_train_s1['Age'].median()
    df_train_s1['Age'].fillna(age_median_s1, inplace=True)
    df_val_s1['Age'].fillna(age_median_s1, inplace=True)

    # Handle missing 'Embarked' values with the most frequent value (mode from training data)
    embarked_mode_s1 = df_train_s1['Embarked'].mode()[0]
    df_train_s1['Embarked'].fillna(embarked_mode_s1, inplace=True)
    df_val_s1['Embarked'].fillna(embarked_mode_s1, inplace=True)

    # Convert 'Sex' and 'Embarked' categorical features to numerical using Label Encoding
    # Fit on training data, transform both
    le_sex_s1 = LabelEncoder()
    df_train_s1['Sex'] = le_sex_s1.fit_transform(df_train_s1['Sex'])
    df_val_s1['Sex'] = le_sex_s1.transform(df_val_s1['Sex'])

    le_embarked_s1 = LabelEncoder()
    df_train_s1['Embarked'] = le_embarked_s1.fit_transform(df_train_s1['Embarked'])
    df_val_s1['Embarked'] = le_embarked_s1.transform(df_val_s1['Embarked'])

    # Train XGBoost Classifier
    xgb_model_s1 = XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)
    xgb_model_s1.fit(df_train_s1, y_train)

    # Train LightGBM Classifier
    lgb_model_s1 = lgb.LGBMClassifier(objective='binary', metric='binary_logloss', random_state=42)
    lgb_model_s1.fit(df_train_s1, y_train)

    # Get prediction probabilities from both models
    xgb_preds_proba_s1 = xgb_model_s1.predict_proba(df_val_s1)[:, 1]
    lgb_preds_proba_s1 = lgb_model_s1.predict_proba(df_val_s1)[:, 1]

    # Simple ensemble: average the predicted probabilities
    ensembled_preds_proba_s1 = (xgb_preds_proba_s1 + lgb_preds_proba_s1) / 2

    return ensembled_preds_proba_s1

# --- Solution 2 Function Definition ---
def get_solution2_proba(X_train, y_train, X_val):
    """
    Applies preprocessing and trains the model from Python Solution 2,
    then returns probabilities for the validation set.
    """
    # Make copies to avoid modifying original splits
    df_train_s2 = X_train.copy()
    df_val_s2 = X_val.copy()

    # Preprocessing consistent with Solution 2, applied to combined data for consistent encoding
    # Combine X_train and X_val to ensure consistent feature engineering (especially for get_dummies)
    # The original solution 2 combines train and test for pre-processing.
    # Here, we combine X_train_split and X_val_split for consistency.
    all_data_s2 = pd.concat([df_train_s2, df_val_s2], ignore_index=True)
    
    # Drop irrelevant columns
    all_data_s2.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1, inplace=True)

    # Fill missing 'Age' with median (calculated from combined data as per original S2 logic)
    age_median_s2 = all_data_s2['Age'].median()
    all_data_s2['Age'].fillna(age_median_s2, inplace=True)

    # Fill missing 'Fare' with median (calculated from combined data as per original S2 logic)
    fare_median_s2 = all_data_s2['Fare'].median()
    all_data_s2['Fare'].fillna(fare_median_s2, inplace=True)

    # Fill missing 'Embarked' with mode (calculated from combined data as per original S2 logic)
    embarked_mode_s2 = all_data_s2['Embarked'].mode()[0]
    all_data_s2['Embarked'].fillna(embarked_mode_s2, inplace=True)

    # Encode categorical features
    le_sex_s2 = LabelEncoder()
    all_data_s2['Sex'] = le_sex_s2.fit_transform(all_data_s2['Sex'])
    
    # One-hot encode 'Embarked' and 'Pclass'
    all_data_s2 = pd.get_dummies(all_data_s2, columns=['Embarked', 'Pclass'], drop_first=True)

    # Split back into processed train and validation sets
    X_train_processed_s2 = all_data_s2.iloc[:len(df_train_s2)]
    X_val_processed_s2 = all_data_s2.iloc[len(df_train_s2):]

    # Initialize and train XGBoost Classifier
    model_s2 = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    model_s2.fit(X_train_processed_s2, y_train)

    # Make prediction probabilities on the validation set
    solution2_preds_proba = model_s2.predict_proba(X_val_processed_s2)[:, 1]

    return solution2_preds_proba

# --- Ensemble Plan Implementation ---

# 1. Standardize Validation Data Generation (done at the beginning of the script)

# 2. Generate Binary Predictions from Solution 1
solution1_preds_proba = get_solution1_ensemble_proba(X_train_split_raw, y_train_split, X_val_split_raw)
s1_binary_preds = (solution1_preds_proba >= 0.5).astype(int)

# 3. Generate Binary Predictions from Solution 2
solution2_preds_proba = get_solution2_proba(X_train_split_raw, y_train_split, X_val_split_raw)
s2_binary_preds = (solution2_preds_proba >= 0.5).astype(int)

# 4. Combine Binary Predictions using Hard Voting with Solution 1 as Tie-Breaker
# As per the ensemble plan:
# - If s1_binary_preds and s2_binary_preds agree, the ensemble prediction is that agreed-upon value.
# - If s1_binary_preds and s2_binary_preds disagree, the ensemble prediction defaults to s1_binary_preds.
# This logic simplifies to always taking s1_binary_preds.
ensembled_y_pred_final = s1_binary_preds

# 5. Evaluate Ensembled Performance
accuracy = accuracy_score(y_val_split, ensembled_y_pred_final)

# Print the final performance metric
print(f"Final Validation Performance: {accuracy}")
