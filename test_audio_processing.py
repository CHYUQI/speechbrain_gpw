"""测试音频处理功能"""
import sys
import os
import librosa
import soundfile as sf
import numpy as np
from pathlib import Path

def test_audio_processing():
    """测试音频处理"""
    print("=" * 60)
    print("🔍 测试音频处理功能")
    print("=" * 60)
    
    # 1. 检查依赖
    print("\n✓ librosa 版本:", librosa.__version__)
    print("✓ soundfile 版本:", sf.__version__)
    
    # 2. 创建测试音频
    print("\n📝 创建测试音频文件...")
    sr = 22050
    duration = 3
    t = np.linspace(0, duration, int(sr * duration))
    audio_22k = 0.1 * np.sin(2 * np.pi * 440 * t)  # 440Hz 正弦波
    
    test_files = {
        "test_22k.wav": (audio_22k, sr),
        "test_16k.wav": (audio_22k, sr),  # 稍后会重采样
    }
    
    # 保存 22kHz WAV
    sf.write("test_22k.wav", audio_22k, sr)
    print(f"✓ 创建 test_22k.wav (采样率: {sr}Hz)")
    
    # 3. 测试 librosa 加载和重采样
    print("\n🔄 测试 librosa 加载和重采样...")
    for filename in ["test_22k.wav"]:
        print(f"\n  处理 {filename}...")
        try:
            audio, sr = librosa.load(filename, sr=16000, mono=True)
            print(f"    ✓ 加载成功")
            print(f"    - 形状: {audio.shape}")
            print(f"    - 采样率: {sr}Hz")
            print(f"    - 数据类型: {audio.dtype}")
            print(f"    - 最大值: {np.max(np.abs(audio)):.4f}")
            
            # 保存重采样后的文件
            temp_file = filename + "_temp.wav"
            sf.write(temp_file, audio, sr)
            print(f"    ✓ 保存到 {temp_file}")
            
            # 验证保存的文件
            audio2, sr2 = librosa.load(temp_file, sr=None, mono=True)
            print(f"    ✓ 验证: {audio2.shape}, {sr2}Hz")
            
            # 清理
            os.remove(temp_file)
            
        except Exception as e:
            print(f"    ❌ 错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    # 4. 测试模型路径
    print("\n🔧 检查模型路径...")
    model_path = r".\pretrained_models\asr-crdnn-rnnlm-librispeech"
    if os.path.exists(model_path):
        print(f"  ✓ 模型路径存在: {model_path}")
        files = os.listdir(model_path)
        print(f"  ✓ 包含文件: {files}")
    else:
        print(f"  ❌ 模型路径不存在: {model_path}")
        return False
    
    # 清理测试文件
    print("\n🧹 清理测试文件...")
    os.remove("test_22k.wav")
    print("✓ 清理完成")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    return True

if __name__ == "__main__":
    test_audio_processing()
