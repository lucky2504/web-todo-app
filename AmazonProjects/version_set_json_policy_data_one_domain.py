import pandas as pd
import json
from datetime import datetime
import os


def get_region_from_filename(filename):
    try:
        name_without_extension = os.path.splitext(filename)[0]
        return name_without_extension.split('_')[1]
    except IndexError:
        return None


def versionjsontopolicy(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)

        domain_name = data.get('policyType', '')
        version_name = data.get('name', '')
        version_id = data.get('id', '')
        version_number = str(data.get('version', ''))
        version_status = data.get('status', '')

        # Simple string concatenation for URLs without escape characters
        version_set_link = f"https://decree.aka.amazon.com/set/{domain_name}/{version_id}/{version_number}?domain={domain_name}"

        result_data = []

        for rule in data.get('rules', []):
            policy_id = rule.get('policyId', '')
            policy_version = str(rule.get('policyVersion', ''))

            # Simple string concatenation for policy link
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

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


# Input file name
input_file = "TRANSPORTATION_NA.txt"

# Extract region from input filename
region = get_region_from_filename(input_file)
if not region:
    print("Could not extract region from filename")
    exit(1)

# Process the data
policy_text_data = versionjsontopolicy(input_file)
policy_text_data = sorted(policy_text_data, key=lambda x: x['Policy Name'])

# Get current datetime
current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')

# Create output filename
output_filename = f'version_policy_json_{current_datetime}.json'

# Generate JSON file with modified parameters
df_policy = pd.DataFrame(policy_text_data)
df_policy.to_json(
    output_filename,
    orient='records',
    indent=4,
    force_ascii=False  # This prevents escape characters
)

print(f"File saved as: {output_filename}")
