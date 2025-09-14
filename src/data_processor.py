import pandas as pd
import numpy as np
import os
from datetime import datetime

class DataProcessor:
    def __init__(self):
        self.category_mapping = {
            'Одежда и обувь': 'fashion',
            'Продукты питания': 'groceries',
            'Кафе и рестораны': 'restaurants',
            'Медицина': 'healthcare',
            'Авто': 'auto',
            'Спорт': 'sports',
            'Развлечения': 'entertainment',
            'АЗС': 'fuel',
            'Кино': 'movies',
            'Питомцы': 'pets',
            'Книги': 'books',
            'Цветы': 'flowers',
            'Едим дома': 'food_delivery',
            'Смотрим дома': 'streaming',
            'Играем дома': 'gaming',
            'Косметика и Парфюмерия': 'cosmetics',
            'Подарки': 'gifts',
            'Ремонт дома': 'home_improvement',
            'Мебель': 'furniture',
            'Спа и массаж': 'spa',
            'Ювелирные украшения': 'jewelry',
            'Такси': 'taxi',
            'Отели': 'hotels',
            'Путешествия': 'travel'
        }
        
        self.transfer_mapping = {
            'salary_in': 'income',
            'stipend_in': 'income',
            'family_in': 'income',
            'cashback_in': 'cashback',
            'refund_in': 'refund',
            'card_in': 'transfer',
            'p2p_out': 'transfer_out',
            'card_out': 'transfer_out',
            'atm_withdrawal': 'cash_withdrawal',
            'utilities_out': 'bills',
            'loan_payment_out': 'loan_payment',
            'cc_repayment_out': 'credit_card_payment',
            'installment_payment_out': 'installment',
            'fx_buy': 'fx',
            'fx_sell': 'fx',
            'invest_out': 'investment',
            'invest_in': 'investment',
            'deposit_topup_out': 'deposit',
            'deposit_fx_topup_out': 'deposit_fx',
            'deposit_fx_withdraw_in': 'deposit_withdrawal',
            'gold_buy_out': 'gold',
            'gold_sell_in': 'gold'
        }
    
    def preprocess_data(self, clients, transactions, transfers):
        """Предобработка данных"""
        features = clients.copy()
        
        # Обработка транзакций
        if not transactions.empty:
            print("Обработка транзакций...")
            transactions['date'] = pd.to_datetime(transactions['date'], errors='coerce')
            transactions = transactions.dropna(subset=['date'])
            transactions['month'] = transactions['date'].dt.month
            transactions['category_en'] = transactions['category'].map(self.category_mapping)
            transactions['category_en'] = transactions['category_en'].fillna('other')
            
            # Статистика по транзакциям
            transaction_stats = transactions.groupby('client_code').agg({
                'amount': ['sum', 'mean', 'count'],
                'category': lambda x: x.mode()[0] if len(x.mode()) > 0 else 'Unknown'
            }).reset_index()
            
            transaction_stats.columns = ['client_code', 'total_spent', 'avg_transaction', 
                                       'transaction_count', 'most_common_category']
            
            # Траты по категориям
            category_spending = transactions.pivot_table(
                index='client_code', 
                columns='category_en', 
                values='amount', 
                aggfunc='sum',
                fill_value=0
            ).reset_index()
            
            features = features.merge(transaction_stats, on='client_code', how='left')
            features = features.merge(category_spending, on='client_code', how='left')
        
        # Обработка переводов
        if not transfers.empty:
            print("Обработка переводов...")
            transfers['date'] = pd.to_datetime(transfers['date'], errors='coerce')
            transfers = transfers.dropna(subset=['date'])
            transfers['month'] = transfers['date'].dt.month
            transfers['type_category'] = transfers['type'].map(self.transfer_mapping)
            transfers['type_category'] = transfers['type_category'].fillna('other')
            
            # Статистика по переводам
            transfer_stats = transfers.groupby('client_code').agg({
                'amount': ['sum', 'mean'],
                'direction': lambda x: (x == 'in').sum() / len(x) if len(x) > 0 else 0
            }).reset_index()
            
            transfer_stats.columns = ['client_code', 'total_transfers', 'avg_transfer', 'income_ratio']
            
            # Переводы по типам
            transfer_types = transfers.pivot_table(
                index='client_code', 
                columns='type_category', 
                values='amount', 
                aggfunc='sum',
                fill_value=0
            ).reset_index()
            
            features = features.merge(transfer_stats, on='client_code', how='left')
            features = features.merge(transfer_types, on='client_code', how='left')
        
        # Заполнение пропусков
        numeric_cols = features.select_dtypes(include=[np.number]).columns
        features[numeric_cols] = features[numeric_cols].fillna(0)
        
        categorical_cols = features.select_dtypes(include=['object']).columns
        features[categorical_cols] = features[categorical_cols].fillna('Unknown')
        
        print("Обработка данных завершена")
        return features