import os
import supabase
from flask import Flask, request, jsonify

# هذه القيم سيتم استبدالها بـ Environment Variables في Vercel
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

app = Flask(__name__)
db = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/add', methods=['POST'])
def add_invoice():
    data = request.json
    # إضافة الفاتورة لقاعدة البيانات
    res = db.table('invoices').insert(data).execute()
    return jsonify(res.data)

@app.route('/api/get', methods=['GET'])
def get_invoices():
    res = db.table('invoices').select("*").order('Date', desc=True).execute()
    return jsonify(res.data)
