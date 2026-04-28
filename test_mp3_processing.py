"""测试MP3处理"""
import os
import sys
import numpy as np
import librosa
import soundfile as sf

def test_mp3_processing():
    """测试MP3文件的完整处理流程"""
    print("=" * 60)
    print("🔍 测试 MP3 处理完整流程")
    print("=" * 60)
    
    # 1. 创建测试WAV
    print("\n1️⃣ 创建测试音频...")
    sr = 16000
    duration = 2
    t = np.linspace(0, duration, int(sr * duration))
    audio = 0.1 * np.sin(2 * np.pi * 440 * t)
    
    wav_file = "test_source.wav"
    mp3_file = "test_source.mp3"
    
    sf.write(wav_file, audio, sr)
    print(f"✓ 创建 {wav_file}")
    
    # 2. 转换为MP3
    print("\n2️⃣ 使用FFmpeg转换为MP3...")
    cmd = f'ffmpeg -i "{wav_file}" -q:a 9 -y "{mp3_file}" 2>nul'
    ret = os.system(cmd)
    if ret == 0 and os.path.exists(mp3_file):
        print(f"✓ 创建 {mp3_file}")
    else:
        print(f"❌ 无法创建MP3")
        return False
    
    # 3. 用librosa加载MP3
    print("\n3️⃣ 用librosa加载MP3...")
    try:
        audio_loaded, sr_loaded = librosa.load(mp3_file, sr=None, mono=True)
        print(f"✓ 加载成功")
        print(f"  - 原始采样率: {sr_loaded}Hz")
        print(f"  - 长度: {len(audio_loaded)} 样本")
    except Exception as e:
        print(f"❌ 加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 4. 重采样到16kHz
    print("\n4️⃣ 重采样到16kHz...")
    try:
        audio_resampled, sr_resampled = librosa.load(mp3_file, sr=16000, mono=True)
        print(f"✓ 重采样成功")
        print(f"  - 目标采样率: {sr_resampled}Hz")
        print(f"  - 重采样后长度: {len(audio_resampled)} 样本")
    except Exception as e:
        print(f"❌ 重采样失败: {e}")
        return False
    
    # 5. 保存为临时WAV
    print("\n5️⃣ 保存为临时WAV...")
    temp_wav = mp3_file + "_temp.wav"
    try:
        sf.write(temp_wav, audio_resampled, sr_resampled)
        print(f"✓ 保存到 {temp_wav}")
        
        # 验证
        audio_verify, sr_verify = librosa.load(temp_wav, sr=None, mono=True)
        print(f"  ✓ 验证: {len(audio_verify)} 样本, {sr_verify}Hz")
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False
    
    # 6. 清理
    print("\n🧹 清理...")
    for f in [wav_file, mp3_file, temp_wav]:
        if os.path.exists(f):
            os.remove(f)
            print(f"✓ 删除 {f}")
    
    print("\n" + "=" * 60)
    print("✅ MP3处理测试通过！")
    print("=" * 60)
    return True

if __name__ == "__main__":
    test_mp3_processing()
