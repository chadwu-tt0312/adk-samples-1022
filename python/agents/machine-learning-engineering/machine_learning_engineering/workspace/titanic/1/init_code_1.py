
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

# Load the dataset from the specified directory
df = pd.read_csv('./input/train.csv')

# --- Preprocessing ---
# Drop columns that are not useful or have too many missing values
df = df.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1)

# Handle missing 'Age' values with median imputation
df['Age'].fillna(df['Age'].median(), inplace=True)

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
# Initialize the XGBoost Classifier
# Using common parameters for a good starting point as per the model description
# use_label_encoder=False is used to suppress a future deprecation warning for XGBoost
model = XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)

# Train the model
model.fit(X_train, y_train)

# --- Prediction and Evaluation ---
# Make predictions on the hold-out validation set
y_pred = model.predict(X_test)

# Calculate accuracy as the evaluation metric
accuracy = accuracy_score(y_test, y_pred)

# Print the final validation performance
print(f"Final Validation Performance: {accuracy:.4f}")
