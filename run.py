#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ArXiv Scholar 启动器
一键安装依赖并启动程序
"""

import subprocess
import sys
import os

def check_and_install_dependencies():
    """检查并安装依赖"""
    print("=" * 50)
    print("    ArXiv Scholar - 智能文献搜索系统")
    print("=" * 50)
    print()
    
    # 检查Python版本
    print(f"[检查] Python版本: {sys.version}")
    if sys.version_info < (3, 7):
        print("[错误] Python版本过低，需要3.7+")
        return False
    
    # 检查依赖
    print("[检查] 正在检查依赖包...")
    missing_packages = []
    
    try:
        import arxiv
        print("   [成功] arxiv 已安装")
    except ImportError:
        missing_packages.append("arxiv==2.1.3")
        print("   [缺失] arxiv 未安装")
    
    try:
        import openai
        print("   [成功] openai 已安装")
    except ImportError:
        missing_packages.append("openai>=1.0.0")
        print("   [缺失] openai 未安装")
    
    try:
        import tkinter
        print("   [成功] tkinter 已安装")
    except ImportError:
        print("   [警告] tkinter 不可用（可能影响GUI）")
    
    # 安装缺失的包
    if missing_packages:
        print(f"\n[安装] 需要安装 {len(missing_packages)} 个包")
        
        choice = input("是否自动安装？[Y/n]: ").strip().lower()
        if choice in ['', 'y', 'yes']:
            try:
                for package in missing_packages:
                    print(f"   正在安装 {package}...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                    print(f"   [完成] {package} 安装完成")
                
                print("\n[完成] 所有依赖已安装")
                return True
            except subprocess.CalledProcessError as e:
                print(f"\n[错误] 安装失败: {e}")
                print("请手动运行: pip install -r requirements.txt")
                return False
        else:
            print("\n请手动安装依赖后再运行程序")
            return False
    else:
        print("\n[完成] 所有依赖检查通过")
        return True

def start_application():
    """启动应用程序"""
    print("\n[启动] 正在启动ArXiv Scholar...")
    
    try:
        # 导入并启动主程序
        from main import main
        main()
    except Exception as e:
        print(f"[错误] 启动失败: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    try:
        # 切换到脚本目录
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # 检查并安装依赖
        if check_and_install_dependencies():
            # 启动程序
            start_application()
        else:
            print("\n环境配置未完成，程序退出")
            
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
    except Exception as e:
        print(f"\n[错误] 发生未知错误: {e}")
    
    input("\n按Enter键退出...")

if __name__ == "__main__":
    main()