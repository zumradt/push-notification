import sys
if sys.platform == "win32":
    import os
    os.system("chcp 65001")

import pandas as pd
import numpy as np
import os
from data_processor import DataProcessor
from product_recommender import ProductRecommender
from push_generator import PushGenerator

def main():
    # Инициализация компонентов
    processor = DataProcessor()
    recommender = ProductRecommender('config/product_config.json')
    push_generator = PushGenerator('templates/push_templates.json')
    
    # Загрузка всех данных из папки
    data_folder = 'data'
    clients, transactions, transfers = processor.load_all_data(data_folder)
    
    print(f"Загружено клиентов: {len(clients)}")
    print(f"Транзакций: {len(transactions)}")
    print(f"Переводов: {len(transfers)}")
    
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
            continue
            
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
    
    # Сохранение результатов
    results_df = pd.DataFrame(recommendations)
    os.makedirs('output', exist_ok=True)
    results_df.to_csv('output/recommendations.csv', index=False, encoding='utf-8')
    
    print(f"\nСгенерировано {len(recommendations)} рекомендаций")
    print("Примеры рекомендаций:")
    for i, rec in enumerate(recommendations[:3]):
        print(f"\nКлиент {rec['client_code']}:")
        print(f"Продукт: {rec['product']}")
        print(f"Пуш: {rec['push_notification']}")

if __name__ == "__main__":
    main()