
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# --- Function encapsulating Solution 1's logic ---
def run_solution_1_logic():
    # Load the Titanic dataset from the specified input directory
    train_df = pd.read_csv('./input/train.csv')

    # Preprocessing
    # Drop columns that are not useful for prediction or require complex feature engineering for this simple example
    train_df.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1, inplace=True)

    # Fill missing Age values with the median
    train_df['Age'].fillna(train_df['Age'].median(), inplace=True)

    # Fill missing Embarked values with the mode
    train_df['Embarked'].fillna(train_df['Embarked'].mode()[0], inplace=True)

    # Convert 'Sex' to numerical: 'male' to 0, 'female' to 1
    train_df['Sex'] = train_df['Sex'].map({'male': 0, 'female': 1})

    # One-hot encode 'Embarked' and 'Pclass' categorical features
    train_df = pd.get_dummies(train_df, columns=['Embarked', 'Pclass'], drop_first=True)

    # Define features (X) and target (y)
    X = train_df.drop('Survived', axis=1)
    y = train_df['Survived']

    # Split data into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize the XGBoost Classifier
    xgb_clf = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)

    # Train the XGBoost model on the training data
    xgb_clf.fit(X_train, y_train)

    return xgb_clf, X_val, y_val

# --- Function encapsulating Solution 2's logic ---
def run_solution_2_logic():
    # Load data from the specified input directory
    train_df = pd.read_csv('./input/train.csv')

    # Separate target variable before preprocessing
    y_sol = train_df['Survived']
    X_sol = train_df.drop('Survived', axis=1)

    # Simple Preprocessing (handle missing values, encode categorical features)
    # Fill missing 'Age' values with the median of the training set
    X_sol['Age'].fillna(X_sol['Age'].median(), inplace=True)

    # Fill missing 'Fare' values with the median of the training set
    # (Note: For the Titanic train.csv, Fare typically has no missing values, but this is part of Sol2's original logic)
    X_sol['Fare'].fillna(X_sol['Fare'].median(), inplace=True)

    # Fill missing 'Embarked' values with the mode of the training set
    X_sol['Embarked'].fillna(X_sol['Embarked'].mode()[0], inplace=True)

    # Map 'Sex' to numerical values
    X_sol['Sex'] = X_sol['Sex'].map({'male': 0, 'female': 1})

    # One-hot encode 'Embarked' and 'Pclass' categorical features
    X_sol = pd.get_dummies(X_sol, columns=['Embarked', 'Pclass'], drop_first=True)

    # Drop unnecessary columns (Name, Ticket, Cabin, PassengerId for training)
    X_sol.drop(['Name', 'Ticket', 'Cabin', 'PassengerId'], axis=1, inplace=True)

    # Split the data into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(X_sol, y_sol, test_size=0.2, random_state=42)

    # Initialize and train XGBoost Classifier
    model = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)
    model.fit(X_train, y_train)

    return model, X_val, y_val

# --- Main Ensemble Implementation ---

# Run Solution 1 to get its trained model and validation data
xgb_clf_sol1, X_val_sol1, y_val_sol1 = run_solution_1_logic()

# Run Solution 2 to get its trained model and validation data
xgb_clf_sol2, X_val_sol2, y_val_sol2 = run_solution_2_logic()

# Get binary predictions from each model on their respective validation sets
y_pred_sol1 = xgb_clf_sol1.predict(X_val_sol1)
y_pred_sol2 = xgb_clf_sol2.predict(X_val_sol2)

# Apply the ensemble plan's "OR" logic:
# if either model predicts 1, the ensemble predicts 1
ensemble_predictions = (y_pred_sol1 | y_pred_sol2).astype(int)

# Evaluate the accuracy of the ensemble
# Since both solutions use identical preprocessing and train_test_split parameters,
# X_val and y_val from both runs are effectively the same.
final_accuracy = accuracy_score(y_val_sol1, ensemble_predictions)

# Print the final validation performance in the required format
print(f"Final Validation Performance: {final_accuracy:.4f}")
