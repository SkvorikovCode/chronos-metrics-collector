# ChronosParser

## Описание
ChronosParser - это скрипт для анализа лог-файлов Chronos и записи статистики в SQL Server Database. Скрипт подсчитывает количество различных типов сообщений (Trace, Error, Debug, Info) и сохраняет результаты в базу данных.

## Требования
- Python 3.7+
- SQL Server
- Доступ к сетевой папке с логами Chronos

## Зависимости
- pyodbc==4.0.39 - для работы с SQL Server
- python-dotenv==1.0.0 - для работы с переменными окружения

## Установка
1. Клонируйте репозиторий
2. Установите зависимости:
```bash
pip install -r requirements.txt
```

## Конфигурация
Создайте файл `.env.chronos` в корневой директории проекта со следующими параметрами:
```env
# Параметры подключения к SQL Server
SQL_DRIVER=SQL Server
SQL_SERVER=server-cod
SQL_DATABASE=Monitor_Logs
SQL_USER=Parsing_User
SQL_PASSWORD=your_password

# Путь к логам
LOGS_DIR=\\\\srv-server-cod\\F$\\LogChronos\\log
```

## Использование
Запустите скрипт командой:
```bash
python ChronosParser_V3.py
```

## Функциональность
1. Поиск самого актуального лог-файла за текущую дату
2. Подсчет количества сообщений по типам:
   - Trace
   - Error
   - Debug
   - Info
3. Запись статистики в SQL Server:
   - Дата и время
   - Общее количество событий
   - Количество ошибок

## Логирование
Скрипт ведет подробное логирование всех операций с указанием:
- Времени выполнения
- Уровня сообщения
- Имени файла
- Номера строки
- Текста сообщения

## Структура базы данных
Таблица `dbo.CHRONOS`:
- datetime - дата и время записи
- events_count - общее количество событий
- error_count - количество ошибок

## Обработка ошибок
- Логирование всех исключений
- Graceful shutdown при ошибках подключения
- Проверка существования файлов и директорий 