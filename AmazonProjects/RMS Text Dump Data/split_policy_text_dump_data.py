import json
import glob
from datetime import datetime
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
    with open(input_file, 'r') as f:
        data = json.load(f)

    print(f"Loaded {len(data)} records from the file")

    # Get all unique DOMAIN and STACK combinations
    unique_combinations = set()
    for record in data:
        domain = record.get('DOMAIN_Name', 'UNKNOWN')
        # stack = record.get('STACK', 'UNKNOWN')
        # unique_combinations.add((domain, stack))
        unique_combinations.add(domain)
    print(f"Found {len(unique_combinations)} unique DOMAIN combinations: ")
    # for domain, stack in sorted(unique_combinations):
    for domain in sorted(unique_combinations):
        domain_records = [record for record in data if record.get('DOMAIN_Name') == domain]

        output_file = f"{current_datetime}_{domain}.txt"
        with open(output_file, 'w') as f:
            json.dump(domain_records, f, indent=4)

        print(f"Saved {len(domain_records)} {domain} records to: {output_file}")



