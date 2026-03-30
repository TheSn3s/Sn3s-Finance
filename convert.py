import openpyxl
import csv
import os

def convert_xlsx_to_csv(xlsx_filepath, csv_filepath):
    try:
        workbook = openpyxl.load_workbook(xlsx_filepath, data_only=True)
        sheet = workbook.active
        with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            for row in sheet.iter_rows():
                row_data = [cell.value for cell in row]
                csv_writer.writerow(row_data)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    xlsx_path = "/home/ubuntu/.openclaw/workspace/atef_office/financial_sheet.xlsx"
    csv_path = "/home/ubuntu/.openclaw/workspace/atef_office/financial_sheet.csv"
    if convert_xlsx_to_csv(xlsx_path, csv_path):
        print("Success")
    else:
        print("Failed")
