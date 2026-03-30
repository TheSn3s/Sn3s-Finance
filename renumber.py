import csv
import os

def renumber_ledger():
    csv_path = "/home/ubuntu/.openclaw/workspace/atef_office/financial_sheet.csv"
    temp_path = "/home/ubuntu/.openclaw/workspace/atef_office/financial_sheet_temp.csv"
    
    if not os.path.exists(csv_path):
        return

    new_rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        counter = 1
        for row in reader:
            # Skip empty rows or rows that are just totals (check if Date is empty)
            if not row or not row[0].strip():
                continue
            
            new_row = row[:7] # Keep first 7 columns
            while len(new_row) < 7:
                new_row.append("")
                
            new_row.append(f"{counter:03d}") # Add serial number as 8th column
            new_rows.append(new_row)
            counter += 1

    with open(temp_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Category', 'Client', 'Project', 'Status', 'Amount', 'Payment Status', 'Notes'])
        writer.writerows(new_rows)
    
    os.replace(temp_path, csv_path)
    print(f"Cleaned and renumbered {len(new_rows)} entries.")

if __name__ == "__main__":
    renumber_ledger()
