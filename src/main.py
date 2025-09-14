import pandas as pd
import numpy as np
import os
import glob
from data_processor import DataProcessor
from product_recommender import ProductRecommender
from push_generator import PushGenerator

def main():
    # Инициализация компонентов
    processor = DataProcessor()
    recommender = ProductRecommender('config/product_config.json')
    push_generator = PushGenerator('templates/push_templates.json')
    
    # Загрузка данных
    data_folder = 'data'
    
    # Загрузка клиентов
    clients_path = os.path.join(data_folder, 'clients.csv')
    if not os.path.exists(clients_path):
        # Попробуем найти файл с другим регистром
        client_files = glob.glob(os.path.join(data_folder, '*client*'))
        if client_files:
            clients_path = client_files[0]
        else:
            raise FileNotFoundError("Файл с клиентами не найден")
    
    clients = pd.read_csv(clients_path)
    print(f"Загружено клиентов: {len(clients)}")
    
    # Загрузка транзакций и переводов
    all_files = os.listdir(data_folder)
    
    transactions_dfs = []
    transfers_dfs = []
    
    for file in all_files:
        if file.lower() == 'clients.csv' or 'client' in file.lower():
            continue
            
        file_path = os.path.join(data_folder, file)
        
        try:
            # Пробуем прочитать файл чтобы определить его тип
            df_sample = pd.read_csv(file_path, nrows=5)
            
            # Определяем тип по колонкам
            if 'category' in df_sample.columns:
                df = pd.read_csv(file_path)
                transactions_dfs.append(df)
                print(f"Загружены транзакции из {file}: {len(df)} записей")
            elif 'type' in df_sample.columns and 'direction' in df_sample.columns:
                df = pd.read_csv(file_path)
                transfers_dfs.append(df)
                print(f"Загружены переводы из {file}: {len(df)} записей")
                
        except Exception as e:
            print(f"Ошибка при чтении файла {file}: {e}")
    
    # Объединение данных
    transactions = pd.concat(transactions_dfs, ignore_index=True) if transactions_dfs else pd.DataFrame()
    transfers = pd.concat(transfers_dfs, ignore_index=True) if transfers_dfs else pd.DataFrame()
    
    print(f"Всего транзакций: {len(transactions)}")
    print(f"Всего переводов: {len(transfers)}")
    
    # Предобработка данных
    client_features = processor.preprocess_data(clients, transactions, transfers)
    
    # Генерация рекомендаций
    recommendations = []
    
    for _, client in clients.iterrows():
        client_code = client['client_code']
        
        # Находим данные клиента
        client_data = client_features[client_features['client_code'] == client_code]
        
        if len(client_data) == 0:
            print(f"Нет данных для клиента {client_code}")
            # Используем резервную рекомендацию
            best_product = "Премиальная карта"
            push_text = push_generator.generate_push(
                best_product, 
                {},
                client.to_dict()
            )
        else:
            client_data = client_data.iloc[0]
            
            # Рекомендация продуктов
            top_products = recommender.recommend_top_products(client_data.to_dict())
            best_product = top_products[0] if top_products else "Премиальная карта"
            
            # Генерация пуш-уведомления
            push_text = push_generator.generate_push(
                best_product, 
                client_data.to_dict(),
                client.to_dict()
            )
        
        recommendations.append({
            'client_code': client_code,
            'product': best_product,
            'push_notification': push_text
        })
    
    # Сохранение результатов с правильной кодировкой
    results_df = pd.DataFrame(recommendations)
    os.makedirs('output', exist_ok=True)
    
    # Сохраняем с UTF-8 кодировкой
    results_df.to_csv('output/recommendations.csv', index=False, encoding='utf-8')
    print("Результаты сохранены в output/recommendations.csv")
    
    print(f"\nСгенерировано {len(recommendations)} рекомендаций")
    print("Примеры рекомендаций:")
    for i, rec in enumerate(recommendations[:5]):
        print(f"\nКлиент {rec['client_code']}:")
        print(f"Продукт: {rec['product']}")
        print(f"Пуш: {rec['push_notification']}")

if __name__ == "__main__":
    main()