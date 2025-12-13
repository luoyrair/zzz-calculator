# cli.py (在项目根目录创建)
"""命令行接口 - 项目根目录入口"""
import sys
import os

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.cli_tools import main

if __name__ == "__main__":
    main()