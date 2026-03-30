from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import csv
import os
from urllib.parse import parse_qs
from datetime import datetime

# Import the existing dashboard generator logic
import update_dashboard

CSV_PATH = "/home/ubuntu/.openclaw/workspace/atef_office/financial_sheet.csv"

class AtefServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/" or self.path == "/dashboard.html":
            update_dashboard.generate_dashboard()
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            with open("/home/ubuntu/.openclaw/workspace/atef_office/dashboard.html", "rb") as f:
                self.wfile.write(f.read())
        elif self.path.startswith("/invoice"):
            query = parse_qs(self.path.split('?')[1]) if '?' in self.path else {}
            serial = query.get('serial', [''])[0]
            self.send_invoice(serial)
        elif self.path == "/signature.png":
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()
            with open("/home/ubuntu/.openclaw/workspace/atef_office/signature.png", "rb") as f:
                self.wfile.write(f.read())
        else:
            self.send_error(404)

    def send_invoice(self, serial):
        entry = None
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('Notes') == serial:
                    entry = row
                    break
        
        if not entry:
            self.send_error(404, "Invoice not found")
            return

        # Formatting values for the invoice
        amount_raw = entry.get('Amount', '0').replace(',', '')
        try:
            amount_val = float(amount_raw)
        except:
            amount_val = 0
            
        amount_fmt = f"KWD {amount_val:,.0f}"
        
        html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Invoice #{serial}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Montserrat', sans-serif; background-color: #f9fafb; color: #000; }}
        .red-header {{ background-color: #f04444; color: white; }}
        .border-red {{ border-bottom: 2px solid #f04444; }}
        @media print {{
            .no-print {{ display: none; }}
            body {{ padding: 0; margin: 0; background-color: white !important; }}
            .invoice-container {{ border: none !important; box-shadow: none !important; }}
        }}
    </style>
</head>
<body class="p-4 md:p-8 flex justify-center">
    <div class="invoice-container w-full max-w-[800px] bg-white min-h-[1100px] flex flex-col shadow-xl border border-slate-100">
        <!-- Red Header Bar -->
        <div class="red-header py-6 text-center mb-10">
            <h1 class="text-3xl font-black uppercase tracking-widest mb-1">Abdullah AlSanousi</h1>
            <p class="text-[10px] font-bold uppercase tracking-[0.3em] opacity-90">Motion Graphics Artist - Content Creator</p>
        </div>

        <div class="px-12 flex-grow">
            <!-- Info Bar -->
            <div class="flex justify-between border-red pb-1 mb-10 font-bold text-[11px] uppercase tracking-tight text-slate-800">
                <div>{entry.get('Date')}</div>
                <div>Invoice #{serial}</div>
                <div>{entry.get('Client')}</div>
            </div>

            <!-- Invoice Header -->
            <h2 class="text-[#f04444] text-xl font-black mb-3">Invoice #{serial}</h2>
            <div class="mb-10 font-bold text-sm text-slate-800">{entry.get('Client')}</div>

            <!-- Table -->
            <table class="w-full text-left mb-8">
                <thead>
                    <tr class="border-red text-[10px] font-black uppercase tracking-widest text-slate-700">
                        <th class="py-2 w-12">ID</th>
                        <th class="py-2 w-12">QTY</th>
                        <th class="py-2">DESCRIPTION</th>
                        <th class="py-2 text-right">COST</th>
                    </tr>
                </thead>
                <tbody class="text-xs">
                    <tr class="border-b border-slate-100">
                        <td class="py-6 align-top text-center text-slate-700">1</td>
                        <td class="py-6 align-top text-center text-slate-700">1</td>
                        <td class="py-6 pr-8">
                            <p class="font-bold text-sm mb-1 text-slate-800">{entry.get('Project')}</p>
                            <p class="text-slate-700 text-[10px] leading-relaxed">Professional Video Production & Motion Graphics Services tailored for your brand's digital presence.</p>
                        </td>
                        <td class="py-6 align-top text-right font-black text-sm whitespace-nowrap text-slate-800">{amount_fmt}</td>
                    </tr>
                </tbody>
            </table>

            <!-- Totals -->
            <div class="flex justify-end mb-16">
                <div class="w-48 text-[11px] font-bold space-y-2">
                    <div class="flex justify-between text-slate-700">
                        <span>Subtotal</span>
                        <span>{amount_fmt}</span>
                    </div>
                    <div class="flex justify-between text-slate-700">
                        <span>Discount</span>
                        <span>KWD 0</span>
                    </div>
                    <div class="flex justify-between border-t-2 border-black pt-2 text-sm font-black text-slate-800">
                        <span>Total</span>
                        <span>{amount_fmt}</span>
                    </div>
                </div>
            </div>

            <!-- Banking Details -->
            <div class="text-[10px] space-y-1 mb-16 text-slate-800 bg-slate-50 p-4 rounded-lg inline-block border border-slate-100">
                <p class="font-black text-slate-900 text-[11px] mb-2 uppercase tracking-wider">Banking Details:</p>
                <p><span class="font-black text-slate-700">Account Holder:</span> Abdullah Faisal Abdullah Alsanousi</p>
                <p><span class="font-black text-slate-700">Bank Name:</span> National Bank of Kuwait (NBK.)</p>
                <p><span class="font-black text-slate-700">Account number:</span> 2006532736</p>
                <p><span class="font-black text-slate-700">IBAN:</span> KW28NBOK00000000002006532736</p>
            </div>

            <!-- Regards & Signature -->
            <div class="text-xs mb-32 relative">
                <p class="text-slate-700 font-bold mb-1">Regards,</p>
                <p class="font-black text-sm text-slate-800">Abdullah AlSanousi</p>
                <div class="absolute left-0 top-4 w-40">
                    <img src="/signature.png" alt="Signature" class="w-full mix-blend-multiply" onerror="this.style.display='none'">
                </div>
            </div>
        </div>

        <!-- Footer Bar -->
        <div class="px-12 py-8 flex justify-between text-[#f04444] font-black text-[9px] uppercase tracking-[0.2em] border-t border-slate-50">
            <div>+965 97116661</div>
            <div>Hello@Sn3s.com</div>
            <div>www.Sn3s.com</div>
            <div>@Sn3s</div>
        </div>

        <!-- Print Button -->
        <div class="fixed bottom-8 right-8 no-print">
            <button onclick="window.print()" class="bg-[#f04444] text-white px-8 py-4 rounded-full font-black shadow-2xl hover:scale-105 transition-all flex items-center gap-3">
                <span>🖨️</span> SAVE AS PDF
            </button>
        </div>
    </div>
</body>
</html>
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        params = json.loads(post_data)

        if self.path == "/add":
            self.add_entry(params)
        elif self.path == "/edit":
            self.edit_entry(params)
        
        update_dashboard.generate_dashboard()
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "success"}).encode())

    def add_entry(self, p):
        # Get next serial
        with open(CSV_PATH, 'r') as f:
            rows = list(csv.reader(f))
            last_serial = 0
            for r in rows[1:]:
                if len(r) >= 8 and r[7].isdigit():
                    last_serial = max(last_serial, int(r[7]))
        
        new_serial = f"{last_serial + 1:03d}"
        new_row = [
            p.get('date', datetime.now().strftime('%Y-%m-%d')),
            p.get('category', 'Video'),
            p.get('client', ''),
            p.get('project', ''),
            p.get('status', 'Delivered'),
            p.get('amount', '0'),
            p.get('payment_status', 'Not Paid'),
            new_serial
        ]
        with open(CSV_PATH, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(new_row)

    def edit_entry(self, p):
        rows = []
        target_serial = p.get('notes') # The serial number
        with open(CSV_PATH, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            for r in reader:
                if len(r) >= 8 and r[7] == target_serial:
                    # Update row
                    r[0] = p.get('date', r[0])
                    r[2] = p.get('client', r[2])
                    r[3] = p.get('project', r[3])
                    r[5] = p.get('amount', r[5])
                    r[6] = p.get('payment_status', r[6])
                rows.append(r)
        
        with open(CSV_PATH, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)

if __name__ == "__main__":
    server = HTTPServer(('0.0.0.0', 18790), AtefServer)
    print("Atef Financial Server started on port 18790")
    server.serve_forever()
