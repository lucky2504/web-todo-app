
import json
import glob
from datetime import datetime

# Columns to keep in the output files
COLUMNS_TO_KEEP = [
    "Serial_Number",
    "DOMAIN_Name",
    "STACK",
    "REGULATION",
    "RULE",
    "RULE_OUTPUT",
    "POLICY_TEXT"
]

# Find JSON files containing masterpolicydata* in the name
matching_files = glob.glob('masterpolicydata*.json')
current_datetime = datetime.now().strftime('%Y%m%d%H%M')

if not matching_files:
    print("No files found matching the pattern 'masterpolicydata*.json'")
else:
    print(f"Found {len(matching_files)} matching file(s):")

    # Use the first matching file
    input_file = matching_files[0]
    print(f"Reading data from: {input_file}")

    # Read the JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} records from the file")

    # Get all unique DOMAIN combinations
    unique_combinations = set()
    for record in data:
        domain = record.get('DOMAIN_Name', 'UNKNOWN')
        unique_combinations.add(domain)

    print(f"Found {len(unique_combinations)} unique DOMAIN combinations: ")

    for domain in sorted(unique_combinations):
        # Filter records for this domain and keep only selected columns
        domain_records = [
            {key: record.get(key) for key in COLUMNS_TO_KEEP}
            for record in data if record.get('DOMAIN_Name') == domain
        ]

        output_file = f"{current_datetime}_{domain}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(domain_records, f, indent=4)

        print(f"Saved {len(domain_records)} {domain} records to: {output_file}")

