
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


# Simple Preprocessing
# Drop irrelevant columns
all_data.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1, inplace=True)

# Fill missing 'Age' with median
all_data['Age'].fillna(all_data['Age'].median(), inplace=True)

# Fill missing 'Fare' with median (relevant for test_df primarily)
all_data['Fare'].fillna(all_data['Fare'].median(), inplace=True)

# Fill missing 'Embarked' with mode
all_data['Embarked'].fillna(all_data['Embarked'].mode()[0], inplace=True)

# Apply log1p transformation to Fare to address its skewed distribution
all_data['Fare'] = np.log1p(all_data['Fare'])

# Discretize 'Age' into categorical bins
# Using quantile-based binning to create 5 bins (adjust q as needed)
all_data['Age_Binned'] = pd.qcut(all_data['Age'], q=5, labels=False, duplicates='drop')

# Discretize transformed 'Fare' into categorical bins
# Using quantile-based binning to create 5 bins (adjust q as needed)
all_data['Fare_Binned'] = pd.qcut(all_data['Fare'], q=5, labels=False, duplicates='drop')

# Drop the original 'Age' and 'Fare' columns as they are replaced by their binned versions
all_data.drop(['Age', 'Fare'], axis=1, inplace=True)

# Encode categorical features
le = LabelEncoder()
all_data['Sex'] = le.fit_transform(all_data['Sex'])

# One-hot encode 'Embarked', 'Pclass', and the newly created binned features
all_data = pd.get_dummies(all_data, columns=['Embarked', 'Pclass', 'Age_Binned', 'Fare_Binned'], drop_first=True)


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
