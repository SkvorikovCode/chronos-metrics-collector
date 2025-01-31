import logging
import os
import time
import re
import datetime
import pyodbc
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env.chronos
load_dotenv('.env.chronos')

# Настройка логгера
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')
logger = logging.getLogger(__name__)

from datetime import datetime # Импортируем класс datetime

def get_latest_log_file(logs_dir):
    """
    Возвращает самый актуальный файл лога из заданной директории.
    """
    logger.info(f"Получаем самый актуальный файл лога из директории '{logs_dir}'")
    current_date = datetime.now().strftime('%Y-%m-%d')

    try:
        log_files = [f for f in os.listdir(logs_dir) if os.path.isfile(os.path.join(logs_dir, f))]
        logger.info(f"Найдено файлов в директории: {len(log_files)}")
    except OSError:
        logger.error(f"Не удалось получить список файлов из директории '{logs_dir}'.", exc_info=True)
        return None

    # Сортировка файлов по дате и времени создания
    log_files.sort(key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)), reverse=True)

    # Поиск файла, соответствующего шаблону
    for log_file in log_files:
        if re.match(rf'log_{current_date}.txt$', log_file):
            logger.info(f"Самый актуальный файл лога: {log_file}")
            return log_file

    logger.warning("Не найдено файлов соответствующих заданному шаблону.")
    return None

def count_log_messages(log_file, value_counts):
    """
    Подсчитывает количество сообщений каждого типа лога в заданном файле.
    """
    logger.info(f"Подсчитываем количество сообщений в файле '{log_file}'")
    if os.path.isfile(log_file):
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                if "|TRACE|" in line:
                    value_counts['|Trace|'] += 1
                elif "|ERROR|" in line:
                    value_counts['|Error|'] += 1
                elif "|INFO|" in line:
                    value_counts['|Info|'] += 1
                elif "|DEBUG|" in line:
                    value_counts['|Debug|'] += 1
        logger.info(f"Подсчитано соощений: {value_counts}")
    else:
        logger.error(f"Файл '{log_file}' не найден.")
def connect_to_sql():
    """
    Подключается к SQL Server Database.
    """
    logger.info("Подключаемся к SQL Server Database...")
    conn_str = (
        f'DRIVER={{{os.getenv("SQL_DRIVER")}}};'
        f'SERVER={os.getenv("SQL_SERVER")};'
        f'DATABASE={os.getenv("SQL_DATABASE")};'
        f'UID={os.getenv("SQL_USER")};'
        f'PWD={os.getenv("SQL_PASSWORD")}'
    )
    # print(conn_str)
    try:
        conn = pyodbc.connect(conn_str)
        logger.info("Соединение с SQL Server Database установлено.")
        return conn
    except pyodbc.Error as ex:
        logger.error("Ошибка при подключении к SQL Server Database.", exc_info=True)
        return None

def write_to_sql(conn, value_counts, date_time):
    """
    Записывает данные в SQL Server Database.
    """
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S') # Используем datetime.now()
    logger.info("Записываем данные в SQL Server Database.")
    try:
        cursor = conn.cursor()

        sql_query = f"INSERT INTO dbo.CHRONOS (datetime, events_count, error_count) VALUES (?, ?, ?)"
        cursor.execute(sql_query, (current_date, sum(value_counts.values()), value_counts['|Error|']))
        conn.commit()

        logger.info("Данные успешно записаны в SQL Server Database.")

    except pyodbc.Error as ex:
        logger.error("Ошибка при записи данных в SQL Server Database.", exc_info=True)
def close_sql_connection(conn):
    """
    Закрывает соединение с SQL Server Database.
    """
    if conn:
        conn.close()
        logger.info("Соединение с SQL Server Database закрыто.")


def main():
    """
    Основная функция.
    """
    logger.info("Начинаем работу")

    logs_dir = os.getenv("LOGS_DIR")

    logger.info("Получаем самый актуальный файл логов.")
    most_recent_log_file = get_latest_log_file(logs_dir)
    if most_recent_log_file:
        logger.info(f"Актуальный лог файл: {most_recent_log_file}")
        value_counts = {"|Trace|": 0, "|Error|": 0, "|Debug|": 0, "|Info|": 0}
        count_log_messages(os.path.join(logs_dir, most_recent_log_file), value_counts)

        # Записываем данные в SQL Server Database
        date_time = most_recent_log_file.split('.')[0]
        conn = connect_to_sql()
        if conn:
            write_to_sql(conn, value_counts, date_time)
            close_sql_connection(conn)

    logger.info("Работа завершена")

if __name__ == "__main__":
    main()
