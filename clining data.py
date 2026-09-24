import pandas as pd
import numpy as np
# 1. Load Data & Assess Missing Values
data = pd.read_csv(r'clinical_survival_data.csv') #built in second_file.py

missing_count = data.isna().sum()
missing_percentage = (missing_count / len(data)) * 100
missing_summary = pd.DataFrame({'Missing Count': missing_count, 
                                'Missing Percentage': missing_percentage})

sorted_missing_summary = missing_summary.sort_values(by='Missing Percentage',
                                                      ascending=False)
print("\nSorted Missing Data Summary (by Missing Percentage):")
print(sorted_missing_summary)
# 2. Inspect Categorical & Numerical Distributions
for col in data.select_dtypes(include=['object']).columns:
    print(f'\n===== {col} =====')
    print(data[col].value_counts(dropna=False))
# Review statistical distribution of continuous variables
data[['age_at_diagnosis_years', 'survival_days']].describe()
# 3. Data Sanity & Validation Checks
print('Checking for negative values in age and survival days...')
print(data[data['age_at_diagnosis_years'] <= 0])
print(data[data['survival_days'] < 0])
print("\nEvent Distribution:")
print(data['event'].value_counts(dropna=False))

pd.crosstab(
    data['event'],
    data['survival_days'].isna(),
    margins=True
)

# Check for duplicate rows
print(f"Total duplicate rows: {data.duplicated().sum()}")
# 4. Handle Missing Data & Filter Subsets
print("\nInspecting records with missing survival data:")
data.loc[
    data['survival_days'].isna(),
    [
        'submitter_id',
        'event',
        'age_at_diagnosis_years',
        'stage_main',
        'ajcc_pathologic_t',
        'ajcc_pathologic_n',
        'ajcc_pathologic_m',
        'prior_treatment'
    ]
]

survival_data = data.dropna(subset=['survival_days']).copy()
print(f"Survival data shape after dropping missing values: {survival_data.shape}")
survival_data.info()
print("\nPatients with missing main stage:")
survival_data.loc[
    survival_data['stage_main'].isna(),
    [
        'submitter_id',
        'stage_main',
        'ajcc_pathologic_t',
        'ajcc_pathologic_n',
        'ajcc_pathologic_m'
    ]
]
print("\nPatients with missing age at diagnosis:")
survival_data.loc[
    survival_data['age_at_diagnosis_years'].isna(),
    ['submitter_id', 'age_at_diagnosis_years', 'stage_main',
     'survival_days', 'event', 'prior_treatment']
]
# 5. Feature Cleaning & Summary Aggregation
survival_data['prior_treatment'] = survival_data['prior_treatment'].replace(
    'Not Reported',
    np.nan
)
survival_data['prior_treatment'].value_counts(dropna=False)
survival_data.groupby('event').agg(
    patients=('submitter_id', 'size'),
    mean_survival=('survival_days', 'mean'),
    median_survival=('survival_days', 'median')
)
# Impute missing ages with the mean/median age of the dataset
# survival_data['age_at_diagnosis_years'] = survival_data['age_at_diagnosis_years'].fillna(
#     survival_data['age_at_diagnosis_years'].mean()
# )
data['age_at_diagnosis_years'] = data['age_at_diagnosis_years'].fillna(
    data['age_at_diagnosis_years'].median()
)
# 6. Export Cleaned Dataset
# survival_data.dropna(subset=['stage_main'])
survival_data.to_csv('cleaned_clinical_survival_data.csv', index=False)
print("\nCleaned survival dataset successfully saved to 'cleaned_clinical_survival_data.csv'")

