@echo off
chcp 65001 >nul
echo 正在安装MC启动器所需的依赖...
echo.
echo 这可能需要几分钟时间，请耐心等待...
echo.
echo 首先升级pip...
python -m pip install --upgrade pip
echo.
echo 安装依赖包...
pip install -r requirements.txt
echo.
echo 如果安装仍然失败，请尝试安装Visual C++ Redistributable
echo 下载地址: https://aka.ms/vs/17/release/vc_redist.x64.exe
echo.
echo 安装完成！现在可以运行 start.bat 启动MC启动器了。
pause
