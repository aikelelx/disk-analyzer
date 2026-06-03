#!/usr/bin/env python3
"""
Disk Analyzer - анализ диска и работа с файлами
"""

import os
import sys
import hashlib
from collections import defaultdict
from datetime import datetime, timedelta

def get_size(size):
    """Форматирует размер"""
    for unit in ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} ПБ"

def format_date(timestamp):
    """Форматирует дату"""
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

def analyze_disk(path="."):
    """Анализирует папку"""
    path = os.path.expanduser(path)
    
    if not os.path.exists(path):
        print(f"❌ Не найдено: {path}")
        return
    
    print(f"\n📊 АНАЛИЗ ПАПКИ: {path}")
    print("=" * 60)
    
    items = []
    total_size = 0
    
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                total_size += size
                items.append((size, item, "📄"))
            elif os.path.isdir(item_path):
                size = get_dir_size(item_path)
                total_size += size
                items.append((size, item, "📁"))
    except:
        pass
    
    items.sort(reverse=True)
    
    print(f"\n📁 Всего элементов: {len(items)}")
    print(f"💾 Общий размер: {get_size(total_size)}")
    print("\n🔝 ТОП-15 ПО РАЗМЕРУ:\n")
    
    for size, name, icon in items[:15]:
        print(f"{icon} {get_size(size):>10} │ {name}")

def get_dir_size(path):
    """Получает размер папки"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    except:
        pass
    return total

def find_duplicates(path="."):
    """Находит дубликаты файлов"""
    path = os.path.expanduser(path)
    print(f"\n🔍 ПОИСК ДУБЛИКАТОВ В: {path}")
    print("=" * 60)
    
    files_by_size = defaultdict(list)
    
    # Сначала группируем по размеру
    for root, dirs, files in os.walk(path):
        for file in files:
            try:
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                files_by_size[size].append(file_path)
            except:
                pass
    
    # Проверяем хэши для файлов одинакового размера
    duplicates = []
    for size, file_list in files_by_size.items():
        if len(file_list) > 1:
            hashes = defaultdict(list)
            for file_path in file_list:
                try:
                    with open(file_path, 'rb') as f:
                        file_hash = hashlib.md5(f.read(4096)).hexdigest()
                    hashes[file_hash].append(file_path)
                except:
                    pass
            
            for hash_val, hash_files in hashes.items():
                if len(hash_files) > 1:
                    duplicates.append((size, hash_files))
    
    if not duplicates:
        print("✅ Дубликатов не найдено")
        return
    
    print(f"\n📋 Найдено {len(duplicates)} групп дубликатов:\n")
    for size, files in duplicates:
        print(f"📎 Размер: {get_size(size)}")
        for f in files:
            print(f"   - {f}")
        print()

def find_old_files(path=".", days=30):
    """Находит старые файлы"""
    path = os.path.expanduser(path)
    cutoff = datetime.now() - timedelta(days=days)
    
    print(f"\n📅 ФАЙЛЫ СТАРШЕ {days} ДНЕЙ В: {path}")
    print("=" * 60)
    
    old_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            try:
                file_path = os.path.join(root, file)
                mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                if mtime < cutoff:
                    size = os.path.getsize(file_path)
                    old_files.append((mtime, size, file_path))
            except:
                pass
    
    old_files.sort()
    
    if not old_files:
        print(f"✅ Файлов старше {days} дней не найдено")
        return
    
    print(f"\n📋 Найдено {len(old_files)} старых файлов:\n")
    for mtime, size, path in old_files[:30]:
        print(f"📅 {mtime.strftime('%Y-%m-%d')} │ {get_size(size):>10} │ {path}")
    
    if len(old_files) > 30:
        print(f"\n... и ещё {len(old_files) - 30} файлов")

def find_empty_dirs(path="."):
    """Находит пустые папки"""
    path = os.path.expanduser(path)
    print(f"\n📁 ПУСТЫЕ ПАПКИ В: {path}")
    print("=" * 60)
    
    empty_dirs = []
    for root, dirs, files in os.walk(path):
        try:
            if not os.listdir(root):
                empty_dirs.append(root)
        except:
            pass
    
    if not empty_dirs:
        print("✅ Пустых папок не найдено")
        return
    
    print(f"\n📋 Найдено {len(empty_dirs)} пустых папок:\n")
    for d in empty_dirs[:30]:
        print(f"   - {d}")

def file_types(path="."):
    """Анализирует типы файлов"""
    path = os.path.expanduser(path)
    print(f"\n📄 ТИПЫ ФАЙЛОВ В: {path}")
    print("=" * 60)
    
    types = defaultdict(int)
    for root, dirs, files in os.walk(path):
        for file in files:
            try:
                ext = os.path.splitext(file)[1].lower() or "без расширения"
                types[ext] += 1
            except:
                pass
    
    types = sorted(types.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n📋 Статистика по типам:\n")
    for ext, count in types[:20]:
        print(f"   {ext:<15} : {count} файлов")

def largest_files(path=".", limit=20):
    """Находит самые большие файлы"""
    path = os.path.expanduser(path)
    print(f"\n🏆 САМЫЕ БОЛЬШИЕ ФАЙЛЫ В: {path}")
    print("=" * 60)
    
    files = []
    for root, dirs, files_list in os.walk(path):
        for file in files_list:
            try:
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                files.append((size, file_path))
            except:
                pass
    
    files.sort(reverse=True)
    
    print(f"\n📋 Топ {limit} самых больших файлов:\n")
    for size, path in files[:limit]:
        print(f"💾 {get_size(size):>10} │ {path}")

def show_help():
    print("""
╔══════════════════════════════════════════════════════════════╗
║              📁 DISK ANALYZER - полный анализ               ║
╚══════════════════════════════════════════════════════════════╝

ИСПОЛЬЗОВАНИЕ:
  diskanalyzer                    - анализ текущей папки
  diskanalyzer ~/Downloads        - анализ указанной папки
  diskanalyzer --duplicates       - поиск дубликатов
  diskanalyzer --old 30           - файлы старше 30 дней
  diskanalyzer --empty            - поиск пустых папок
  diskanalyzer --types            - статистика по типам
  diskanalyzer --large            - топ больших файлов
  diskanalyzer --help             - эта справка

ПРИМЕРЫ:
  diskanalyzer /home
  diskanalyzer --duplicates ~/Downloads
  diskanalyzer --old 60
  diskanalyzer --types /var/log
""")

def main():
    if len(sys.argv) < 2:
        analyze_disk(".")
        return
    
    arg = sys.argv[1]
    
    if arg == '--help' or arg == '-h':
        show_help()
    elif arg == '--duplicates':
        path = sys.argv[2] if len(sys.argv) > 2 else "."
        find_duplicates(path)
    elif arg == '--old':
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        path = sys.argv[3] if len(sys.argv) > 3 else "."
        find_old_files(path, days)
    elif arg == '--empty':
        path = sys.argv[2] if len(sys.argv) > 2 else "."
        find_empty_dirs(path)
    elif arg == '--types':
        path = sys.argv[2] if len(sys.argv) > 2 else "."
        file_types(path)
    elif arg == '--large':
        path = sys.argv[2] if len(sys.argv) > 2 else "."
        largest_files(path)
    else:
        analyze_disk(arg)

if __name__ == "__main__":
    main()
