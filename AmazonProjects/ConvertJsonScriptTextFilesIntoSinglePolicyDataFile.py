import pandas as pd
import json
from datetime import datetime
import os
import glob


def get_region_from_filename(filename):
    try:
        name_without_extension = os.path.splitext(filename)[0]
        return name_without_extension.split('_')[1]
    except IndexError:
        return None


def versionjsontopolicy(file_path, region):
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'utf-16', 'cp1252']
        data = None

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    data = json.load(file)
                print(f"Successfully read file with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
            except json.JSONDecodeError as e:
                print(f"JSON decode error with {encoding} encoding: {e}")
                continue

        if data is None:
            print(f"Could not read file {file_path} with any encoding")
            return []

        domain_name = data.get('policyType', '')
        version_name = data.get('name', '')
        version_id = data.get('id', '')
        version_number = str(data.get('version', ''))
        version_status = data.get('status', '')

        version_set_link = f"https://decree.aka.amazon.com/set/{domain_name}/{version_id}/{version_number}?domain={domain_name}"

        result_data = []

        for rule in data.get('rules', []):
            policy_id = rule.get('policyId', '')
            policy_version = str(rule.get('policyVersion', ''))

            policy_link = f"https://decree.aka.amazon.com/policy/{policy_id}/{policy_version}/edit?view={policy_version}&domain={domain_name}"

            rule_dict = {
                'Domain Name': domain_name,
                'Region': region,
                'Version Set Name': version_name,
                'Version Set ID': version_id,
                'Version Set Link': version_set_link,
                'Version Set Number': version_number,
                'Version Status': version_status,
                'Policy Name': rule.get('metricName', ''),
                'Policy Id': policy_id,
                'Policy Version': policy_version,
                'Policy Predicate': json.dumps(rule.get('predicate', {}), ensure_ascii=False),
                'Policy Rule Action': json.dumps(rule.get('ruleAction', {}), ensure_ascii=False),
                'Policy Rule Priority': str(rule.get('ruleAction', {}).get('priority', '')),
                'Policy Link': policy_link,
            }
            result_data.append(rule_dict)

        return result_data

    except Exception as e:
        print(f"An error occurred with file {file_path}: {e}")
        return []


# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Change to the script directory
os.chdir(script_dir)

# Get all .txt files in the directory
all_txt_files = glob.glob("*.txt")

if not all_txt_files:
    print("No .txt files found in the directory")
    exit(1)

# Combined data from all files
all_policy_data = []

# Process each file
for input_file in all_txt_files:
    print(f"\nProcessing file: {input_file}")

    # Extract region from filename
    region = get_region_from_filename(input_file)
    if not region:
        print(f"Could not extract region from filename: {input_file}")
        continue

    # Process the file and add its data to the combined list
    file_data = versionjsontopolicy(input_file, region)
    all_policy_data.extend(file_data)

# Sort all combined data
all_policy_data = sorted(all_policy_data, key=lambda x: x['Policy Name'])
all_policy_data = sorted(all_policy_data, key=lambda x: x['Region'])
all_policy_data = sorted(all_policy_data, key=lambda x: x['Domain Name'])

# Get current datetime
current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')

# Create output filename with full path
output_filename = os.path.join(script_dir, f'version_policy_json_{current_datetime}.json')

# Write combined JSON file
try:
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(all_policy_data, f, indent=4, ensure_ascii=False)
    print(f"\nProcessing complete. Combined data saved as: {output_filename}")
    print(f"Total number of files processed: {len(all_txt_files)}")
    print(f"Total number of policies: {len(all_policy_data)}")
except Exception as e:
    print(f"\nError writing output file: {e}")
