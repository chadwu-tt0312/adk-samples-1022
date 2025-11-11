
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

# Load data from the specified ./input directory
train_df = pd.read_csv(os.path.join('input', 'train.csv'))
test_df = pd.read_csv(os.path.join('input', 'test.csv'))

# Combine for preprocessing
all_data = pd.concat([train_df.drop('Survived', axis=1), test_df], ignore_index=True)


# Simple Preprocessing (Enhanced with Feature Engineering)

# 1. Feature Engineering: Create FamilySize and IsAlone
all_data['FamilySize'] = all_data['SibSp'] + all_data['Parch'] + 1
all_data['IsAlone'] = (all_data['FamilySize'] == 1).astype(int)

# 2. Feature Engineering: Extract and Standardize Title from Name
all_data['Title'] = all_data['Name'].str.extract(' ([A-Za-z]+)\.', expand=False)
# Group rare titles
all_data['Title'] = all_data['Title'].replace(['Lady', 'Countess','Capt', 'Col',\
 	'Don', 'Dr', 'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')
# Standardize common titles
all_data['Title'] = all_data['Title'].replace('Mlle', 'Miss')
all_data['Title'] = all_data['Title'].replace('Ms', 'Miss')
all_data['Title'] = all_data['Title'].replace('Mme', 'Mrs')
# Fill any potential NaN titles (if regex failed to match) with 'Rare'
all_data['Title'].fillna('Rare', inplace=True)


# 3. Drop irrelevant columns and original features now captured by new ones
# PassengerId, Ticket, Cabin are irrelevant as before.
# Name is dropped after title extraction.
# SibSp and Parch are dropped as their information is consolidated into FamilySize.
columns_to_drop = ['PassengerId', 'Name', 'Ticket', 'Cabin', 'SibSp', 'Parch']
all_data.drop(columns_to_drop, axis=1, inplace=True)

# 4. Fill missing values (Age, Fare, Embarked) as per original plan
all_data['Age'].fillna(all_data['Age'].median(), inplace=True)
all_data['Fare'].fillna(all_data['Fare'].median(), inplace=True)
all_data['Embarked'].fillna(all_data['Embarked'].mode()[0], inplace=True)

# 5. Encode categorical features (existing and new ones)
le = LabelEncoder()
all_data['Sex'] = le.fit_transform(all_data['Sex'])

# One-hot encode 'Title' (new), 'Embarked', and 'Pclass' (existing)
all_data = pd.get_dummies(all_data, columns=['Title', 'Embarked', 'Pclass'], drop_first=True)


# Split back into train and test
X_train_processed = all_data.iloc[:len(train_df)]
# X_test_processed is for actual test set predictions, not used for validation score.
# However, it's created as part of the preprocessing pipeline.
X_test_processed = all_data.iloc[len(train_df):] 
y_train = train_df['Survived']

# Train-test split for validation
X_train_model, X_val_model, y_train_model, y_val_model = train_test_split(
    X_train_processed, y_train, test_size=0.2, random_state=42
)

# Initialize and train XGBoost Classifier
# use_label_encoder=False is specified to suppress a warning in recent XGBoost versions.
# eval_metric='logloss' is suitable for binary classification.
model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
model.fit(X_train_model, y_train_model)

# Make predictions on the validation set
y_pred_val = model.predict(X_val_model)

# Evaluate model using accuracy
accuracy = accuracy_score(y_val_model, y_pred_val)

# Print the final performance metric in the required format
print(f"Final Validation Performance: {accuracy}")
