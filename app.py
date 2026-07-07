from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def proxy():
    data = request.json
    # 前端会传 messages, api_url, api_key
    messages = data.get('messages')
    api_url = data.get('api_url')
    api_key = data.get('api_key')
    
    if not api_url or not api_key:
        return jsonify({"error": "请先配置 API URL 和 Key"}), 400
    
    # 确保 URL 以 /chat/completions 结尾
    if not api_url.endswith('/chat/completions'):
        api_url = api_url.rstrip('/') + '/chat/completions'
    
    headers = {
        "Authorization": "Bearer " + api_key,
        "Content-Type": "application/json"
    }
    
    # 如果前端传了 model，也可以用，否则默认 gemini-2.5-pro
    model = data.get('model', 'gemini-2.5-pro')
    payload = {
        "model": model,
        "messages": messages,
        "stream": False
    }
    
    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()  # 如果请求失败（如4xx或5xx），则抛出异常
        return jsonify(resp.json()), resp.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))