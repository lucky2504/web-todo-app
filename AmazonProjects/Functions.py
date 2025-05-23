#Functions for policy and predicate data merging
import win32com.client
import os
from itertools import product


def get_pol_pred_list(policysheet, pol_pred_column_list, pol_pred):
    # Select the sheet with "policies" data
    sheet = policysheet
    col_list = pol_pred_column_list
    po_pr = pol_pred

    # Find the last row in column A
    last_row = sheet.Cells(sheet.Rows.Count, "A").End(-4162).Row

    policy_list = []
    end_to_end_line_item_list = []
    # Process each row to build the policy_list line item
    for row in range(1, last_row + 1):
        #print(f"Processing {row}")
        policy_line = []
        end_to_end_line = []
        # Check if first column had header as policy
        if sheet.Range(f"A{row}").Value == po_pr:
            policy_row = row
            #policy string
            value = sheet.Range(f"A{row}").Value
            policy_line.append(value)

            #attr string
            value = ""
            for col in col_list:
                attr = sheet.Range(f"{col}{row}").Value

                if attr is None:
                    pass #skip empty cells
                elif attr == "Output":
                    #Output String
                    policy_line.append(attr)
                    value = value[:-2]
                elif attr != "":
                    value = value + attr + "; "
            policy_line.append(value)
        else:
            # policy string
            value = sheet.Range(f"A{row}").Value
            policy_line.append(value)

            # attr string
            value = ""
            for col in col_list:
                attr = sheet.Range(f"{col}{row}").Value
                header_attr = sheet.Range(f"{col}{policy_row}").Value

                if attr is None:
                    pass  # skip empty cells
                elif header_attr == "Output":
                    # Output String
                    policy_line.append(attr)
                    value = value[:-2]
                elif attr != "":
                    value = value + sheet.Range(f"{col}{policy_row}").Value + ": " + attr + "; "

            policy_line.append(value)
        policy_list.append(policy_line)

    return policy_list

def parse_count_string(input_string):
    # If multiple COUNT patterns (contains 'or')
    if ' or COUNT  ' in input_string:
        # Split by 'or COUNT  ' to separate multiple counts
        parts = input_string.split(' or COUNT  ')
        result = []

        # Handle first part (has 'COUNT  ' at start)
        first_part = parts[0].replace('COUNT  ', '')
        pred_parts = first_part.split(' matching ')
        result.append([pred_parts[0].strip(), pred_parts[1].strip()])

        # Handle remaining parts
        for part in parts[1:]:
            # Remove everything after ':'
            clean_part = part.split(':')[0]
            pred_parts = clean_part.split(' matching ')
            result.append([pred_parts[0].strip(), pred_parts[1].strip()])

        return result

    # If single COUNT pattern
    else:
        # Remove 'COUNT  ' and everything after ':'
        clean_string = input_string.replace('COUNT  ', '').split(':')[0]
        # Split on 'matching'
        pred_parts = clean_string.split(' matching ')
        return [pred_parts[0].strip(), pred_parts[1].strip()]

def get_matching_predicates(predicate_list, search_items):
    result = []

    # If search_items is not a list of lists, convert it to one
    if not isinstance(search_items[0], list):
        search_items = [search_items]

    for search_item in search_items:
        for pred in predicate_list:
            # For the first item (predicate name), exact match is required
            if pred[0] == search_item[0]:
                # For the second item, split by comma and check if any part matches
                search_values = [x.strip() for x in search_item[1].split(',')]
                if any(val == pred[1] for val in search_values):
                    result.append(pred[2])
                    # print(f"Matched: {search_item[0]}, {pred[1]}")

    return result


def flatten_nested_list(nested_list):
    base = nested_list[:3]  # First two elements are always base elements
    # print("base: ")
    # print(base)
    # print("nestedlist2: ")
    # print(nested_list[2])
    # Check if third item is a list or not
    if not isinstance(nested_list[3], list):
        # If not a list, return single item with the third element as is
        return [nested_list]

    predicates = nested_list[3]  # List of predicates
    # print("predicates: ")
    # print(predicates)

    def process_list(input_list):
        # Convert non-list items to lists and unnest nested lists
        processed_lists = []
        for item in input_list:
            # print("item of input list: ")
            # print(item)
            if not isinstance(item, list):
                # If item is not a list, convert to single-item list
                processed_lists.append([item])
                # print("processed item: ")
                # print([item])
            elif any(isinstance(subitem, list) for subitem in item):
                # If item contains nested lists, extend with those nested lists
                processed_lists.extend(item)
                # print("processed item: ")
                # print(extend(item))
            else:
                # If item is a simple list, add it as is
                processed_lists.append(item)
                # print("processed item: ")
                # print(item)

        # Do product and convert result to list of lists
        result = [list(x) for x in product(*processed_lists)]
        expanded_list = []
        for item in result:
            part = ""

            for attr in item:
                part = part + "; " + attr
            expandeditem = part[2:]
            # print("expandeditem: ")
            # print(expandeditem)
            expanded_list.append(expandeditem)

        # print("expanded list: ")
        # print(expanded_list)
        return expanded_list

    expanded_list = process_list(predicates)
    nested_list = []
    for pred in expanded_list:
        # print("pred: ")
        # print(pred)
        nested_list.append([*base, f"{pred}"])
        # print("appended_line")
        # print([*base, f"{pred}"])
    return nested_list

def list_to_string(lst):
    return ', '.join(map(str, lst))

# Code to get all attributes used in each line item of policy when end to end line is in column 3
def get_all_attr_used(expanded_list):
    index_of_item = 0
    pol_attr_list = []
    for item in expanded_list:

        if item[1] == 'Output':
            item.append("Attributes used: ")  # Add empty column for consistency
            if pol_attr_list == []:
                pol_index = index_of_item
                pass
            else:
                pol_attr_list = list(set(pol_attr_list))
                pol_attr = (", ".join(pol_attr_list))
                expanded_list[pol_index][5] = pol_attr
                pol_attr_list = []
            continue

        attr_list = []

        try:
            # Split the attribute line into individual predicates
            pred_list = item[3].split("; ")

            # Extract attribute names
            for pred_item in pred_list:
                pred_string = pred_item.split(": ")[0]
                attr_list.append(pred_string)
                pol_attr_list.append(pred_string)

            # Remove duplicates and sort
            attr_list = list(set(attr_list))
            attr_list.sort()

            # Create the attributes string
            if attr_list:
                item.append(", ".join(attr_list))
            else:
                item.append("")

        except Exception as e:
            print(f"Error processing row: {item}")
            print(f"Error: {str(e)}")
            item.append("")  # Add empty column in case of error

    pol_attr_list = list(set(pol_attr_list))
    pol_attr = (", ".join(pol_attr_list))
    expanded_list[pol_index + 1][5] = pol_attr

    return expanded_list

#Change headers of predicate and policy columns
def change_headers(pol_pred_list):
    for index_of_item in range(len(pol_pred_list) - 1):  # Stop one item before the end
        current_item = pol_pred_list[index_of_item]
        next_item = pol_pred_list[index_of_item + 1]

        if current_item[0] in ['policy', 'predicate']:
            if next_item[0] in ['policy', 'predicate']:
                current_item[0] = "Name of policy/predicate"
                current_item[2] = "E2E_Line"
            else:
                current_item[0] = next_item[0]

    return pol_pred_list

def check_matches(A, predicate_list):
    return any(item in A for item, _, _ in predicate_list)

def expand_list(first_list,second_list):
    Policy_list = first_list
    predicate_list = second_list
    E2EList = []
    for policy_line in Policy_list:

        try:
            if policy_line[0] == "Name of policy/predicate" and policy_line[1] == "Output":
                E2Epolicyline = policy_line
                E2Epolicyline.append("E2E_Attribute_Line")

            elif policy_line[1] == "Output":
                E2Epolicyline = policy_line
                E2Epolicyline.append("E2E_Attribute_Line")

            else:
                # print("not policy line")
                E2Epolicyline = policy_line
                attr_header_attr = policy_line[2].split("; ")
                attr_line = []
                for attr in attr_header_attr:
                    if "COUNT  " not in attr:
                        search_items = attr.split(": ")
                        complete_line = get_matching_predicates(predicate_list, search_items)
                        if complete_line == []:
                            attr_line.append(attr)
                        else:
                            attr_line.append(complete_line)
                    else:
                        complete_line = []
                        search_items = parse_count_string(attr)
                        # print(search_items)
                        complete_line = get_matching_predicates(predicate_list, search_items)
                        # print(complete_line)
                        if complete_line == []:
                            complete_line = [attr]
                        else:
                            pass
                        attr_line.append(complete_line)
                E2Epolicyline.append(attr_line)

            E2EList.append(E2Epolicyline)
            # print("for policy line: ")
            # print(policy_line)
            # print("E2E policy line: ")
            # print(E2Epolicyline)

        except Exception as e:
            print(f"Error processing line: {policy_line}")
            print(f"Error message: {str(e)}")

    print("E2E List: ")
    print(E2EList)


    expanded_list = []
    row = 1
    for policy_item in E2EList:
        flattened_items = flatten_nested_list(policy_item)
        for item in flattened_items:
            expanded_list.append(item)
            print("Flattened item: ")
            print(item)

            row += 1
    return expanded_list


#predicate_list = [['Name of policy/predicate', 'Output', 'E2E_Line'], ['FE Battery ASIN Predicate (Policy 1 of 4)', 'Output', 'HTRC; Hazmat Exception'], ['FE Battery ASIN Predicate (Policy 1 of 4)', 'Small Lithium Ion In Equipment', 'HTRC: in 9; Hazmat Exception: in AU_SmallLithiumIonBatteryInEquipment, JP_SmallLithiumIonBatteryInEquipment'], ['FE Battery ASIN Predicate (Policy 1 of 4)', 'Small Lithium Ion Standalone', 'HTRC: in 9; Hazmat Exception: in AU_SmallLithiumIonBatteryStandalone, JP_SmallLithiumIonBatteryStandalone'], ['FE Battery ASIN Predicate (Policy 1 of 4)', 'Small Lithium Ion With Equipment', 'HTRC: in 9; Hazmat Exception: in AU_SmallLithiumIonBatteryWithEquipment, JP_SmallLithiumIonBatteryWithEquipment'], ['FE Battery ASIN Predicate (Policy 1 of 4)', 'Small Lithium Metal In Equipment', 'HTRC: in 9; Hazmat Exception: in AU_SmallLithiumMetalBatteryInEquipment, JP_SmallLithiumMetalBatteryInEquipment'], ['FE Battery ASIN Predicate (Policy 1 of 4)', 'Small Lithium Metal Standalone', 'HTRC: in 9; Hazmat Exception: in AU_SmallLithiumMetalBatteryStandalone, JP_SmallLithiumMetalBatteryStandalone'], ['FE Battery ASIN Predicate (Policy 1 of 4)', 'Small Lithium Metal With Equipment', 'HTRC: in 9; Hazmat Exception: in AU_SmallLithiumMetalBatteryWithEquipment, JP_SmallLithiumMetalBatteryWithEquipment'], ['FE Battery ASIN Predicate (Policy 1 of 4)', 'None', 'HTRC: in 9; Hazmat Exception: Not Exists or not in AU_SmallLithiumIonBatteryInEquipment, AU_SmallLithiumIonBatteryStandalone, AU_SmallLithiumIonBatteryWithEquipment, AU_SmallLithiumMetalBatteryInEquipment, AU_SmallLithiumMetalBatteryStandalone, AU_SmallLithiumMetalBatteryWithEquipment, JP_SmallLithiumIonBatteryInEquipment, JP_SmallLithiumIonBatteryStandalone, JP_SmallLithiumIonBatteryWithEquipment, JP_SmallLithiumMetalBatteryInEquipment, JP_SmallLithiumMetalBatteryStandalone, JP_SmallLithiumMetalBatteryWithEquipment'], ['FE Battery ASIN Predicate (Policy 1 of 4)', 'None', 'HTRC: Not Exists or not in 9'], ['SG DG predicate', 'Output', 'Hazmat Exception; HTRC; UNID'], ['SG DG predicate', 'LQ', 'Hazmat Exception: in SG_LimitedQuantity; HTRC: in 2.1, 2.2, 3, 4.1, 5.1, 5.2, 6.1, 8, 9'], ['SG DG predicate', 'unknown hazmat', 'Hazmat Exception: in SG_LimitedQuantity; HTRC: Not Exists or not in 2.1, 2.2, 3, 4.1, 5.1, 5.2, 6.1, 8, 9'], ['SG DG predicate', 'No\u200bAir', 'Hazmat Exception: in SG_NoAir; HTRC: in 2.1, 2.2, 3, 4.1, 5.1, 5.2, 6.1, 8, 9'], ['SG DG predicate', 'unknown hazmat', 'Hazmat Exception: in SG_NoAir; HTRC: Not Exists or not in 2.1, 2.2, 3, 4.1, 5.1, 5.2, 6.1, 8, 9'], ['SG DG predicate', 'small gas aerosol', 'Hazmat Exception: in SG_SmallAerosols, SG_SmallGasCartridges; HTRC: in 2.1, 2.2'], ['SG DG predicate', 'unknown hazmat', 'Hazmat Exception: in SG_SmallAerosols, SG_SmallGasCartridges; HTRC: Not Exists or not in 2.1, 2.2'], ['SG DG predicate', 'small glue', 'Hazmat Exception: in SG_SmallGlue; HTRC: in 3, 4.1, 9'], ['SG DG predicate', 'unknown hazmat', 'Hazmat Exception: in SG_SmallGlue; HTRC: Not Exists or not in 3, 4.1, 9'], ['SG DG predicate', 'In Equipment Libat', 'Hazmat Exception: in SG_SmallLithiumIonBatteryInEquipment, SG_SmallLithiumMetalBatteryInEquipment; HTRC: in 9'], ['SG DG predicate', 'unknown hazmat', 'Hazmat Exception: in SG_SmallLithiumIonBatteryInEquipment, SG_SmallLithiumMetalBatteryInEquipment; HTRC: Not Exists or not in 9'], ['SG DG predicate', 'Standalone Libat', 'Hazmat Exception: in SG_SmallLithiumIonBatteryStandalone, SG_SmallLithiumMetalBatteryStandalone; HTRC: in 9'], ['SG DG predicate', 'unknown hazmat', 'Hazmat Exception: in SG_SmallLithiumIonBatteryStandalone, SG_SmallLithiumMetalBatteryStandalone; HTRC: Not Exists or not in 9'], ['SG DG predicate', 'With Equipment Libat', 'Hazmat Exception: in SG_SmallLithiumIonBatteryWithEquipment, SG_SmallLithiumMetalBatteryWithEquipment; HTRC: in 9'], ['SG DG predicate', 'unknown hazmat', 'Hazmat Exception: in SG_SmallLithiumIonBatteryWithEquipment, SG_SmallLithiumMetalBatteryWithEquipment; HTRC: Not Exists or not in 9'], ['SG DG predicate', 'Unregulated', 'Hazmat Exception: in SG_Unregulated; HTRC: in 2.1, 2.2, 3, 4.1, 5.1, 5.2, 6.1, 8, 9'], ['SG DG predicate', 'unknown hazmat', 'Hazmat Exception: in SG_Unregulated; HTRC: Not Exists or not in 2.1, 2.2, 3, 4.1, 5.1, 5.2, 6.1, 8, 9'], ['SG DG predicate', 'unknown hazmat', 'Hazmat Exception: Exists; HTRC: Exists'], ['SG DG predicate', 'fully regulated', 'Hazmat Exception: Not Exists; HTRC: Exists; UNID: Exists'], ['SG DG predicate', 'UTC', 'Hazmat Exception: Not Exists; HTRC: Exists; UNID: Not Exists'], ['SG DG predicate', 'not hazmat', 'Hazmat Exception: Not Exists or not in SG_LimitedQuantity, SG_NoAir, SG_SmallAerosols, SG_SmallGasCartridges, SG_SmallGlue, SG_SmallLithiumIonBatteryInEquipment, SG_SmallLithiumIonBatteryStandalone, SG_SmallLithiumIonBatteryWithEquipment, SG_SmallLithiumMetalBatteryInEquipment, SG_SmallLithiumMetalBatteryStandalone, SG_SmallLithiumMetalBatteryWithEquipment, SG_Unregulated; HTRC: Not Exists'], ['JP NON-LIBAT Predicates', 'Output', 'HTRC; Hazmat Exception; UNID'], ['JP NON-LIBAT Predicates', 'Ground/Hazmat_\u200bJP', 'HTRC: in 2.1, 2.2, 2.3, 3, 4.1, 4.2, 4.3, 5.1, 5.2, 6.1, 6.2, 8, 9; Hazmat Exception: in JP_FDL, JP_LimitedQuantity, JP_LithiumBattery, JP_MagnetizedMaterial, JP_MediumLithiumIonBattery, JP_MediumLithiumMetalBattery, JP_SmallGlue'], ['JP NON-LIBAT Predicates', 'JAPAN_\u200bPOST_\u200bMAIL eligible', 'HTRC: in 2.1, 2.2, 4.1, 5.1, 5.2, 6.1, 6.2, 8, 9; Hazmat Exception: in JP_GroundOnly'], ['JP NON-LIBAT Predicates', 'Air-\u200beligible', 'HTRC: in 3; Hazmat Exception: in JP_GroundOnly; UNID: in NA1993, UN0000'], ['JP NON-LIBAT Predicates', 'Ground/Hazmat_\u200bJP', 'HTRC: Not Exists or not in 3; Hazmat Exception: in JP_GroundOnly; UNID: in NA1993, UN0000'], ['JP NON-LIBAT Predicates', 'Ground/Hazmat_\u200bJP', 'HTRC: Not Exists or not in 2.1, 2.2, 4.1, 5.1, 5.2, 6.1, 6.2, 8, 9; Hazmat Exception: in JP_GroundOnly; UNID: Not Exists or not in NA1993, UN0000'], ['JP NON-LIBAT Predicates', 'JP_\u200bNo\u200bAir any HTRC', 'HTRC: in 2.1, 2.2, 2.3, 3, 4.1, 4.2, 4.3, 5.1, 5.2, 6.1, 6.2, 8, 9; Hazmat Exception: in JP_NoAir'], ['JP NON-LIBAT Predicates', 'Lithium Battery', 'HTRC: in 9; Hazmat Exception: in JP_SmallLithiumIonBatteryInEquipment, JP_SmallLithiumIonBatteryStandalone, JP_SmallLithiumIonBatteryWithEquipment, JP_SmallLithiumMetalBatteryInEquipment, JP_SmallLithiumMetalBatteryOverEquipmentException, JP_SmallLithiumMetalBatteryStandalone, JP_SmallLithiumMetalBatteryWithEquipment'], ['JP NON-LIBAT Predicates', 'Misclassified', 'HTRC: Not Exists or not in 9; Hazmat Exception: in JP_SmallLithiumIonBatteryInEquipment, JP_SmallLithiumIonBatteryStandalone, JP_SmallLithiumIonBatteryWithEquipment, JP_SmallLithiumMetalBatteryInEquipment, JP_SmallLithiumMetalBatteryOverEquipmentException, JP_SmallLithiumMetalBatteryStandalone, JP_SmallLithiumMetalBatteryWithEquipment'], ['JP NON-LIBAT Predicates', 'Unregulated', 'HTRC: in 2.1, 2.2, 3, 4.1, 5.1, 5.2, 6.1, 8, 9; Hazmat Exception: in JP_Unregulated'], ['JP NON-LIBAT Predicates', 'Misclassified', 'HTRC: Not Exists or not in 2.1, 2.2, 3, 4.1, 5.1, 5.2, 6.1, 8, 9; Hazmat Exception: in JP_Unregulated'], ['JP NON-LIBAT Predicates', 'Missing valid hazmat exception', 'HTRC: in 2.1, 2.2, 2.3, 3, 4.1, 4.2, 4.3, 5.1, 5.2, 6.1, 6.2, 8, 9; Hazmat Exception: Not Exists or not in JP_FDL, JP_GroundOnly, JP_LimitedQuantity, JP_LithiumBattery, JP_MagnetizedMaterial, JP_MediumLithiumIonBattery, JP_MediumLithiumMetalBattery, JP_NoAir, JP_SmallGlue, JP_SmallLithiumIonBatteryInEquipment, JP_SmallLithiumIonBatteryStandalone, JP_SmallLithiumIonBatteryWithEquipment, JP_SmallLithiumMetalBatteryInEquipment, JP_SmallLithiumMetalBatteryOverEquipmentException, JP_SmallLithiumMetalBatteryStandalone, JP_SmallLithiumMetalBatteryWithEquipment, JP_Unregulated'], ['JP NON-LIBAT Predicates', 'Hazmat missing exception', 'HTRC: in 2.1, 2.2, 2.3, 3, 4.1, 4.2, 4.3, 5.1, 5.2, 6.1, 6.2, 8, 9; Hazmat Exception: Not Exists'], ['JP NON-LIBAT Predicates', 'None', 'HTRC: Not Exists or not in 2.1, 2.2, 2.3, 3, 4.1, 4.2, 4.3, 5.1, 5.2, 6.1, 6.2, 8, 9'], ['JP Valid HTRC', 'Output', 'HTRC'], ['JP Valid HTRC', 'Valid HTRC JP', 'HTRC: in 2.1, 2.2, 2.3, 3, 4.1, 4.2, 4.3, 5.1, 5.2, 6.1, 6.2, 8, 9'], ['JP Valid HTRC', 'Invalid HTRC JP', 'HTRC: Not Exists or not in 2.1, 2.2, 2.3, 3, 4.1, 4.2, 4.3, 5.1, 5.2, 6.1, 6.2, 8, 9'], ['JP Valid HTRC', 'None', 'HTRC: Not Exists']]
#Policy_list = [['Name of policy/predicate', 'Output', 'E2E_Line'], ['AU Battery combo restrictions', 'Output', 'Origin Org Unit; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment'], ['AU Battery combo restrictions', 'DENY ALL smg', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: (>= 1)'], ['AU Battery combo restrictions', 'DENY ALL smg', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: (< 1); COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: > 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: >= 1'], ['AU Battery combo restrictions', 'DENY: LIBAT_\u200bAU_\u200bAIR, LIBAT_\u200bAU_\u200bAIR_\u200bIN_\u200bEQUIPMENT_\u200bONLY', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: (< 1); COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: > 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: < 1'], ['AU Battery combo restrictions', 'DENY ALL smg', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: (< 1); COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: > 1'], ['AU Battery combo restrictions', 'DENY ALL smg', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: (< 1); COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: <= 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: > 1'], ['AU Battery combo restrictions', 'DENY: LIBAT_\u200bAU_\u200bAIR, LIBAT_\u200bAU_\u200bAIR_\u200bIN_\u200bEQUIPMENT_\u200bONLY', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: (< 1); COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: <= 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: <= 1'], ['AU Battery combo restrictions', 'DENY ALL smg', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: (>= 1)'], ['AU Battery combo restrictions', 'DENY ALL smg', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: > 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: (< 1)'], ['AU Battery combo restrictions', 'DENY: LIBAT_\u200bAU_\u200bAIR, LIBAT_\u200bAU_\u200bAIR_\u200bIN_\u200bEQUIPMENT_\u200bONLY', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: > 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: (< 1)'], ['AU Battery combo restrictions', 'DENY ALL smg', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: > 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: (< 1)'], ['AU Battery combo restrictions', 'DENY ALL smg', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: <= 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: > 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: (< 1)'], ['AU Battery combo restrictions', 'DENY: LIBAT_\u200bAU_\u200bAIR, LIBAT_\u200bAU_\u200bAIR_\u200bIN_\u200bEQUIPMENT_\u200bONLY', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: <= 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: <= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment or COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: (< 1)'], ['AU Battery combo restrictions', 'DENY ALL smg', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: >= 1'], ['AU Battery combo restrictions', 'DENY ALL smg', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: > 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: < 1'], ['AU Battery combo restrictions', 'DENY: LIBAT_\u200bAU_\u200bAIR_\u200bIN_\u200bEQUIPMENT_\u200bONLY', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: > 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: < 1'], ['AU Battery combo restrictions', 'DENY ALL smg', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: > 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: < 1'], ['AU Battery combo restrictions', 'DENY: LIBAT_\u200bAU_\u200bAIR_\u200bIN_\u200bEQUIPMENT_\u200bONLY', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: <= 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: < 1'], ['AU Battery combo restrictions', 'DENY ALL smg', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: > 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: >= 1'], ['AU Battery combo restrictions', 'DENY: LIBAT_\u200bAU_\u200bAIR_\u200bIN_\u200bEQUIPMENT_\u200bONLY', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: > 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: >= 1'], ['AU Battery combo restrictions', 'DENY ALL smg', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: > 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: >= 1'], ['AU Battery combo restrictions', 'DENY: LIBAT_\u200bAU_\u200bAIR_\u200bIN_\u200bEQUIPMENT_\u200bONLY', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: <= 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: >= 1'], ['AU Battery combo restrictions', 'DENY: LIBAT_\u200bAU_\u200bAIR_\u200bIN_\u200bEQUIPMENT_\u200bONLY', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: > 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: > 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: < 1'], ['AU Battery combo restrictions', 'DENY ALL smg', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: > 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: > 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: < 1'], ['AU Battery combo restrictions', 'ALLOW ALL ', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: > 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: <= 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: < 1'], ['AU Battery combo restrictions', 'DENY ALL smg', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: > 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: >= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: < 1'], ['AU Battery combo restrictions', 'DENY: LIBAT_\u200bAU_\u200bAIR_\u200bIN_\u200bEQUIPMENT_\u200bONLY', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: > 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: < 1'], ['AU Battery combo restrictions', 'DENY: LIBAT_\u200bAU_\u200bAIR_\u200bIN_\u200bEQUIPMENT_\u200bONLY', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: <= 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: > 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: < 1'], ['AU Battery combo restrictions', 'ALLOW ALL ', 'Origin Org Unit: in AU; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion In Equipment: <= 0; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal In Equipment: <= 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal Standalone: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Ion With Equipment: < 1; COUNT  FE Battery ASIN Predicate (Policy 1 of 4) matching Small Lithium Metal With Equipment: < 1'], ['AU Battery combo restrictions', 'ALLOW ALL ', 'Origin Org Unit: Not Exists or not in AU'], ['SG Ground only', 'Output', 'Origin Org Unit; COUNT  SG DG predicate matching No\u200bAir, Standalone Libat'], ['SG Ground only', 'ALLOW: Ground and LIBAT_\u200bSG_\u200bGROUND DENY: International', 'Origin Org Unit: in SG; COUNT  SG DG predicate matching No\u200bAir, Standalone Libat: >= 1'], ['SG Ground only', 'ALLOW ALL mode and destination and smg', 'Origin Org Unit: in SG; COUNT  SG DG predicate matching No\u200bAir, Standalone Libat: < 1'], ['SG Ground only', 'ALLOW ALL mode and destination and smg', 'Origin Org Unit: Not Exists or not in SG'], ['JP Valid HTRC SMG', 'Output', 'Origin Org Unit; JP Valid HTRC'], ['JP Valid HTRC SMG', 'DENY ALL mode and destination and smg', 'Origin Org Unit: in JP; JP Valid HTRC: Invalid HTRC JP'], ['JP Valid HTRC SMG', 'ALLOW ALL mode and destination and smg', 'Origin Org Unit: in JP; JP Valid HTRC: Not Invalid HTRC JP'], ['JP Valid HTRC SMG', 'ALLOW ALL mode and destination and smg', 'Origin Org Unit: Not Exists or not in JP'], ['JP ground only', 'Output', 'Origin Org Unit; COUNT  JP NON-\u200bLIBAT Predicates matching Ground/Hazmat_\u200bJP'], ['JP ground only', 'DENY: International ALLOW: Ground and HAZMAT_\u200bJP', 'Origin Org Unit: in JP; COUNT  JP NON-\u200bLIBAT Predicates matching Ground/Hazmat_\u200bJP: >= 1'], ['JP ground only', 'ALLOW ALL mode and destination and smg', 'Origin Org Unit: in JP; COUNT  JP NON-\u200bLIBAT Predicates matching Ground/Hazmat_\u200bJP: < 1'], ['JP ground only', 'ALLOW ALL mode and destination and smg', 'Origin Org Unit: Not Exists or not in JP']]
