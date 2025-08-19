#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
import csv
from datetime import datetime
import webbrowser
import sys
import os

# 导入搜索引擎
from search_engine import LLMQueryGenerator, Config

class ModernArxivSearchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("智能文献搜索系统 - ArXiv Scholar")
        self.root.geometry("1400x900")
        self.root.state('zoomed')  # 最大化窗口
        
        # 现代化配色方案
        self.colors = {
            'primary': '#2c3e50',      # 深蓝灰
            'secondary': '#3498db',    # 亮蓝
            'accent': '#e74c3c',       # 红色强调
            'success': '#27ae60',      # 绿色
            'warning': '#f39c12',      # 橙色
            'bg_light': '#ecf0f1',     # 浅灰背景
            'bg_dark': '#34495e',      # 深色背景
            'text_primary': '#2c3e50', # 主文字
            'text_secondary': '#7f8c8d', # 次要文字
            'white': '#ffffff',
            'border': '#bdc3c7'        # 边框色
        }
        
        # 设置现代化样式
        self.setup_styles()
        
        # 初始化搜索引擎
        try:
            self.config = Config()
            self.generator = LLMQueryGenerator(self.config)
        except Exception as e:
            messagebox.showerror("初始化错误", f"无法初始化搜索引擎: {e}")
            return
        
        # 存储搜索结果
        self.current_results = None
        self.search_history = []
        
        # 初始化UI变量
        self.query_var = tk.StringVar()
        self.search_strategy = tk.StringVar(value="smart")
        self.enable_restructure = tk.BooleanVar(value=True)
        self.max_results = tk.IntVar(value=15)
        self.status_var = tk.StringVar(value="🟢 系统就绪 | 智能文献搜索引擎已启动")
        
        self.setup_ui()
        
    def setup_styles(self):
        """设置现代化样式"""
        style = ttk.Style()
        
        # 使用现代主题
        try:
            style.theme_use('clam')
        except:
            pass
        
        # 配置样式
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 24, 'bold'),
                       foreground=self.colors['primary'],
                       background=self.colors['bg_light'])
        
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 11),
                       foreground=self.colors['text_secondary'],
                       background=self.colors['bg_light'])
        
        style.configure('Header.TLabel',
                       font=('Segoe UI', 12, 'bold'),
                       foreground=self.colors['primary'],
                       background=self.colors['white'])
        
        style.configure('Modern.TButton',
                       font=('Segoe UI', 10, 'bold'),
                       foreground=self.colors['white'],
                       background=self.colors['secondary'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(15, 8))
        
        style.map('Modern.TButton',
                 background=[('active', '#2980b9'),
                           ('pressed', '#1f5f8b')])
        
        style.configure('Search.TButton',
                       font=('Segoe UI', 11, 'bold'),
                       foreground=self.colors['white'],
                       background=self.colors['success'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(20, 10))
        
        style.map('Search.TButton',
                 background=[('active', '#229954'),
                           ('pressed', '#1e8449')])
        
        style.configure('Danger.TButton',
                       font=('Segoe UI', 10),
                       foreground=self.colors['white'],
                       background=self.colors['accent'],
                       borderwidth=0,
                       focuscolor='none',
                       padding=(12, 6))
        
        style.configure('Modern.TFrame',
                       background=self.colors['white'],
                       borderwidth=1,
                       relief='solid')
        
        style.configure('Card.TFrame',
                       background=self.colors['white'],
                       borderwidth=0,
                       relief='flat')
        
        style.configure('Modern.TLabelFrame',
                       background=self.colors['white'],
                       borderwidth=2,
                       relief='solid',
                       bordercolor=self.colors['border'])
        
        style.configure('Modern.TLabelFrame.Label',
                       font=('Segoe UI', 11, 'bold'),
                       foreground=self.colors['primary'],
                       background=self.colors['white'])
        
        style.configure('Modern.TEntry',
                       font=('Segoe UI', 11),
                       borderwidth=2,
                       relief='solid',
                       bordercolor=self.colors['border'],
                       focuscolor=self.colors['secondary'])
        
        style.configure('Modern.TCombobox',
                       font=('Segoe UI', 10),
                       borderwidth=2,
                       relief='solid',
                       bordercolor=self.colors['border'])
        
        style.configure('Heading',
                       font=('Segoe UI', 10, 'bold'),
                       foreground=self.colors['primary'])
        
        style.configure('Treeview',
                       font=('Segoe UI', 9),
                       background=self.colors['white'],
                       foreground=self.colors['text_primary'],
                       rowheight=25,
                       borderwidth=1)
        
        style.configure('Treeview.Heading',
                       font=('Segoe UI', 10, 'bold'),
                       background=self.colors['bg_light'],
                       foreground=self.colors['primary'],
                       borderwidth=1)
        
        style.map('Treeview.Heading',
                 background=[('active', self.colors['secondary'])])
        
        style.map('Treeview',
                 background=[('selected', self.colors['secondary']),
                           ('alternate', '#f8f9fa')])
        
        # 设置根窗口背景
        self.root.configure(bg=self.colors['bg_light'])
        
    def setup_ui(self):
        """设置用户界面"""
        # 创建主容器
        main_container = tk.Frame(self.root, bg=self.colors['bg_light'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 创建头部区域
        self.setup_header(main_container)
        
        # 创建主内容区域
        content_frame = tk.Frame(main_container, bg=self.colors['bg_light'])
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # 左侧搜索面板
        left_panel = tk.Frame(content_frame, bg=self.colors['bg_light'])
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        # 右侧结果面板
        right_panel = tk.Frame(content_frame, bg=self.colors['bg_light'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 设置各个区域
        self.setup_search_panel(left_panel)
        self.setup_results_panel(right_panel)
        
        # 底部状态栏
        self.setup_status_bar(main_container)
        
    def setup_header(self, parent):
        """设置头部区域"""
        header_frame = tk.Frame(parent, bg=self.colors['bg_light'])
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 标题和图标
        title_frame = tk.Frame(header_frame, bg=self.colors['bg_light'])
        title_frame.pack(side=tk.LEFT)
        
        title_label = ttk.Label(title_frame, text="🎓 ArXiv Scholar", 
                               style='Title.TLabel')
        title_label.pack(anchor=tk.W)
        
        subtitle_label = ttk.Label(title_frame, 
                                  text="智能文献搜索与发现平台 | 基于AI的学术研究助手",
                                  style='Subtitle.TLabel')
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
        # 右侧功能按钮
        header_buttons = tk.Frame(header_frame, bg=self.colors['bg_light'])
        header_buttons.pack(side=tk.RIGHT, pady=(10, 0))
        
        ttk.Button(header_buttons, text="📖 使用帮助", 
                  command=self.show_help).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(header_buttons, text="设置", 
                  command=self.show_settings).pack(side=tk.RIGHT, padx=(5, 0))
        
    def setup_search_panel(self, parent):
        """设置搜索面板"""
        # 搜索卡片
        search_card = ttk.Frame(parent, style='Card.TFrame', padding=20)
        search_card.pack(fill=tk.X, pady=(0, 15))
        
        # 为卡片添加阴影效果
        shadow_frame = tk.Frame(parent, bg='#d5d8dc', height=2)
        shadow_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 搜索输入区域
        ttk.Label(search_card, text="研究主题", 
                 style='Header.TLabel').pack(anchor=tk.W, pady=(0, 8))
        
        search_entry = ttk.Entry(search_card, textvariable=self.query_var, 
                               font=('Segoe UI', 12))
        search_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)
        search_entry.bind('<Return>', lambda e: self.start_search())
        
        # 占位符提示
        placeholder_label = ttk.Label(search_card, 
                                    text="提示：支持中文描述，如：深度学习图像分类、量子计算算法等",
                                    style='Subtitle.TLabel')
        placeholder_label.pack(anchor=tk.W, pady=(0, 20))
        
        # 搜索选项
        options_frame = ttk.LabelFrame(search_card, text="搜索选项", 
                                      padding=15)
        options_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 策略选择
        strategy_frame = tk.Frame(options_frame, bg=self.colors['white'])
        strategy_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(strategy_frame, text="策略模式:", font=('Segoe UI', 10, 'bold')).pack(side=tk.LEFT)
        
        strategy_combo = ttk.Combobox(strategy_frame, textvariable=self.search_strategy,
                                    values=["smart", "balanced", "broad", "precise"],
                                    state="readonly", width=12)
        strategy_combo.pack(side=tk.LEFT, padx=(10, 0))
        strategy_combo.bind('<<ComboboxSelected>>', self.on_strategy_change)
        
        # 策略说明
        self.strategy_info = ttk.Label(options_frame, 
                                      text="智能模式：自动选择最佳策略，支持查询重构",
                                      style='Subtitle.TLabel')
        self.strategy_info.pack(anchor=tk.W, pady=(5, 15))
        
        # 其他选项
        options_row = tk.Frame(options_frame, bg=self.colors['white'])
        options_row.pack(fill=tk.X)
        
        restructure_cb = ttk.Checkbutton(options_row, text="启用智能查询重构",
                                       variable=self.enable_restructure)
        restructure_cb.pack(side=tk.LEFT)
        
        # 结果数量
        results_frame = tk.Frame(options_row, bg=self.colors['white'])
        results_frame.pack(side=tk.RIGHT)
        
        ttk.Label(results_frame, text="最大结果:").pack(side=tk.LEFT)
        results_spinbox = ttk.Spinbox(results_frame, from_=5, to=50, width=6,
                                    textvariable=self.max_results)
        results_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        # 搜索按钮
        button_frame = tk.Frame(search_card, bg=self.colors['white'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.search_btn = ttk.Button(button_frame, text="开始搜索",
                                   command=self.start_search)
        self.search_btn.pack(fill=tk.X, pady=(0, 5))
        
        self.stop_btn = ttk.Button(button_frame, text="⏹ 停止搜索",
                                 command=self.stop_search, state='disabled')
        self.stop_btn.pack(fill=tk.X)
        
        # 功能按钮区域
        actions_card = ttk.Frame(parent, padding=15)
        actions_card.pack(fill=tk.X, pady=(15, 0))
        
        ttk.Label(actions_card, text="🛠️ 功能操作", style='Header.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        self.export_btn = ttk.Button(actions_card, text="导出结果",
                                   command=self.export_results, state='disabled')
        self.export_btn.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(actions_card, text="📝 搜索历史",
                  command=self.show_history).pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(actions_card, text="🗑️ 清空结果",
                  command=self.clear_results).pack(fill=tk.X)
        
    def setup_results_panel(self, parent):
        """设置结果显示面板"""
        # 结果卡片
        results_card = ttk.Frame(parent, padding=15)
        results_card.pack(fill=tk.BOTH, expand=True)
        
        # 结果头部
        results_header = tk.Frame(results_card, bg=self.colors['white'])
        results_header.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(results_header, text="📚 搜索结果", style='Header.TLabel').pack(side=tk.LEFT)
        
        self.results_info = ttk.Label(results_header, text="请输入搜索词开始探索学术世界",
                                    style='Subtitle.TLabel')
        self.results_info.pack(side=tk.RIGHT)
        
        # 结果列表容器
        results_container = tk.Frame(results_card, bg=self.colors['white'])
        results_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建Treeview
        columns = ('#', '标题', '作者', '日期', '分类', '引用')
        self.results_tree = ttk.Treeview(results_container, columns=columns, show='headings', height=20)
        
        # 设置列
        self.results_tree.heading('#', text='#')
        self.results_tree.heading('标题', text='论文标题')
        self.results_tree.heading('作者', text='作者')
        self.results_tree.heading('日期', text='发布日期')
        self.results_tree.heading('分类', text='学科分类')
        self.results_tree.heading('引用', text='相关度')
        
        self.results_tree.column('#', width=50, anchor='center')
        self.results_tree.column('标题', width=450, anchor='w')
        self.results_tree.column('作者', width=200, anchor='w')
        self.results_tree.column('日期', width=100, anchor='center')
        self.results_tree.column('分类', width=150, anchor='w')
        self.results_tree.column('引用', width=80, anchor='center')
        
        # 添加滚动条
        tree_scroll_y = ttk.Scrollbar(results_container, orient="vertical", command=self.results_tree.yview)
        tree_scroll_x = ttk.Scrollbar(results_container, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
        
        # 布局
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        results_container.grid_rowconfigure(0, weight=1)
        results_container.grid_columnconfigure(0, weight=1)
        
        # 绑定事件
        self.results_tree.bind('<Double-1>', self.show_paper_details)
        self.results_tree.bind('<Button-3>', self.show_context_menu)  # 右键菜单
        
        # 设置交替行颜色
        self.results_tree.tag_configure('oddrow', background='#f8f9fa')
        self.results_tree.tag_configure('evenrow', background=self.colors['white'])
        
    def setup_status_bar(self, parent):
        """设置状态栏"""
        status_frame = tk.Frame(parent, bg=self.colors['primary'], height=35)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        status_frame.pack_propagate(False)
        
        status_label = tk.Label(status_frame, textvariable=self.status_var,
                              bg=self.colors['primary'], fg=self.colors['white'],
                              font=('Segoe UI', 10), anchor=tk.W)
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=15, pady=8)
        
        # 右侧状态信息
        time_label = tk.Label(status_frame, text=datetime.now().strftime("日期: %Y-%m-%d %H:%M"),
                            bg=self.colors['primary'], fg=self.colors['white'],
                            font=('Segoe UI', 9))
        time_label.pack(side=tk.RIGHT, padx=15, pady=8)
        
    def on_strategy_change(self, event=None):
        """策略选择改变时的处理"""
        strategy = self.search_strategy.get()
        strategy_descriptions = {
            "smart": "智能模式：自动选择最佳策略，支持查询重构",
            "balanced": "⚖️ 平衡模式：综合考虑召回率和精准度",
            "broad": "🌐 宽泛模式：扩大搜索范围，优先保证找到文献",
            "precise": "精确模式：使用专业术语，重点关注最相关文献"
        }
        self.strategy_info.config(text=strategy_descriptions.get(strategy, ""))
        
        if strategy == "smart":
            self.enable_restructure.set(True)
    
    def show_help(self):
        """显示帮助信息"""
        help_window = tk.Toplevel(self.root)
        help_window.title("📖 使用帮助")
        help_window.geometry("600x500")
        help_window.transient(self.root)
        help_window.configure(bg=self.colors['white'])
        
        help_text = """
🎓 ArXiv Scholar 使用指南

📝 搜索技巧：
• 支持中文自然语言描述
• 例如：深度学习图像分类、量子计算算法等
• 系统会自动将中文转换为英文学术查询

搜索策略：
• 智能模式：AI自动选择最佳策略
• 平衡模式：兼顾查全率和查准率
• 宽泛模式：优先保证找到相关文献
• 精确模式：重点关注最相关的文献

查询重构：
• 当搜索无结果时自动重构查询
• 保持核心概念，扩大搜索范围
• 提高文献发现成功率

结果操作：
• 双击查看论文详情
• 右键显示更多操作
• 支持多种格式导出

快捷键：
• Enter：开始搜索
• Ctrl+E：导出结果
• F5：刷新界面
        """
        
        text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, 
                                              font=('Segoe UI', 11), bg=self.colors['white'])
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        text_widget.insert(tk.END, help_text)
        text_widget.config(state=tk.DISABLED)
    
    def show_settings(self):
        """显示设置窗口"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("系统设置")
        settings_window.geometry("500x400")
        settings_window.transient(self.root)
        settings_window.configure(bg=self.colors['white'])
        
        # TODO: 实现设置功能
        ttk.Label(settings_window, text="设置功能开发中...", 
                 style='Header.TLabel').pack(pady=50)
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        selection = self.results_tree.selection()
        if not selection:
            return
            
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="📖 查看详情", command=lambda: self.show_paper_details(event))
        context_menu.add_command(label="🌐 打开链接", command=self.open_paper_link)
        context_menu.add_command(label="下载PDF", command=self.download_pdf)
        context_menu.add_separator()
        context_menu.add_command(label="复制标题", command=self.copy_title)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    # 复用之前的核心方法（稍作修改以适应新UI）
    def start_search(self):
        """开始搜索"""
        query = self.query_var.get().strip()
        if not query:
            messagebox.showwarning("输入提醒", "请输入要搜索的研究主题")
            return
            
        self.config.max_results = self.max_results.get()
        
        self.search_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.export_btn.config(state='disabled')
        
        self.clear_results()
        
        self.status_var.set(f"正在搜索: {query}")
        
        self.search_thread = threading.Thread(target=self.perform_search, args=(query,))
        self.search_thread.daemon = True
        self.search_thread.start()
    
    def perform_search(self, query):
        """执行搜索（在后台线程中运行）"""
        try:
            strategy = self.search_strategy.get()
            
            if strategy == "smart":
                result = self.generator.smart_search(query, self.enable_restructure.get())
            else:
                # 单一策略模式的实现...
                search_query = self.generator.generate_query(query, strategy)
                search = self.generator.search_arxiv(search_query)
                
                results = []
                try:
                    for paper in search.results():
                        results.append({
                            'title': paper.title,
                            'authors': [author.name for author in paper.authors],
                            'summary': paper.summary,
                            'published': paper.published,
                            'url': paper.entry_id,
                            'pdf_url': paper.pdf_url,
                            'categories': paper.categories
                        })
                except Exception as e:
                    self.root.after(0, self.search_error, f"搜索API调用失败: {e}")
                    return
                
                result = {
                    'strategy': strategy,
                    'query': search_query,
                    'results': results,
                    'count': len(results),
                    'search_input': query,
                    'used_restructure': False
                }
            
            self.root.after(0, self.update_search_results, result, query)
            
        except Exception as e:
            self.root.after(0, self.search_error, str(e))
    
    def update_search_results(self, result, query):
        """更新搜索结果显示"""
        self.current_results = result
        
        self.search_history.append({
            'query': query,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'count': result['count'],
            'strategy': result['strategy'],
            'used_restructure': result.get('used_restructure', False)
        })
        
        # 更新结果信息
        info_text = f"找到 {result['count']} 篇文献 | 策略: {result['strategy']}"
        if result.get('used_restructure'):
            info_text += f" | 已重构"
            
        self.results_info.config(text=info_text)
        
        # 填充结果到Treeview
        for i, paper in enumerate(result['results'], 1):
            authors_text = ', '.join(paper['authors'][:2])
            if len(paper['authors']) > 2:
                authors_text += f" 等{len(paper['authors'])}人"
                
            date_text = paper['published'].strftime('%Y-%m-%d')
            categories_text = ', '.join(paper['categories'][:2])
            
            # 交替行颜色
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            
            self.results_tree.insert('', 'end', values=(
                f"{i:02d}",
                paper['title'][:80] + '...' if len(paper['title']) > 80 else paper['title'],
                authors_text,
                date_text,
                categories_text,
                "⭐⭐⭐"  # 模拟相关度评分
            ), tags=(tag,))
        
        self.search_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        if result['count'] > 0:
            self.export_btn.config(state='normal')
        
        self.status_var.set(f"搜索完成 | 找到 {result['count']} 篇高质量文献")
    
    def search_error(self, error_msg):
        """处理搜索错误"""
        messagebox.showerror("搜索错误", f"搜索过程中发生错误:\n{error_msg}")
        
        self.search_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_var.set("搜索失败 | 请检查网络连接或重试")
    
    def stop_search(self):
        """停止搜索"""
        self.search_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_var.set("⏹ 搜索已停止")
    
    def clear_results(self):
        """清空搜索结果"""
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        self.results_info.config(text="请输入搜索词开始探索学术世界")
        self.export_btn.config(state='disabled')
        self.current_results = None
    
    def show_paper_details(self, event):
        """显示论文详情"""
        selection = self.results_tree.selection()
        if not selection or not self.current_results:
            return
            
        item = self.results_tree.item(selection[0])
        paper_index = int(item['values'][0]) - 1
        
        if paper_index < len(self.current_results['results']):
            paper = self.current_results['results'][paper_index]
            self.show_detail_window(paper)
    
    def show_detail_window(self, paper):
        """显示论文详情窗口"""
        detail_window = tk.Toplevel(self.root)
        detail_window.title("📖 论文详情")
        detail_window.geometry("900x700")
        detail_window.transient(self.root)
        detail_window.configure(bg=self.colors['white'])
        
        # 详情内容
        detail_frame = tk.Frame(detail_window, bg=self.colors['white'])
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = tk.Label(detail_frame, text=paper['title'],
                              font=('Segoe UI', 14, 'bold'),
                              fg=self.colors['primary'], bg=self.colors['white'],
                              wraplength=850, justify=tk.LEFT)
        title_label.pack(anchor=tk.W, pady=(0, 15))
        
        # 基本信息
        info_frame = tk.Frame(detail_frame, bg=self.colors['bg_light'], relief=tk.SOLID, bd=1)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        info_text = f"""
👥 作者: {', '.join(paper['authors'])}
发布日期: {paper['published'].strftime('%Y年%m月%d日')}
分类: {', '.join(paper['categories'])}
🌐 arXiv链接: {paper['url']}
PDF链接: {paper['pdf_url']}
        """
        
        info_label = tk.Label(info_frame, text=info_text.strip(),
                             font=('Segoe UI', 10), bg=self.colors['bg_light'],
                             fg=self.colors['text_primary'], justify=tk.LEFT)
        info_label.pack(anchor=tk.W, padx=15, pady=15)
        
        # 摘要
        abstract_label = tk.Label(detail_frame, text="📝 摘要:",
                                 font=('Segoe UI', 12, 'bold'),
                                 fg=self.colors['primary'], bg=self.colors['white'])
        abstract_label.pack(anchor=tk.W, pady=(0, 5))
        
        abstract_text = scrolledtext.ScrolledText(detail_frame, wrap=tk.WORD,
                                                font=('Segoe UI', 11), height=15,
                                                bg=self.colors['white'])
        abstract_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        abstract_text.insert(tk.END, paper['summary'])
        abstract_text.config(state=tk.DISABLED)
        
        # 操作按钮
        button_frame = tk.Frame(detail_frame, bg=self.colors['white'])
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="🌐 打开arXiv页面",
                  command=lambda: webbrowser.open(paper['url']),
                  style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="下载PDF",
                  command=lambda: webbrowser.open(paper['pdf_url']),
                  style='Modern.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="复制引用",
                  command=lambda: self.copy_citation(paper),
                  style='Modern.TButton').pack(side=tk.LEFT)
    
    # 添加一些辅助方法
    def open_paper_link(self):
        """打开论文链接"""
        selection = self.results_tree.selection()
        if selection and self.current_results:
            item = self.results_tree.item(selection[0])
            paper_index = int(item['values'][0]) - 1
            if paper_index < len(self.current_results['results']):
                paper = self.current_results['results'][paper_index]
                webbrowser.open(paper['url'])
    
    def download_pdf(self):
        """下载PDF"""
        selection = self.results_tree.selection()
        if selection and self.current_results:
            item = self.results_tree.item(selection[0])
            paper_index = int(item['values'][0]) - 1
            if paper_index < len(self.current_results['results']):
                paper = self.current_results['results'][paper_index]
                webbrowser.open(paper['pdf_url'])
    
    def copy_title(self):
        """复制标题"""
        selection = self.results_tree.selection()
        if selection and self.current_results:
            item = self.results_tree.item(selection[0])
            paper_index = int(item['values'][0]) - 1
            if paper_index < len(self.current_results['results']):
                paper = self.current_results['results'][paper_index]
                self.root.clipboard_clear()
                self.root.clipboard_append(paper['title'])
                self.status_var.set("标题已复制到剪贴板")
    
    def copy_citation(self, paper):
        """复制引用格式"""
        citation = f"{', '.join(paper['authors'][:3])}{'et al.' if len(paper['authors']) > 3 else ''}. {paper['title']}. arXiv preprint arXiv:{paper['url'].split('/')[-1]} ({paper['published'].year})."
        self.root.clipboard_clear()
        self.root.clipboard_append(citation)
        self.status_var.set("引用格式已复制到剪贴板")
    
    # 导出和历史功能保持不变...
    def export_results(self):
        """导出搜索结果"""
        if not self.current_results or self.current_results['count'] == 0:
            messagebox.showwarning("导出提醒", "没有可导出的结果")
            return
        
        # 简化导出，直接导出为CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialname=f"arxiv_search_{timestamp}.csv"
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['标题', '作者', '发布日期', '分类', 'arXiv链接', 'PDF链接', '摘要'])
                    
                    for paper in self.current_results['results']:
                        writer.writerow([
                            paper['title'],
                            '; '.join(paper['authors']),
                            paper['published'].strftime('%Y-%m-%d'),
                            '; '.join(paper['categories']),
                            paper['url'],
                            paper['pdf_url'],
                            paper['summary']
                        ])
                
                messagebox.showinfo("导出成功", f"结果已导出到: {filename}")
                self.status_var.set(f"成功导出 {self.current_results['count']} 篇文献")
            except Exception as e:
                messagebox.showerror("导出错误", f"导出失败: {e}")
    
    def show_history(self):
        """显示搜索历史"""
        history_window = tk.Toplevel(self.root)
        history_window.title("📝 搜索历史")
        history_window.geometry("800x500")
        history_window.transient(self.root)
        history_window.configure(bg=self.colors['white'])
        
        # 历史列表
        columns = ('时间', '查询词', '策略', '结果数', '查询重构')
        history_tree = ttk.Treeview(history_window, columns=columns, show='headings')
        
        for col in columns:
            history_tree.heading(col, text=col)
        
        history_tree.column('时间', width=120)
        history_tree.column('查询词', width=300)
        history_tree.column('策略', width=100)
        history_tree.column('结果数', width=80)
        history_tree.column('查询重构', width=100)
        
        history_scroll = ttk.Scrollbar(history_window, orient="vertical", command=history_tree.yview)
        history_tree.configure(yscrollcommand=history_scroll.set)
        
        history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        history_scroll.pack(side=tk.RIGHT, fill=tk.Y, pady=20)
        
        # 填充历史数据
        for item in reversed(self.search_history):
            history_tree.insert('', 'end', values=(
                item['timestamp'],
                item['query'],
                item.get('strategy', 'unknown'),
                item['count'],
                '已重构' if item['used_restructure'] else '未重构'
            ))

def main():
    root = tk.Tk()
    app = ModernArxivSearchGUI(root)
    
    # 绑定快捷键
    root.bind('<Control-e>', lambda e: app.export_results())
    root.bind('<F5>', lambda e: app.clear_results())
    
    root.mainloop()

if __name__ == "__main__":
    main()