import keyboard
import subprocess
import os
import time
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
from datetime import datetime
import glob
import sys
import atexit
import getpass
import threading
import ctypes
from ctypes import wintypes
import psutil
import shutil

# 确保中文显示正常
import matplotlib
matplotlib.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]

class TextFileManager:
    def __init__(self):
        self.current_file_path = None
        self.file_creation_time = None
        self.desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
        self.running = True  
        self.registered_hotkeys = []
        
        # 确保程序完全独立运行的关键设置
        self.make_fully_standalone()
        
        if not os.path.exists(self.desktop_path):
            os.makedirs(self.desktop_path)
        
        # 创建隐藏的主窗口（用于对话框）
        self.root = tk.Tk()
        self.root.withdraw()  
        self.root.protocol("WM_DELETE_WINDOW", self.on_root_close)
        
        self.start_hotkey_service()
        
        atexit.register(self.cleanup)
        self.setup_autostart()
        
        print("文本文件管理器已启动，完全独立运行中...")
        print("进程名称: 麟时文件管理器")
        print("快捷键:")
        print("Win+Alt+W - 创建并打开新的临时文件")
        print("Win+Alt+S - 保存当前文件并输入备注")
        print("Win+Alt+R - 浏览所有已保存的文件")
        print("要退出程序，请在任务管理器中结束进程")

    def make_fully_standalone(self):
        """确保程序完全独立运行，不依赖任何父进程"""
        if os.name == 'nt':
            try:
                # 更改控制台标题，便于在任务管理器中识别
                ctypes.windll.kernel32.SetConsoleTitleW("麟时文件管理器")
                
                # 获取当前进程ID
                current_pid = os.getpid()
                
                # 创建新的进程组，彻底脱离父进程控制
                if ctypes.windll.kernel32.SetProcessGroupId(current_pid, current_pid) == 0:
                    print("已创建独立进程组，完全脱离父进程控制")
                
                # 设置进程为正常优先级
                h_process = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, current_pid)
                ctypes.windll.kernel32.SetPriorityClass(h_process, 0x00000020)  # 正常优先级
                
                # 忽略所有控制台关闭事件
                @ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.DWORD)
                def console_handler(dwCtrlType):
                    # 忽略所有控制事件，包括关闭控制台窗口
                    return True
                ctypes.windll.kernel32.SetConsoleCtrlHandler(console_handler, True)
                
            except Exception as e:
                print(f"设置独立运行时出错: {str(e)}")

    def on_root_close(self):
        """处理主窗口关闭事件，确保程序继续运行"""
        self.root.withdraw()

    def start_hotkey_service(self):
        # 定义快捷键列表
        hotkeys = [
            ('win+alt+w', self.create_and_open_file),
            ('win+alt+s', self.save_current_file),
            ('win+alt+r', self.browse_files_with_links)
        ]
        self.registered_hotkeys = hotkeys
        
        # 初始注册快捷键
        for hotkey, callback in hotkeys:
            keyboard.add_hotkey(hotkey, callback, suppress=False)
        
        # 启动监听线程
        self.hotkey_service = threading.Thread(target=self.hotkey_listener, daemon=False)
        self.hotkey_service.name = "HotkeyListener"
        self.hotkey_service.start()

    def hotkey_listener(self):
        """快捷键监听循环，定期重新注册确保有效"""
        while self.running:
            time.sleep(1)  # 每1秒重新注册一次
            for hotkey, callback in self.registered_hotkeys:
                try:
                    keyboard.remove_hotkey(hotkey)
                except:
                    pass  # 忽略移除失败的情况
                keyboard.add_hotkey(hotkey, callback, suppress=False)

    def setup_autostart(self):
        """设置程序开机自启，确保每次开机后自动独立运行"""
        try:
            if os.name == 'nt':
                # 获取当前程序路径（兼容打包后的exe）
                if getattr(sys, 'frozen', False):
                    # 打包后的可执行文件
                    exe_path = sys.executable
                else:
                    # 未打包时使用pythonw.exe运行脚本，避免显示控制台窗口
                    python_exe = os.path.join(sys.prefix, 'pythonw.exe')
                    script_path = os.path.abspath(sys.argv[0])
                    exe_path = f'"{python_exe}" "{script_path}"'
                
                # 开机启动目录
                user = getpass.getuser()
                autostart_path = f"C:\\Users\\{user}\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"
                shortcut_name = "麟时文件管理器.lnk"
                shortcut_path = os.path.join(autostart_path, shortcut_name)
                
                # 创建快捷方式（如果不存在）
                if not os.path.exists(shortcut_path):
                    self.create_shortcut(exe_path, shortcut_path)
                    print(f"已设置开机自启，快捷方式位于: {shortcut_path}")
                else:
                    print("开机自启已设置")
            else:
                print("非Windows系统，暂不支持开机自启设置")
        except Exception as e:
            print(f"设置开机自启时出错: {str(e)}")

    def cleanup(self):
        """程序退出时的清理工作"""
        self.running = False
        keyboard.unhook_all_hotkeys()

    def get_beijing_time(self):
        beijing_timestamp = time.time() + 8 * 3600
        return datetime.fromtimestamp(beijing_timestamp).strftime("%Y%m%d_%H%M%S")

    def create_and_open_file(self):
        self.root.after(0, self._create_and_open_file_impl)

    def _create_and_open_file_impl(self):
        try:
            self.file_creation_time = self.get_beijing_time()
            temp_filename = f"麟时文件_{self.file_creation_time}.txt"
            self.current_file_path = os.path.join(self.desktop_path, temp_filename)
            
            with open(self.current_file_path, 'w', encoding='utf-8') as f:
                pass
            
            self.open_file(self.current_file_path)
            print(f"已创建并打开临时文件: {self.current_file_path}")
            
        except Exception as e:
            print(f"创建文件时出错: {str(e)}")
            messagebox.showerror("错误", f"创建文件时出错: {str(e)}")

    def save_current_file(self):
        self.root.after(0, self._save_current_file_impl)

    def _save_current_file_impl(self):
        if not self.current_file_path or not os.path.exists(self.current_file_path):
            self.show_always_on_top_message("提示", "没有可保存的临时文件，请先创建新文件(Win+Alt+W)")
            return
        
        # 显示高优先级的备注输入窗口（核心改进）
        note = self.show_always_on_top_input("输入备注", "请输入文件备注:")
        if not note:
            return
            
        invalid_chars = '/\\:*?"<>|'
        for char in invalid_chars:
            note = note.replace(char, '_')
        
        # 生成新文件路径，保持原有命名格式
        new_filename = f"{note}_麟时文件_{self.file_creation_time}.txt"
        new_file_path = os.path.join(self.desktop_path, new_filename)
        
        try:
            # 提示用户先在编辑器中保存内容
            self.show_always_on_top_message("提示", "请确保已在编辑器中保存文件内容，然后点击确定继续")
            
            # 关闭文件编辑器（兼容多种编辑器）
            if not self.close_file(self.current_file_path):
                if not self.show_always_on_top_yesno("提示", "无法自动关闭文件编辑器，请手动关闭文件后点击'是'继续"):
                    return
            
            # 检查文件是否已关闭
            if not self.is_file_closed(self.current_file_path):
                self.show_always_on_top_message("错误", "文件仍在被占用，请确保已关闭文件后重试")
                return
            
            # 复制原文件内容到新文件
            shutil.copy2(self.current_file_path, new_file_path)
            
            # 保存后删除源文件（核心改进）
            try:
                os.remove(self.current_file_path)
                print(f"已删除源文件: {self.current_file_path}")
            except Exception as e:
                print(f"删除源文件时出错: {str(e)}")
                self.show_always_on_top_message("警告", f"已创建新文件，但删除源文件时出错:\n{str(e)}")
            
            print(f"已创建新文件并复制内容: {new_file_path}")
            self.show_always_on_top_message("成功", f"文件已保存为:\n{new_file_path}")
            
            # 重置当前文件路径
            self.current_file_path = None
            self.file_creation_time = None
            
        except Exception as e:
            print(f"保存文件时出错: {str(e)}")
            self.show_always_on_top_message("错误", f"保存文件时出错: {str(e)}\n请确保文件已关闭")

    def show_always_on_top_message(self, title, message):
        """显示始终置顶的消息框"""
        msg_box = tk.Toplevel(self.root)
        msg_box.withdraw()
        msg_box.title(title)
        msg_box.geometry("300x150")
        msg_box.configure(bg="#f0f0f0")
        msg_box.attributes("-topmost", True)  # 窗口置顶
        
        label = ttk.Label(msg_box, text=message, wraplength=280)
        label.pack(pady=20)
        
        btn = ttk.Button(msg_box, text="确定", command=msg_box.destroy)
        btn.pack(pady=10)
        
        # 确保窗口显示在最前面
        msg_box.update_idletasks()
        msg_box.deiconify()
        msg_box.lift()
        self.root.wait_window(msg_box)

    def show_always_on_top_yesno(self, title, message):
        """显示始终置顶的Yes/No对话框"""
        msg_box = tk.Toplevel(self.root)
        msg_box.withdraw()
        msg_box.title(title)
        msg_box.geometry("300x150")
        msg_box.configure(bg="#f0f0f0")
        msg_box.attributes("-topmost", True)  # 窗口置顶
        result = [False]  # 使用列表存储结果
        
        label = ttk.Label(msg_box, text=message, wraplength=280)
        label.pack(pady=20)
        
        def on_yes():
            result[0] = True
            msg_box.destroy()
            
        def on_no():
            result[0] = False
            msg_box.destroy()
        
        btn_frame = ttk.Frame(msg_box)
        btn_frame.pack(pady=10)
        
        yes_btn = ttk.Button(btn_frame, text="是", command=on_yes)
        yes_btn.pack(side=tk.LEFT, padx=10)
        
        no_btn = ttk.Button(btn_frame, text="否", command=on_no)
        no_btn.pack(side=tk.LEFT, padx=10)
        
        # 确保窗口显示在最前面
        msg_box.update_idletasks()
        msg_box.deiconify()
        msg_box.lift()
        self.root.wait_window(msg_box)
        
        return result[0]

    def show_always_on_top_input(self, title, prompt):
        """显示始终置顶的输入对话框（核心改进）"""
        input_box = tk.Toplevel(self.root)
        input_box.withdraw()
        input_box.title(title)
        input_box.geometry("300x150")
        input_box.configure(bg="#f0f0f0")
        input_box.attributes("-topmost", True)  # 窗口置顶
        result = [None]  # 使用列表存储结果
        
        label = ttk.Label(input_box, text=prompt, wraplength=280)
        label.pack(pady=10)
        
        entry = ttk.Entry(input_box, width=30)
        entry.pack(pady=10)
        entry.focus_set()  # 设置焦点
        
        def on_ok():
            result[0] = entry.get()
            input_box.destroy()
            
        def on_cancel():
            result[0] = None
            input_box.destroy()
        
        btn_frame = ttk.Frame(input_box)
        btn_frame.pack(pady=10)
        
        ok_btn = ttk.Button(btn_frame, text="确定", command=on_ok)
        ok_btn.pack(side=tk.LEFT, padx=10)
        
        cancel_btn = ttk.Button(btn_frame, text="取消", command=on_cancel)
        cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # 按Enter键确认
        input_box.bind('<Return>', lambda event: on_ok())
        # 按ESC键取消
        input_box.bind('<Escape>', lambda event: on_cancel())
        
        # 确保窗口显示在最前面
        input_box.update_idletasks()
        input_box.deiconify()
        input_box.lift()
        self.root.wait_window(input_box)
        
        return result[0]

    def is_file_closed(self, file_path):
        if not os.path.exists(file_path):
            return True
            
        try:
            with open(file_path, 'a'):
                return True
        except IOError:
            return False

    def close_file(self, file_path):
        try:
            if os.name == 'nt':
                filename = os.path.basename(file_path)
                
                # 尝试关闭记事本
                notepad_result = subprocess.run(
                    ['taskkill', '/f', '/im', 'notepad.exe', '/fi', f'windowtitle eq {filename}*'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
                )
                
                # 尝试关闭VSCode
                code_result = subprocess.run(
                    ['taskkill', '/f', '/im', 'code.exe', '/fi', f'windowtitle eq {filename}*'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
                )
                
                # 尝试关闭Notepad++
                notepadplus_result = subprocess.run(
                    ['taskkill', '/f', '/im', 'notepad++.exe', '/fi', f'windowtitle eq {filename}*'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
                )
                
                return notepad_result.returncode == 0 or code_result.returncode == 0 or notepadplus_result.returncode == 0
        
        except Exception as e:
            print(f"尝试关闭文件时出错: {str(e)}")
        
        return False

    def open_file(self, file_path):
        try:
            if os.name == 'nt':
                os.startfile(file_path)
            else:
                opener = 'open' if os.name == 'posix' else 'xdg-open'
                subprocess.Popen([opener, file_path])
        except Exception as e:
            print(f"打开文件时出错: {str(e)}")
            self.show_always_on_top_message("错误", f"打开文件时出错: {str(e)}")

    def browse_files_with_links(self):
        self.root.after(0, self._browse_files_with_links_impl)

    def _browse_files_with_links_impl(self):
        pattern = os.path.join(self.desktop_path, "*.txt")
        files = glob.glob(pattern)
        
        valid_files = []
        for file in files:
            filename = os.path.basename(file)
            if "麟时文件" in filename and filename.endswith(".txt"):
                valid_files.append(file)
        
        if not valid_files:
            self.show_always_on_top_message("提示", "没有找到符合条件的文件")
            return
        
        browse_window = tk.Toplevel(self.root)
        browse_window.title("文件列表 - 点击文件名编辑")
        browse_window.geometry("600x400")
        browse_window.configure(bg="#f0f0f0")
        browse_window.attributes("-topmost", True)  # 窗口置顶
        
        frame = ttk.Frame(browse_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        canvas = tk.Canvas(frame)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        for i, file_path in enumerate(valid_files):
            filename = os.path.basename(file_path)
            
            link = ttk.Label(
                scrollable_frame, 
                text=filename, 
                foreground="blue", 
                cursor="hand2",
                font=("SimHei", 10)
            )
            link.grid(row=i, column=0, sticky="w", pady=5, padx=5)
            
            def on_link_click(event, path=file_path):
                self.open_file(path)
                browse_window.destroy()
                
            link.bind("<Button-1>", on_link_click)

    def run(self):
        """主运行循环"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"\n程序异常: {str(e)}")
            if not self.hotkey_service.is_alive():
                print("快捷键服务已停止，尝试重启...")
                self.start_hotkey_service()
            self.run()

if __name__ == "__main__":
    # 确保只运行一个实例
    if os.name == 'nt':
        process_name = "麟时文件管理器"
        count = 0
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                cmdline = proc.info['cmdline'] if proc.info['cmdline'] is not None else []
                if process_name in proc.info['name'] or any(process_name in arg for arg in cmdline if arg):
                    count += 1
                    if count > 1:
                        print("程序已在后台运行")
                        sys.exit(0)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    # 检查依赖库
    required_libs = ['keyboard', 'pywin32']
    missing_libs = []
    
    
    
    # 启动程序
    manager = TextFileManager()
    manager.run()
