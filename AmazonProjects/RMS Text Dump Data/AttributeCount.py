

import os
import glob
import json

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Find the file starting with "masterpolicydata"
pattern = os.path.join(script_dir, "masterpolicydata*")
matching_files = glob.glob(pattern)

if not matching_files:
    print("No file starting with 'masterpolicydata' found.")
    exit()

input_file = matching_files[0]
print(f"Reading: {input_file}")

# Load JSON data
with open(input_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Fields to extract directly
key_fields = ["Serial_Number", "DOMAIN_Name", "STACK", "REGULATION", "RULE"]

# Fields to EXCLUDE from attribute detection (these are metadata/output fields, not attributes)
exclude_fields = set(key_fields + [
    "RULE_OUTPUT", "POLICY_TEXT", "ATTRIBUTES_USED", "ORDER_OF_ATTRIBUTES",
    "LINE_COUNT", "CHAR_COUNT", "DownloadDate"
])

output = []

for item in data:
    base_record = {field: item.get(field, "") for field in key_fields}

    for key, value in item.items():
        # Skip key fields, metadata fields, and domain output fields
        if key in exclude_fields:
            continue

        # An attribute is "used" if its value is non-null and non-empty
        if value is not None and value != "" and value!= "ALLOW_ALL":
            record = base_record.copy()
            record["Attributes"] = key
            output.append(record)

# Save output
output_file = os.path.join(script_dir, "attributes_count.json")
with open(output_file, 'w') as f:
    json.dump(output, f, indent=4)

print(f"Done! {len(output)} rows written to: {output_file}")