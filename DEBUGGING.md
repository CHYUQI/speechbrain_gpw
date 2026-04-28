# MP3 识别张量大小不匹配问题 - 完整解决方案

## 问题诊断流程

### 1. 启用详细日志
已在 `web.py` 中添加日志记录。启动应用时查看控制台输出：

```bash
python web.py
```

注意以下日志信息：
- `处理音频...` - 检查librosa是否成功加载MP3
- `加载成功 - 采样率: XXHz` - 查看原始采样率
- `识别完成: ...` - 最终的识别结果

### 2. 测试MP3处理
运行MP3测试脚本：

```bash
python test_mp3_processing.py
```

输出应该显示：
- ✓ MP3创建成功
- ✓ librosa加载成功
- ✓ 重采样成功

### 3. 测试完整ASR流程
运行ASR推理测试：

```bash
python test_asr_inference.py
```

### 4. 真实MP3文件测试
如果有真实的MP3文件，可以这样测试：

```python
from web import process_audio
from speechbrain.inference.ASR import EncoderDecoderASR

# 处理你的MP3文件
model = EncoderDecoderASR.from_hparams(
    source=r".\pretrained_models\asr-crdnn-rnnlm-librispeech",
    savedir=r".\pretrained_models\asr-crdnn-rnnlm-librispeech",
    run_opts={"device": "cpu"}
)

# 处理音频
processed = process_audio("your_file.mp3")

# 识别
result = model.transcribe_file(processed)
print(result)
```

## 常见问题和解决方案

### 问题1: FFmpeg 未找到
**症状**: `librosa.load()` 无法打开MP3
**解决**:
```bash
# Windows - 使用Chocolatey
choco install ffmpeg

# 或从官网下载: https://ffmpeg.org/download.html
```

### 问题2: 音频长度不匹配
**症状**: "tensor a (2551) must match tensor b (2500)"
**原因**: 模型期望特定长度的输入
**解决**: 已在 `process_audio()` 中处理 - 统一转换为16kHz

### 问题3: 临时文件未清理
**症状**: `uploads` 文件夹中有 `*_temp.wav` 残留
**修复**: web.py已添加异常处理自动清理

### 问题4: MP3编码问题
**症状**: librosa无法解码某些MP3
**解决方案**:
```python
# 在process_audio中添加更多错误处理
try:
    audio, sr = librosa.load(filepath, sr=target_sr, mono=True)
except Exception as e:
    # 尝试用audioread的其他后端
    audio, sr = librosa.load(filepath, sr=target_sr, mono=True, 
                             backend='audioread')
```

## 调试技巧

### 1. 查看日志文件
web.py会输出详细日志，运行时注意控制台输出

### 2. 测试特定MP3文件
```python
import librosa
import numpy as np

file = "your_file.mp3"
try:
    audio, sr = librosa.load(file, sr=None, mono=True)
    print(f"成功加载: {len(audio)} 样本, {sr}Hz")
    print(f"统计: min={np.min(audio):.4f}, max={np.max(audio):.4f}, mean={np.mean(np.abs(audio)):.4f}")
except Exception as e:
    print(f"失败: {e}")
```

### 3. 检查模型输入要求
查看 `pretrained_models/asr-crdnn-rnnlm-librispeech/hyperparams.yaml`：
- 查看期望的采样率
- 查看特征提取参数

## 最终检查清单

- [ ] FFmpeg 已安装
- [ ] librosa 已安装 (`pip install librosa`)
- [ ] audioread 已安装 (`pip install audioread`)
- [ ] 模型文件完整 (`pretrained_models/asr-crdnn-rnnlm-librispeech/`)
- [ ] 测试脚本都通过了
- [ ] web.py 能正常启动且无错误

## 如果还是不行

请收集以下信息：

1. **完整的错误堆栈**:
   ```python
   import traceback
   try:
       # 你的代码
   except Exception as e:
       traceback.print_exc()
   ```

2. **MP3文件信息**:
   ```bash
   ffprobe your_file.mp3
   ```

3. **Python环境**:
   ```bash
   pip list | grep -E "librosa|soundfile|torch|speechbrain"
   ```

4. **系统信息**:
   ```bash
   python --version
   ffmpeg -version
   ```

---

**关键点**: 所有的音频都会被统一处理为 **16kHz 单声道 WAV** 再送入模型，这应该解决张量大小不匹配问题。
