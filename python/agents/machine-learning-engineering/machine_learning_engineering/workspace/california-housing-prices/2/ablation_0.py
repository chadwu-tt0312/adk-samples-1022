
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.impute import SimpleImputer
import os
import sys

def run_ablation_experiment(experiment_name, skip_feature_engineering=False, skip_initial_imputation=False):
    print(f"\n--- Running Experiment: {experiment_name} ---")

    train_file = "./input/train.csv"

    try:
        train_df = pd.read_csv(train_file)
    except FileNotFoundError:
        print(f"Error: Ensure '{train_file}' exists in the './input' directory for ablation study.")
        return None

    X = train_df.drop("median_house_value", axis=1)
    y = train_df["median_house_value"]

    # Make a copy to avoid modifying the original X for subsequent experiments
    X_processed = X.copy()

    # Initial Imputation for 'total_bedrooms'
    if 'total_bedrooms' in X_processed.columns: # Check if column exists before trying to impute
        if not skip_initial_imputation:
            imputer = SimpleImputer(strategy="median")
            X_processed['total_bedrooms'] = imputer.fit_transform(X_processed[['total_bedrooms']])
        else:
            print("Skipping initial specific imputation for 'total_bedrooms'.")

    # Feature Engineering
    if not skip_feature_engineering:
        print("Applying Feature Engineering.")
        # Ensure 'households' and 'total_rooms' exist before creating derived features
        # And handle division by zero by replacing 0 with 1
        X_processed['households_safe'] = X_processed['households'].replace(0, 1) if 'households' in X_processed.columns else 1
        X_processed['total_rooms_safe'] = X_processed['total_rooms'].replace(0, 1) if 'total_rooms' in X_processed.columns else 1

        if 'total_rooms' in X_processed.columns and 'households_safe' in X_processed.columns:
            X_processed['rooms_per_household'] = X_processed['total_rooms'] / X_processed['households_safe']
        if 'total_bedrooms' in X_processed.columns and 'total_rooms_safe' in X_processed.columns:
            X_processed['bedrooms_per_room'] = X_processed['total_bedrooms'] / X_processed['total_rooms_safe']
        if 'population' in X_processed.columns and 'households_safe' in X_processed.columns:
            X_processed['population_per_household'] = X_processed['population'] / X_processed['households_safe']

        X_processed = X_processed.drop(columns=['households_safe', 'total_rooms_safe'], errors='ignore')
    else:
        print("Skipping Feature Engineering.")

    # After feature engineering (or if skipped), there might be NaNs or infs.
    # Replace inf/-inf with NaN
    X_processed.replace([np.inf, -np.inf], np.nan, inplace=True)
    
    # General Imputation for any remaining NaN values in all columns
    print("Applying general imputation for any remaining NaNs to ensure model compatibility.")
    nan_cols = X_processed.columns[X_processed.isnull().any()].tolist()
    if nan_cols:
        imputer_general = SimpleImputer(strategy="median")
        X_processed[nan_cols] = imputer_general.fit_transform(X_processed[nan_cols])

    # Split training data for validation
    X_train, X_val, y_train, y_val = train_test_split(X_processed, y, test_size=0.2, random_state=42)

    # Initialize and train the model
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    # Evaluation
    y_pred_val = model.predict(X_val)
    rmse = np.sqrt(mean_squared_error(y_val, y_pred_val))

    print(f"Validation Performance ({experiment_name}): RMSE = {rmse:.4f}")
    return rmse

def main_ablation():
    results = {}

    # 0. Baseline Experiment (Original script's logic on train/val)
    results['Baseline'] = run_ablation_experiment('Baseline',
                                                  skip_feature_engineering=False,
                                                  skip_initial_imputation=False)

    # 1. Ablation: No Feature Engineering
    results['No Feature Engineering'] = run_ablation_experiment('No Feature Engineering',
                                                                skip_feature_engineering=True,
                                                                skip_initial_imputation=False)

    # 2. Ablation: No specific 'total_bedrooms' imputation (relying on general imputation if NaNs persist)
    results['No Initial total_bedrooms Imputation'] = run_ablation_experiment('No Initial total_bedrooms Imputation',
                                                                              skip_feature_engineering=False,
                                                                              skip_initial_imputation=True)

    print("\n--- Ablation Study Results ---")
    baseline_rmse = results.get('Baseline')

    for name, rmse in results.items():
        if rmse is not None:
            print(f"{name}: RMSE = {rmse:.4f}")

    if baseline_rmse is not None:
        print("\n--- Contribution Analysis ---")
        contributions = {}
        
        # Calculate impact of removing Feature Engineering
        if 'No Feature Engineering' in results and results['No Feature Engineering'] is not None:
            # If RMSE increases when FE is removed, FE was beneficial.
            impact_fe = results['No Feature Engineering'] - baseline_rmse
            if impact_fe > 0:
                contributions['Feature Engineering'] = impact_fe
                print(f"Removing Feature Engineering worsened performance by {impact_fe:.4f} RMSE (larger RMSE). "
                      "This suggests Feature Engineering contributes positively.")
            elif impact_fe < 0:
                print(f"Removing Feature Engineering improved performance by {-impact_fe:.4f} RMSE (smaller RMSE). "
                      "This suggests Feature Engineering might not be optimal or adds noise.")
            else:
                print("Removing Feature Engineering had no significant impact on performance.")

        # Calculate impact of removing initial 'total_bedrooms' imputation
        if 'No Initial total_bedrooms Imputation' in results and results['No Initial total_bedrooms Imputation'] is not None:
            # If RMSE increases when initial imputation is removed, it was beneficial.
            impact_imputation = results['No Initial total_bedrooms Imputation'] - baseline_rmse
            if impact_imputation > 0:
                contributions['Initial total_bedrooms Imputation'] = impact_imputation
                print(f"Removing initial 'total_bedrooms' imputation worsened performance by {impact_imputation:.4f} RMSE (larger RMSE). "
                      "This suggests initial 'total_bedrooms' imputation contributes positively.")
            elif impact_imputation < 0:
                print(f"Removing initial 'total_bedrooms' imputation improved performance by {-impact_imputation:.4f} RMSE (smaller RMSE). "
                      "This suggests initial 'total_bedrooms' imputation might not be optimal or the general imputation was sufficient.")
            else:
                print("Removing initial 'total_bedrooms' imputation had no significant impact on performance.")
        
        if contributions:
            # Find the component whose removal caused the largest increase in RMSE (i.e., the most positive contribution)
            most_contributing_part = max(contributions, key=contributions.get)
            if contributions[most_contributing_part] > 0:
                print(f"\nBased on this ablation study, the part of the code that contributes the most to the overall performance is: "
                      f"'{most_contributing_part}', as its removal led to the largest degradation in RMSE (an increase of {contributions[most_contributing_part]:.4f}).")
            else:
                print("\nBased on this ablation study, no single ablated part showed a clear positive contribution, or their removal led to improvements.")
        else:
            print("\nUnable to determine the most contributing part from the ablation results.")
    else:
        print("\nBaseline RMSE could not be established, preventing contribution analysis.")

if __name__ == "__main__":
    main_ablation()
