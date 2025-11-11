
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


from sklearn.impute import KNNImputer
import pandas as pd

# Select relevant columns for KNN imputation, including 'Age' itself
# The plan specifies 'Pclass', 'Sex', and 'SibSp' as features to leverage.
imputation_features = ['Pclass', 'Sex', 'SibSp', 'Age']
df_for_knn = df[imputation_features].copy()

# Ensure 'Sex' is numerical for the KNNImputer.
# If 'Sex' is an object type (e.g., 'male', 'female' strings), map it to numerical values.
# This conversion is done on a temporary DataFrame to avoid modifying the original 'Sex' column directly
# and ensures the imputer receives numerical data without creating new dummy columns in the main DataFrame.
if df_for_knn['Sex'].dtype == 'object':
    df_for_knn['Sex'] = df_for_knn['Sex'].map({'male': 0, 'female': 1})
    # It's good practice to handle potential NaNs if other unexpected categories were present,
    # but for typical Titanic datasets, 'male'/'female' covers most cases.

# Initialize KNNImputer. n_neighbors can be tuned, 5 is a common default.
knn_imputer = KNNImputer(n_neighbors=5)

# Apply KNN imputation to the selected features.
# The imputer returns a numpy array.
imputed_data = knn_imputer.fit_transform(df_for_knn)

# Update the 'Age' column in the original DataFrame with the newly imputed values.
# The imputed_data array maintains the column order from df_for_knn.
df['Age'] = pd.DataFrame(imputed_data, columns=imputation_features, index=df_for_knn.index)['Age']


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
