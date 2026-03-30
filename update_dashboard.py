import csv
import json
import os
from datetime import datetime

def generate_dashboard():
    csv_path = "/home/ubuntu/.openclaw/workspace/atef_office/financial_sheet.csv"
    data = []
    
    if not os.path.exists(csv_path):
        return
        
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get('Date') or not row.get('Date').strip():
                continue
            # Ensure keys exist and handle None
            entry = {
                'Date': row.get('Date', '') or '',
                'Category': row.get('Category', '') or '',
                'Client': row.get('Client', '') or '',
                'Project': row.get('Project', '') or '',
                'Status': row.get('Status', '') or '',
                'Amount': row.get('Amount', '0') or '0',
                'PaymentStatus': row.get('Payment Status', 'Paid') or 'Paid',
                'Notes': row.get('Notes', '') or ''
            }
            data.append(entry)

    # Calculate Stats
    total_income = 0
    outstanding = 0
    current_year = str(datetime.now().year)
    year_income = 0
    
    monthly_data = {}

    for entry in data:
        try:
            val_clean = entry['Amount'].replace(',', '').strip()
            if val_clean == '-': val_clean = '0'
            amt = float(val_clean)
        except:
            amt = 0
            
        total_income += amt
        if current_year in entry['Date']:
            year_income += amt
        if entry['PaymentStatus'] == 'Not Paid':
            outstanding += amt
            
        try:
            date_obj = None
            raw_date = entry['Date']
            if '-' in raw_date:
                date_obj = datetime.strptime(raw_date, '%Y-%m-%d')
            elif '/' in raw_date:
                date_obj = datetime.strptime(raw_date, '%d/%m/%Y')
            
            if date_obj:
                month_key = date_obj.strftime('%Y-%m')
                monthly_data[month_key] = monthly_data.get(month_key, 0) + amt
        except:
            pass

    sorted_months = sorted(monthly_data.keys())
    chart_labels = sorted_months[-24:] # Show last 2 years
    chart_values = [monthly_data[m] for m in chart_labels]

    # HTML Template with JavaScript Filtering
    html = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sn3s Financial Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Tajawal', sans-serif; background-color: #f1f5f9; }}
        .filter-input {{ @apply bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500; }}
    </style>
</head>
<body class="p-4 md:p-8">
    <div class="max-w-7xl mx-auto">
        <header class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
            <div>
                <h1 class="text-3xl font-bold text-slate-800">النظام المالي - عبدالله السنعوسي</h1>
                <p class="text-slate-500">متابعة الفواتير، الإيرادات، والمبالغ المعلقة</p>
            </div>
            <div class="bg-white px-4 py-2 rounded-lg shadow-sm text-sm text-slate-600 border border-slate-200">
                📅 تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}
            </div>
        </header>

        <!-- Stats -->
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div class="flex items-center gap-3 mb-2">
                    <span class="p-2 bg-blue-50 text-blue-600 rounded-lg text-xl">💰</span>
                    <span class="text-slate-500 font-bold">إجمالي الدخل</span>
                </div>
                <div class="text-3xl font-black text-slate-800">{total_income:,.0f} <span class="text-lg">د.ك</span></div>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
                <div class="flex items-center gap-3 mb-2">
                    <span class="p-2 bg-green-50 text-green-600 rounded-lg text-xl">📈</span>
                    <span class="text-slate-500 font-bold">دخل {current_year}</span>
                </div>
                <div class="text-3xl font-black text-slate-800">{year_income:,.0f} <span class="text-lg">د.ك</span></div>
            </div>
            <div class="bg-white p-6 rounded-2xl shadow-sm border border-red-100">
                <div class="flex items-center gap-3 mb-2">
                    <span class="p-2 bg-red-50 text-red-600 rounded-lg text-xl">🚩</span>
                    <span class="text-slate-500 font-bold">مبالغ معلقة</span>
                </div>
                <div class="text-3xl font-black text-red-600">{outstanding:,.0f} <span class="text-lg">د.ك</span></div>
            </div>
        </div>

        <!-- Chart -->
        <div class="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 mb-8">
            <h2 class="text-lg font-bold mb-6 text-slate-800">تحليل الإيرادات الشهرية</h2>
            <div class="h-[300px]">
                <canvas id="growthChart"></canvas>
            </div>
        </div>

        <!-- Search & Filter -->
        <div class="bg-white p-6 rounded-t-2xl shadow-sm border border-slate-200 border-b-0">
            <div class="flex justify-between items-center mb-4">
                <h2 class="text-lg font-bold text-slate-800">تصفية وفلترة العمليات</h2>
                <button onclick="openModal('add')" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-bold transition-all shadow-md shadow-blue-100 flex items-center gap-2">
                    <span>➕</span> إضافة مشروع جديد
                </button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <input type="text" id="searchClient" placeholder="بحث بالعميل أو المشروع..." class="bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                <div class="flex gap-2">
                    <input type="date" id="dateFrom" class="bg-slate-50 border border-slate-200 rounded-lg px-2 py-2 text-sm w-full">
                    <input type="date" id="dateTo" class="bg-slate-50 border border-slate-200 rounded-lg px-2 py-2 text-sm w-full">
                </div>
                <select id="filterStatus" class="bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-sm">
                    <option value="all">كل الحالات</option>
                    <option value="Paid">مدفوع</option>
                    <option value="Not Paid">معلق</option>
                </select>
                <div class="flex items-center gap-2 text-slate-500 text-sm">
                    عدد النتائج: <span id="resultCount" class="font-bold text-blue-600">0</span>
                </div>
            </div>
        </div>

        <!-- Full Ledger Table -->
        <div class="bg-white rounded-b-2xl shadow-sm border border-slate-200 overflow-hidden mb-12">
            <div class="overflow-x-auto">
                <table class="w-full text-right border-collapse">
                    <thead class="bg-slate-50 text-slate-500 text-xs uppercase font-bold border-b border-slate-200">
                        <tr>
                            <th class="p-4">#</th>
                            <th class="p-4">التاريخ</th>
                            <th class="p-4">العميل</th>
                            <th class="p-4">المشروع</th>
                            <th class="p-4">المبلغ</th>
                            <th class="p-4">الحالة</th>
                            <th class="p-4">إجراء</th>
                        </tr>
                    </thead>
                    <tbody id="ledgerBody" class="text-slate-700 text-sm">
                        <!-- JS handles content -->
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Modal -->
    <div id="modal" class="fixed inset-0 bg-slate-900/50 backdrop-blur-sm hidden flex items-center justify-center p-4 z-50">
        <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md overflow-hidden">
            <div class="p-6 border-b border-slate-100 flex justify-between items-center">
                <h3 id="modalTitle" class="text-xl font-bold text-slate-800">إضافة مشروع جديد</h3>
                <button onclick="closeModal()" class="text-slate-400 hover:text-slate-600 text-2xl">&times;</button>
            </div>
            <form id="projectForm" class="p-6 space-y-4">
                <input type="hidden" id="editSerial">
                <div>
                    <label class="block text-xs font-bold text-slate-500 mb-1 uppercase">التاريخ</label>
                    <input type="date" id="fDate" required class="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-500 mb-1 uppercase">العميل</label>
                    <input type="text" id="fClient" required placeholder="اسم العميل..." class="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                </div>
                <div>
                    <label class="block text-xs font-bold text-slate-500 mb-1 uppercase">المشروع</label>
                    <input type="text" id="fProject" required placeholder="وصف المشروع..." class="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-500 mb-1 uppercase">المبلغ (د.ك)</label>
                        <input type="number" id="fAmount" required step="0.5" class="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-500 mb-1 uppercase">حالة الدفع</label>
                        <select id="fPaymentStatus" class="w-full bg-slate-50 border border-slate-200 rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
                            <option value="Paid">مدفوع ✅</option>
                            <option value="Not Paid">معلق 🚩</option>
                        </select>
                    </div>
                </div>
                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl shadow-lg shadow-blue-100 transition-all mt-4">حفظ البيانات</button>
            </form>
        </div>
    </div>

    <script>
        const rawData = {json.dumps(data)};
        
        function openModal(mode, serial = null) {{
            const modal = document.getElementById('modal');
            const title = document.getElementById('modalTitle');
            const form = document.getElementById('projectForm');
            form.reset();
            document.getElementById('fDate').value = new Date().toISOString().split('T')[0];

            if (mode === 'edit') {{
                title.innerText = 'تعديل مشروع رقم ' + serial;
                const entry = rawData.find(e => e.Notes === serial);
                if (entry) {{
                    document.getElementById('editSerial').value = serial;
                    document.getElementById('fDate').value = entry.Date;
                    document.getElementById('fClient').value = entry.Client;
                    document.getElementById('fProject').value = entry.Project;
                    document.getElementById('fAmount').value = parseFloat(entry.Amount.replace(',',''));
                    document.getElementById('fPaymentStatus').value = entry.PaymentStatus;
                }}
            }} else {{
                title.innerText = 'إضافة مشروع جديد';
                document.getElementById('editSerial').value = '';
            }}
            
            modal.classList.remove('hidden');
        }}

        function closeModal() {{
            document.getElementById('modal').classList.add('hidden');
        }}

        document.getElementById('projectForm').onsubmit = async (e) => {{
            e.preventDefault();
            const serial = document.getElementById('editSerial').value;
            const endpoint = serial ? '/edit' : '/add';
            
            const payload = {{
                date: document.getElementById('fDate').value,
                client: document.getElementById('fClient').value,
                project: document.getElementById('fProject').value,
                amount: document.getElementById('fAmount').value,
                payment_status: document.getElementById('fPaymentStatus').value,
                notes: serial
            }};

            const res = await fetch(endpoint, {{
                method: 'POST',
                body: JSON.stringify(payload)
            }});
            
            if (res.ok) {{
                location.reload();
            }}
        }};

        function renderTable(filterData) {{
            const tbody = document.getElementById('ledgerBody');
            tbody.innerHTML = '';
            document.getElementById('resultCount').innerText = filterData.length;

            filterData.forEach(e => {{
                const tr = document.createElement('tr');
                tr.className = 'border-b border-slate-50 hover:bg-blue-50/30 transition-colors group';
                
                const isNotPaid = e.PaymentStatus === 'Not Paid';
                const statusClass = isNotPaid ? 'bg-red-100 text-red-600' : 'bg-green-100 text-green-600';
                const statusText = isNotPaid ? 'معلق' : 'مدفوع';

                tr.innerHTML = `
                    <td class="p-4 font-mono text-blue-600 font-bold">${{e.Notes}}</td>
                    <td class="p-4 text-slate-500">${{e.Date}}</td>
                    <td class="p-4 font-bold text-slate-800">${{e.Client}}</td>
                    <td class="p-4 text-xs max-w-[200px] truncate">${{e.Project}}</td>
                    <td class="p-4 font-bold">${{parseFloat(e.Amount.replace(',','')).toLocaleString()}} د.ك</td>
                    <td class="p-4">
                        <span class="px-2 py-1 rounded-full text-[10px] font-bold uppercase ${{statusClass}}">
                            ${{statusText}}
                        </span>
                    </td>
                    <td class="p-4">
                        <div class="flex items-center gap-2">
                            <button onclick="openModal('edit', '${{e.Notes}}')" class="opacity-0 group-hover:opacity-100 bg-slate-100 hover:bg-slate-200 text-slate-600 p-2 rounded-lg transition-all" title="تعديل">
                                ✏️
                            </button>
                            <a href="/invoice?serial=${{e.Notes}}" target="_blank" class="opacity-0 group-hover:opacity-100 bg-blue-50 hover:bg-blue-100 text-blue-600 p-2 rounded-lg transition-all" title="عرض الفاتورة">
                                📄
                            </a>
                        </div>
                    </td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function applyFilters() {{
            const search = document.getElementById('searchClient').value.toLowerCase();
            const status = document.getElementById('filterStatus').value;
            const from = document.getElementById('dateFrom').value;
            const to = document.getElementById('dateTo').value;

            const filtered = rawData.filter(e => {{
                const matchesSearch = e.Client.toLowerCase().includes(search) || e.Project.toLowerCase().includes(search) || e.Notes.includes(search);
                const matchesStatus = status === 'all' || (status === 'Paid' && e.PaymentStatus !== 'Not Paid') || (status === 'Not Paid' && e.PaymentStatus === 'Not Paid');
                
                let matchesDate = true;
                if (from || to) {{
                    const eDate = new Date(e.Date);
                    if (from && eDate < new Date(from)) matchesDate = false;
                    if (to && eDate > new Date(to)) matchesDate = false;
                }}

                return matchesSearch && matchesStatus && matchesDate;
            }});

            renderTable(filtered.reverse());
        }}

        // Listeners
        document.getElementById('searchClient').addEventListener('input', applyFilters);
        document.getElementById('filterStatus').addEventListener('change', applyFilters);
        document.getElementById('dateFrom').addEventListener('change', applyFilters);
        document.getElementById('dateTo').addEventListener('change', applyFilters);

        // Init Chart
        const ctx = document.getElementById('growthChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(chart_labels)},
                datasets: [{{
                    label: 'الإيرادات الشهرية (د.ك)',
                    data: {json.dumps(chart_values)},
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#2563eb'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    y: {{ beginAtZero: true, grid: {{ color: '#f1f5f9' }} }},
                    x: {{ grid: {{ display: false }} }}
                }},
                plugins: {{ legend: {{ display: false }} }}
            }}
        }});

        // Initial render
        renderTable([...rawData].reverse());
    </script>
</body>
</html>
    """
    
    with open("/home/ubuntu/.openclaw/workspace/atef_office/dashboard.html", "w", encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    generate_dashboard()
