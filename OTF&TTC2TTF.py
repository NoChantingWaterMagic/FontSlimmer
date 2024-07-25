import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from fontTools.ttLib import TTFont, ttCollection

def select_files():
    filetypes = (
        ('font files', '*.ttf *.ttc *.otf'),
        ('All files', '*.*')
    )
    filenames = filedialog.askopenfilenames(
        title='选择字体文件',
        initialdir='/',
        filetypes=filetypes)

    file_list.delete(0, tk.END)
    for filename in filenames:
        file_list.insert(tk.END, filename.replace(os.sep, '/'))

def get_font_name(font):
    nameID_order = [(1, 3, 2052), (16, 3, 0), (1, 3, 0), (4, 3, 0)]
    for (nameID, platformID, langID) in nameID_order:
        for record in font['name'].names:
            if record.nameID == nameID and record.platformID == platformID:
                if langID == 0 or record.langID == langID:
                    return record.string.decode('utf-16-be' if record.platformID == 3 else 'latin-1').replace(" ", "_")
    return "Unnamed_Font"

def convert_fonts():
    output_dir = filedialog.askdirectory(title='选择输出目录')
    if not output_dir:
        messagebox.showinfo("信息", "需要选择一个输出目录")
        return

    output_dir = os.path.join(output_dir, "otf+ttc2TTF").replace(os.sep, '/')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    total_files = len(file_list.get(0, tk.END))
    progress_bar['value'] = 0
    progress_bar['maximum'] = total_files

    for index, font_path in enumerate(file_list.get(0, tk.END), start=1):
        try:
            font_ext = os.path.splitext(font_path)[1].lower()
            if font_ext == '.ttc':
                ttc = ttCollection.TTCollection(font_path)
                for idx, font in enumerate(ttc.fonts):
                    font_name = get_font_name(font)
                    output_path = os.path.join(output_dir, f"{font_name}.ttf").replace(os.sep, '/')
                    font.save(output_path)
            elif font_ext in ['.otf', '.ttf']:  # Handle OTF and TTF similarly
                font = TTFont(font_path)
                font.flavor = None  # Ensures conversion to TTF if it's an OTF
                font_name = get_font_name(font)
                output_path = os.path.join(output_dir, f"{font_name}.ttf").replace(os.sep, '/')
                font.save(output_path)
            update_status(f"已转换: {font_path} -> {output_path}")
            progress_bar['value'] = index
            app.update_idletasks()  # Update progress bar
        except Exception as e:
            update_status(f"错误: 转换 {font_path} 失败，{str(e)}")
            continue

def update_status(message):
    status_text.configure(state='normal')
    status_text.insert(tk.END, message + "\n")
    status_text.configure(state='disabled')
    status_text.see(tk.END)

app = tk.Tk()
app.title('字体转换工具')
app.geometry('600x450')

frame = tk.Frame(app)
frame.pack(fill=tk.BOTH, expand=True)

status_text = scrolledtext.ScrolledText(frame, state='normal', height=2)
status_text.insert(tk.END, '选择otf和ttc格式文件转换成ttf')
status_text.configure(state='disabled')
status_text.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)

file_list = tk.Listbox(frame, height=6)
file_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

scrollbar = tk.Scrollbar(file_list)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
file_list.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=file_list.yview)

button_frame = tk.Frame(frame)
button_frame.pack(fill=tk.X, expand=False)

btn_select = tk.Button(button_frame, text='选择字体文件', command=select_files)
btn_select.pack(side=tk.LEFT, padx=10, pady=10)

btn_convert = tk.Button(button_frame, text='转换为TTF', command=convert_fonts)
btn_convert.pack(side=tk.LEFT, padx=10, pady=10)

progress_bar = ttk.Progressbar(button_frame, orient='horizontal', mode='determinate', length=280)
progress_bar.pack(side=tk.LEFT, padx=10, pady=10)

status_text = scrolledtext.ScrolledText(frame, state='disabled', height=8)
status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

app.mainloop()
