Disk Analyzer

Инструмент для анализа дискового пространства в Linux.
Возможности

    Анализ размера папок и файлов

    Поиск дубликатов по содержимому

    Поиск файлов старше N дней

    Поиск пустых папок

    Статистика по типам файлов

    Поиск самых больших файлов

Установка

git clone https://github.com/aikelelx/disk-analyzer.git
cd disk-analyzer
chmod +x scripts/install.sh
./scripts/install.sh
Использование

diskanalyzer анализ текущей папки
diskanalyzer /путь/к/папке анализ указанной папки
diskanalyzer --duplicates поиск дубликатов
diskanalyzer --old 30 поиск файлов старше 30 дней
diskanalyzer --empty поиск пустых папок
diskanalyzer --types статистика по типам файлов
diskanalyzer --large поиск самых больших файлов
diskanalyzer --help справка
Примеры

diskanalyzer ~/Загрузки
diskanalyzer --duplicates ~
diskanalyzer --old 60 /var/log
diskanalyzer --large /
Требования

    Python 3.6+

    Операционная система Linux

Лицензия

MIT
Автор

GitHub: aikelelx
Репозиторий

https://github.com/aikelelx/disk-analyzer
