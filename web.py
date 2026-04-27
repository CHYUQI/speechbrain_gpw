
import os
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from speechbrain.inference.ASR import EncoderDecoderASR
from werkzeug.utils import secure_filename

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"wav"}
LOCAL_MODEL_PATH = r".\pretrained_models\asr-crdnn-rnnlm-librispeech"

# 创建上传文件夹
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 最大 100MB

# 全局模型对象
asr_model = None

def allowed_file(filename):
    """检查文件是否允许"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def load_model():
    """加载模型"""
    global asr_model
    if asr_model is None:
        print("🔧 加载模型中...")
        asr_model = EncoderDecoderASR.from_hparams(
            source=LOCAL_MODEL_PATH,
            savedir=LOCAL_MODEL_PATH,
            run_opts={"device": "cpu"}
        )
        print("✅ 模型加载完成")
    return asr_model

@app.route("/")
def index():
    """主页"""
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    """处理文件上传和识别"""
    try:
        # 检查是否有文件
        if "file" not in request.files:
            return jsonify({"error": "没有文件"}), 400
        
        file = request.files["file"]
        
        if file.filename == "":
            return jsonify({"error": "没有选择文件"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "只支持 .wav 文件"}), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        
        # 加载模型
        model = load_model()
        
        # 识别语音
        result = model.transcribe_file(filepath)
        
        # 清理上传的文件
        os.remove(filepath)
        
        return jsonify({
            "success": True,
            "filename": filename,
            "result": result
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)