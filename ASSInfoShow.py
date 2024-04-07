import tkinter as tk
from tkinter import filedialog, scrolledtext
from tkinter.ttk import Progressbar
import os
import re

class ASSProcessorApp:
    def __init__(self, root):
        """ 初始化函数，设置主窗口对象和窗口标题，初始化UI界面 """
        self.root = root
        self.root.title("ASS字幕处理工具")
        self.setup_ui()

    def setup_ui(self):
        """ 设置UI界面的布局和控件 """
        # 创建一个容器框架
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True)

        # 创建一个按钮，用于加载ASS字幕文件
        self.load_btn = tk.Button(self.frame, text="加载ASS文件", command=self.load_files)
        self.load_btn.pack(pady=10)

        # 创建一个滚动文本区域，用于显示处理结果
        self.text_area = scrolledtext.ScrolledText(self.frame, width=70, height=10)
        self.text_area.pack(pady=10, fill=tk.BOTH, expand=True)

        # 创建一个进度条，用于显示文件处理进度
        self.progress = Progressbar(self.frame, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10, side=tk.BOTTOM)

        # 创建一个按钮，用于导出处理结果
        self.export_btn = tk.Button(self.frame, text="导出结果", command=self.export_results)
        self.export_btn.pack(pady=10)

        # 初始化存储字体名和字符的集合
        self.font_names = set()
        self.characters = set()

    def load_files(self):
        """ 加载文件并处理每个文件，更新进度条 """
        file_paths = filedialog.askopenfilenames(title="选择ASS字幕文件", filetypes=(("ASS Files", "*.ass"),))
        total_files = len(file_paths)
        self.progress['maximum'] = total_files
        self.progress['value'] = 0

        for file_path in file_paths:
            self.process_file(file_path)
            self.progress['value'] += 1
            self.root.update_idletasks()

        self.display_results()

    def process_file(self, file_path):
        """ 读取单个文件，提取字体名和对话中的字符 """
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 提取字体名称
        styles = re.findall(r"Style:.*?,(.*?),", content)
        self.font_names.update(styles)

        # 提取对话中的字符
        dialogues = re.findall(r"Dialogue:.*?,.*?,.*?,.*?,.*?,.*?,.*?,.*?,.*?,(.*?)\n", content)
        text = ' '.join(dialogues)
        self.characters.update(set(text))

    def display_results(self):
        """ 显示提取的结果在文本区域中 """
        self.text_area.insert(tk.END, f"处理完成。\n共获取{len(self.font_names)}种Fontname。\n")
        self.text_area.insert(tk.END, f"获取到的Fontnames: {', '.join(self.font_names)}\n")
        self.text_area.insert(tk.END, f"共获取{len(self.characters)}个字符。\n")
        self.text_area.insert(tk.END, f"获取到的字符: {', '.join(self.characters)}\n")

    def export_results(self):
        """ 导出提取的结果到TXT文件 """
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], initialfile="ASSInfo")
        if not file_path:
            return

        with open(file_path, "w", encoding="utf-8") as file:
            file.write("\n".join(self.font_names))
            file.write("\n\n")
            file.write("".join(self.characters))

        self.text_area.insert(tk.END, "TXT文件已保存。\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ASSProcessorApp(root)
    root.mainloop()

