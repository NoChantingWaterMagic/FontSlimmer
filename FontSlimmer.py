import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
import os
import random
import string
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options
import pyperclip
import shutil


def reset_app():
    """重置应用程序状态"""
    lbl_fonts.config(text="未加载字体")
    lbl_chars.config(text="未加载字符")
    txt_display.config(state=tk.NORMAL)
    txt_display.delete('1.0', tk.END)
    txt_display.config(state=tk.DISABLED)
    progress_bar['value'] = 0
    progress_label.config(text="0/0")
    lbl_status.config(text="")

def load_fonts():
    reset_app()  # 每次加载字体前重置应用状态
    global font_paths
    font_paths = filedialog.askopenfilenames(filetypes=[("TrueType 字体文件", "*.ttf")])
    if font_paths:
        lbl_fonts.config(text=f"已加载 {len(font_paths)} 个字体")

def load_characters():
    txt_path = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt")])
    if txt_path:
        with open(txt_path, 'r', encoding='utf-8') as file:
            global characters
            characters = file.read()
        display_characters(characters)


def read_clipboard():
    try:
        clipboard_content = pyperclip.paste()
        if clipboard_content:
            global characters
            characters = clipboard_content
            display_characters(characters)
        else:
            messagebox.showinfo("读取剪贴板", "剪贴板为空，请复制一些文本后再试。")
    except Exception as e:
        messagebox.showerror("读取剪贴板错误", f"无法从剪贴板读取数据: {e}")

def display_characters(characters):
    char_set = set(characters)
    txt_display.config(state=tk.NORMAL)
    txt_display.delete('1.0', tk.END)
    txt_display.insert(tk.END, ', '.join(char_set))
    txt_display.config(state=tk.DISABLED)
    lbl_chars.config(text=f"已加载字符: 共 {len(char_set)} 个独特字符")

def generate_random_folder_name():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=10))

def subset_fonts():
    if not font_paths or not characters:
        lbl_status.config(text="错误: 请先加载字体文件和字符集。")
        return
    output_dir = filedialog.askdirectory()
    if not output_dir:
        lbl_status.config(text="错误: 未选择输出目录。")
        return

    new_fonts_path = os.path.join(output_dir, "NewFontsReady2Use")
    if os.path.exists(new_fonts_path):
        try:
            shutil.rmtree(new_fonts_path)
        except Exception as e:
            lbl_status.config(text=f"错误: 无法删除旧文件夹 {new_fonts_path}: {e}")
            return
    os.makedirs(new_fonts_path, exist_ok=True)

    options = Options()
    options.layout_features = ['*']
    options.name_IDs = ['*']
    options.name_legacy = True
    options.notdef_outline = True
    options.recalc_bounds = True
    options.recalc_timestamp = False
    options.canonical_order = True

    total_fonts = len(font_paths)
    progress_bar['maximum'] = total_fonts
    for index, font_path in enumerate(font_paths):
        try:
            font = TTFont(font_path)
            original_name = font['name'].names
            subsetter = Subsetter(options=options)
            subsetter.populate(text=characters)
            subsetter.subset(font)
            font['name'].names = original_name
            output_path = os.path.join(new_fonts_path, os.path.basename(font_path))
            font.save(output_path)
            progress_bar['value'] = index + 1
            progress_label.config(text=f"{index + 1}/{total_fonts}")
            root.update_idletasks()
        except Exception as e:
            lbl_status.config(text=f"处理失败 {os.path.basename(font_path)}: {e}")
            continue  # Continue processing the next font even if the current one fails
    lbl_status.config(text="程序运行完成。")

root = tk.Tk()
root.title("字体子集化工具")
root.geometry("410x480")

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

ttk.Button(frame, text="加载字体", command=load_fonts).grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")
lbl_fonts = ttk.Label(frame, text="未加载字体")
lbl_fonts.grid(row=1, column=0, columnspan=2, pady=5)

ttk.Button(frame, text="从txt加载字符", command=load_characters).grid(row=2, column=0, sticky="ew", padx=5, pady=10)
ttk.Button(frame, text="读取剪贴板", command=read_clipboard).grid(row=2, column=1, sticky="ew", padx=5, pady=10)
lbl_chars = ttk.Label(frame, text="未加载字符")
lbl_chars.grid(row=3, column=0, columnspan=2, pady=5)

txt_display = scrolledtext.ScrolledText(frame, height=10, width=50)
txt_display.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")
txt_display.config(state=tk.DISABLED)

progress_bar = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
progress_bar.grid(row=5, column=0, columnspan=2, pady=20, sticky="ew")
progress_label = ttk.Label(frame, text="0/0")
progress_label.grid(row=6, column=0, columnspan=2, pady=5)

ttk.Button(frame, text="子集化字体", command=subset_fonts).grid(row=7, column=0, columnspan=2, pady=10, sticky="ew")
lbl_status = ttk.Label(frame, text="")
lbl_status.grid(row=8, column=0, columnspan=2, pady=5)

root.mainloop()



