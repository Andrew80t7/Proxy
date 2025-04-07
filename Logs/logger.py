import logging
import os
from datetime import datetime

# Определяем директорию для хранения логов
log_dir = os.path.dirname(os.path.abspath(
    __file__))  # Получаем абсолютный путь текущего файла, чтобы использовать его как директорию для логов.

if not os.path.exists(log_dir):  # Проверяем, существует ли директория для логов.
    os.makedirs(log_dir)  # Если директория не существует, создаем её.

# Формат вывода логов (включая дату, имя логгера, уровень логирования и сообщение)
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Формат отображения даты (год-месяц-день час:минуты:секунды)
date_format = '%Y-%m-%d %H:%M:%S'

# Создание объекта логгера с именем 'ProxyServer'
logger = logging.getLogger('ProxyServer')

# Устанавливаем минимальный уровень логирования для этого логгера (DEBUG – самый низкий уровень, будет записываться всё)
logger.setLevel(logging.DEBUG)

# Создаем файл для логов
log_file = os.path.join(log_dir, f'proxy_{datetime.now().strftime("%Y%m%d")}.log')

# Создаем обработчик для записи логов в файл (с кодировкой UTF-8)
file_handler = logging.FileHandler(log_file, encoding='utf-8')

# Устанавливаем уровень логирования для записи в файл
file_handler.setLevel(logging.DEBUG)

# Настроим формат логов, который будет использоваться для записи в файл
file_handler.setFormatter(logging.Formatter(log_format, date_format))

# Создаем обработчик для вывода логов в консоль
console_handler = logging.StreamHandler()

# Устанавливаем уровень логирования для вывода в консоль (INFO – будет выводиться информация и более высокие уровни)
console_handler.setLevel(logging.INFO)

# Настроим формат логов, который будет использоваться для вывода в консоль
console_handler.setFormatter(logging.Formatter(log_format, date_format))

# Добавляем оба обработчика (файл и консоль) в логгер
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def get_logger():
    """Возвращает настроенный логгер"""
    return logger
