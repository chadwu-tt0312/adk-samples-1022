
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
import lightgbm as lgb
from sklearn.metrics import accuracy_score
import numpy as np

# Load the dataset from the specified directory
df = pd.read_csv('./input/train.csv')

# --- Preprocessing ---
# Drop columns that are not useful or have too many missing values
df = df.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1)


# Handle missing 'Age' values with mean imputation
df['Age'].fillna(df['Age'].mean(), inplace=True)


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
# Train the XGBoost Classifier (from base solution)
xgb_model = XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)
xgb_model.fit(X_train, y_train)

# Train the LightGBM Classifier (from reference solution)
lgb_model = lgb.LGBMClassifier(objective='binary', metric='binary_logloss', random_state=42)
lgb_model.fit(X_train, y_train)

# --- Prediction and Ensembling ---
# Get prediction probabilities from both models
xgb_preds_proba = xgb_model.predict_proba(X_test)[:, 1] # Probability of the positive class
lgb_preds_proba = lgb_model.predict_proba(X_test)[:, 1] # Probability of the positive class

# Simple ensemble: average the predicted probabilities
ensembled_preds_proba = (xgb_preds_proba + lgb_preds_proba) / 2

# Convert averaged probabilities to binary predictions using a 0.5 threshold
ensembled_y_pred = (ensembled_preds_proba >= 0.5).astype(int)

# --- Evaluation ---
# Calculate accuracy of the ensembled predictions
accuracy = accuracy_score(y_test, ensembled_y_pred)

# Print the final validation performance
print(f"Final Validation Performance: {accuracy:.4f}")
