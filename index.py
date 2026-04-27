
import os
import csv
from pathlib import Path
from speechbrain.inference.ASR import EncoderDecoderASR
from tqdm import tqdm

# 本地模型路径
LOCAL_MODEL_PATH = r".\pretrained_models\asr-crdnn-rnnlm-librispeech"

# 扫描当前目录的所有 WAV 文件
current_dir = Path(".")
wav_files = sorted(current_dir.glob("*.wav"))

if not wav_files:
    print("❌ 当前目录下没有找到 .wav 文件")
    exit(1)

print(f"📁 找到 {len(wav_files)} 个 WAV 文件\n")

# 加载模型一次
print("🔧 加载模型中...")
asr_model = EncoderDecoderASR.from_hparams(
    source=LOCAL_MODEL_PATH,
    savedir=LOCAL_MODEL_PATH,
    run_opts={"device": "cpu"}
)
print("✅ 模型加载完成\n")

# 处理所有 WAV 文件
results = []
errors = []

print("🎙️  开始识别语音...\n")
for wav_file in tqdm(wav_files, desc="处理中", unit="文件"):
    try:
        file_name = wav_file.name
        result = asr_model.transcribe_file(str(wav_file))
        
        results.append({
            "文件名": file_name,
            "识别结果": result
        })
        
        print(f"✓ {file_name}")
        print(f"  结果: {result}\n")
        
    except Exception as e:
        error_msg = f"{wav_file.name}: {str(e)}"
        errors.append(error_msg)
        print(f"✗ {wav_file.name}")
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