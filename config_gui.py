"""GUI окно для настройки API ключа DeepSeek"""
import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
from pathlib import Path


class ConfigWindow:
    """Окно настройки конфигурации"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Настройка DeepSeek API")
        self.root.geometry("500x300")
        self.root.resizable(False, False)
        
        # Центрирование окна
        self.center_window()
        
        # Загрузка существующей конфигурации
        self.load_config()
        
        # Создание интерфейса
        self.create_widgets()
    
    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def load_config(self):
        """Загрузка существующей конфигурации"""
        self.api_key = ""
        self.model = "deepseek-chat"
        self.temperature = 0.7
        self.max_tokens = 1000
        
        # Пытаемся загрузить из config.py
        try:
            if os.path.exists("config.py"):
                with open("config.py", "r", encoding="utf-8") as f:
                    content = f.read()
                    # Извлекаем API ключ
                    if 'DEEPSEEK_API_KEY = "' in content:
                        start = content.find('DEEPSEEK_API_KEY = "') + len('DEEPSEEK_API_KEY = "')
                        end = content.find('"', start)
                        self.api_key = content[start:end]
        except Exception:
            pass
        
        # Пытаемся загрузить из config.json
        try:
            if os.path.exists("config.json"):
                with open("config.json", "r", encoding="utf-8") as f:
                    config = json.load(f)
                    if "deepseek" in config:
                        self.api_key = config["deepseek"].get("api_key", "")
                        self.model = config["deepseek"].get("model", "deepseek-chat")
                    if "request" in config:
                        self.temperature = config["request"].get("temperature", 0.7)
                        self.max_tokens = config["request"].get("max_tokens", 1000)
        except Exception:
            pass
    
    def create_widgets(self):
        """Создание элементов интерфейса"""
        # Заголовок
        title_label = tk.Label(
            self.root,
            text="🔑 Настройка DeepSeek API",
            font=("Arial", 16, "bold"),
            pady=10
        )
        title_label.pack()
        
        # Фрейм для полей ввода
        input_frame = tk.Frame(self.root, padx=20, pady=10)
        input_frame.pack(fill=tk.BOTH, expand=True)
        
        # API Key
        api_label = tk.Label(input_frame, text="API Key:", font=("Arial", 10))
        api_label.grid(row=0, column=0, sticky="w", pady=5)
        
        self.api_entry = tk.Entry(input_frame, width=50, show="*", font=("Arial", 10))
        self.api_entry.insert(0, self.api_key)
        self.api_entry.grid(row=0, column=1, pady=5, padx=10)
        
        # Кнопка показать/скрыть
        self.show_btn = tk.Button(
            input_frame,
            text="👁️",
            command=self.toggle_visibility,
            width=3
        )
        self.show_btn.grid(row=0, column=2, pady=5)
        
        # Model
        model_label = tk.Label(input_frame, text="Model:", font=("Arial", 10))
        model_label.grid(row=1, column=0, sticky="w", pady=5)
        
        self.model_entry = tk.Entry(input_frame, width=50, font=("Arial", 10))
        self.model_entry.insert(0, self.model)
        self.model_entry.grid(row=1, column=1, pady=5, padx=10)
        
        # Temperature
        temp_label = tk.Label(input_frame, text="Temperature:", font=("Arial", 10))
        temp_label.grid(row=2, column=0, sticky="w", pady=5)
        
        self.temp_entry = tk.Entry(input_frame, width=50, font=("Arial", 10))
        self.temp_entry.insert(0, str(self.temperature))
        self.temp_entry.grid(row=2, column=1, pady=5, padx=10)
        
        # Max Tokens
        tokens_label = tk.Label(input_frame, text="Max Tokens:", font=("Arial", 10))
        tokens_label.grid(row=3, column=0, sticky="w", pady=5)
        
        self.tokens_entry = tk.Entry(input_frame, width=50, font=("Arial", 10))
        self.tokens_entry.insert(0, str(self.max_tokens))
        self.tokens_entry.grid(row=3, column=1, pady=5, padx=10)
        
        # Информация
        info_label = tk.Label(
            input_frame,
            text="💡 Получите API ключ на: https://platform.deepseek.com/",
            font=("Arial", 8),
            fg="gray",
            cursor="hand2"
        )
        info_label.grid(row=4, column=0, columnspan=3, pady=10)
        info_label.bind("<Button-1>", lambda e: self.open_url("https://platform.deepseek.com/"))
        
        # Фрейм для кнопок
        button_frame = tk.Frame(self.root, pady=10)
        button_frame.pack()
        
        # Кнопка Сохранить
        save_btn = tk.Button(
            button_frame,
            text="💾 Сохранить",
            command=self.save_config,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5,
            cursor="hand2"
        )
        save_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка Отмена
        cancel_btn = tk.Button(
            button_frame,
            text="❌ Отмена",
            command=self.root.destroy,
            bg="#f44336",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5,
            cursor="hand2"
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка Тест
        test_btn = tk.Button(
            button_frame,
            text="🧪 Тест подключения",
            command=self.test_connection,
            bg="#2196F3",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5,
            cursor="hand2"
        )
        test_btn.pack(side=tk.LEFT, padx=5)
    
    def toggle_visibility(self):
        """Переключение видимости API ключа"""
        if self.api_entry.cget("show") == "*":
            self.api_entry.config(show="")
            self.show_btn.config(text="🙈")
        else:
            self.api_entry.config(show="*")
            self.show_btn.config(text="👁️")
    
    def open_url(self, url):
        """Открытие URL в браузере"""
        import webbrowser
        webbrowser.open(url)
    
    def validate_inputs(self):
        """Валидация введенных данных"""
        api_key = self.api_entry.get().strip()
        
        if not api_key:
            messagebox.showerror("Ошибка", "Пожалуйста, введите API ключ!")
            return False
        
        if api_key == "your_deepseek_api_key_here":
            messagebox.showerror("Ошибка", "Пожалуйста, введите реальный API ключ!")
            return False
        
        try:
            temperature = float(self.temp_entry.get())
            if not 0.0 <= temperature <= 2.0:
                messagebox.showerror("Ошибка", "Temperature должен быть от 0.0 до 2.0!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Temperature должен быть числом!")
            return False
        
        try:
            max_tokens = int(self.tokens_entry.get())
            if max_tokens < 1:
                messagebox.showerror("Ошибка", "Max Tokens должен быть больше 0!")
                return False
        except ValueError:
            messagebox.showerror("Ошибка", "Max Tokens должен быть целым числом!")
            return False
        
        return True
    
    def save_config(self):
        """Сохранение конфигурации"""
        if not self.validate_inputs():
            return
        
        api_key = self.api_entry.get().strip()
        model = self.model_entry.get().strip()
        temperature = float(self.temp_entry.get())
        max_tokens = int(self.tokens_entry.get())
        
        # Сохранение в config.py
        try:
            config_content = f'''"""Конфигурационный файл для подключения к DeepSeek API"""

# DeepSeek API настройки
DEEPSEEK_API_KEY = "{api_key}"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "{model}"

# Настройки запросов
TEMPERATURE = {temperature}
MAX_TOKENS = {max_tokens}
TIMEOUT = 30

# Системный промпт для AI
SYSTEM_PROMPT = """Ты - ассистент для управления компьютером через голосовые команды.
Твоя задача - преобразовывать голосовые команды пользователя в JSON команды для выполнения.

Доступные команды:
- media_control: управление медиа (play, pause, next, previous, volume_up, volume_down)
- system_control: управление системой (shutdown, restart, sleep, lock)
- app_control: управление приложениями (open_app, close_app)

Формат ответа - строго JSON:
{{
    "action": "название_команды",
    "params": {{
        "command": "конкретная_команда",
        "value": "значение_если_нужно"
    }},
    "description": "описание_действия"
}}

Примеры:
Пользователь: "Включи музыку" -> {{"action": "media_control", "params": {{"command": "play"}}, "description": "Воспроизведение медиа"}}
Пользователь: "Выключи компьютер" -> {{"action": "system_control", "params": {{"command": "shutdown"}}, "description": "Выключение компьютера"}}
Пользователь: "Следующий трек" -> {{"action": "media_control", "params": {{"command": "next"}}, "description": "Следующий трек"}}
"""
'''
            with open("config.py", "w", encoding="utf-8") as f:
                f.write(config_content)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить config.py: {e}")
            return
        
        # Сохранение в config.json
        try:
            config_json = {
                "deepseek": {
                    "api_key": api_key,
                    "api_url": "https://api.deepseek.com/v1/chat/completions",
                    "model": model
                },
                "request": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "timeout": 30
                }
            }
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config_json, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить config.json: {e}")
            return
        
        messagebox.showinfo("Успех", "Конфигурация успешно сохранена!")
        self.root.destroy()
    
    def test_connection(self):
        """Тестирование подключения к API"""
        if not self.validate_inputs():
            return
        
        api_key = self.api_entry.get().strip()
        model = self.model_entry.get().strip()
        
        try:
            import requests
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            data = {
                "model": model,
                "messages": [
                    {"role": "user", "content": "Привет! Ответь одним словом: работает"}
                ],
                "max_tokens": 10
            }
            
            messagebox.showinfo("Тест", "Проверка подключения...")
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                message = result["choices"][0]["message"]["content"]
                messagebox.showinfo("✅ Успех", f"Подключение работает!\n\nОтвет: {message}")
            else:
                error_msg = response.text
                messagebox.showerror("❌ Ошибка", f"Не удалось подключиться:\n\n{error_msg}")
        
        except ImportError:
            messagebox.showerror("Ошибка", "Библиотека 'requests' не установлена!\n\nУстановите: pip install requests")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка подключения:\n\n{str(e)}")
    
    def run(self):
        """Запуск окна"""
        self.root.mainloop()


if __name__ == "__main__":
    app = ConfigWindow()
    app.run()

