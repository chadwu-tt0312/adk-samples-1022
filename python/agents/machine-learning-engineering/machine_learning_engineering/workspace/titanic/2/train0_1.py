
import pandas as pd
import numpy as np
import xgboost as xgb
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelEncoder

# Load data from the specified input directory
train_df = pd.read_csv('./input/train.csv')

# Separate target variable before preprocessing
y = train_df['Survived']
X = train_df.drop('Survived', axis=1)

# --- Common Preprocessing Steps for both models ---
# Fill missing 'Age' values with the median of the training set
X['Age'].fillna(X['Age'].median(), inplace=True)

# Fill missing 'Fare' values with the median of the training set
X['Fare'].fillna(X['Fare'].median(), inplace=True)

# Fill missing 'Embarked' values with the mode of the training set
X['Embarked'].fillna(X['Embarked'].mode()[0], inplace=True)

# Drop unnecessary columns (Name, Ticket, Cabin, PassengerId for training)
X.drop(['Name', 'Ticket', 'Cabin', 'PassengerId'], axis=1, inplace=True)


# --- Create separate preprocessed datasets for XGBoost and LightGBM ---

# Preprocessing for XGBoost model (following base solution's approach)
X_xgb = X.copy()
# Map 'Sex' to numerical values
X_xgb['Sex'] = X_xgb['Sex'].map({'male': 0, 'female': 1})
# One-hot encode 'Embarked' and 'Pclass' categorical features
X_xgb = pd.get_dummies(X_xgb, columns=['Embarked', 'Pclass'], drop_first=True)

# Preprocessing for LightGBM model (following reference solution's approach)
X_lgbm = X.copy()
le = LabelEncoder()
# Label encode 'Sex' and 'Embarked'
X_lgbm['Sex'] = le.fit_transform(X_lgbm['Sex'])
X_lgbm['Embarked'] = le.fit_transform(X_lgbm['Embarked'])
# Convert categorical columns to 'category' dtype for LightGBM
# LightGBM can efficiently handle categorical features when specified
for col in ['Sex', 'Pclass', 'Embarked']:
    X_lgbm[col] = X_lgbm[col].astype('category')


# Split the data into training and validation sets for both models
# Ensure the split is consistent by splitting indices first
X_idx_train, X_idx_val, y_train, y_val = train_test_split(X.index, y, test_size=0.2, random_state=42)

# Apply the split indices to the preprocessed dataframes
X_xgb_train = X_xgb.loc[X_idx_train]
X_xgb_val = X_xgb.loc[X_idx_val]

X_lgbm_train = X_lgbm.loc[X_idx_train]
X_lgbm_val = X_lgbm.loc[X_idx_val]


# --- Initialize and train XGBoost Classifier (from base solution) ---
model_xgb = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)
model_xgb.fit(X_xgb_train, y_train)

# --- Initialize and train LightGBM Classifier (from reference solution) ---
model_lgbm = lgb.LGBMClassifier(objective='binary', random_state=42)
model_lgbm.fit(X_lgbm_train, y_train)


# --- Make Predictions (probabilities for ensembling) ---
# Get prediction probabilities from XGBoost model
y_pred_proba_xgb = model_xgb.predict_proba(X_xgb_val)[:, 1]

# Get prediction probabilities from LightGBM model
y_pred_proba_lgbm = model_lgbm.predict_proba(X_lgbm_val)[:, 1]


# --- Ensemble the predictions ---
# Simple averaging of probabilities from both models
y_pred_proba_ensemble = (y_pred_proba_xgb + y_pred_proba_lgbm) / 2

# Convert averaged probabilities to binary predictions using a 0.5 threshold
y_pred_ensemble = (y_pred_proba_ensemble >= 0.5).astype(int)


# --- Calculate the accuracy score of the ensemble model ---
accuracy = accuracy_score(y_val, y_pred_ensemble)

# Print the final validation performance in the required format
print(f'Final Validation Performance: {accuracy:.4f}')

