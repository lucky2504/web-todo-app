import pandas as pd
import os
from datetime import datetime

current_datetime = datetime.now().strftime('%Y%m%d%H%M')
datetime_string = datetime.now().strftime('%Y%m%d%H%M')

# Path to the folder containing text files
folder_path = "Text Dump DATA"
keyword = input("Enter the keyword to search for: ")

# Get list of all .txt files in the folder
txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt') and keyword.lower() in f.lower()]

# Loop through each text file
for input_file in txt_files:
    # Construct full file path
    filepath = os.path.join(folder_path, input_file)

    # Extract filename and domain information
    filename = input_file.split('.')[0]
    DOMAIN = filename.split('_')[0]
    STACK = filename.split('_')[1]
    DownloadDate = datetime_string

    match DOMAIN:
        case 'TRANSPORTATION':
            output_cols = ['Output mode', 'Output smg', 'Output destination', 'Output tags']
            output_strings = [' mode |', ' smg |', ' destination |', ' tags |']
            attributes = ['OriginOrgUnit', 'OriginCountry', 'DestinationCountry', 'DestinationPostalCode', 'is_hazmat', 'hazmat_exception', 'hazmat_transportation_regulatory_class', 'hazmat_united_nations_regulatory_id', 'hazmat_regulatory_packing_group', 'packing_instruction', 'is_liquid_double_sealed', 'liquid_packaging_type', 'is_swa', 'shipper_trust_level', 'product_type', 'website_shipping_weight', 'PackageWeight', 'lithium_battery_weight', 'item_hazmat_weight', 'liquid_volume', 'item_hazmat_volume', 'medicine_classification', 'battery_cell_composition', 'battery_weight', 'contains_liquid_contents', 'customer_restriction_type', 'derived.battery_cell_count', 'derived.battery_count', 'fallback.item_weight', 'fallback.lithium_ion_battery_count', 'fallback.lithium_metal_battery_count', 'gl_product_group']
        case 'SHIPOPTION':
            output_cols = ['shipOptions','restrictionAction']
            output_strings = [' shipOptions |',' restrictionAction |']
            attributes = ['marketplace', 'rablId', 'restrictedDestinations', 'permittedModes', 'addressTypes', 'hazmat_exception', 'hazmat_united_nations_regulatory_id', 'hazmat_transportation_regulatory_class', 'fulfillmentManagerId', 'battery.lithium_metal', 'battery.lithium_ion']
        case 'BOX':
            output_cols = ['boxClass', 'minHeight','minLength','minWidth']
            output_strings = [' boxClass |',' minHeight |',' minLength |',' minWidth |']
            attributes = ['OriginOrgUnit', 'DestinationCountry', 'DestinationPostalCode', 'hazmat_exception', 'hazmat_transportation_regulatory_class', 'hazmat_united_nations_regulatory_id', 'sioc_capable', 'regulated_sioc_override', 'package_level']
        case 'RETURNS':
            output_cols = ['returnClass']
            output_strings = [' returnClass |']
            attributes = ['Country', 'OriginOrgUnit', 'marketplaceId', 'hazmat_exception', 'hazmat_proper_shipping_name', 'hazmat_transportation_regulatory_class', 'hazmat_united_nations_regulatory_id', 'gl_product_group_type', 'product_type', 'product_category', 'product_subcategory', 'power_source_type', 'restricted_product_class']
        case 'LABELING':
            output_cols = ['batteryStatements','secondaryLabels','unidStatements','palletLabels','packLabels','hazmatLabelStatementsIdentifier']
            output_strings = [' batteryStatements |',' secondaryLabels |',' unidStatements |',' palletLabels |',' packLabels |',' hazmatLabelStatementsIdentifier |']
            attributes = ['Country', 'DestinationCountry', 'hazmat_exception', 'hazmat_transportation_regulatory_class', 'hazmat_united_nations_regulatory_id', 'is_international', 'battery_cell_composition']
        case 'STORAGE':
            output_cols = ['dropZone','storageClass','storageLevel']
            output_strings = [' dropZone |',' storageClass |',' storageLevel |']
            attributes = ['org', 'Country', 'hazmat_exception', 'hazmat_regulatory_packing_group', 'hazmat_transportation_regulatory_class', 'hazmat_united_nations_regulatory_id', 'product_category', 'product_subcategory', 'product_type', 'product_type_name', 'restricted_product_class', 'state_of_matter', 'alcohol_content', 'eu2008_labeling_hazard', 'ghs_statement', 'gl_product_group', 'gl_product_group_type', 'item_hazmat_volume', 'item_hazmat_weight', 'package_level']
        case 'DONATION':
            output_cols = ['donationEligible','outputReasonAttributes']
            output_strings = [' donationEligible |',' outputReasonAttributes |']
            attributes = ['Country', 'gl_product_group_type', 'product_subcategory', 'isSellerOptedIn', 'is_fba', 'asinStatus', 'blocked_waste_category', 'check_distribution_type', 'distribution_type', 'has_memory', 'hazmat_transportation_regulatory_class', 'is_quarantined', 'Manufacture_on_demand_id', 'storageClassSet', 'website_rejected']
        case 'MESSAGING':
            output_cols = ['messageId']
            output_strings = [' messageId |']
            attributes = ['domain', 'org', 'storageRecommendation', 'maq_hard_capacity_breach', 'Domain Name', 'hazmat_exception', 'hazmat_transportation_regulatory_class', 'hazmat_united_nations_regulatory_id', 'InvalidorTombstonedASIN', 'product_compliance_approved', 'restricted_product_class', 'storageClass', 'storageClassSet', 'utc_classification', 'warehouse_process']
        case 'WASTE':
            output_cols = ['wasteCategory','wasteCategoryType','wasteType','wasteStorageClass']
            output_strings = [' wasteCategory |',' wasteCategoryType |',' wasteType |',' wasteStorageClass |']
            attributes = ['Country', 'storageClassSet', 'org', 'hazmat_transportation_regulatory_class', 'hazmat_exception', 'storageClass', 'state_of_matter', 'gl_product_group_type', 'ghs_statement']
        case 'WASTEPROFILE':
            output_cols = ['wasteProfile']
            output_strings = [' wasteProfile |']
            attributes = ['Country', 'wasteCategoryType', 'wasteCategory', 'sbrwp', 'hazmat_united_nations_regulatory_id', 'state_of_matter', 'state', 'gl_product_group_type']
        case _:
            raise ValueError(f"Unknown domain: {DOMAIN}")

    def create_rule_analysis_df(file_path, DOMAIN, STACK, attributes, output_cols, output_strings):
        with open(file_path, 'r') as file:
            content = file.read()

        number_of_output_cols = len(output_cols) + 1

        # Split content into individual rules
        rules = content.split('\nRule: ')
        if rules[0].startswith('Rule: '):
            rules[0] = rules[0][6:]  # Remove 'Rule: ' from the first rule

        data = []

        for rule in rules:
            if not rule.strip():
                continue

            rule_dict = {}
            lines = rule.strip().split('\n')
            line_count = len(lines) - number_of_output_cols

            rule_dict['DOMAIN'] = DOMAIN
            rule_dict['STACK'] = STACK
            rule_dict['RULE'] = lines[0].rsplit('_', 1)[0]
            rule_dict['LINE_COUNT'] = str(line_count)
            rule_dict['DownloadDate'] = DownloadDate

            #Get rule outputs
            outputs = []
            for out_col, out_str in zip(output_cols, output_strings):
                for line in lines[1:number_of_output_cols]:
                    line = line.strip()
                    line = line.rstrip(',')
                    if out_str in line:
                        outputs.append(out_str.strip() + " "+ line.replace(out_str,""))
                        rule_dict[out_col] = line.replace(out_str,"")
                        break
            rule_dict['RULE_OUTPUT'] = '; '.join(outputs)

            policy_text = '\n'.join(lines[number_of_output_cols:])
            rule_dict['POLICY_TEXT'] = policy_text
            rule_dict['CHAR_COUNT'] = str(len(policy_text))

            # policy_text = []
            # for line in lines[number_of_output_cols:]:
            #     line = line.strip()
            #     policy_text.append(line)
            # rule_dict['POLICY_TEXT'] = ": ".join(policy_text)
            # rule_dict['CHAR_COUNT'] = len(": ".join(policy_text))

            attribute_order = []
            for line in lines[number_of_output_cols:]:
                line = line.strip()
                for attr in attributes:
                    if attr in line:
                        attribute_order.append(attr)
            rule_dict['ORDER_OF_ATTRIBUTES'] = ", ".join(attribute_order)
            rule_dict['ATTRIBUTES_USED'] = ', '.join(dict.fromkeys(attribute_order))


            for attr in attributes:
                attr_value = []
                for line in lines[number_of_output_cols:]:
                    line = line.strip()
                    if attr in line:
                        attr_value.append(line.replace(attr, ""))
                attribute_value = "; ".join(attr_value)
                rule_dict[attr] = attribute_value

            data.append(rule_dict)

        df = pd.DataFrame(data)
        return df

    df = create_rule_analysis_df(filepath, DOMAIN, STACK, attributes, output_cols, output_strings)

    # Defining the column order
    base_columns = ['DOMAIN', 'STACK', 'RULE', 'RULE_OUTPUT', 'POLICY_TEXT', 'ATTRIBUTES_USED', 'ORDER_OF_ATTRIBUTES', 'LINE_COUNT', 'CHAR_COUNT', 'DownloadDate']

    # Create final column order list
    final_column_order = base_columns + output_cols + attributes

    # Sort DataFrame by RULE column and reorder columns
    df_sorted = df.sort_values('RULE')[final_column_order]

    # Save to JSON
    output_filename = f"policyattribute_{filename}_{DownloadDate}.json"
    json_output = df_sorted.to_json(orient='records', indent=4)

    #Write data into output file
    with open(output_filename, 'w') as f:
        f.write(json_output)
