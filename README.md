# OneClickCopaw

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/PySide6-GUI-green.svg" alt="PySide6">
  <img src="https://img.shields.io/badge/Platform-Windows-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

<p align="center">
  <strong>一键启动 Copaw 桌面环境的图形化工具</strong>
</p>

---

## 安装与使用

### 方式一：下载 EXE 文件（推荐）

> 适合不想安装 Python 环境的用户

1. 点击仓库右侧的 **Releases** 或直接访问 [Releases 页面](https://github.com/iwanglei1/OneClickCopaw/releases)
2. 下载最新版本的 `main.exe` 文件
3. 双击运行即可

**就是这么简单！** 无需安装 Python，无需配置环境，一键启动。

### 方式二：学习如何打包

> 适合想学习如何将 Copaw 打包成一键安装包的高级用户

详见下方 [打包教程](#打包教程) 章节。

---

## 功能特点

- **一键初始化** - 自动执行 `copaw init --defaults --accept-security`
- **一键启动** - 自动启动 Copaw 桌面环境
- **图形化界面** - 基于 PySide6 的现代化 GUI
- **实时日志** - 深色主题控制台，实时显示执行状态
- **独立可执行文件** - 支持 PyInstaller 打包为单个 EXE 文件

## 界面预览

```
┌─────────────────────────────────────────────────────┐
│              一键启动环境                             │
├─────────────────────────────────────────────────────┤
│  >>> 开始执行: copaw init --defaults                │
│  -------------------------------------------------- │
│  ✓ 初始化完成！                                      │
│  >>> 开始执行: copaw desktop                         │
│  -------------------------------------------------- │
│  ✓ 所有任务执行完毕！                                │
├─────────────────────────────────────────────────────┤
│           [  一键初始化并启动  ]                      │
└─────────────────────────────────────────────────────┘
```

## 打包教程

本项目的核心价值在于：**教你如何将 Copaw 打包成一个无需 Python 环境的一键安装包**。

### 打包步骤

1. **克隆项目**
   ```bash
   git clone https://github.com/iwanglei1/OneClickCopaw.git
   cd OneClickCopaw
   ```

2. **安装依赖**
   ```bash
   pip install pyinstaller PySide6 copaw reme
   ```

3. **执行打包**
   ```bash
   python build_exe.py
   ```

4. **获取 EXE 文件**

   打包完成后，在 `dist/` 目录下找到 `main.exe`

### 核心技术点

本项目解决了以下打包难题：

| 问题 | 解决方案 |
|-----|---------|
| CLI 交互式提示阻塞 | 拦截 `--internal-cli` 参数，模拟用户输入 |
| PyInstaller 下 uvicorn 加载失败 | 直接导入 app 对象，绕过字符串加载 |
| 隐式导入缺失 | 自动收集所有包的 metadata 和 hiddenimports |
| GUI 实时日志 | 使用 QProcess 捕获子进程输出 |

### 关键文件说明

- **[main.py](main.py)** - 主程序，包含 GUI 界面和 CLI 适配器
- **[build_exe.py](build_exe.py)** - 自动生成 .spec 文件并执行打包

## 项目结构

```
OneClickCopaw/
├── main.py        # 主程序（GUI + CLI 适配器）
├── build_exe.py   # PyInstaller 打包脚本
├── find.py        # 入口点查找工具
├── .gitignore     # Git 忽略规则
└── README.md      # 项目说明文档
```

## 技术实现

### 核心功能

| 功能模块 | 说明 |
|---------|------|
| CLI 拦截器 | 自动处理 Copaw CLI 的交互式提示 |
| 进程适配 | 绕过 PyInstaller 下 uvicorn 的字符串加载问题 |
| GUI 界面 | PySide6 实现的现代化图形界面 |
| 日志系统 | QProcess 实时捕获并显示命令输出 |

### 支持的 Copaw 渠道

打包脚本已内置以下渠道的隐式导入：

- Discord
- Telegram
- 钉钉 (DingTalk)
- 飞书 (Feishu)
- iMessage
- Matrix
- Mattermost
- MQTT
- QQ
- Voice (Twilio)

## 依赖项

- Python >= 3.10
- PySide6
- copaw
- reme
- PyInstaller (打包时需要)

## 常见问题

<details>
<summary><b>Q: 打包后的 EXE 文件太大怎么办？</b></summary>

这是正常现象，PyInstaller 会将 Python 运行时和所有依赖打包进单个文件。可以使用 UPX 压缩（已在打包脚本中启用）来减小体积。
</details>

<details>
<summary><b>Q: 启动时提示缺少模块？</b></summary>

请确保在打包前已安装所有依赖：`pip install PySide6 copaw reme`
</details>

<details>
<summary><b>Q: 如何更新到最新版本？</b></summary>

```bash
git pull origin main
pip install --upgrade copaw reme
python build_exe.py
```
</details>

## 开发计划

- [ ] 添加系统托盘图标
- [ ] 支持自定义初始化参数
- [ ] 多语言支持
- [ ] 自动更新功能

## 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 致谢

- [Copaw](https://github.com/xing61/copaw) - 核心框架
- [PySide6](https://www.qt.io/qt-for-python) - GUI 框架
- [PyInstaller](https://pyinstaller.org/) - 打包工具

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/iwanglei1">iwanglei1</a>
</p>
