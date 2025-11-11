
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

def run_ablation_experiment(ablation_type=None):
    """
    Runs the Titanic survival prediction model with specified ablations.

    Args:
        ablation_type (str, optional): Type of ablation to perform.
            - None (default): Runs the baseline solution.
            - 'age_mean_imputation': Uses mean for Age imputation instead of median.
            - 'embarked_label_encode': Uses LabelEncoder for Embarked instead of One-Hot encoding.
    Returns:
        float: Validation accuracy of the model.
    """
    # Load data - focusing only on train_df for validation study
    train_df = pd.read_csv(os.path.join('input', 'train.csv'))

    # Separate target variable before any processing
    y_train_full = train_df['Survived']
    X_train_full = train_df.drop('Survived', axis=1)

    # Make a copy for current experiment to ensure isolation between runs
    X_processed = X_train_full.copy()

    # --- Preprocessing Steps ---

    # Drop irrelevant columns (common across all ablations for this study)
    X_processed.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1, inplace=True)

    # Fill missing 'Age'
    if ablation_type == 'age_mean_imputation':
        # Ablation 1: Use mean imputation for Age
        X_processed['Age'].fillna(X_processed['Age'].mean(), inplace=True)
    else:
        # Baseline: Use median imputation for Age
        X_processed['Age'].fillna(X_processed['Age'].median(), inplace=True)

    # Fill missing 'Fare' with median (no missing Fare in train_df, but good practice)
    X_processed['Fare'].fillna(X_processed['Fare'].median(), inplace=True)

    # Fill missing 'Embarked' with mode
    X_processed['Embarked'].fillna(X_processed['Embarked'].mode()[0], inplace=True)

    # Encode 'Sex' using LabelEncoder
    le_sex = LabelEncoder()
    X_processed['Sex'] = le_sex.fit_transform(X_processed['Sex'])

    # Encode 'Embarked' and 'Pclass'
    if ablation_type == 'embarked_label_encode':
        # Ablation 2: Use LabelEncoder for Embarked, Pclass remains One-Hot encoded
        le_embarked = LabelEncoder()
        X_processed['Embarked'] = le_embarked.fit_transform(X_processed['Embarked'])
        # Pclass still one-hot encoded as per baseline's handling of Pclass
        X_processed = pd.get_dummies(X_processed, columns=['Pclass'], drop_first=True)
    else:
        # Baseline: One-hot encode both Embarked and Pclass
        X_processed = pd.get_dummies(X_processed, columns=['Embarked', 'Pclass'], drop_first=True)

    # --- Model Training and Evaluation ---

    # Train-validation split
    X_train_model, X_val_model, y_train_model, y_val_model = train_test_split(
        X_processed, y_train_full, test_size=0.2, random_state=42
    )

    # Initialize and train XGBoost Classifier
    # use_label_encoder=False and eval_metric='logloss' retained for consistency with original solution
    model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    model.fit(X_train_model, y_train_model)

    # Make predictions on the validation set
    y_pred_val = model.predict(X_val_model)

    # Evaluate model using accuracy
    accuracy = accuracy_score(y_val_model, y_pred_val)
    return accuracy

# --- Main execution for ablation study ---

# 1. Run Baseline Experiment
baseline_accuracy = run_ablation_experiment(ablation_type=None)
print(f"Baseline Performance (Original Solution): {baseline_accuracy:.4f}")

# 2. Ablation: Age Mean Imputation (instead of Median)
age_mean_accuracy = run_ablation_experiment(ablation_type='age_mean_imputation')
print(f"Ablation (Age: Mean Imputation vs. Median): {age_mean_accuracy:.4f}")

# 3. Ablation: Embarked Label Encoding (instead of One-Hot)
embarked_le_accuracy = run_ablation_experiment(ablation_type='embarked_label_encode')
print(f"Ablation (Embarked: Label Encoding vs. One-Hot Encoding): {embarked_le_accuracy:.4f}")

print("\n--- Ablation Study Summary ---")

# Calculate performance changes relative to baseline
diff_age = age_mean_accuracy - baseline_accuracy
diff_embarked = embarked_le_accuracy - baseline_accuracy

if abs(diff_age) > abs(diff_embarked):
    most_impactful_part = "Age imputation method"
    impact_description = f"Changing 'Age' imputation from median to mean resulted in a performance {'increase' if diff_age > 0 else 'decrease'} of {abs(diff_age):.4f}."
elif abs(diff_embarked) > abs(diff_age):
    most_impactful_part = "Embarked encoding method"
    impact_description = f"Changing 'Embarked' encoding from one-hot to label encoding resulted in a performance {'increase' if diff_embarked > 0 else 'decrease'} of {abs(diff_embarked):.4f}."
else:
    most_impactful_part = "Both ablations had a similar magnitude of impact."
    impact_description = "The impact was either very small or comparable between the two modifications."

print(f"Based on these ablations, the '{most_impactful_part}' contributes the most to the model's overall performance among the tested modifications.")
print(impact_description)
