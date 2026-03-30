import zipfile
import xml.etree.ElementTree as ET
import csv
from datetime import datetime, timedelta

def excel_serial_to_date(serial):
    try:
        serial = float(serial)
        if serial >= 60:
            return (datetime(1899, 12, 30) + timedelta(days=serial)).strftime('%Y-%m-%d')
        else:
            return (datetime(1899, 12, 31) + timedelta(days=serial)).strftime('%Y-%m-%d')
    except:
        return serial

def parse_xlsx(xlsx_path, out_csv):
    with zipfile.ZipFile(xlsx_path, 'r') as z:
        # Load Shared Strings
        strings = []
        try:
            with z.open('xl/sharedStrings.xml') as f:
                tree = ET.parse(f)
                for si in tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
                    t_node = si.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
                    if t_node is not None:
                        strings.append(t_node.text)
                    else:
                        # Handle rich text strings
                        text = "".join([t.text for t in si.findall('.//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t') if t.text])
                        strings.append(text)
        except KeyError:
            pass

        # Load Sheet1
        with z.open('xl/worksheets/sheet1.xml') as f:
            tree = ET.parse(f)
            ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
            rows = []
            for row in tree.findall('.//ns:row', ns):
                cells = {}
                max_col = 0
                for c in row.findall('ns:c', ns):
                    r_ref = c.get('r')
                    # Convert column letter to index
                    col_str = "".join([char for char in r_ref if char.isalpha()])
                    col_idx = 0
                    for char in col_str:
                        col_idx = col_idx * 26 + (ord(char.upper()) - ord('A') + 1)
                    
                    val_node = c.find('ns:v', ns)
                    val = val_node.text if val_node is not None else ""
                    
                    if c.get('t') == 's':
                        val = strings[int(val)] if val else ""
                    
                    # Simple date detection for column A
                    if col_idx == 1 and val and val.replace('.','',1).isdigit():
                        val = excel_serial_to_date(val)

                    cells[col_idx] = val
                    if col_idx > max_col: max_col = col_idx
                
                row_data = [cells.get(i, "") for i in range(1, max_col + 1)]
                rows.append(row_data)

            with open(out_csv, 'w', newline='', encoding='utf-8') as cf:
                writer = csv.writer(cf)
                writer.writerows(rows)

if __name__ == "__main__":
    parse_xlsx("/home/ubuntu/.openclaw/workspace/atef_office/financial_sheet.xlsx", "/home/ubuntu/.openclaw/workspace/atef_office/financial_sheet.csv")
