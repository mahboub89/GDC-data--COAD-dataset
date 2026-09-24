import requests
import json
import pandas as pd
# 1. Optional: Inspect GDC Diagnosis Dictionary Schema
base_url = "https://api.gdc.cancer.gov"
url = base_url + "/v0/submission/_dictionary/diagnosis"
response = requests.get(url)
print(response.status_code)
diagnosis_dict = response.json()
print(diagnosis_dict.keys())
print(diagnosis_dict["properties"].keys())
# 2. Request Extended Clinical & Pathological Fields
fields = [
    "submitter_id",
    "diagnoses.age_at_diagnosis",
    "diagnoses.ajcc_pathologic_stage",
    "diagnoses.ajcc_pathologic_t",
    "diagnoses.ajcc_pathologic_n",
    "diagnoses.ajcc_pathologic_m",
    "diagnoses.tumor_grade",
    "diagnoses.primary_diagnosis",
    "diagnoses.morphology",
    "diagnoses.tumor_focality",
    "diagnoses.tumor_depth",
    "diagnoses.metastasis_at_diagnosis",
    "diagnoses.prior_malignancy",
    "diagnoses.prior_treatment",
    "diagnoses.residual_disease",
    "diagnoses.margin_distance",
    "diagnoses.margins_involved_site",
    "diagnoses.tumor_regression_grade"
]

params = {
    "filters": json.dumps(filters),
    "fields": ",".join(fields),
    "format": "JSON",
    "size": 10000
}

url = "https://api.gdc.cancer.gov/cases"
response = requests.get(url, params=params)
print(f"Extended Clinical API Status Code: {response.status_code}")

data = response.json()
clinical_candidates = pd.DataFrame(data["data"]["hits"])
clinical_candidates.head()

clinical_candidates['diagnoses'][0]
clinical_candidates["diagnoses"].apply(len).value_counts()
# 3. Flatten Nested Diagnoses JSON Data
diagnoses_df = pd.json_normalize(
    clinical_candidates["diagnoses"].apply(
        lambda x: x[0] if isinstance(x, list) and len(x) > 0 else {}
    )
)

diagnoses_df.head()

clinical_final = pd.concat(
    [
        clinical_candidates[["id", "submitter_id"]].reset_index(drop=True),
        diagnoses_df.reset_index(drop=True)
    ],
    axis=1
)

clinical_final.head()
clinical_final.info()
clinical_final['prior_treatment'].value_counts(dropna=False)
# 4. Merge with Previous Survival Dataset
df = pd.read_csv(r'first_survival_dataset.csv') #was built in first_file.py
df1 = df.merge(
    clinical_final,
    on="submitter_id",
    how="left"
)
df1.head()

df.shape
clinical_final.shape
df1.shape
df1.columns

# 5. Select Final Features & Export
list_col= ['submitter_id','age_at_diagnosis_years','stage_main','event', 'survival_days',
'ajcc_pathologic_t','ajcc_pathologic_n', 'ajcc_pathologic_m', 'prior_treatment']
data = df1[list_col]
data.head()

data.shape
data.info()
data.to_csv('clinical_survival_data.csv', index=False)
print("Final clinical and survival dataset successfully saved to 'clinical_survival_data.csv'")
