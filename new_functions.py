
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
