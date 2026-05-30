# app.py - 后端主文件
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os
from collections import defaultdict

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# 数据存储文件
DATA_FILE = 'finance_data.json'

# 默认数据
def default_data():
    return {
        'transactions': [],
        'monthly_budget': 3000
    }

def load_data():
    """从文件加载数据"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default_data()
    return default_data()

def save_data(data):
    """保存数据到文件"""
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# 辅助函数
def get_current_year_month():
    now = datetime.now()
    return f"{now.year}-{str(now.month).zfill(2)}"

def get_record_month(date_str):
    """从日期字符串解析出 年-月，兼容 YYYY-MM-DD、ISO 格式、时间戳等"""
    if not date_str:
        return get_current_year_month()
    try:
        # 支持 ISO 格式（包含时间部分）的日期字符串
        date_part = str(date_str).split('T')[0]
        d = datetime.strptime(date_part, '%Y-%m-%d')
        return f"{d.year}-{str(d.month).zfill(2)}"
    except Exception:
        try:
            # 支持时间戳（秒或毫秒）
            ts = float(date_str)
            if ts > 1e12:  # 可能是毫秒
                ts = ts / 1000.0
            d = datetime.fromtimestamp(ts)
            return f"{d.year}-{str(d.month).zfill(2)}"
        except Exception:
            return get_current_year_month()

def filter_current_month(transactions):
    current_ym = get_current_year_month()
    return [t for t in transactions if get_record_month(t.get('date')) == current_ym]

def get_monthly_stats(transactions):
    """获取本月统计"""
    month_txs = filter_current_month(transactions)
    total_income = sum(float(t.get('amount', 0)) for t in month_txs if t.get('type') == 'income')
    total_expense = sum(float(t.get('amount', 0)) for t in month_txs if t.get('type') == 'expense')
    
    # 按类别统计支出
    category_map = defaultdict(float)
    for t in month_txs:
        if t.get('type') == 'expense':
            category_map[t.get('category', '其他')] += float(t.get('amount', 0))
    
    return {
        'total_income': total_income,
        'total_expense': total_expense,
        'category_stats': dict(category_map),
        'transaction_count': len(month_txs)
    }

def generate_advice(transactions, budget):
    """生成智能建议"""
    month_txs = filter_current_month(transactions)
    expenses = [t for t in month_txs if t.get('type') == 'expense']
    total_expense = sum(float(e.get('amount', 0)) for e in expenses)
    
    # 类别统计
    cat_map = defaultdict(float)
    for e in expenses:
        cat_map[e.get('category', '其他')] += float(e.get('amount', 0))
    
    # 找出最大支出类别
    max_cat = max(cat_map.items(), key=lambda x: x[1]) if cat_map else (None, 0)
    
    advice_parts = []
    
    # 预算相关建议（避免除以零）
    try:
        budget_val = float(budget) if budget is not None else 0.0
    except Exception:
        budget_val = 0.0

    if budget_val > 0:
        if total_expense > budget_val:
            advice_parts.append(f"⚠️ 本月已超出预算 ¥{total_expense - budget_val:.2f}，超出{((total_expense-budget_val)/budget_val*100):.1f}%")
        elif total_expense > budget_val * 0.85:
            advice_parts.append(f"⚠️ 目前支出已达预算的{(total_expense/budget_val*100):.1f}%，接近上限")
        elif total_expense > 0:
            advice_parts.append(f"✅ 支出在预算范围内，剩余 ¥{budget_val - total_expense:.2f}")
    else:
        if total_expense > 0:
            advice_parts.append(f"ℹ️ 未设置有效预算，当前支出 ¥{total_expense:.2f}")
    
    # 类别建议
    if max_cat[0]:
        cat = max_cat[0]
        amount = max_cat[1]
        advice_parts.append(f"📊 主要消费类别：{cat} (¥{amount:.2f})")
        
        cat_suggestions = {
            '餐饮': '餐饮支出占比较高，可尝试减少外卖、增加自制餐食',
            '娱乐': '娱乐开销偏高，建议设定每月娱乐预算上限',
            '交通': '交通费用较高，可考虑公共交通或拼车',
            '学习': '学习投资值得鼓励，但可多利用免费资源',
            '住房': '住房是固定支出，可关注节能节电减少杂费'
        }
        if cat in cat_suggestions:
            advice_parts.append(f"💡 {cat_suggestions[cat]}")
    
    # 收入和储蓄建议
    total_income = sum(float(t.get('amount', 0)) for t in month_txs if t.get('type') == 'income')
    if total_income > 0:
        net = total_income - total_expense
        if net < 0:
            advice_parts.append(f"📉 本月入不敷出，建议削减「{max_cat[0] if max_cat[0] else '非必要'}」开支")
        elif net < 500:
            advice_parts.append(f"💰 本月结余较少，建议将预算降低5%-10%，增加储蓄")
        else:
            advice_parts.append(f"🎯 财务状况良好，建议将结余的20%作为应急基金")
    else:
        advice_parts.append(f"📝 未记录收入，建议录入收入项以便更好规划")
    
    # 趋势分析（与上月对比）
    current_ym = get_current_year_month()
    prev_month_expense = 0
    for t in transactions:
        tx_month = get_record_month(t.get('date'))
        year, month = map(int, current_ym.split('-'))
        prev_year = year if month > 1 else year - 1
        prev_month = month - 1 if month > 1 else 12
        prev_ym = f"{prev_year}-{str(prev_month).zfill(2)}"
        if tx_month == prev_ym and t.get('type') == 'expense':
            prev_month_expense += float(t.get('amount', 0))
    
    if prev_month_expense > 0:
        diff = total_expense - prev_month_expense
        if diff > 0:
            advice_parts.append(f"📈 比上月增加 ¥{diff:.2f}，注意控制开支")
        else:
            advice_parts.append(f"📉 比上月减少 ¥{abs(diff):.2f}，继续保持")
    
    return ' | '.join(advice_parts) if advice_parts else '继续记账，获取更多个性化建议'

# ========== API 路由 ==========

@app.route('/')
def index():
    """首页"""
    return send_from_directory('templates', 'index.html')

@app.route('/sw.js')
def service_worker():
    """PWA Service Worker — 必须从根路径提供以获取正确 scope"""
    return send_from_directory('templates', 'sw.js', mimetype='application/javascript')

@app.route('/static/<path:filename>')
def static_files(filename):
    """PWA 静态资源（manifest.json、图标等）"""
    return send_from_directory('templates', filename)

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """获取所有交易记录"""
    data = load_data()
    return jsonify({
        'success': True,
        'transactions': data['transactions']
    })

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    """添加交易记录"""
    data = load_data()
    transaction = request.json
    
    # 验证必填字段
    required = ['type', 'amount', 'category', 'date']
    for field in required:
        if field not in transaction:
            return jsonify({'success': False, 'error': f'缺少字段: {field}'}), 400
    # 确保 amount 为数字
    try:
        transaction['amount'] = float(transaction.get('amount', 0))
    except Exception:
        return jsonify({'success': False, 'error': '金额格式无效'}), 400

    # 验证 type
    if transaction.get('type') not in ('income', 'expense'):
        return jsonify({'success': False, 'error': 'type 必须为 "income" 或 "expense"'}), 400

    # 生成整数 ID 和时间戳
    transaction['id'] = int(datetime.now().timestamp() * 1000) + (abs(hash(str(transaction))) % 1000)
    transaction['created_at'] = datetime.now().isoformat()

    data['transactions'].append(transaction)
    save_data(data)
    
    return jsonify({'success': True, 'transaction': transaction})

@app.route('/api/transactions/<int:tx_id>', methods=['DELETE'])
def delete_transaction(tx_id):
    """删除交易记录"""
    data = load_data()
    original_len = len(data['transactions'])
    data['transactions'] = [t for t in data['transactions'] if t.get('id') != tx_id]
    
    if len(data['transactions']) == original_len:
        return jsonify({'success': False, 'error': '记录不存在'}), 404
    
    save_data(data)
    return jsonify({'success': True})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取统计数据"""
    data = load_data()
    stats = get_monthly_stats(data['transactions'])
    return jsonify({
        'success': True,
        'stats': stats
    })

@app.route('/api/budget', methods=['GET'])
def get_budget():
    """获取月度预算"""
    data = load_data()
    return jsonify({
        'success': True,
        'budget': data.get('monthly_budget', 3000)
    })

@app.route('/api/budget', methods=['PUT'])
def update_budget():
    """更新月度预算"""
    data = load_data()
    new_budget = request.json.get('budget')
    
    if new_budget is None or new_budget < 0:
        return jsonify({'success': False, 'error': '预算金额无效'}), 400
    
    data['monthly_budget'] = float(new_budget)
    save_data(data)
    
    return jsonify({'success': True, 'budget': data['monthly_budget']})

@app.route('/api/advice', methods=['GET'])
def get_advice():
    """获取智能建议"""
    data = load_data()
    advice = generate_advice(data['transactions'], data.get('monthly_budget', 3000))
    return jsonify({
        'success': True,
        'advice': advice
    })

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """获取仪表板汇总数据"""
    data = load_data()
    transactions = data['transactions']
    budget = data.get('monthly_budget', 3000)
    
    month_txs = filter_current_month(transactions)
    total_income = sum(t['amount'] for t in month_txs if t['type'] == 'income')
    total_expense = sum(t['amount'] for t in month_txs if t['type'] == 'expense')
    
    # 类别统计（用于图表）
    cat_map = defaultdict(float)
    for t in month_txs:
        if t['type'] == 'expense':
            cat_map[t['category']] += t['amount']
    
    # 最近交易（最新10条）
    recent = sorted(transactions, key=lambda x: x.get('date', ''), reverse=True)[:10]
    
    return jsonify({
        'success': True,
        'dashboard': {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': total_income - total_expense,
            'budget': budget,
            'budget_remaining': budget - total_expense,
            'budget_percent': min(100, (total_expense / budget * 100) if budget > 0 else 0),
            'category_stats': dict(cat_map),
            'recent_transactions': recent,
            'advice': generate_advice(transactions, budget)
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)