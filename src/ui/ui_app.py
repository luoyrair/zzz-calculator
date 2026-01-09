#!/usr/bin/env python3
"""
绝区零驱动盘属性计算器 - UI主入口 (适配新架构)
"""

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from src.ui.main_window import MainWindow
from src.core.app import ApplicationCore


class ZZZUIApplication:
    """UI应用程序 - 适配新架构"""

    def __init__(self):
        # 初始化应用核心
        self.app_core = ApplicationCore()

        # 创建Qt应用
        self.qt_app = QApplication(sys.argv)

        # 设置字体
        self._setup_font()

        # 加载样式
        self._load_stylesheet()

        # 创建主窗口
        self.main_window = MainWindow(self.app_core)

    def _setup_font(self):
        """设置字体"""
        # 尝试使用微软雅黑，如果不存在则使用系统默认字体
        font = QFont("Microsoft YaHei", 9)
        if font.exactMatch():
            self.qt_app.setFont(font)
        else:
            # 尝试使用其他中文字体
            for font_name in ["SimHei", "NSimSun", "FangSong", "KaiTi"]:
                font = QFont(font_name, 9)
                if font.exactMatch():
                    self.qt_app.setFont(font)
                    break

    def _load_stylesheet(self):
        """加载样式表"""
        try:
            # 尝试从文件加载样式
            style_file = Path(__file__).parent / "styles" / "style.qss"
            if style_file.exists():
                with open(style_file, 'r', encoding='utf-8') as f:
                    style = f.read()
                    self.qt_app.setStyleSheet(style)
            else:
                # 使用内联样式
                self._apply_inline_styles()
        except Exception as e:
            print(f"加载样式表失败: {e}")
            self._apply_inline_styles()

    def _apply_inline_styles(self):
        """应用内联样式"""
        inline_style = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            background-color: white;
        }
        QComboBox {
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 5px;
            background-color: white;
            min-width: 200px;
        }
        QComboBox:hover {
            border-color: #3498db;
        }
        QTabWidget::pane {
            border: 1px solid #cccccc;
            background-color: white;
        }
        QStatusBar {
            background-color: #2c3e50;
            color: white;
        }
        """
        self.qt_app.setStyleSheet(inline_style)

    def run(self):
        """运行应用程序"""
        self.main_window.show()
        return self.qt_app.exec()