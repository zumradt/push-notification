import pandas as pd
import numpy as np
import json

class ProductRecommender:
    def __init__(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.products = self.config['products']
    
    def calculate_product_scores(self, client_data):
        """Расчет скоринга для каждого продукта"""
        scores = {}
        
        for product_name, product_config in self.products.items():
            score = self._calculate_product_score(product_name, product_config, client_data)
            scores[product_name] = score
        
        return scores
    
    def _calculate_product_score(self, product_name, product_config, client_data):
        """Расчет скора для конкретного продукта"""
        score = 0
        
        if product_name == "Карта для путешествий":
            travel_spending = client_data.get('travel', 0) + client_data.get('taxi', 0) + client_data.get('hotels', 0)
            if travel_spending > product_config.get('min_threshold', 30000):
                score = travel_spending * 0.04  # Expected cashback
        
        elif product_name == "Премиальная карта":
            balance = client_data.get('avg_monthly_balance_KZT', 0)
            if balance > product_config.get('min_balance', 500000):
                restaurant_spending = client_data.get('restaurants', 0)
                jewelry_spending = client_data.get('jewelry', 0)
                score = min(balance * 0.04, 100000) + (restaurant_spending + jewelry_spending) * 0.02
        
        elif product_name == "Кредитная карта":
            top_categories = self._get_top_spending_categories(client_data, 3)
            if top_categories and client_data.get('transaction_count', 0) > 10:
                score = sum([client_data.get(cat, 0) for cat in top_categories]) * 0.1
        
        elif product_name == "Обмен валют":
            fx_operations = client_data.get('fx', 0)
            if fx_operations > 100000:
                score = fx_operations * 0.01  # Estimated savings
        
        elif product_name == "Кредит наличными":
            if client_data.get('total_spent', 0) > client_data.get('avg_monthly_balance_KZT', 0) * 2:
                score = 1000  # Basic need score
        
        elif product_name in ["Депозит Мультивалютный", "Депозит Сберегательный", "Депозит Накопительный"]:
            balance = client_data.get('avg_monthly_balance_KZT', 0)
            if balance > 500000:
                score = balance * 0.15  # Expected interest
        
        elif product_name == "Инвестиции":
            if client_data.get('investment', 0) > 0 or client_data.get('avg_monthly_balance_KZT', 0) > 1000000:
                score = 5000
        
        elif product_name == "Золотые слитки":
            if client_data.get('gold', 0) > 0 or client_data.get('avg_monthly_balance_KZT', 0) > 2000000:
                score = 3000
        
        return max(score, 0)
    
    def _get_top_spending_categories(self, client_data, n=3):
        """Получение топ-N категорий трат"""
        category_columns = [col for col in client_data.index if col in [
            'fashion', 'groceries', 'restaurants', 'healthcare', 'auto', 
            'sports', 'entertainment', 'fuel', 'movies', 'pets', 'books',
            'flowers', 'food_delivery', 'streaming', 'gaming', 'cosmetics',
            'gifts', 'home_improvement', 'furniture', 'spa', 'jewelry',
            'taxi', 'hotels', 'travel'
        ]]
        
        category_spending = {col: client_data.get(col, 0) for col in category_columns}
        sorted_categories = sorted(category_spending.items(), key=lambda x: x[1], reverse=True)
        
        return [cat[0] for cat in sorted_categories[:n]]
    
    def recommend_top_products(self, client_data, top_n=4):
        """Рекомендация топ-N продуктов"""
        scores = self.calculate_product_scores(client_data)
        sorted_products = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return [product[0] for product in sorted_products[:top_n]]