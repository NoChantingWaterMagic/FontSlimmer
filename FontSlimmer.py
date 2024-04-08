import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk
import os
from fontTools.ttLib import TTFont
from fontTools.subset import Subsetter, Options

def load_fonts():
    """加载字体文件。此函数用于弹出文件选择对话框，让用户选择要处理的TrueType字体文件，并在界面上显示已加载的字体数量。"""
    global font_paths  # 使用全局变量存储字体文件路径
    font_paths = filedialog.askopenfilenames(filetypes=[("TrueType 字体文件", "*.ttf")])  # 文件选择对话框
    if font_paths:
        lbl_fonts.config(text=f"已加载 {len(font_paths)} 个字体")  # 更新界面上的字体文件数量显示

def load_characters():
    """加载字符集。此函数用于加载用户指定的文本文件，提取文件中的所有字符，并在界面上显示这些字符。"""
    txt_path = filedialog.askopenfilename(filetypes=[("文本文件", "*.txt")])  # 文件选择对话框
    if txt_path:
        with open(txt_path, 'r', encoding='utf-8') as file:
            global characters  # 使用全局变量存储字符集
            characters = file.read()
            char_set = set(characters)  # 提取所有独特的字符
            txt_display.config(state=tk.NORMAL)
            txt_display.delete('1.0', tk.END)
            txt_display.insert(tk.END, ', '.join(char_set))
            txt_display.config(state=tk.DISABLED)
            lbl_chars.config(text=f"已加载字符: 共 {len(char_set)} 个独特字符")  # 显示加载的字符数量

def subset_fonts():
    """进行字体子集化处理。此函数用于读取已加载的字体文件，应用子集化处理，并将处理后的结果保存到用户指定的目录。"""
    if not font_paths or not characters:
        lbl_status.config(text="错误: 请先加载字体文件和字符集。")  # 检查是否已加载字体和字符
        return
    output_dir = filedialog.askdirectory()  # 弹出目录选择对话框
    if not output_dir:
        lbl_status.config(text="错误: 未选择输出目录。")  # 检查是否已选择输出目录
        return

    options = Options()
    options.layout_features = ['*']  # 保留所有字体布局特性
    options.name_IDs = ['*']  # 保留所有名称标识符
    options.name_legacy = True
    options.notdef_outline = True
    options.recalc_bounds = True
    options.recalc_timestamp = False
    options.canonical_order = True  # 保证表的规范顺序

    total_fonts = len(font_paths)
    progress_bar['maximum'] = total_fonts  # 设置进度条最大值
    for index, font_path in enumerate(font_paths):
        try:
            font = TTFont(font_path)
            original_name = font['name'].names  # 备份原始的name表
            subsetter = Subsetter(options=options)
            subsetter.populate(text=characters)
            subsetter.subset(font)
            font['name'].names = original_name  # 恢复原始的name表
            output_path = os.path.join(output_dir, os.path.basename(font_path))
            font.save(output_path)
            progress_bar['value'] = index + 1
            progress_label.config(text=f"{index + 1}/{total_fonts}")
            root.update_idletasks()
        except Exception as e:
            lbl_status.config(text=f"处理失败 {os.path.basename(font_path)}: {e}")  # 异常处理
            return
    lbl_status.config(text="程序运行完成。")  # 更新状态显示

# 设置GUI界面和布局
root = tk.Tk()
root.title("字体子集化工具")
root.geometry("1000x700")  # 设置默认窗口大小

frame = tk.Frame(root)
frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

ttk.Button(frame, text="加载字体", command=load_fonts).pack(pady=10)
lbl_fonts = ttk.Label(frame, text="未加载字体")
lbl_fonts.pack(pady=5)

ttk.Button(frame, text="加载字符", command=load_characters).pack(pady=10)
lbl_chars = ttk.Label(frame, text="未加载字符")
lbl_chars.pack(pady=5)

txt_display = scrolledtext.ScrolledText(frame, height=10, width=70)
txt_display.pack(pady=10, fill=tk.BOTH, expand=True)
txt_display.config(state=tk.DISABLED)

progress_bar = ttk.Progressbar(frame, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=20)
progress_label = ttk.Label(frame, text="0/0")
progress_label.pack(pady=5)

ttk.Button(frame, text="子集化字体", command=subset_fonts).pack(pady=10)
lbl_status = ttk.Label(frame, text="")
lbl_status.pack(pady=5)

root.mainloop()

