
import os
import csv
from pathlib import Path
from speechbrain.inference.ASR import EncoderDecoderASR
from tqdm import tqdm
import librosa
import soundfile as sf
from audio_splitter import split_audio

# 本地模型路径
LOCAL_MODEL_PATH = r".\pretrained_models\asr-crdnn-rnnlm-librispeech"
MAX_AUDIO_DURATION = 10  # 单段最大时长（秒）

# 扫描当前目录的所有音频文件（支持多种格式）
current_dir = Path(".")
audio_files = sorted(list(current_dir.glob("*.wav")) + 
                     list(current_dir.glob("*.mp3")) +
                     list(current_dir.glob("*.flac")) +
                     list(current_dir.glob("*.m4a")) +
                     list(current_dir.glob("*.ogg")))

if not audio_files:
    print("❌ 当前目录下没有找到音频文件")
    exit(1)

print(f"📁 找到 {len(audio_files)} 个音频文件\n")

# 加载模型一次
print("🔧 加载模型中...")
asr_model = EncoderDecoderASR.from_hparams(
    source=LOCAL_MODEL_PATH,
    savedir=LOCAL_MODEL_PATH,
    run_opts={"device": "cpu"}
)
print("✅ 模型加载完成\n")

def process_audio(audio, sr, max_duration=MAX_AUDIO_DURATION):
    """处理音频：转换格式并分割长音频"""
    audio_duration = len(audio) / sr
    temp_files = []
    
    if audio_duration > max_duration:
        print(f"  💔 长音频 ({audio_duration:.2f}s > {max_duration}s)，分割处理...")
        segments, _ = split_audio(audio, max_duration=max_duration, sample_rate=sr, overlap=0.5)
        
        for i, segment in enumerate(segments):
            temp_file = f"_temp_segment_{i}.wav"
            sf.write(temp_file, segment, sr)
            temp_files.append(temp_file)
    else:
        temp_file = "_temp.wav"
        sf.write(temp_file, audio, sr)
        temp_files.append(temp_file)
    
    return temp_files

# 处理所有音频文件
results = []
errors = []

print("🎙️  开始识别语音...\n")
for audio_file in tqdm(audio_files, desc="处理中", unit="文件"):
    try:
        file_name = final_result
        })
        
        print(f"  结果: {final_
        # 处理音频（可能需要分割）
        temp_files = process_audio(audio, sr)
        
        # 识别所有片段
        segment_results = []
        for temp_file in temp_files:
            try:
                result = asr_model.transcribe_file(temp_file)
                segment_results.append(result)
            except Exception as e:
                print(f"  ⚠️ 片段识别失败: {str(e)}")
                segment_results.append(f"[失败: {str(e)}]")
        
        # 合并结果
        final_result = " ".join(segment_results)
        
        # 清理临时文件
        for temp_file in temp_files:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        
        results.append({
            "文件名": file_name,
            "识别结果": result
        })
        
        print(f"✓ {file_name}")
        print(f"  结果: {result}\n")
        
    except Exception as e:
        error_msg = f"{audio_file.name}: {str(e)}"
        errors.append(error_msg)
        print(f"✗ {audio_file.name}")
        print(f"  错误: {str(e)}\n")

# 输出统计信息
print("=" * 60)
print(f"📊 处理完成！")
print(f"✅ 成功: {len(results)} 个文件")
print(f"❌ 失败: {len(errors)} 个文件")
print("=" * 60)

# 保存结果到 CSV
output_file = "speech_recognition_results.csv"
if results:
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["文件名", "识别结果"])
        writer.writeheader()
        writer.writerows(results)
    print(f"\n📄 结果已保存到: {output_file}")

# 保存错误日志
if errors:
    error_file = "speech_recognition_errors.log"
    with open(error_file, "w", encoding="utf-8") as f:
        f.write("识别失败的文件列表\n")
        f.write("=" * 50 + "\n")
        for error in errors:
            f.write(error + "\n")
    print(f"⚠️  错误日志已保存到: {error_file}")