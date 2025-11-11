

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
import lightgbm as lgb
from sklearn.metrics import accuracy_score
import numpy as np

# --- Function to run the pipeline with configurable options for ablation ---
def run_pipeline(df_original, use_ensemble=True, age_imputation_method='median'):
    df = df_original.copy()

    # --- Preprocessing ---
    # Drop columns that are not useful or have too many missing values
    df = df.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1)

    # Handle missing 'Age' values based on specified method
    if age_imputation_method == 'median':
        df['Age'].fillna(df['Age'].median(), inplace=True)
    elif age_imputation_method == 'mean':
        df['Age'].fillna(df['Age'].mean(), inplace=True)
    # If no specific method, assume original behavior or handle as error for safety
    # For this study, we only check median vs mean

    # Handle missing 'Embarked' values with the most frequent value (mode)
    df['Embarked'].fillna(df['Embarked'].mode()[0], inplace=True)

    # Convert 'Sex' and 'Embarked' categorical features to numerical using Label Encoding
    le_sex = LabelEncoder()
    df['Sex'] = le_sex.fit_transform(df['Sex'])

    le_embarked = LabelEncoder()
    df['Embarked'] = le_embarked.fit_transform(df['Embarked'])

    # Define features (X) and target (y)
    X = df.drop('Survived', axis=1)
    y = df['Survived']

    # Split the data into training and testing sets to create a hold-out validation set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- Model Training ---
    # Train the XGBoost Classifier
    xgb_model = XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)
    xgb_model.fit(X_train, y_train)

    if use_ensemble:
        # Train the LightGBM Classifier
        lgb_model = lgb.LGBMClassifier(objective='binary', metric='binary_logloss', random_state=42)
        lgb_model.fit(X_train, y_train)

    # --- Prediction and Ensembling ---
    # Get prediction probabilities from XGBoost model
    xgb_preds_proba = xgb_model.predict_proba(X_test)[:, 1]

    if use_ensemble:
        # Get prediction probabilities from LightGBM model
        lgb_preds_proba = lgb_model.predict_proba(X_test)[:, 1]
        # Simple ensemble: average the predicted probabilities
        ensembled_preds_proba = (xgb_preds_proba + lgb_preds_proba) / 2
        final_y_pred = (ensembled_preds_proba >= 0.5).astype(int)
    else:
        # If not ensembling, use XGBoost's direct predictions
        final_y_pred = (xgb_preds_proba >= 0.5).astype(int)

    # --- Evaluation ---
    # Calculate accuracy
    accuracy = accuracy_score(y_test, final_y_pred)
    return accuracy

# Load the dataset once for all experiments
original_df = pd.read_csv('./input/train.csv')

# --- Baseline Performance (Full Solution) ---
baseline_accuracy = run_pipeline(original_df, use_ensemble=True, age_imputation_method='median')
print(f"Baseline Validation Performance (Full Solution): {baseline_accuracy:.4f}")

# --- Ablation 1: Remove LightGBM from ensemble (Use only XGBoost) ---
# This means setting use_ensemble=False, effectively removing the contribution of LightGBM and the averaging.
ablation1_accuracy = run_pipeline(original_df, use_ensemble=False, age_imputation_method='median')
print(f"Ablation 1 Performance (XGBoost only, no ensemble): {ablation1_accuracy:.4f}")

# --- Ablation 2: Change 'Age' imputation from median to mean ---
# This means changing the age_imputation_method parameter while keeping the ensemble.
ablation2_accuracy = run_pipeline(original_df, use_ensemble=True, age_imputation_method='mean')
print(f"Ablation 2 Performance (Age imputed with Mean): {ablation2_accuracy:.4f}")

# --- Ablation Study Conclusion ---
# Calculate the impact of each ablation relative to the baseline
impact_ensemble_removal = baseline_accuracy - ablation1_accuracy # Positive if removing ensemble hurts
impact_age_imputation_change = baseline_accuracy - ablation2_accuracy # Positive if changing imputation hurts

print("\n--- Ablation Study Conclusion ---")
if impact_ensemble_removal > 0 and impact_ensemble_removal > impact_age_imputation_change:
    print(f"The part of the code that contributes the most positively to the overall performance is the ensembling of LightGBM with XGBoost. Its removal (Ablation 1) resulted in the largest drop in accuracy of {impact_ensemble_removal:.4f}.")
elif impact_age_imputation_change > 0 and impact_age_imputation_change > impact_ensemble_removal:
    print(f"The part of the code that contributes the most positively to the overall performance is the 'Age' imputation strategy (median). Changing it to mean imputation (Ablation 2) resulted in the largest drop in accuracy of {impact_age_imputation_change:.4f}.")
elif impact_ensemble_removal > 0 and impact_age_imputation_change > 0 and abs(impact_ensemble_removal - impact_age_imputation_change) < 0.001:
    print(f"Both ensembling and 'Age' imputation (median) contribute positively and similarly to performance. Removing ensemble caused a {impact_ensemble_removal:.4f} drop, and changing age imputation caused a {impact_age_imputation_change:.4f} drop.")
else:
    print("Neither of the ablated components showed a significant positive contribution (i.e., their removal/change did not cause a substantial drop in performance), or their removal/change unexpectedly improved performance.")
