import win32com.client
import os
import Functions as fu
from AmazonProjects.Functions import change_headers

excel = None
wb = None

try:
    filepath = input("Please provide the filepath to the workbook: ") # Get the workbook name
    file_path = os.path.abspath(filepath) # Get absolute path of the Excel file
    excel = win32com.client.Dispatch("Excel.Application") # Create Excel application object
    excel.Visible = True # Make Excel visible
    wb = excel.Workbooks.Open(file_path) # Open the workbook

    # Build predicate list
    predicate_sheet = wb.Worksheets(input("Please provide the name of the predicate sheet: "))  # ask for predicate sheet name and open it
    predicate_start_col = ord(input("Please provide the start column of predicate data (excluding predicate column): ").upper())
    predicate_end_col = ord(input("Please provide the end column of predicate data: ").upper())
    pred_column_list = [chr(i) for i in range(predicate_start_col, predicate_end_col + 1)] # Create list using list comprehension

    pol_pred = "predicate"
    predicate_list = fu.get_pol_pred_list(predicate_sheet,pred_column_list,pol_pred)
    predicate_list = change_headers(predicate_list)
    print("Predicate List: ")
    print(predicate_list)

    # Build policy list
    policy_sheet = wb.Worksheets(input("Please provide the name of the policy sheet: "))  # ask for policy sheet name and open it
    pol_start_col = ord(input("Please provide the start column of policy data (excluding policy name column): ").upper())
    pol_end_col = ord(input("Please provide the end column of policy data: ").upper())
    pol_column_list = [chr(i) for i in range(pol_start_col, pol_end_col + 1)] # Create list using list comprehension

    pol_pred = "policy"
    Policy_list = fu.get_pol_pred_list(policy_sheet,pol_column_list,pol_pred)
    Policy_list = change_headers(Policy_list)
    print("Policy List: ")
    print(Policy_list)

    # ask_user = input("Do you want to expand predicate list? Y/N: ")
    #
    # if ask_user.strip() == 'Y':
    #     pass
    # else:
    #     quit()
    #
    # expanded_predicate_list = expand_list(predicate_list,predicate_list)
    # print("Expanded Predicate List: ")
    # print(expanded_predicate_list)

    ask_user = input("Do you want to merge policy and predicate data? Y/N: ")

    if ask_user.strip() == 'Y':
        pass
    else:
        quit()

    expanded_policy_list = fu.expand_list(Policy_list,predicate_list)
    print("Expanded Policy List: ")
    print(expanded_policy_list)

    for item in expanded_policy_list:
        print(item)

    #Print Expanded Policy List
    #Add new worksheet
    ws = wb.Sheets.Add()
    ws.Name = "expanded_data"

    row = 1
    for policy_item in expanded_policy_list:
        col = 1
        for item in policy_item:
            ws.Cells(row, col).Value = item[:254]
            col = col + 1
        row = row + 1

    print("\nSuccessfully processed all rows")
    print(f"Data written to sheet expanded_data")

except Exception as e:
    print(f"An error occurred: {str(e)}")