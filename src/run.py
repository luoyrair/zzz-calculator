#!/usr/bin/env python3
import sys
from pathlib import Path

# 运行报错"进程已结束，退出代码为 -1073740791 (0xc0000409)"时用下面注释的的代码

import traceback

# 1. 降低递归限制，让错误更快出现
sys.setrecursionlimit(100)  # 默认是1000，降低到100让问题更快暴露


# 2. 设置全局异常钩子
def debug_hook(exc_type, exc_value, exc_traceback):
    print("=== 递归深度异常 ===")
    traceback.print_exception(exc_type, exc_value, exc_traceback)

    # 获取调用栈信息
    stack_summary = traceback.extract_stack()
    print("\n=== 调用栈（最近20个）===")
    for frame in stack_summary[-20:]:
        print(f"  File: {frame.filename}, Line: {frame.lineno}, Function: {frame.name}")
        print(f"    Code: {frame.line}")

    # 检查递归模式
    print("\n=== 递归模式分析 ===")
    functions = [frame.name for frame in stack_summary]
    from collections import Counter
    func_counts = Counter(functions)
    print("函数调用次数统计:")
    for func, count in func_counts.most_common(10):
        print(f"  {func}: {count}次")

sys.excepthook = debug_hook

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    # 导入并运行主UI
    from src.ui.ui_app import ZZZUIApplication

    app = ZZZUIApplication()
    sys.exit(app.run())