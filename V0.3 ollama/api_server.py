from flask import Flask, request, jsonify
from agent0.8 import OllamaClient
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/image', methods=['POST'])
def analyze_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    # 保存临时文件
    temp_path = f"temp_{file.filename}"
    file.save(temp_path)
    # 调用 OllamaClient 进行分析
    client = OllamaClient(model_name="qwen2.5vl:7b")
    result = client.getimageinfo(temp_path)
    os.remove(temp_path)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
