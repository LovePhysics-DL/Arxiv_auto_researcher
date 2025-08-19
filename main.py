#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ArXiv Scholar - 智能文献搜索系统
简化版主程序
"""

import tkinter as tk
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def main():
    """主程序入口"""
    try:
        # 导入GUI模块
        from main_window import ModernArxivSearchGUI
        
        print("启动ArXiv Scholar...")
        
        # 创建主窗口
        root = tk.Tk()
        app = ModernArxivSearchGUI(root)
        
        # 绑定关闭事件
        def on_closing():
            print("正在关闭应用...")
            root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        print("GUI已启动成功！")
        root.mainloop()
        
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装所有依赖：pip install -r requirements.txt")
        input("按Enter键退出...")
        
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按Enter键退出...")

if __name__ == "__main__":
    main()