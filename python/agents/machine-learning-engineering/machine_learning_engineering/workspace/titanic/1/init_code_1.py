
import pandas as pd
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

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
# drop_first=True avoids multicollinearity
train_df = pd.get_dummies(train_df, columns=['Embarked', 'Pclass'], drop_first=True)

# Define features (X) and target (y)
X = train_df.drop('Survived', axis=1)
y = train_df['Survived']

# Split data into training and validation sets
# A test_size of 0.2 means 20% of the data will be used for validation
# random_state ensures reproducibility of the split
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize the LightGBM Classifier
# objective='binary' for binary classification (survival prediction)
# random_state for reproducibility
lgb_clf = lgb.LGBMClassifier(objective='binary', random_state=42)

# Train the LightGBM model on the training data
lgb_clf.fit(X_train, y_train)

# Make predictions on the validation set
y_pred_lgb = lgb_clf.predict(X_val)

# Evaluate accuracy on the validation set
# Accuracy is a suitable metric for this balanced binary classification task
accuracy_lgb = accuracy_score(y_val, y_pred_lgb)

# Print the final validation performance in the required format
print(f"Final Validation Performance: {accuracy_lgb:.4f}")
