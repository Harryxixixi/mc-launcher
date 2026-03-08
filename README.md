# MC启动器

一个简单的跨平台Minecraft启动器，支持Windows和Mac系统。

## 功能特点

- 跨平台支持（Windows和Mac）
- 简洁的用户界面
- 支持不同版本的Minecraft
- 基本的账户管理

## 安装说明

### 前提条件

- Python 3.7或更高版本

### 三种版本选择

1. **PyQt6版本**（功能更丰富但需要额外安装）：
   - 需要安装PyQt6库
   - 运行 `install.bat` 安装依赖
   - 然后运行 `start.bat` 启动

2. **Tkinter版本**（基础功能，无需额外安装）：
   - Tkinter是Python标准库的一部分，无需额外安装
   - 直接运行 `start_tkinter.bat` 启动

3. **最终版本**（推荐，功能最全）：
   - 自动检测和安装Java环境
   - 自动下载Minecraft游戏文件
   - 使用Tkinter，无需额外安装依赖
   - 直接运行 `start_final.bat` 启动

### 安装步骤

1. 克隆此仓库
2. 选择一个版本：
   - 对于PyQt6版本：运行 `install.bat` 安装依赖，然后运行 `start.bat`
   - 对于Tkinter版本：直接运行 `start_tkinter.bat`

### 注意事项

- 如果PyQt6版本遇到DLL加载失败等问题，请尝试安装Visual C++ Redistributable
- 下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe

## 使用说明

1. 启动程序后，输入你的Minecraft用户名
2. 选择你想要运行的Minecraft版本
3. 点击"启动游戏"按钮

## 开发者

dyq && Hray

## 许可证

MIT License