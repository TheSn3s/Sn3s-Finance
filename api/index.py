from flask import Flask, request, jsonify, send_file
import os
import json
from datetime import datetime
from supabase import create_client, Client
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Environment Variables from Vercel
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

@app.route('/api/get', methods=['GET'])
def get_all():
    try:
        res = supabase.table('invoices').select("*").order('Date', desc=True).execute()
        return jsonify(res.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/add', methods=['POST'])
def add_new():
    try:
        data = request.json
        # Generate next serial if not provided
        if not data.get('Notes'):
            res_last = supabase.table('invoices').select("Notes").order("Notes", desc=True).limit(1).execute()
            last_val = int(res_last.data[0]['Notes']) if res_last.data else 0
            data['Notes'] = f"{last_val + 1:03d}"
            
        res = supabase.table('invoices').insert(data).execute()
        return jsonify({"status": "success", "data": res.data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/invoice', methods=['GET'])
def get_pdf():
    serial = request.args.get('serial')
    # سيقوم هذا الجزء باسترجاع بيانات الفاتورة من Supabase وبناء الـ HTML
    res = supabase.table('invoices').select("*").eq('Notes', serial).single().execute()
    if not res.data:
        return "Invoice not found", 404
    # (هنا سأضع كود الـ HTML الخاص بالفاتورة الذي أصلحناه سابقاً)
    return f"<h1>Invoice #{serial} for {res.data['Client']}</h1><p>Work in progress - Building template...</p>"

if __name__ == "__main__":
    app.run()
