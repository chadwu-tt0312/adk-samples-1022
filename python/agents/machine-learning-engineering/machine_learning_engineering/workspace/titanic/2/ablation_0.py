
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load data from the specified input directory
train_df_original = pd.read_csv('./input/train.csv')

# --- Function to run a specific configuration and return accuracy ---
def run_configuration(df, skip_age_fare_imputation=False, n_estimators_val=None):
    y = df['Survived']
    X = df.drop('Survived', axis=1)

    X_processed = X.copy()

    # Preprocessing steps
    if not skip_age_fare_imputation:
        X_processed['Age'].fillna(X_processed['Age'].median(), inplace=True)
        X_processed['Fare'].fillna(X_processed['Fare'].median(), inplace=True)
    
    X_processed['Embarked'].fillna(X_processed['Embarked'].mode()[0], inplace=True)
    X_processed['Sex'] = X_processed['Sex'].map({'male': 0, 'female': 1})
    X_processed = pd.get_dummies(X_processed, columns=['Embarked', 'Pclass'], drop_first=True)
    X_processed.drop(['Name', 'Ticket', 'Cabin', 'PassengerId'], axis=1, inplace=True)

    X_train, X_val, y_train, y_val = train_test_split(X_processed, y, test_size=0.2, random_state=42)

    # Initialize XGBoost Classifier with specified n_estimators or default
    model_params = {
        'objective': 'binary:logistic',
        'eval_metric': 'logloss',
        'use_label_encoder': False,
        'random_state': 42
    }
    if n_estimators_val is not None:
        model_params['n_estimators'] = n_estimators_val
    
    model = xgb.XGBClassifier(**model_params)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_val)
    accuracy = accuracy_score(y_val, y_pred)
    return accuracy

# --- Baseline Run ---
baseline_accuracy = run_configuration(train_df_original.copy())
print(f'Baseline Performance: {baseline_accuracy:.4f}')

# --- Ablation 1: Skip Age and Fare Imputation ---
ablation_no_imputation_accuracy = run_configuration(train_df_original.copy(), skip_age_fare_imputation=True)
print(f'Ablation (Skip Age/Fare Imputation) Performance: {ablation_no_imputation_accuracy:.4f}')

# --- Ablation 2: Reduce n_estimators in XGBoost (e.g., from default 100 to 10) ---
ablation_reduced_estimators_accuracy = run_configuration(train_df_original.copy(), n_estimators_val=10)
print(f'Ablation (Reduced n_estimators to 10) Performance: {ablation_reduced_estimators_accuracy:.4f}')

# --- Determine and print the most contributing part ---
performance_deltas = {
    "Age/Fare Imputation": baseline_accuracy - ablation_no_imputation_accuracy, # Positive if removal hurts
    "Number of XGBoost Estimators": baseline_accuracy - ablation_reduced_estimators_accuracy # Positive if reduction hurts
}

max_detrimental_ablation = None
max_detriment_value = -float('inf')

for k, v in performance_deltas.items():
    if v > max_detriment_value:
        max_detriment_value = v
        max_detrimental_ablation = k

if max_detriment_value > 0:
    print(f'The "{max_detrimental_ablation}" part contributes the most to the overall performance, as its removal/reduction caused the largest performance drop ({max_detriment_value:.4f}).')
elif max_detriment_value < 0:
    max_improvement_ablation = None
    max_improvement_value = 0
    for k, v in performance_deltas.items():
        if v < max_improvement_value:
            max_improvement_value = v
            max_improvement_ablation = k
    print(f'Interestingly, modifying/removing "{max_improvement_ablation}" led to the largest performance improvement ({( - max_improvement_value):.4f}). This suggests the original implementation of this part could be suboptimal.')
else:
    print('No significant change in performance was observed for the tested ablations, indicating that the ablated parts do not significantly contribute to the current model\'s performance or the changes were not impactful enough.')
