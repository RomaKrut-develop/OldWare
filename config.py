# Конфигурация приложения Flask
class Config:
    # Секретный ключ для защиты сессий и подписей
    SECRET_KEY = 'your_secret_key_here'  # Замените на настоящий секретный ключ в продакшене
    
    # URI для подключения к базе данных (SQLite в данном случае)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    
    # Отключаем отслеживание модификаций для оптимизации
    SQLALCHEMY_TRACK_MODIFICATIONS = False