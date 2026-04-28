"""
音频分割处理模块
处理超长音频的分割和识别
"""
import numpy as np
from typing import List, Tuple

def calculate_max_samples(max_duration_seconds=10, sample_rate=16000):
    """
    计算模型能处理的最大样本数
    
    Args:
        max_duration_seconds: 模型能处理的最大时长（秒）
        sample_rate: 采样率
    
    Returns:
        最大样本数
    """
    return int(max_duration_seconds * sample_rate)

def split_audio(audio: np.ndarray, max_duration=10, sample_rate=16000, overlap=0.5):
    """
    分割长音频为多个片段
    
    Args:
        audio: 音频数据
        max_duration: 每段最大时长（秒）
        sample_rate: 采样率
        overlap: 重叠比例（0-1）
    
    Returns:
        音频片段列表和对应的起始时间
    """
    max_samples = calculate_max_samples(max_duration, sample_rate)
    overlap_samples = int(max_samples * overlap)
    stride = max_samples - overlap_samples
    
    segments = []
    start_times = []
    
    for i in range(0, len(audio), stride):
        end = min(i + max_samples, len(audio))
        segment = audio[i:end]
        
        # 如果最后一段太短，丢弃它
        if len(segment) < max_samples * 0.5:
            break
        
        start_time = i / sample_rate
        segments.append(segment)
        start_times.append(start_time)
    
    return segments, start_times

def test_split_audio():
    """测试音频分割"""
    print("=" * 60)
    print("🔍 测试音频分割功能")
    print("=" * 60)
    
    # 创建102秒的音频
    sr = 16000
    duration = 102
    total_samples = int(sr * duration)
    audio = np.random.randn(total_samples)
    
    print(f"\n原始音频:")
    print(f"  - 时长: {duration}秒")
    print(f"  - 样本数: {total_samples}")
    print(f"  - 采样率: {sr}Hz")
    
    # 分割
    segments, start_times = split_audio(audio, max_duration=10, sample_rate=sr, overlap=0.5)
    
    print(f"\n分割结果 (最大10秒/段, 50%重叠):")
    print(f"  - 分段数: {len(segments)}")
    for i, (seg, start_time) in enumerate(zip(segments, start_times)):
        duration_seg = len(seg) / sr
        print(f"  [{i+1}] 起始: {start_time:.2f}s, 时长: {duration_seg:.2f}s, 样本: {len(seg)}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_split_audio()
