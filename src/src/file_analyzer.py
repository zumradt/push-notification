import os
import pandas as pd

def analyze_data_folder(data_folder):
    """Анализ структуры файлов в папке"""
    files = os.listdir(data_folder)
    
    print("Файлы в папке data:")
    for file in files:
        file_path = os.path.join(data_folder, file)
        if os.path.isfile(file_path):
            try:
                # Пытаемся прочитать первые несколько строк
                if file.endswith('.csv'):
                    df = pd.read_csv(file_path, nrows=5)
                    print(f"{file}: {len(df.columns)} колонок, пример данных: {list(df.columns)}")
                else:
                    print(f"{file}: не CSV файл")
            except Exception as e:
                print(f"{file}: ошибка чтения - {e}")

if __name__ == "__main__":
    analyze_data_folder('data')