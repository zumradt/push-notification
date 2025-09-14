import os
import pandas as pd
import glob

def analyze_data_folder():
    """Анализируем структуру файлов в папке data"""
    data_folder = 'data'
    
    if not os.path.exists(data_folder):
        print("Папка data не существует!")
        return
    
    files = os.listdir(data_folder)
    print(f"Найдено файлов: {len(files)}")
    
    for file in files:
        file_path = os.path.join(data_folder, file)
        print(f"\n--- Анализ файла: {file} ---")
        
        try:
            # Пробуем прочитать файл
            if file.endswith('.csv'):
                df = pd.read_csv(file_path, nrows=3)
                print(f"Колонки: {list(df.columns)}")
                print(f"Размер: {df.shape}")
                print("Первые строки:")
                print(df.head(2).to_string())
            else:
                print("Не CSV файл")
                
        except Exception as e:
            print(f"Ошибка чтения: {e}")
            
        # Проверяем кодировку
        try:
            with open(file_path, 'rb') as f:
                content = f.read(1000)
                # Простые проверки кодировки
                if b'\xd0' in content or b'\xd1' in content:
                    print("Возможно UTF-8 с русскими символами")
                else:
                    print("Кодировка не определена")
        except:
            print("Не удалось проверить кодировку")

if __name__ == "__main__":
    analyze_data_folder()