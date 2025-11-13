
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import os

# Load the Titanic dataset from the specified input directory
train_df = pd.read_csv('./input/train.csv')

# --- Store imputation values from the training data for consistent preprocessing of test data ---
# Calculate median age from training data
median_age = train_df['Age'].median()
# Calculate mode embarked from training data
mode_embarked = train_df['Embarked'].mode()[0]
# Calculate median fare from training data (test data is known to have missing Fares)
median_fare = train_df['Fare'].median()

# --- Preprocessing for training data ---
# Drop columns that are not useful for prediction or require complex feature engineering for this simple example
train_df.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1, inplace=True)

# Fill missing Age values with the median from training data
train_df['Age'].fillna(median_age, inplace=True)

# Fill missing Embarked values with the mode from training data
train_df['Embarked'].fillna(mode_embarked, inplace=True)

# Convert 'Sex' to numerical: 'male' to 0, 'female' to 1
train_df['Sex'] = train_df['Sex'].map({'male': 0, 'female': 1})

# One-hot encode 'Embarked' and 'Pclass' categorical features
# drop_first=True avoids multicollinearity, though not strictly necessary for simple models,
# it's good practice for tree-based models and general ML.
train_df = pd.get_dummies(train_df, columns=['Embarked', 'Pclass'], drop_first=True)

# Define features (X) and target (y)
X = train_df.drop('Survived', axis=1)
y = train_df['Survived']

# Split data into training and validation sets (as in the original solution for validation performance reporting)
# A test_size of 0.2 means 20% of the data will be used for validation
# random_state ensures reproducibility of the split
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize the XGBoost Classifier
# objective='binary:logistic' for binary classification (survival prediction)
# eval_metric='logloss' is a common metric for binary classification problems in XGBoost
# use_label_encoder=False suppresses a future deprecation warning
# random_state for reproducibility
xgb_clf = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)

# Train the XGBoost model on the training split
xgb_clf.fit(X_train, y_train)

# Make predictions on the validation set
y_pred_xgb = xgb_clf.predict(X_val)

# Evaluate accuracy on the validation set
# Accuracy is a suitable metric for this balanced binary classification task
accuracy_xgb = accuracy_score(y_val, y_pred_xgb)

# Print the final validation performance in the required format
print(f"Final Validation Performance: {accuracy_xgb:.4f}")

# --- Submission part: Train model on full data and predict on test set ---

# Re-initialize and train the model on the entire training dataset for final submission
# This uses all available training data to build the most robust model for prediction.
final_xgb_clf = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)
final_xgb_clf.fit(X, y) # Train on full X, y

# Load test data
test_df = pd.read_csv('./input/test.csv')

# Store PassengerIds for the submission file
passenger_ids = test_df['PassengerId']

# Preprocessing for test data (consistent with training data preprocessing)
# Drop columns as done for training data
test_df.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1, inplace=True)

# Fill missing Age values with the median from the training data
test_df['Age'].fillna(median_age, inplace=True)

# Fill missing Embarked values with the mode from the training data
test_df['Embarked'].fillna(mode_embarked, inplace=True)

# Fill missing Fare values with the median from the training data (as test data has missing Fares)
test_df['Fare'].fillna(median_fare, inplace=True)

# Convert 'Sex' to numerical: 'male' to 0, 'female' to 1
test_df['Sex'] = test_df['Sex'].map({'male': 0, 'female': 1})

# One-hot encode 'Embarked' and 'Pclass' categorical features
test_df = pd.get_dummies(test_df, columns=['Embarked', 'Pclass'], drop_first=True)

# Align columns between training and test sets to ensure consistency
# This handles potential discrepancies in one-hot encoded columns if
# not all categories are present in both train and test.
missing_cols_in_test = set(X.columns) - set(test_df.columns)
for c in missing_cols_in_test:
    test_df[c] = 0 # Add missing columns to test_df and fill with 0

extra_cols_in_test = set(test_df.columns) - set(X.columns)
if len(extra_cols_in_test) > 0:
    test_df.drop(columns=list(extra_cols_in_test), inplace=True) # Drop extra columns from test_df

test_df = test_df[X.columns] # Ensure the order of columns is the same as in training data

# Make predictions on the preprocessed test set using the model trained on full data
test_predictions = final_xgb_clf.predict(test_df)

# Create submission file DataFrame
submission_df = pd.DataFrame({'PassengerId': passenger_ids, 'Survived': test_predictions})

# Create the './final' directory if it doesn't exist
os.makedirs('./final', exist_ok=True)

# Save the submission file to the specified directory
submission_df.to_csv('./final/submission.csv', index=False)
