
import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from speechbrain.inference.ASR import EncoderDecoderASR
from werkzeug.utils import secure_filename
import librosa
import soundfile as sf
import traceback
import logging
import numpy as np
from audio_splitter import split_audio

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 配置
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"wav", "mp3", "flac", "m4a", "ogg"}
LOCAL_MODEL_PATH = r".\pretrained_models\asr-crdnn-rnnlm-librispeech"
MAX_AUDIO_DURATION = 10  # 单段最大时长（秒）

# 创建上传文件夹
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024  # 最大 100MB

# 全局模型对象
asr_model = None

def allowed_file(filename):
    """检查文件是否允许"""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def process_audio_with_splitting(filepath, target_sr=16000, max_duration=MAX_AUDIO_DURATION):
    """处理音频：加载、重采样、分割长音频"""
    temp_files = []
    try:
        logger.info(f"开始处理音频: {filepath}")
        logger.info(f"  文件大小: {os.path.getsize(filepath)} bytes")
        
        # 加载音频
        logger.info(f"  使用librosa加载文件...")
        audio, sr = librosa.load(filepath, sr=target_sr, mono=True)
        
        audio_duration = len(audio) / sr
        logger.info(f"  加载成功 - 采样率: {sr}Hz, 长度: {len(audio)} 样本 ({audio_duration:.2f}秒)")
        
        # 检查是否需要分割
        if audio_duration > max_duration:
            logger.info(f"  检测到长音频 ({audio_duration:.2f}秒 > {max_duration}秒)，执行分割...")
            segments, start_times = split_audio(audio, max_duration=max_duration, sample_rate=sr, overlap=0.5)
            logger.info(f"  分割为 {len(segments)} 段")
            
            # 保存每一段
            for i, segment in enumerate(segments):
                temp_wav_path = f"{filepath}_segment_{i}.wav"
                sf.write(temp_wav_path, segment, sr)
                temp_files.append(temp_wav_path)
                seg_duration = len(segment) / sr
                logger.info(f"    段{i+1}: 保存到 {temp_wav_path} ({seg_duration:.2f}秒)")
        else:
            # 短音频直接保存
            logger.info(f"  音频长度正常 ({audio_duration:.2f}秒)，直接保存...")
            temp_wav_path = filepath + "_temp.wav"
            sf.write(temp_wav_path, audio, sr)
            temp_files.append(temp_wav_path)
            logger.info(f"  保存到: {temp_wav_path}")
        
        logger.info(f"  处理完成，共生成 {len(temp_files)} 个临时文件")
        return temp_files
        
    except Exception as e:
        logger.error(f"音频处理失败: {str(e)}")
        logger.error(traceback.format_exc())
        # 清理已创建的临时文件
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        raise Exception(f"音频处理失败: {str(e)}")

def load_model():
    """加载模型"""
    global asr_model
    if asr_model is None:
        try:
            logger.info("🔧 加载模型中...")
            asr_model = EncoderDecoderASR.from_hparams(
                source=LOCAL_MODEL_PATH,
                savedir=LOCAL_MODEL_PATH,
                run_opts={"device": "cpu"}
            )
            logger.info("✅ 模型加载完成")
        except Exception as e:
            logger.error(f"模型加载失败: {str(e)}")
            logger.error(traceback.format_exc())
            raise
    return asr_model

def transcribe_segments(model, temp_files):
    """识别所有音频片段"""
    results = []
    logger.info(f"开始识别 {len(temp_files)} 个音频片段...")
    
    for i, temp_file in enumerate(temp_files):
        try:
            logger.info(f"  识别片段 {i+1}/{len(temp_files)}: {temp_file}")
            result = model.transcribe_file(temp_file)
            logger.info(f"    ✓ 结果: {result}")
            results.append(result)
        except Exception as e:
            logger.error(f"    ❌ 片段 {i+1} 识别失败: {str(e)}")
            results.append(f"[识别失败: {str(e)}]")
    
    # 合并结果
    final_result = " ".join(results)
    logger.info(f"最终识别结果: {final_result}")
    return final_result

@app.route("/")
def index():
    """主页"""
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload_file():
    """处理文件上传和识别"""
    temp_files = []
    filepath = None
    
    try:
        logger.info("=" * 60)
        logger.info("接收到上传请求")
        
        # 检查是否有文件
        if "file" not in request.files:
            logger.warning("请求中没有文件字段")
            return jsonify({"error": "没有文件"}), 400
        
        file = request.files["file"]
        logger.info(f"文件名: {file.filename}")
        
        if file.filename == "":
            logger.warning("文件名为空")
            return jsonify({"error": "没有选择文件"}), 400
        
        if not allowed_file(file.filename):
            logger.warning(f"文件格式不支持: {file.filename}")
            return jsonify({"error": "只支持 .wav, .mp3, .flac, .m4a, .ogg 文件"}), 400
        
        # 保存文件
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        logger.info(f"保存文件到: {filepath}")
        file.save(filepath)
        logger.info(f"文件保存完成, 大小: {os.path.getsize(filepath)} bytes")
        
        # 加载模型
        logger.info("加载模型...")
        model = load_model()
        
        # 处理音频（统一采样率、格式和分割长音频）
        logger.info("处理音频...")
        temp_files = process_audio_with_splitting(filepath)
        
        # 识别语音
        logger.info("开始语音识别...")
        result = transcribe_segments(model, temp_files)
        
        # 清理上传的文件和临时文件
        logger.info("清理临时文件...")
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"删除: {filepath}")
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                logger.info(f"删除: {temp_file}")
        
        logger.info("=" * 60)
        return jsonify({
            "success": True,
            "filename": filename,
            "result": result
        })
    
    except Exception as e:
        logger.error(f"处理过程中出错: {str(e)}")
        logger.error(traceback.format_exc())
        
        # 清理文件
        try:
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
        except:
            pass
        
        logger.info("=" * 60)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("启动Flask应用")
    logger.info(f"模型路径: {LOCAL_MODEL_PATH}")
    logger.info(f"上传文件夹: {UPLOAD_FOLDER}")
    logger.info(f"最大单段时长: {MAX_AUDIO_DURATION}秒")
    logger.info("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=8080)
