#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import platform
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import time
import json
import urllib.request
import zipfile
import shutil
import hashlib
import tempfile

class MinecraftLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("MC启动器")
        self.root.geometry("400x300")
        self.root.resizable(False, False)

        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 用户名输入
        username_frame = ttk.Frame(main_frame)
        username_frame.pack(fill=tk.X, pady=5)

        ttk.Label(username_frame, text="用户名:").pack(side=tk.LEFT)
        self.username_entry = ttk.Entry(username_frame)
        self.username_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        # 版本选择
        version_frame = ttk.Frame(main_frame)
        version_frame.pack(fill=tk.X, pady=5)

        ttk.Label(version_frame, text="游戏版本:").pack(side=tk.LEFT)
        self.version_combo = ttk.Combobox(version_frame, state="readonly")
        self.version_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        # 进度条
        self.progress = ttk.Progressbar(main_frame, orient="horizontal", length=100, mode="determinate")
        self.progress.pack(fill=tk.X, pady=10)
        self.progress.configure(value=0)

        # 启动按钮
        self.launch_button = ttk.Button(main_frame, text="启动游戏", command=self.launch_game)
        self.launch_button.pack(pady=10)

        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 加载版本列表
        self.load_versions()

    def load_versions(self):
        """加载Minecraft版本列表"""
        # 这里简化处理，实际应该从官方API获取版本信息
        versions = ["1.19.4", "1.19.3", "1.19.2", "1.19.1", "1.19",
                   "1.18.2", "1.18.1", "1.18", "1.17.1", "1.17",
                   "1.16.5", "1.16.4", "1.16.3", "1.16.2", "1.16.1", "1.16"]
        self.version_combo['values'] = versions
        if versions:
            self.version_combo.current(0)
        self.status_var.set("版本列表已加载")

    def launch_game(self):
        """启动Minecraft游戏"""
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showwarning("警告", "请输入用户名")
            return

        version = self.version_combo.get()
        if not version:
            messagebox.showwarning("警告", "请选择游戏版本")
            return

        # 禁用按钮，防止重复点击
        self.launch_button.config(state=tk.DISABLED)
        self.progress.configure(value=0)
        self.status_var.set("准备启动游戏...")

        # 在新线程中执行启动操作，避免界面冻结
        thread = threading.Thread(target=self._launch_game_thread, args=(username, version))
        thread.daemon = True
        thread.start()

    def _launch_game_thread(self, username, version):
        """在新线程中执行游戏启动操作"""
        try:
            # 获取Minecraft路径
            if platform.system() == "Windows":
                mc_path = os.path.expandvars(r"%APPDATA%\.minecraft")
            elif platform.system() == "Darwin":  # macOS
                mc_path = os.path.expanduser("~/Library/Application Support/minecraft")
            else:
                mc_path = os.path.expanduser("~/.minecraft")

            # 确保Minecraft目录存在
            if not os.path.exists(mc_path):
                os.makedirs(mc_path, exist_ok=True)

            # 更新状态
            self.root.after(0, lambda: self.status_var.set("检查Minecraft安装..."))
            self.progress.configure(value=10)

            # 检查Java是否安装
            java_path = self._find_java()
            if not java_path:
                self.root.after(0, lambda: messagebox.showerror("错误", "未找到Java安装，请先安装Java运行环境"))
                return

            # 更新状态
            self.root.after(0, lambda: self.status_var.set("检查游戏版本..."))
            self.progress.configure(value=20)

            # 检查版本是否已下载
            version_dir = os.path.join(mc_path, "versions", version)
            version_file = os.path.join(version_dir, f"{version}.json")

            if not os.path.exists(version_file):
                # 下载版本
                self.root.after(0, lambda: self.status_var.set(f"下载Minecraft {version}..."))
                self.progress.configure(value=30)
                if not self._download_version(mc_path, version):
                    self.root.after(0, lambda: messagebox.showerror("错误", f"下载Minecraft {version}失败"))
                    return

            # 更新状态
            self.root.after(0, lambda: self.status_var.set("准备启动游戏..."))
            self.progress.configure(value=70)

            # 检查jar文件是否存在
            jar_file = os.path.join(version_dir, f"{version}.jar")
            if not os.path.exists(jar_file):
                self.root.after(0, lambda: messagebox.showerror("错误", f"未找到游戏文件: {jar_file}"))
                return

            # 构建启动命令
            self.root.after(0, lambda: self.status_var.set("启动游戏..."))
            self.progress.configure(value=90)

            # 获取内存设置
            max_memory = "2G"  # 默认2GB内存
            min_memory = "1G"  # 默认1GB内存

            # 构建命令
            command = [
                java_path,
                f"-Xmx{max_memory}",
                f"-Xms{min_memory}",
                "-Djava.library.path=" + os.path.join(version_dir, "natives"),
                "-cp",
                jar_file,
                "net.minecraft.client.main.Main",
                "--username",
                username,
                "--version",
                version,
                "--gameDir",
                mc_path,
                "--assetsDir",
                os.path.join(mc_path, "assets"),
                "--assetIndex",
                version,
                "--uuid",
                "0",  # 简化处理，使用默认UUID
                "--accessToken",
                "0",  # 简化处理，使用默认访问令牌
                "--userType",
                "legacy",
                "--width",
                "854",
                "--height",
                "480"
            ]

            # 启动游戏
            subprocess.Popen(command)

            # 更新状态
            self.root.after(0, lambda: self.status_var.set("游戏启动成功!"))
            self.progress.configure(value=100)
            self.root.after(0, lambda: messagebox.showinfo("成功", f"游戏已启动!\n用户名: {username}\n版本: {version}"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"启动游戏时出错: {str(e)}"))
        finally:
            # 恢复按钮状态
            self.root.after(0, lambda: self.launch_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.progress.configure(value=0))
            self.root.after(0, lambda: self.status_var.set("就绪"))

    def _find_java(self):
        """查找Java安装路径"""
        # 常见的Java安装路径
        java_paths = []

        if platform.system() == "Windows":
            java_paths.extend([
                os.path.expandvars(r"%ProgramFiles%\Java\*\bin\java.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Java\*\bin\java.exe"),
            ])
        elif platform.system() == "Darwin":  # macOS
            java_paths.extend([
                "/Library/Java/JavaVirtualMachines/*/Contents/Home/bin/java",
                "/System/Library/Frameworks/JavaVM.framework/Versions/Current/Commands/java",
            ])
        else:  # Linux
            java_paths.extend([
                "/usr/bin/java",
                "/usr/local/bin/java",
            ])

        # 尝试使用which/where命令查找Java
        try:
            if platform.system() == "Windows":
                java_path = subprocess.check_output(["where", "java"], stderr=subprocess.DEVNULL).decode().strip()
            else:
                java_path = subprocess.check_output(["which", "java"], stderr=subprocess.DEVNULL).decode().strip()
            if java_path and os.path.exists(java_path):
                return java_path
        except:
            pass

        # 检查常见路径
        import glob
        for pattern in java_paths:
            for path in glob.glob(pattern):
                if os.path.exists(path):
                    return path

        # 如果找不到Java，尝试自动下载
        self.root.after(0, lambda: self.status_var.set("未找到Java，正在自动下载..."))
        return self._download_java()


    def _download_java(self):
        """下载并安装Java运行环境"""
        try:
            # 创建Java目录
            java_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "java")
            os.makedirs(java_dir, exist_ok=True)

            # 根据操作系统选择Java版本
            if platform.system() == "Windows":
                # Windows 64位
                java_url = "https://download.oracle.com/java/17/latest/jdk-17_windows-x64_bin.zip"
                java_file = os.path.join(java_dir, "jdk-17_windows-x64_bin.zip")
                extracted_dir = os.path.join(java_dir, "jdk-17")
            elif platform.system() == "Darwin":  # macOS
                # macOS x64
                java_url = "https://download.oracle.com/java/17/latest/jdk-17_macos-x64_bin.tar.gz"
                java_file = os.path.join(java_dir, "jdk-17_macos-x64_bin.tar.gz")
                extracted_dir = os.path.join(java_dir, "jdk-17.jdk")
            else:  # Linux
                # Linux x64
                java_url = "https://download.oracle.com/java/17/latest/jdk-17_linux-x64_bin.tar.gz"
                java_file = os.path.join(java_dir, "jdk-17_linux-x64_bin.tar.gz")
                extracted_dir = os.path.join(java_dir, "jdk-17")

            # 检查是否已经下载并解压
            java_executable = None
            if platform.system() == "Windows":
                java_executable = os.path.join(extracted_dir, "bin", "java.exe")
            else:
                java_executable = os.path.join(extracted_dir, "bin", "java")

            if os.path.exists(java_executable):
                return java_executable

            # 下载Java
            self.root.after(0, lambda: self.status_var.set("正在下载Java运行环境..."))
            self.progress.configure(value=30)

            # 显示下载进度
            def progress_hook(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(100, int(block_num * block_size * 100 / total_size))
                    self.progress.configure(value=30 + percent // 10)  # 30-40的范围
                    self.root.update_idletasks()

            # 下载文件
            urllib.request.urlretrieve(java_url, java_file, progress_hook)

            # 解压文件
            self.root.after(0, lambda: self.status_var.set("正在解压Java运行环境..."))
            self.progress.configure(value=50)

            if platform.system() == "Windows":
                with zipfile.ZipFile(java_file, 'r') as zip_ref:
                    zip_ref.extractall(java_dir)
            else:
                import tarfile
                with tarfile.open(java_file, 'r:*') as tar_ref:
                    tar_ref.extractall(java_dir)

            # 删除压缩文件
            os.remove(java_file)

            self.progress.configure(value=60)

            # 验证Java是否安装成功
            if os.path.exists(java_executable):
                self.root.after(0, lambda: self.status_var.set("Java运行环境安装成功"))
                return java_executable
            else:
                self.root.after(0, lambda: messagebox.showerror("错误", "Java运行环境安装失败"))
                return None

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"下载Java运行环境时出错: {str(e)}"))
            return None

    def _download_version(self, mc_path, version):
        """下载指定版本的Minecraft"""
        try:
            # 创建版本目录
            version_dir = os.path.join(mc_path, "versions", version)
            os.makedirs(version_dir, exist_ok=True)

            # 版本清单URL
            manifest_url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"

            # 下载版本清单
            with urllib.request.urlopen(manifest_url) as response:
                manifest = json.loads(response.read().decode())

            # 查找指定版本
            version_info = None
            for v in manifest["versions"]:
                if v["id"] == version:
                    version_info = v
                    break

            if not version_info:
                return False

            # 下载版本信息
            with urllib.request.urlopen(version_info["url"]) as response:
                version_data = json.loads(response.read().decode())

            # 保存版本信息
            version_file = os.path.join(version_dir, f"{version}.json")
            with open(version_file, "w") as f:
                json.dump(version_data, f, indent=2)

            # 下载客户端jar
            client_url = version_data["downloads"]["client"]["url"]
            client_file = os.path.join(version_dir, f"{version}.jar")

            # 显示下载进度
            def progress_hook(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(100, int(block_num * block_size * 100 / total_size))
                    self.progress.configure(value=30 + percent // 10)  # 30-40的范围
                    self.root.update_idletasks()

            # 下载文件
            urllib.request.urlretrieve(client_url, client_file, progress_hook)

            # 创建natives目录
            natives_dir = os.path.join(version_dir, "natives")
            os.makedirs(natives_dir, exist_ok=True)

            # 这里简化处理，实际应该下载并解压库文件到natives目录
            # 由于实现完整的库下载和提取比较复杂，这里只是创建目录

            return True

        except Exception as e:
            print(f"下载版本出错: {e}")
            return False

if __name__ == "__main__":
    root = tk.Tk()
    app = MinecraftLauncher(root)
    root.mainloop()