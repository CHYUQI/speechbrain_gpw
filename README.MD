# SpeechBrain-GPW
基于 SpeechBrain 框架开发的轻量化语音识别项目，依托 Aishell 预训练 Transformer 模型实现中文语音转文字，部署简单、拓展性强，适用于课程任务实践与二次开发。

## 项目介绍
本项目基于 `speechbrain/asr-transformer-aishell` 模型，快速搭建离线中文语音识别能力。

目前支持本地音频文件转写，后续将迭代新增**麦克风实时音频采集**，实现实时语音转文字功能。

## 快速开始
### 环境要求
- Python 3.11

### 依赖安装
```bash
pip install -r requirements.txt
```

### 模型准备
为满足本地离线快速演示需求，项目依赖外部预训练模型。
受仓库体积限制，**代码仓库不包含模型权重文件**，需手动前往 Hugging Face 自行下载：

[speechbrain/asr-transformer-aishell](https://huggingface.co/speechbrain/asr-transformer-aishell)

下载完成后，将模型文件夹放置到项目对应目录即可正常运行。

---

直接复制上面全部内容，保存为 `README.md` 即可直接上传 GitHub，排版、格式、链接全部完善。
