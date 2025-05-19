#Functions for policy and predicate data merging
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


predicate_list = [['predicate', 'Output',
                   'attribute 1; attribute 2; attribute 3; attribute 4; attribute 5; attribute 6; attribute 7; attribute 8; attribute 9; attribute 10; attribute 11; attribute 12'],
                  ['predicate', 'Output', 'HTRC; Hazmat Exception; UNID'],
                  ['JP NON-LIBAT Predicates', 'Ground/Hazmat_\u200bJP',
                   'HTRC: in 2.1, 2.2, 2.3, 3, 4.1, 4.2, 4.3, 5.1, 5.2, 6.1, 6.2, 8, 9; Hazmat Exception: in JP_FDL, JP_LimitedQuantity, JP_LithiumBattery, JP_MagnetizedMaterial, JP_MediumLithiumIonBattery, JP_MediumLithiumMetalBattery, JP_SmallGlue'],
                  ['JP NON-LIBAT Predicates', 'JAPAN_\u200bPOST_\u200bMAIL eligible',
                   'HTRC: in 2.1, 2.2, 4.1, 5.1, 5.2, 6.1, 6.2, 8, 9; Hazmat Exception: in JP_GroundOnly'],
                  ['JP NON-LIBAT Predicates', 'Air-\u200beligible',
                   'HTRC: in 3; Hazmat Exception: in JP_GroundOnly; UNID: in NA1993, UN0000'],
                  ['JP NON-LIBAT Predicates', 'Ground/Hazmat_\u200bJP',
                   'HTRC: Not Exists or not in 3; Hazmat Exception: in JP_GroundOnly; UNID: in NA1993, UN0000'],
                  ['JP NON-LIBAT Predicates', 'Ground/Hazmat_\u200bJP',
                   'HTRC: Not Exists or not in 2.1, 2.2, 4.1, 5.1, 5.2, 6.1, 6.2, 8, 9; Hazmat Exception: in JP_GroundOnly; UNID: Not Exists or not in NA1993, UN0000'],
                  ['JP NON-LIBAT Predicates', 'JP_\u200bNo\u200bAir any HTRC',
                   'HTRC: in 2.1, 2.2, 2.3, 3, 4.1, 4.2, 4.3, 5.1, 5.2, 6.1, 6.2, 8, 9; Hazmat Exception: in JP_NoAir'],
                  ['JP NON-LIBAT Predicates', 'Lithium Battery',
                   'HTRC: in 9; Hazmat Exception: in JP_SmallLithiumIonBatteryInEquipment, JP_SmallLithiumIonBatteryStandalone, JP_SmallLithiumIonBatteryWithEquipment, JP_SmallLithiumMetalBatteryInEquipment, JP_SmallLithiumMetalBatteryOverEquipmentException, JP_SmallLithiumMetalBatteryStandalone, JP_SmallLithiumMetalBatteryWithEquipment'],
                  ['JP NON-LIBAT Predicates', 'Misclassified',
                   'HTRC: Not Exists or not in 9; Hazmat Exception: in JP_SmallLithiumIonBatteryInEquipment, JP_SmallLithiumIonBatteryStandalone, JP_SmallLithiumIonBatteryWithEquipment, JP_SmallLithiumMetalBatteryInEquipment, JP_SmallLithiumMetalBatteryOverEquipmentException, JP_SmallLithiumMetalBatteryStandalone, JP_SmallLithiumMetalBatteryWithEquipment'],
                  ['JP NON-LIBAT Predicates', 'Unregulated',
                   'HTRC: in 2.1, 2.2, 3, 4.1, 5.1, 5.2, 6.1, 8, 9; Hazmat Exception: in JP_Unregulated'],
                  ['JP NON-LIBAT Predicates', 'Misclassified',
                   'HTRC: Not Exists or not in 2.1, 2.2, 3, 4.1, 5.1, 5.2, 6.1, 8, 9; Hazmat Exception: in JP_Unregulated'],
                  ['JP NON-LIBAT Predicates', 'Missing valid hazmat exception',
                   'HTRC: in 2.1, 2.2, 2.3, 3, 4.1, 4.2, 4.3, 5.1, 5.2, 6.1, 6.2, 8, 9; Hazmat Exception: Not Exists or not in JP_FDL, JP_GroundOnly, JP_LimitedQuantity, JP_LithiumBattery, JP_MagnetizedMaterial, JP_MediumLithiumIonBattery, JP_MediumLithiumMetalBattery, JP_NoAir, JP_SmallGlue, JP_SmallLithiumIonBatteryInEquipment, JP_SmallLithiumIonBatteryStandalone, JP_SmallLithiumIonBatteryWithEquipment, JP_SmallLithiumMetalBatteryInEquipment, JP_SmallLithiumMetalBatteryOverEquipmentException, JP_SmallLithiumMetalBatteryStandalone, JP_SmallLithiumMetalBatteryWithEquipment, JP_Unregulated'],
                  ['JP NON-LIBAT Predicates', 'Hazmat missing exception',
                   'HTRC: in 2.1, 2.2, 2.3, 3, 4.1, 4.2, 4.3, 5.1, 5.2, 6.1, 6.2, 8, 9; Hazmat Exception: Not Exists'],
                  ['JP NON-LIBAT Predicates', 'None',
                   'HTRC: Not Exists or not in 2.1, 2.2, 2.3, 3, 4.1, 4.2, 4.3, 5.1, 5.2, 6.1, 6.2, 8, 9']]


# print(predicate_list)

# Code to get all attributes used in each line item of policy when end to end line is in column 3
def get_all_attr_used(predicate_policy_list):
    predicate_list = predicate_policy_list
    index_of_item = 0
    for item in predicate_list:
        print(item)
        item.append("attributes used: ")
        if item[0] == 'predicate':
            item[3] = item[3] + item[2]
            if predicate_list[index_of_item + 1][0] == 'predicate':
                item[2] = "End to End Line"
                item[3] = "AAll attributes of domain - "
            else:
                predicate_list[index_of_item][0] = predicate_list[index_of_item + 1][0]
                item[3] = item[3][17:]
        else:
            pred_list = predicate_list[index_of_item][2].split("; ")
            for pred_item in pred_list:
                pred_string = pred_item.split(": ")[0]
                item[3] = item[3] + ", " + pred_string
            item[3] = item[3][19:]
        index_of_item = index_of_item + 1
    for item in predicate_list:
        print(item)

    all_attributes_of_domain = []
    for item in predicate_list:
        print(item)
        if "; " in item[3]:
            item_list = item[3].split("; ")
        else:
            item_list = item[3].split(", ")
        for attr in item_list:
            all_attributes_of_domain.append(attr)
    all_attributes_of_domain = list(set(all_attributes_of_domain))
    all_attributes_of_domain.sort()
    print(all_attributes_of_domain)