
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load data from the specified input directory
train_df = pd.read_csv('./input/train.csv')

# Separate target variable before preprocessing
y = train_df['Survived']
X = train_df.drop('Survived', axis=1)

# Simple Preprocessing (handle missing values, encode categorical features)
# Fill missing 'Age' values with the median of the training set
X['Age'].fillna(X['Age'].median(), inplace=True)

# Fill missing 'Fare' values with the median of the training set
X['Fare'].fillna(X['Fare'].median(), inplace=True)

# Fill missing 'Embarked' values with the mode of the training set
X['Embarked'].fillna(X['Embarked'].mode()[0], inplace=True)

# Map 'Sex' to numerical values
X['Sex'] = X['Sex'].map({'male': 0, 'female': 1})

# One-hot encode 'Embarked' and 'Pclass' categorical features
X = pd.get_dummies(X, columns=['Embarked', 'Pclass'], drop_first=True)

# Drop unnecessary columns (Name, Ticket, Cabin, PassengerId for training)
X.drop(['Name', 'Ticket', 'Cabin', 'PassengerId'], axis=1, inplace=True)

# Split the data into training and validation sets
# Using a 80/20 split for training and validation, with a fixed random_state for reproducibility
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train XGBoost Classifier
# Using binary:logistic objective for binary classification
# eval_metric='logloss' is a common metric for classification tasks
# use_label_encoder=False to suppress a future deprecation warning
# random_state for reproducibility
model = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)
model.fit(X_train, y_train)

# Make predictions on the validation set
y_pred = model.predict(X_val)

# Calculate the accuracy score on the validation set
# Accuracy is a suitable evaluation metric for this task as requested.
accuracy = accuracy_score(y_val, y_pred)

# Print the final validation performance in the required format
print(f'Final Validation Performance: {accuracy:.4f}')
