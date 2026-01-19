import pandas as pd
import json
from datetime import datetime
import os
import glob

def create_rule_analysis_df(file_path, DOMAIN, STACK, attributes, output_cols, output_strings, current_datetime):
    with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
        content = file.read()

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
        output_lines = [line for line in lines[1:6] if ' | ' in line]
        output_lines = sorted(output_lines, key=len, reverse=True)
        number_of_output_cols = len(output_lines) + 1
        line_count = len(lines) - number_of_output_cols
        rule_dict['RULE_OUTPUT'] = '; '.join(output_lines)

        rule_dict['DOMAIN_Name'] = DOMAIN
        rule_dict['STACK'] = STACK
        rule_dict['RULE'] = lines[0].rsplit('_', 1)[0].strip()
        rule_dict['LINE_COUNT'] = str(line_count)
        rule_dict['DownloadDate'] = current_datetime

        #Get rule outputs
        for out_col, out_str in zip(output_cols, output_strings):
            for line in output_lines:
                line = line.strip()
                line = line.rstrip(',')
                if out_str in line:
                    rule_dict[out_col] = line.replace(out_str,"")
                    break
                elif out_str.strip(" |").strip() in line:
                    rule_dict[out_col] = line
                    break

        policy_text = '\n'.join(lines[number_of_output_cols:])
        rule_dict['POLICY_TEXT'] = policy_text
        rule_dict['CHAR_COUNT'] = str(len(policy_text))

        attribute_order = []
        for line in lines[number_of_output_cols:]:
            line = line.strip()
            for attr in attributes:
                if attr in line:
                    attribute_order.append(attr.strip())
        rule_dict['ORDER_OF_ATTRIBUTES'] = ", ".join(attribute_order)
        rule_dict['ATTRIBUTES_USED'] = ', '.join(dict.fromkeys(attribute_order))


        for attr in attributes:
            attr_value = []
            for line in lines[number_of_output_cols:]:
                line = line.strip()
                if attr in line:
                    attr_value.append(line.replace(attr, ""))
            attribute_value = ' \n'.join(attr_value)
            rule_dict[attr.strip()] = attribute_value

        data.append(rule_dict)

    df = pd.DataFrame(data)
    return df

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

current_datetime = datetime.now().strftime('%Y%m%d%H%M')

output_cols = ['BOX_boxClass', 'BOX_minHeight', 'BOX_minLength', 'BOX_minWidth', 'REMOVAL_donationEligible', 'REMOVAL_donationReason', 'LABELING_batteryStatements', 'LABELING_unidStatements', 'LABELING_palletLabels', 'LABELING_packLabels', 'MESSAGING_messageIds', 'RETURNS_returnClass', 'RETURNS_returnClasses', 'SHIPOPTION_shipOptions', 'SHIPOPTION_restrictionAction', 'STORAGE_dropZone', 'STORAGE_storageLevel', 'STORAGE_storageClass', 'STORAGE_designatedQuantity', 'TRANSPORTATION_mode', 'TRANSPORTATION_shipMethodGroup', 'TRANSPORTATION_destination', 'TRANSPORTATION_tags', 'WASTE_wasteCategories', 'WASTE_wasteCategoryType', 'WASTE_wasteType', 'WASTE_wasteStorageClass', 'WASTEPROFILE_wasteProfiles']
output_strings = [ ' boxClass |',  ' minHeight |',  ' minLength |',  ' minWidth |',  ' donationEligible |',  ' donationReason |',  ' batteryStatements |',  ' unidStatements |',  ' palletLabels |',  ' packLabels |',  ' messageIds |',  ' returnClass |',  ' returnClasses |',  ' shipOptions |',  ' restrictionAction |',  ' dropZone |',  ' storageLevel |',  ' storageClass |',  ' designatedQuantity |',  ' mode |',  ' shipMethodGroup |',   ' destination |',   ' tags |',  ' wasteCategories |',  ' wasteCategoryType |',  ' wasteType |',  ' wasteStorageClass |',  ' wasteProfiles |']
attributes = ['addressTypes ', 'alcoholContent ', 'asinStatus ', 'batteryCellComposition ', 'batteryWeight ', 'blockedWasteCategories ', 'checkDistributionType ', 'containsFoodOrBeverage ', 'containsLiquidContents ', 'country ', 'customerRestrictionType ', 'batteryCellCount ', 'batteryCount ', 'customerReturn ', 'deliveryProgram ', 'destinationCountry ', 'destinationPostalCode ', 'distributionType ', 'domain ', 'eu2008LabelingHazard ', 'eu2008LabelingPrecautionary ', 'eu2008LabelingRisk ', 'eu2008LabelingSafety ', 'expirationDatedProduct ', 'expired ', 'fba ', 'fcStorageMethod ', 'flashpoint ', 'floorRecommendation ', 'fuelType ', 'fulfillmentManagerId ', 'fulfillmentShipmentId ', 'ghsClassificationClass ', 'ghsStatement ', 'ghsStatements ', 'glProductGroup ', 'hazmat ', 'hazmatException ', 'hazmatProperShippingName ', 'hazmatRegulatoryPackingGroup ', 'hazmatTransportationRegulatoryClass ', 'hazmatTransportationRegulatorySubsidiaryClass ', 'hazmatType ', 'hazmatUnitedNationsRegulatoryId ', 'invalidOrTombstonedAsin ', 'inventoryCondition ', 'iog ', 'itemHazmatVolume ', 'itemHazmatWieght ', 'itemName ', 'itemPackageWeight ', 'itemWeight ', 'liquidContentsDescription ', 'liquidDoubleSealed ', 'liquidPackagingType ', 'liquidVolume ', 'lithiumBatteryEnergyContent ', 'lithiumBatteryPackaging ', 'lithiumBatteryVoltage ', 'lithiumBatteryWeight ', 'lithiumIonBatteryCount ', 'lithiumMetalBatteryCount ', 'manufactureOnDemandId ', 'maqHardCapacityBreach ', 'maqSoftCapacityBreach ', 'marketplaceId ', 'medicineClassification ', 'memoryPresent ', 'originCountry ', 'originPostalCode ', 'packageLevel ', 'packageWeight ', 'packingInstruction ', 'permitted ', 'permittedModes ', 'phValue ', 'productComplianceApproved ', 'podRecommendation ', 'powerSourceType ', 'productCategory ', 'productSubCategory ', 'productType ', 'programParticipation ', 'productExpirationType ', 'quantity ', 'quarantined ', 'rablIds ', 'recommendedBrowseNodes ', 'regulatedSiocOverride ', 'restrictedDestinations ', 'restrictedProductClass ', 'sellerId ', 'sellerOptedIn ', 'shipperDangerousGoodsEnabled ', 'shipperTrustLevel ', 'shipperTrustScore ', 'shippingPrograms ', 'shipWithAmazon ', 'siocCapable ', 'siteId ', 'sponsoredListingCategoryId ', 'state ', 'stateOfMatter ', 'storageClass ', 'storageClasses ', 'storageClassVolumes ', 'storagePermitted ', 'temperatureRating ', 'title ', 'utcClassification ', 'warehouseProcess ', 'wasteBusinessProgram ', 'wasteCategories ', 'wasteCategoryType ', 'websiteRejected ', 'websiteShippingWeight ']

# Process each file
for input_file in all_txt_files:
    print(f"\nProcessing file: {input_file}")

    # Process the file and add its data to the combined list
    file_path = os.path.join(script_dir, input_file)

    # Extract filename and domain information
    filename = input_file.split('.')[0]
    DOMAIN = filename.split('_')[0]
    STACK = filename.split('_')[1]
    DownloadDate = current_datetime
    df = create_rule_analysis_df(file_path, DOMAIN, STACK, attributes, output_cols, output_strings, current_datetime)

    # Defining the column order
    base_columns = ['DOMAIN_Name', 'STACK', 'RULE', 'RULE_OUTPUT', 'POLICY_TEXT', 'ATTRIBUTES_USED', 'ORDER_OF_ATTRIBUTES', 'LINE_COUNT', 'CHAR_COUNT', 'DownloadDate']

    # Create final column order list
    final_column_order = ['Serial_Number'] + base_columns + output_cols + [attr.strip() for attr in attributes]

    # Ensure all columns exist in the DataFrame
    for col in final_column_order:
        if col not in df.columns:
            df[col] = None  # or '' for empty string

    # Sort DataFrame by RULE column and reorder columns
    df_sorted = df.sort_values('RULE')[final_column_order]
    all_policy_data.extend(df_sorted.to_dict('records'))

# Sort all combined data
all_policy_data = sorted(all_policy_data,
                        key=lambda x: (x['DOMAIN_Name'],
                                      x['STACK'],
                                      x['RULE'],
                                      x['POLICY_TEXT'],
                                      x['RULE_OUTPUT']))

# Add Serial Number column with reset per unique DOMAIN_STACK_RULE
current_key = None
counter = 0

for record in all_policy_data:
    # Create unique key for DOMAIN_STACK_RULE combination
    key = f"{record['DOMAIN_Name']}_{record['STACK']}_{record['RULE']}"

    # Reset counter when we encounter a new DOMAIN_STACK_RULE combination
    if key != current_key:
        current_key = key
        counter = 1
    else:
        counter += 1

    # Add serial number to the record
    record['Serial_Number'] = f"{key}_{counter:05d}"

# Create output filename with full path
output_filename = os.path.join(script_dir, f'masterpolicydata_{current_datetime}.json')

# Create output filename with full path
output_filename = os.path.join(script_dir, f'masterpolicydata_{current_datetime}.json')

# Write combined JSON file
try:
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(all_policy_data, f, indent=4, ensure_ascii=False)
    print(f"\nProcessing complete. Combined data saved as: {output_filename}")
    print(f"Total number of files processed: {len(all_txt_files)}")
    print(f"Total number of policies: {len(all_policy_data)}")
except Exception as e:
    print(f"\nError writing output file: {e}")
