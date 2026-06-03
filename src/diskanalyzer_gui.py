#!/usr/bin/env python3
import os
import sys
import hashlib
import threading
import tkinter as tk
from tkinter import ttk, filedialog
from collections import defaultdict
from datetime import datetime, timedelta

class DiskAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Disk Analyzer")
        self.root.geometry("950x750")
        self.root.resizable(True, True)
        self.current_path = tk.StringVar(value=os.path.expanduser("~"))
        self.setup_ui()
        self.root.protocol("WM_DELETE_WINDOW", self.root.quit)
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        top_frame = ttk.LabelFrame(main_frame, text="Выбор директории", padding="5")
        top_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(top_frame, text="Путь:").pack(side=tk.LEFT, padx=5)
        entry = ttk.Entry(top_frame, textvariable=self.current_path, width=70)
        entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(top_frame, text="Обзор", command=self.select_path).pack(side=tk.LEFT, padx=5)
        
        button_frame = ttk.LabelFrame(main_frame, text="Действия", padding="5")
        button_frame.pack(fill=tk.X, pady=5)
        
        buttons = [
            ("Анализ папки", self.start_analyze),
            ("Поиск дубликатов", self.start_duplicates),
            ("Старые файлы", self.start_old),
            ("Пустые папки", self.start_empty),
            ("Типы файлов", self.start_types),
            ("Самые большие", self.start_large),
            ("Очистить", self.clear_result),
            ("Закрыть", self.root.quit)
        ]
        
        for text, command in buttons:
            ttk.Button(button_frame, text=text, command=command).pack(side=tk.LEFT, padx=3, pady=3)
        
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)
        
        self.status_var = tk.StringVar(value="Готов")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=2)
        
        result_frame = ttk.LabelFrame(main_frame, text="Результаты", padding="5")
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        text_frame = ttk.Frame(result_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.result_text = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10), yscrollcommand=scrollbar.set)
        self.result_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.result_text.yview)
    
    def select_path(self):
        path = filedialog.askdirectory()
        if path:
            self.current_path.set(path)
    
    def clear_result(self):
        self.result_text.delete(1.0, tk.END)
    
    def log(self, msg):
        self.result_text.insert(tk.END, msg + "\n")
        self.result_text.see(tk.END)
        self.root.update_idletasks()
    
    def set_status(self, msg):
        self.status_var.set(msg)
        self.root.update_idletasks()
    
    def start_progress(self):
        self.progress.start(10)
        self.set_status("Работает...")
    
    def stop_progress(self):
        self.progress.stop()
        self.set_status("Готов")
    
    def get_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
    
    def get_dir_size(self, path):
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self.get_dir_size(entry.path)
        except:
            pass
        return total
    
    def run_thread(self, target):
        self.clear_result()
        self.start_progress()
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        self.check_thread(thread)
    
    def check_thread(self, thread):
        if thread.is_alive():
            self.root.after(100, lambda: self.check_thread(thread))
        else:
            self.stop_progress()
    
    def do_analyze(self):
        path = os.path.expanduser(self.current_path.get())
        if not os.path.exists(path):
            self.log(f"Ошибка: {path} не существует")
            return
        self.log(f"Анализ: {path}")
        self.log("=" * 60)
        items = []
        total = 0
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                total += size
                items.append((size, item, "FILE"))
            elif os.path.isdir(item_path):
                size = self.get_dir_size(item_path)
                total += size
                items.append((size, item, "DIR"))
        items.sort(reverse=True)
        self.log(f"Всего: {len(items)} элементов")
        self.log(f"Размер: {self.get_size(total)}")
        self.log("\nТоп 15:\n")
        for size, name, typ in items[:15]:
            self.log(f"{self.get_size(size):>12} | {typ} | {name}")
    
    def start_analyze(self):
        self.run_thread(self.do_analyze)
    
    def do_duplicates(self):
        path = os.path.expanduser(self.current_path.get())
        self.log(f"Поиск дубликатов: {path}")
        self.log("=" * 60)
        by_size = defaultdict(list)
        for root, dirs, files in os.walk(path):
            for file in files:
                try:
                    fp = os.path.join(root, file)
                    by_size[os.path.getsize(fp)].append(fp)
                except:
                    pass
        dup = []
        for size, flist in by_size.items():
            if len(flist) > 1:
                hashes = defaultdict(list)
                for fp in flist:
                    try:
                        with open(fp, 'rb') as f:
                            h = hashlib.md5(f.read(4096)).hexdigest()
                        hashes[h].append(fp)
                    except:
                        pass
                for h, hlist in hashes.items():
                    if len(hlist) > 1:
                        dup.append((size, hlist))
        if not dup:
            self.log("Дубликатов нет")
            return
        self.log(f"Найдено {len(dup)} групп\n")
        for size, files in dup:
            self.log(f"Размер: {self.get_size(size)}")
            for f in files:
                self.log(f"  - {f}")
            self.log("")
    
    def start_duplicates(self):
        self.run_thread(self.do_duplicates)
    
    def do_old(self):
        path = os.path.expanduser(self.current_path.get())
        days = 30
        cutoff = datetime.now() - timedelta(days=days)
        self.log(f"Файлы старше {days} дней: {path}")
        self.log("=" * 60)
        old = []
        for root, dirs, files in os.walk(path):
            for file in files:
                try:
                    fp = os.path.join(root, file)
                    mtime = datetime.fromtimestamp(os.path.getmtime(fp))
                    if mtime < cutoff:
                        old.append((mtime, os.path.getsize(fp), fp))
                except:
                    pass
        old.sort()
        if not old:
            self.log("Нет старых файлов")
            return
        self.log(f"Найдено {len(old)} файлов\n")
        for mtime, size, fp in old[:50]:
            self.log(f"{mtime.strftime('%Y-%m-%d')} | {self.get_size(size):>12} | {fp}")
    
    def start_old(self):
        self.run_thread(self.do_old)
    
    def do_empty(self):
        path = os.path.expanduser(self.current_path.get())
        self.log(f"Пустые папки: {path}")
        self.log("=" * 60)
        empty = []
        for root, dirs, files in os.walk(path):
            try:
                if not os.listdir(root):
                    empty.append(root)
            except:
                pass
        if not empty:
            self.log("Пустых папок нет")
            return
        self.log(f"Найдено {len(empty)} папок\n")
        for d in empty[:50]:
            self.log(f"  - {d}")
    
    def start_empty(self):
        self.run_thread(self.do_empty)
    
    def do_types(self):
        path = os.path.expanduser(self.current_path.get())
        self.log(f"Типы файлов: {path}")
        self.log("=" * 60)
        types = defaultdict(int)
        for root, dirs, files in os.walk(path):
            for file in files:
                try:
                    ext = os.path.splitext(file)[1].lower() or "no_ext"
                    types[ext] += 1
                except:
                    pass
        types = sorted(types.items(), key=lambda x: x[1], reverse=True)
        for ext, count in types[:30]:
            self.log(f"{ext:<20} : {count} файлов")
    
    def start_types(self):
        self.run_thread(self.do_types)
    
    def do_large(self):
        path = os.path.expanduser(self.current_path.get())
        self.log(f"Крупные файлы: {path}")
        self.log("=" * 60)
        files = []
        for root, dirs, flist in os.walk(path):
            for file in flist:
                try:
                    fp = os.path.join(root, file)
                    files.append((os.path.getsize(fp), fp))
                except:
                    pass
        files.sort(reverse=True)
        self.log("\nТоп 30:\n")
        for size, fp in files[:30]:
            self.log(f"{self.get_size(size):>12} | {fp}")
    
    def start_large(self):
        self.run_thread(self.do_large)

def main():
    root = tk.Tk()
    app = DiskAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
