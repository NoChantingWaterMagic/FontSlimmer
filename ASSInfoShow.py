import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from tkinter.ttk import Progressbar, Label, Frame, Button
import os
import re
import pyperclip
import shutil
import sys

class ASSProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ASS字幕处理工具")
        self.root.geometry("800x700")  # 设置窗口大小
        self.default_font_path = os.path.expanduser("E:/hc550/root/kod_yyfiles/TU 100Pro/超级字体整合包 XZ/超级字体整合包 XZ 2024年1月下载")
        self.setup_ui()
        self.fuzzy_matched_fonts = []  # 用于存储模糊匹配到的字体名称

    def setup_ui(self):
        self.main_frame = Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.first_row_frame = Frame(self.main_frame)
        self.first_row_frame.pack(fill=tk.X)
        self.button_frame = Frame(self.first_row_frame)
        self.button_frame.pack(side=tk.TOP, expand=True)

        self.path_btn = Button(self.button_frame, text="添加寻找字体路径", command=self.set_font_path)
        self.path_btn.pack(side=tk.LEFT, padx=5)
        self.load_btn = Button(self.button_frame, text="加载ASS文件", command=self.load_and_initialize)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        self.find_font_btn = Button(self.button_frame, text="寻找字体", command=self.find_fonts)
        self.find_font_btn.pack(side=tk.LEFT, padx=5)

        self.status_frame = Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, pady=10)
        self.info_label = Label(self.status_frame, text="", wraplength=760)
        self.info_label.pack()

        self.text_area_frame = Frame(self.main_frame)
        self.text_area_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        self.text_area = scrolledtext.ScrolledText(self.text_area_frame, width=90, height=20)
        self.text_area.pack(pady=10, fill=tk.BOTH, expand=True)

        self.print_info_frame = Frame(self.main_frame)
        self.print_info_frame.pack(fill=tk.X, pady=10)
        self.clipboard_info_label = Label(self.print_info_frame, text="")
        self.clipboard_info_label.pack()

        self.bottom_frame = Frame(self.main_frame)
        self.bottom_frame.pack(fill=tk.X, pady=10)
        self.restart_btn = Button(self.bottom_frame, text="重启程序", command=self.restart_program)
        self.restart_btn.pack(side=tk.TOP, padx=10, pady=5)
        self.export_btn = Button(self.bottom_frame, text="导出结果", command=self.export_results)
        self.export_btn.pack(side=tk.LEFT, padx=10)
        self.progress = Progressbar(self.bottom_frame, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(side=tk.LEFT, padx=20, expand=True, fill=tk.X)
        self.copy_btn = Button(self.bottom_frame, text="复制结果", command=self.copy_results)
        self.copy_btn.pack(side=tk.LEFT, padx=10)

        self.font_names = set()
        self.characters = set()
        self.found_fonts = set()
        self.otf_count = 0

    def set_font_path(self):
        new_path = filedialog.askdirectory(title="选择新的字体文件夹路径")
        if new_path:
            self.default_font_path = new_path
            self.info_label.config(text=f"字体路径已更新到: {self.default_font_path}")

    def find_fonts(self):
        output_path = filedialog.askdirectory(title="选择输出路径")
        if not output_path:
            return

        # 统一路径分隔符
        output_path = output_path.replace('\\', '/')
        target_folder = os.path.join(output_path, "FontsFounded").replace('\\', '/')
        if os.path.exists(target_folder):
            shutil.rmtree(target_folder)
        os.makedirs(target_folder)

        ttf_otf_folder = os.path.join(target_folder, "OTF+TTF").replace('\\', '/')
        os.makedirs(ttf_otf_folder)

        font_extensions = {'.ttf': ['.ttf', '.TTF'], '.otf': ['.otf', '.OTF'], '.ttc': ['.ttc', '.TTC']}
        remaining_fonts = self.process_font_files(self.default_font_path.replace('\\', '/'), target_folder,
                                                  self.font_names.copy(),
                                                  font_extensions['.ttf'])
        remaining_fonts = self.process_font_files(self.default_font_path.replace('\\', '/'), ttf_otf_folder,
                                                  remaining_fonts,
                                                  font_extensions['.otf'])
        self.process_font_files(self.default_font_path.replace('\\', '/'), ttf_otf_folder, remaining_fonts,
                                font_extensions['.ttc'],
                                fuzzy=True)

        total_fonts = len(self.font_names)
        missing_count = len(remaining_fonts)
        message = f"字体搜索完成，结果已保存在: {target_folder}\n"
        if missing_count > 0:
            message += f"有{missing_count}个字体缺失（共{total_fonts}个）：{', '.join(remaining_fonts)}\n"
        if self.fuzzy_matched_fonts:
            message += f"模糊匹配找到的字体：{', '.join(self.fuzzy_matched_fonts)}"
        self.info_label.config(text=message)

    def process_font_files(self, search_path, output_path, font_list, extensions, fuzzy=False):
        for font_name in font_list.copy():
            found = False
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    file_base_name, file_ext = os.path.splitext(file)
                    if (fuzzy and font_name.lower() in file_base_name.lower() and file_ext.lower() in extensions) or (
                            not fuzzy and font_name.lower() == file_base_name.lower() and file_ext.lower() in extensions):
                        shutil.copy(os.path.join(root, file), output_path)
                        self.text_area.insert(tk.END, f"已找到并复制字体: {file}\n")
                        if fuzzy:
                            self.fuzzy_matched_fonts.append(font_name)
                        font_list.remove(font_name)
                        found = True
                        break
                if found:
                    break
        return font_list

    def update_fuzzy_match_info(self, fuzzy_found_fonts):
        # 在文本区域显示模糊匹配的详情
        if fuzzy_found_fonts:
            fuzzy_matched_info = "模糊匹配找到的字体：" + "、".join(fuzzy_found_fonts)
            self.text_area.insert(tk.END, f"{fuzzy_matched_info}\n")

    def load_and_initialize(self):
        self.initialize()
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
        # 尝试以不同的编码格式打开文件
        for encoding in ['utf-8', 'utf-16', 'gbk']:
            try:
                with open(file_path, 'r', encoding=encoding) as file:
                    content = file.read()
                # 如果成功读取，跳出循环
                break
            except UnicodeDecodeError:
                continue
        else:
            # 如果所有编码都失败了，显示错误消息并跳过此文件
            self.info_label.config(text=f"无法读取文件 {file_path}，尝试了utf-8, utf-16, 和gbk编码。")
            return

        # 提取字体名和对话内容
        styles = re.findall(r"Style:.*?,(.*?),", content)
        self.font_names.update(styles)

        dialogues = re.findall(r"Dialogue:.*?,.*?,.*?,.*?,.*?,.*?,.*?,.*?,.*?,(.*?)\n", content)
        text = ' '.join(dialogues)
        self.characters.update(set(text))

    def display_results(self):
        self.text_area.insert(tk.END, f"处理完成。\n获取到的字体: {', '.join(self.font_names)}\n")
        self.text_area.insert(tk.END, f"获取到的字符: {', '.join(self.characters)}\n")

    def export_results(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")],
                                                 initialfile="ASSInfo")
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

    def restart_program(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

if __name__ == "__main__":
    root = tk.Tk()
    app = ASSProcessorApp(root)
    root.mainloop()


