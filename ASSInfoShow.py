import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from tkinter.ttk import Progressbar, Label, Frame
import os
import re
import pyperclip

class ASSProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ASS字幕处理工具")
        self.root.geometry("800x600")  # 设置默认的窗口大小
        self.setup_ui()

    def setup_ui(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.load_btn = tk.Button(self.frame, text="加载ASS文件", command=self.load_and_initialize)
        self.load_btn.pack(pady=10)

        self.info_label = Label(self.frame, text="")
        self.info_label.pack()

        self.text_area = scrolledtext.ScrolledText(self.frame, width=90, height=20)
        self.text_area.pack(pady=10, fill=tk.BOTH, expand=True)

        # 用于显示复制到剪贴板的字符数量
        self.clipboard_info_label = Label(self.frame, text="")
        self.clipboard_info_label.pack(pady=10)

        # 底部容器，包含导出结果、进度条和复制结果按钮
        self.bottom_frame = Frame(self.frame)
        self.bottom_frame.pack(fill=tk.X, pady=10)

        self.export_btn = tk.Button(self.bottom_frame, text="导出结果", command=self.export_results)
        self.export_btn.pack(side=tk.LEFT, padx=10)

        self.progress = Progressbar(self.bottom_frame, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(side=tk.LEFT, padx=20, expand=True, fill=tk.X)

        self.copy_btn = tk.Button(self.bottom_frame, text="复制结果", command=self.copy_results)
        self.copy_btn.pack(side=tk.LEFT, padx=10)

        self.font_names = set()
        self.characters = set()

    def load_and_initialize(self):
        # 清空先前的数据
        self.initialize()
        # 打开文件对话框并加载文件
        self.load_files()

    def load_files(self):
        file_paths = filedialog.askopenfilenames(title="选择ASS字幕文件", filetypes=(("ASS Files", "*.ass"),))
        total_files = len(file_paths)
        self.progress['maximum'] = total_files
        self.progress['value'] = 0

        for file_path in file_paths:
            self.process_file(file_path)
            self.progress['value'] += 1
            self.root.update_idletasks()

        self.display_results()
        self.info_label.config(text=f"读取了{total_files}个ASS字幕文件，获取到了{len(self.font_names)}种字体，共获取{len(self.characters)}个字符。")

    def process_file(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        styles = re.findall(r"Style:.*?,(.*?),", content)
        self.font_names.update(styles)

        dialogues = re.findall(r"Dialogue:.*?,.*?,.*?,.*?,.*?,.*?,.*?,.*?,.*?,(.*?)\n", content)
        text = ' '.join(dialogues)
        self.characters.update(set(text))

    def display_results(self):
        self.text_area.insert(tk.END, f"处理完成。\n获取到的字体: {', '.join(self.font_names)}\n")
        self.text_area.insert(tk.END, f"获取到的字符: {', '.join(self.characters)}\n")

    def export_results(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")], initialfile="ASSInfo")
        if not file_path:
            return

        with open(file_path, "w", encoding='utf-8') as file:
            file.write("\n".join(self.font_names))
            file.write("\n\n")
            file.write("".join(self.characters))

        self.text_area.insert(tk.END, "TXT文件已保存。\n")

    def initialize(self):
        self.font_names.clear()
        self.characters.clear()
        self.text_area.delete('1.0', tk.END)
        self.progress['value'] = 0
        self.clipboard_info_label.config(text="")

    def copy_results(self):
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

