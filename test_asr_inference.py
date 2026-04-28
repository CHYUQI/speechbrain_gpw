"""测试完整的ASR流程"""
import sys
import os
import librosa
import soundfile as sf
import numpy as np
from speechbrain.inference.ASR import EncoderDecoderASR

def test_asr_with_different_formats():
    """测试不同音频格式的ASR识别"""
    print("=" * 60)
    print("🔍 测试 ASR 模型推理")
    print("=" * 60)
    
    # 模型路径
    model_path = r".\pretrained_models\asr-crdnn-rnnlm-librispeech"
    
    # 1. 加载模型
    print("\n🔧 加载模型...")
    try:
        asr_model = EncoderDecoderASR.from_hparams(
            source=model_path,
            savedir=model_path,
            run_opts={"device": "cpu"}
        )
        print("✅ 模型加载成功")
    except Exception as e:
        print(f"❌ 模型加载失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # 2. 创建测试音频
    print("\n📝 创建测试音频...")
    sr = 16000
    duration = 3
    t = np.linspace(0, duration, int(sr * duration))
    # 创建一些音频（白噪声）
    audio_16k = 0.05 * np.random.randn(int(sr * duration))
    
    sf.write("test_16k.wav", audio_16k, sr)
    print("✓ 创建 test_16k.wav (16kHz)")
    
    # 3. 直接在16kHz上测试
    print("\n🎙️ 测试16kHz WAV文件...")
    try:
        result = asr_model.transcribe_file("test_16k.wav")
        print(f"✓ 识别成功: {result}")
    except Exception as e:
        print(f"❌ 识别失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 4. 测试处理后的音频
    print("\n🎙️ 测试处理后的音频...")
    try:
        # 加载22kHz音频
        audio_22k = librosa.util.normalize(audio_16k[:int(22050*2)])
        sf.write("test_22k.wav", audio_22k, 22050)
        print("✓ 创建 test_22k.wav (22kHz)")
        
        # 处理：加载并重采样到16kHz
        audio_processed, sr_processed = librosa.load("test_22k.wav", sr=16000, mono=True)
        print(f"  ✓ 重采样: {audio_processed.shape}, {sr_processed}Hz")
        
        # 保存处理后的文件
        sf.write("test_22k_processed.wav", audio_processed, sr_processed)
        
        # 用处理后的文件识别
        result = asr_model.transcribe_file("test_22k_processed.wav")
        print(f"✓ 识别成功: {result}")
        
        os.remove("test_22k.wav")
        os.remove("test_22k_processed.wav")
        
    except Exception as e:
        print(f"❌ 识别失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 5. 清理
    print("\n🧹 清理测试文件...")
    os.remove("test_16k.wav")
    print("✓ 清理完成")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)
    return True

if __name__ == "__main__":
    test_asr_with_different_formats()
