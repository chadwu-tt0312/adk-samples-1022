
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# --- Modified Python Solution 1 ---
def get_solution1_model_and_data():
    train_df = pd.read_csv('./input/train.csv')

    # Preprocessing
    train_df.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1, inplace=True)
    train_df['Age'].fillna(train_df['Age'].median(), inplace=True)
    train_df['Embarked'].fillna(train_df['Embarked'].mode()[0], inplace=True)
    train_df['Sex'] = train_df['Sex'].map({'male': 0, 'female': 1})
    train_df = pd.get_dummies(train_df, columns=['Embarked', 'Pclass'], drop_first=True)

    X = train_df.drop('Survived', axis=1)
    y = train_df['Survived']

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    xgb_clf = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)
    xgb_clf.fit(X_train, y_train)

    return xgb_clf, X_val, y_val

# --- Modified Python Solution 2 ---
def get_solution2_model_and_data():
    train_df = pd.read_csv('./input/train.csv')

    y = train_df['Survived']
    X = train_df.drop('Survived', axis=1)

    # Simple Preprocessing (handle missing values, encode categorical features)
    X['Age'].fillna(X['Age'].median(), inplace=True)
    # Fare has no missing values in train.csv, so this line is effectively a no-op for training data
    X['Fare'].fillna(X['Fare'].median(), inplace=True) 
    X['Embarked'].fillna(X['Embarked'].mode()[0], inplace=True)
    X['Sex'] = X['Sex'].map({'male': 0, 'female': 1})
    X = pd.get_dummies(X, columns=['Embarked', 'Pclass'], drop_first=True)
    X.drop(['Name', 'Ticket', 'Cabin', 'PassengerId'], axis=1, inplace=True)

    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)
    model.fit(X_train, y_train)

    return model, X_val, y_val

# --- Ensemble Implementation ---

# Get trained model and validation data from Solution 1
model_sol1, X_val_sol1, y_val_sol1 = get_solution1_model_and_data()

# Get trained model and validation data from Solution 2
model_sol2, X_val_sol2, y_val_sol2 = get_solution2_model_and_data()

# Predict probabilities using both models on their respective validation sets.
# As per the plan, X_val and y_val from both solutions are effectively the same.
y_proba_sol1 = model_sol1.predict_proba(X_val_sol1)
y_proba_sol2 = model_sol2.predict_proba(X_val_sol2)

# Average the probabilities of the positive class (survival)
ensemble_proba = (y_proba_sol1[:, 1] + y_proba_sol2[:, 1]) / 2

# Convert averaged probabilities into binary predictions using a 0.5 threshold
ensemble_predictions = (ensemble_proba > 0.5).astype(int)

# Evaluate the accuracy of the ensembled predictions against the common y_val
ensemble_accuracy = accuracy_score(y_val_sol1, ensemble_predictions)

# Print the final validation performance in the required format
print(f'Final Validation Performance: {ensemble_accuracy:.4f}')
