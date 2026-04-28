"""检查librosa是否能加载MP3"""
import librosa
import os

print("=" * 60)
print("🔍 检查 librosa MP3 支持")
print("=" * 60)

# 检查可用的音频后端
print("\n📚 检查音频后端...")
try:
    import soundfile
    print("✓ soundfile 已安装")
except ImportError:
    print("❌ soundfile 未安装")

try:
    import audioread
    print("✓ audioread 已安装")
except ImportError:
    print("❌ audioread 未安装 (需要ffmpeg支持)")

# 尝试检查ffmpeg
print("\n🔧 检查 FFmpeg...")
result = os.system("ffmpeg -version > nul 2>&1")
if result == 0:
    print("✓ FFmpeg 已安装")
else:
    print("❌ FFmpeg 未安装")
    print("\n⚠️  建议: 安装ffmpeg来支持MP3/OGG/FLAC等格式")
    print("   - Windows: choco install ffmpeg 或从 https://ffmpeg.org 下载")
    print("   - Python: pip install audioread")

# 显示librosa支持的后端
print("\n📋 librosa 当前配置:")
print(f"librosa 版本: {librosa.__version__}")

print("\n" + "=" * 60)
