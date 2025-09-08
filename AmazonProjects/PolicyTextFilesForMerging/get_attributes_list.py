import json
import pandas as pd

# Read the JSON file
with open('combined_output1.json', 'r') as file:
    data = json.load(file)

# Extract required columns
result = []
for item in data:
    # Split ATTRIBUTES_USED by comma and clean up whitespace
    attributes = [attr.strip() for attr in item['ATTRIBUTES_USED'].split(',')]
    policy = 1
    for attribute in attributes:
            result.append({
            'DOMAIN': item['DOMAIN'],
            'STACK': item['STACK'],
            'ATTRIBUTES_USED': attribute,
            'Policies Using': policy
    })

# Convert to DataFrame for better viewing (optional)
df = pd.DataFrame(result)

# print dataframe view
print("\nDataFrame view:")
print(df)

# Save DataFrame to Excel file
excel_filename = 'Attributes Used.xlsx'
df.to_excel(excel_filename, index=False)
print(f"\nData has been saved to {excel_filename}")