
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Load the Titanic dataset
train_df_original = pd.read_csv('./input/train.csv')

# --- Original Solution Run ---
df_base = train_df_original.copy()
df_base.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1, inplace=True)
df_base['Age'].fillna(df_base['Age'].median(), inplace=True)
df_base['Embarked'].fillna(df_base['Embarked'].mode()[0], inplace=True)
df_base['Sex'] = df_base['Sex'].map({'male': 0, 'female': 1})
df_base = pd.get_dummies(df_base, columns=['Embarked', 'Pclass'], drop_first=True)

X_base = df_base.drop('Survived', axis=1)
y_base = df_base['Survived']

X_train_base, X_val_base, y_train_base, y_val_base = train_test_split(X_base, y_base, test_size=0.2, random_state=42)

xgb_clf_base = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)
xgb_clf_base.fit(X_train_base, y_train_base)
y_pred_base = xgb_clf_base.predict(X_val_base)
accuracy_base = accuracy_score(y_val_base, y_pred_base)
print(f"Original Model Final Validation Performance: {accuracy_base:.4f}")

# --- Ablation 1: Remove drop_first=True for one-hot encoding ---
df_ablation1 = train_df_original.copy()
df_ablation1.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1, inplace=True)
df_ablation1['Age'].fillna(df_ablation1['Age'].median(), inplace=True)
df_ablation1['Embarked'].fillna(df_ablation1['Embarked'].mode()[0], inplace=True)
df_ablation1['Sex'] = df_ablation1['Sex'].map({'male': 0, 'female': 1})
# Modified line: drop_first=False (or omit, as default is False)
df_ablation1 = pd.get_dummies(df_ablation1, columns=['Embarked', 'Pclass'], drop_first=False)

X_ablation1 = df_ablation1.drop('Survived', axis=1)
y_ablation1 = df_ablation1['Survived']

X_train_ablation1, X_val_ablation1, y_train_ablation1, y_val_ablation1 = train_test_split(X_ablation1, y_ablation1, test_size=0.2, random_state=42)

xgb_clf_ablation1 = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)
xgb_clf_ablation1.fit(X_train_ablation1, y_train_ablation1)
y_pred_ablation1 = xgb_clf_ablation1.predict(X_val_ablation1)
accuracy_ablation1 = accuracy_score(y_val_ablation1, y_pred_ablation1)
print(f"Ablation 1 (no drop_first=True for One-Hot Encoding) Final Validation Performance: {accuracy_ablation1:.4f}")

# --- Ablation 2: Impute 'Age' with mean instead of median ---
df_ablation2 = train_df_original.copy()
df_ablation2.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1, inplace=True)
# Modified line: Fill missing Age values with the mean
df_ablation2['Age'].fillna(df_ablation2['Age'].mean(), inplace=True)
df_ablation2['Embarked'].fillna(df_ablation2['Embarked'].mode()[0], inplace=True)
df_ablation2['Sex'] = df_ablation2['Sex'].map({'male': 0, 'female': 1})
df_ablation2 = pd.get_dummies(df_ablation2, columns=['Embarked', 'Pclass'], drop_first=True)

X_ablation2 = df_ablation2.drop('Survived', axis=1)
y_ablation2 = df_ablation2['Survived']

X_train_ablation2, X_val_ablation2, y_train_ablation2, y_val_ablation2 = train_test_split(X_ablation2, y_ablation2, test_size=0.2, random_state=42)

xgb_clf_ablation2 = xgb.XGBClassifier(objective='binary:logistic', eval_metric='logloss', use_label_encoder=False, random_state=42)
xgb_clf_ablation2.fit(X_train_ablation2, y_train_ablation2)
y_pred_ablation2 = xgb_clf_ablation2.predict(X_val_ablation2)
accuracy_ablation2 = accuracy_score(y_val_ablation2, y_pred_ablation2)
print(f"Ablation 2 (Age mean imputation) Final Validation Performance: {accuracy_ablation2:.4f}")

# --- Conclusion on contributions ---
impact_drop_first = accuracy_base - accuracy_ablation1 # Positive if original `drop_first=True` was better
impact_age_imputation = accuracy_base - accuracy_ablation2 # Positive if original median imputation was better

if impact_drop_first > 0 and impact_age_imputation > 0:
    if impact_drop_first > impact_age_imputation:
        print("\nBased on this ablation study, the use of `drop_first=True` in one-hot encoding contributes most to the overall performance, as its removal caused the largest performance drop.")
    elif impact_age_imputation > impact_drop_first:
        print("\nBased on this ablation study, the use of median imputation for 'Age' contributes most to the overall performance, as changing it to mean imputation caused the largest performance drop.")
    else:
        print("\nBased on this ablation study, both `drop_first=True` in one-hot encoding and median imputation for 'Age' contribute similarly to the overall performance.")
elif impact_drop_first < 0 and impact_age_imputation < 0:
    if abs(impact_drop_first) > abs(impact_age_imputation):
        print("\nBased on this ablation study, the original choice of `drop_first=True` for one-hot encoding was less optimal, as removing it improved performance more than the other ablation.")
    elif abs(impact_age_imputation) > abs(impact_drop_first):
        print("\nBased on this ablation study, the original choice of median imputation for 'Age' was less optimal, as changing it to mean imputation improved performance more than the other ablation.")
    else:
        print("\nBased on this ablation study, both original choices for `drop_first=True` and 'Age' imputation were similarly less optimal, as their alternatives improved performance similarly.")
elif impact_drop_first > 0 and impact_age_imputation < 0:
    if impact_drop_first > abs(impact_age_imputation):
        print("\nBased on this ablation study, the use of `drop_first=True` in one-hot encoding contributes most to the overall performance.")
    else:
        print("\nBased on this ablation study, the original choice for 'Age' imputation was less optimal, leading to a performance gain when changed, which was a larger impact than the positive contribution of `drop_first=True`.")
elif impact_drop_first < 0 and impact_age_imputation > 0:
    if abs(impact_drop_first) > impact_age_imputation:
        print("\nBased on this ablation study, the original choice for `drop_first=True` in one-hot encoding was less optimal, leading to a performance gain when changed, which was a larger impact than the positive contribution of median 'Age' imputation.")
    else:
        print("\nBased on this ablation study, the use of median imputation for 'Age' contributes most to the overall performance.")
else: # One or both had 0 impact
    print("\nBased on this ablation study, neither of the ablated parts showed a significant discernible contribution to the overall performance in this specific context.")
