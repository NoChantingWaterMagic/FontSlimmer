import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from tkinter.ttk import Progressbar, Label, Frame
import os
import re
import pyperclip

class ASSProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ASS字幕处理工具")  # 设置窗口标题
        self.root.geometry("800x600")  # 设置默认的窗口大小
        self.setup_ui()

    def setup_ui(self):
        # 主框架设置
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # 加载文件按钮
        self.load_btn = tk.Button(self.frame, text="加载ASS文件", command=self.load_and_initialize)
        self.load_btn.pack(pady=10)

        # 信息显示标签
        self.info_label = Label(self.frame, text="")
        self.info_label.pack()

        # 滚动文本区域用于显示处理结果
        self.text_area = scrolledtext.ScrolledText(self.frame, width=90, height=20)
        self.text_area.pack(pady=10, fill=tk.BOTH, expand=True)

        # 剪贴板信息显示标签
        self.clipboard_info_label = Label(self.frame, text="")
        self.clipboard_info_label.pack(pady=10)

        # 底部框架，包括按钮和进度条
        self.bottom_frame = Frame(self.frame)
        self.bottom_frame.pack(fill=tk.X, pady=10)

        self.export_btn = tk.Button(self.bottom_frame, text="导出结果", command=self.export_results)
        self.export_btn.pack(side=tk.LEFT, padx=10)

        self.progress = Progressbar(self.bottom_frame, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(side=tk.LEFT, padx=20, expand=True, fill=tk.X)

        self.copy_btn = tk.Button(self.bottom_frame, text="复制结果", command=self.copy_results)
        self.copy_btn.pack(side=tk.LEFT, padx=10)

        # 初始化用于存储数据的集合
        self.font_names = set()
        self.characters = set()

    def load_and_initialize(self):
        # 初始化数据
        self.initialize()
        # 加载文件
        self.load_files()

    def load_files(self):
        # 打开文件选择对话框，选择多个ASS字幕文件
        file_paths = filedialog.askopenfilenames(title="选择ASS字幕文件", filetypes=(("ASS Files", "*.ass"),))
        total_files = len(file_paths)
        self.progress['maximum'] = total_files
        self.progress['value'] = 0

        # 依次处理每个文件，并更新进度条
        for file_path in file_paths:
            self.process_file(file_path)
            self.progress['value'] += 1
            self.root.update_idletasks()

        # 显示处理结果
        self.display_results()
        self.info_label.config(text=f"读取了{total_files}个ASS字幕文件，获取到了{len(self.font_names)}种字体，共获取{len(self.characters)}个字符。")

    def process_file(self, file_path):
        # 打开并读取文件内容
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 正则表达式匹配字体样式
        styles = re.findall(r"Style:.*?,(.*?),", content)
        self.font_names.update(styles)

        # 正则表达式匹配对话内容
        dialogues = re.findall(r"Dialogue:.*?,.*?,.*?,.*?,.*?,.*?,.*?,.*?,.*?,(.*?)\n", content)
        text = ' '.join(dialogues)
        self.characters.update(set(text))

    def display_results(self):
        # 在文本区域显示获取到的字体和字符
        self.text_area.insert(tk.END, f"处理完成。\n获取到的字体: {', '.join(self.font_names)}\n")
        self.text_area.insert(tk.END, f"获取到的字符: {', '.join(self.characters)}\n")

    def export_results(self):
        # 弹出文件保存对话框
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], initialfile="ASSInfo")
        if not file_path:
            return

        # 保存字体和字符到文本文件
        with open(file_path, "w", encoding='utf-8') as file:
            file.write("\n".join(self.font_names))
            file.write("\n\n")
            file.write("".join(self.characters))

        self.text_area.insert(tk.END, "TXT文件已保存。\n")

    def initialize(self):
        # 清空数据集合和文本区域，重置进度条
        self.font_names.clear()
        self.characters.clear()
        self.text_area.delete('1.0', tk.END)
        self.progress['value'] = 0
        self.clipboard_info_label.config(text="")

    def copy_results(self):
        # 复制字符到剪贴板
        if self.characters:
            character_string = ''.join(self.characters)
            pyperclip.copy(character_string)
            self.clipboard_info_label.config(text=f"共复制了{len(self.characters)}个字符到剪切板。")
        else:
            messagebox.showinfo("复制结果", "没有字符可复制。")

if __name__ == "__main__":
    root = tk.Tk()
    app = ASSProcessorApp(root)
    root.mainloop()


