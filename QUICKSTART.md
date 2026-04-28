# 快速起步指南

## 问题已解决 ✅

**MP3 识别错误** `tensor a (2551) must match tensor b (2500)` 已彻底解决！

## 原因
- MP3 是 102 秒长音频
- 模型最多支持 ~10 秒音频
- 解决方案: **自动分割处理**

## 修复内容

### 新增文件
```
audio_splitter.py       - 音频分割模块
SOLUTION_SUMMARY.md     - 完整解决方案文档
DEBUGGING.md            - 调试指南
```

### 更新文件
```
web.py                  - 支持自动音频分割
index.py                - 支持自动音频分割
requirements.txt        - 添加了 librosa
```

## 立即使用

### 1️⃣ 启动 Web 服务

```bash
python web.py
```

然后访问 `http://localhost:8080`

上传您的 MP3 文件，自动处理！

### 2️⃣ 批量处理

```bash
# 将音频文件放在项目根目录
cp your_files/*.mp3 .

# 运行处理
python index.py

# 查看结果
cat speech_recognition_results.csv
```

## 工作原理

```
长音频 (102秒)
    ↓
加载并重采样到 16kHz
    ↓
检测: 时长 > 10秒?
    ↓
分割成 10 秒片段 (50%重叠)
    ↓
逐段送入模型识别
    ↓
合并所有片段结果
    ↓
✅ 完成!
```

## 支持的格式

✅ MP3 (测试过，有效)
✅ WAV
✅ FLAC
✅ M4A  
✅ OGG

## 主要改进

| 原问题 | 新方案 |
|--------|--------|
| 长MP3无法识别 | ✅ 自动分割 |
| 张量大小不匹配 | ✅ 完全解决 |
| 识别中断 | ✅ 稳定运行 |
| 无合并结果 | ✅ 智能合并 |

## 测试验证

使用 Bus Sample 00.mp3 (102秒) 成功通过测试:
- ✅ 加载完成
- ✅ 分割成 20 段
- ✅ 逐段识别成功
- ✅ 结果合并正常

## 常见问题

**Q: 为什么分割成 10 秒?**
A: 这是模型的最大支持长度，超过会报错

**Q: MP3 能导入吗?**
A: 需要 FFmpeg。如果提示错误，安装:
```bash
# Windows
choco install ffmpeg

# 或从官网下载: https://ffmpeg.org/download.html
```

**Q: 识别结果能有多准?**
A: 取决于模型和音频质量。LibriSpeech 模型对英文最优

## 文档

详细文档: [SOLUTION_SUMMARY.md](SOLUTION_SUMMARY.md)
调试指南: [DEBUGGING.md](DEBUGGING.md)

---

**现在完全可以使用了！** 🚀
