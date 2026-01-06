import pandas as pd
import json
from datetime import datetime
import os
import glob

def versionjsontopolicy(file_path):
    try:
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'utf-16', 'cp1252']
        data = None

        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    data = json.load(file)
                    data = data.get('ruleSet', '')
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

        domain_name = data.get('domain', {}).get('name', '')
        version_name = data.get('name', '')
        version_id = data.get('id', '')
        version_number = str(data.get('version', {}).get('major', ''))
        minor_version = str(data.get('version', {}).get('minor', ''))
        version_status = data.get('status', '')
        region = data.get('region', '')
        version_set_link = f"https://rms.aft.amazon.dev/domain/{domain_name}/rule-sets/{version_id}?majorVersion={version_number}&minorVersion={minor_version}"
        last_update_timestamp = data.get('audit', {}).get('lastUpdatedOn', 0)
        if last_update_timestamp:
            last_update_date = datetime.fromtimestamp(last_update_timestamp).strftime('%d-%b-%Y %H:%M')
        else:
            last_update_date = "No timestamp available"
        result_data = []

        for rule in data.get('regulations', []):
            policy_id = rule.get('id', '')
            policy_version = str(rule.get('version', {}).get('major', ''))
            policy_minor_version = str(rule.get('version', {}).get('minor', ''))
            policy_link = f"https://rms.aft.amazon.dev/regulation/{policy_id}?majorVersion={policy_version}&minorVersion={policy_minor_version}"
            policy_status = rule.get('ruleSetRegulationStatus', '')

            rule_dict = {
                'Domain Name': domain_name.upper(),
                'Region': region,
                'Version Set Name': version_name,
                'Version Set ID': version_id,
                'Version Set Link': version_set_link,
                'Version Set Number': version_number,
                'Version Status': version_status,
                'Version Last Updated Date': last_update_date,
                'Policy Name': rule.get('name', '').strip(),
                'Policy Id': policy_id,
                'Policy Major Version': policy_version,
                'Policy Minor Version': policy_minor_version,
                'Policy Status': policy_status,
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

    # Process the file and add its data to the combined list
    file_data = versionjsontopolicy(input_file)
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
