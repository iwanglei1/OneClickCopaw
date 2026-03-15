import os
import sys
import subprocess
from importlib.metadata import distributions

print("正在生成 .spec 文件并打包...")

# ==========================================
# 路径
# ==========================================
import reme, copaw

reme_dir  = os.path.dirname(reme.__file__).replace("\\", "\\\\")
copaw_dir = os.path.dirname(copaw.__file__).replace("\\", "\\\\")

# ==========================================
# copy-metadata 列表
# ==========================================
packages = [dist.metadata['Name'] for dist in distributions() if dist.metadata['Name']]
copy_metadata = "\n".join([f"    '{pkg}'," for pkg in packages])

# ==========================================
# hidden-imports 列表
# ==========================================
hidden_imports = [
    "copaw",
    "copaw.cli.main",
    "copaw.app._app",
    "copaw.app.channels.console",
    "copaw.app.channels.console.channel",
    "copaw.app.channels.dingtalk",
    "copaw.app.channels.dingtalk.channel",
    "copaw.app.channels.dingtalk.constants",
    "copaw.app.channels.dingtalk.content_utils",
    "copaw.app.channels.dingtalk.handler",
    "copaw.app.channels.dingtalk.markdown",
    "copaw.app.channels.dingtalk.utils",
    "copaw.app.channels.discord_",
    "copaw.app.channels.discord_.channel",
    "copaw.app.channels.feishu",
    "copaw.app.channels.feishu.channel",
    "copaw.app.channels.feishu.constants",
    "copaw.app.channels.feishu.utils",
    "copaw.app.channels.imessage",
    "copaw.app.channels.imessage.channel",
    "copaw.app.channels.matrix",
    "copaw.app.channels.matrix.channel",
    "copaw.app.channels.mattermost",
    "copaw.app.channels.mattermost.channel",
    "copaw.app.channels.mqtt",
    "copaw.app.channels.mqtt.channel",
    "copaw.app.channels.qq",
    "copaw.app.channels.qq.channel",
    "copaw.app.channels.telegram",
    "copaw.app.channels.telegram.channel",
    "copaw.app.channels.telegram.format_html",
    "copaw.app.channels.voice",
    "copaw.app.channels.voice.channel",
    "copaw.app.channels.voice.conversation_relay",
    "copaw.app.channels.voice.session",
    "copaw.app.channels.voice.twilio_manager",
    "copaw.app.channels.voice.twiml",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.loops.asyncio",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
]
hidden_imports_str = "\n".join([f"    '{m}'," for m in hidden_imports])

# ==========================================
# 生成 .spec 文件内容
# ==========================================
spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import copy_metadata

block_cipher = None

# copy-metadata for all installed packages
all_metadata = []
packages = [
{copy_metadata}
]
for pkg in packages:
    try:
        all_metadata += copy_metadata(pkg)
    except Exception:
        pass

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('{reme_dir}', 'reme'),
        ('{copaw_dir}', 'copaw'),
    ] + all_metadata,
    hiddenimports=[
{hidden_imports_str}
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    onefile=True,
)
"""

# ==========================================
# 写入 spec 文件并调用 pyinstaller
# ==========================================
spec_path = "main.spec"
with open(spec_path, "w", encoding="utf-8") as f:
    f.write(spec_content)

print(f"已生成 {spec_path}，开始打包...\n")
subprocess.run([sys.executable, "-m", "PyInstaller", spec_path], check=True)
print("\n打包完成！请去 dist 文件夹下查看生成的 main.exe")