import pandas as pd
import numpy as np
import os
import re
from datetime import datetime
import json

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
    
    def load_all_data(self, data_folder):
        """Загрузка всех данных из папки"""
        all_files = os.listdir(data_folder)
        
        # Загрузка клиентов
        clients_file = [f for f in all_files if f.lower() == 'clients.csv']
        if not clients_file:
            raise FileNotFoundError("Файл clients.csv не найден")
        
        clients = pd.read_csv(os.path.join(data_folder, clients_file[0]))
        
        # Загрузка транзакций и переводов
        transactions_dfs = []
        transfers_dfs = []
        
        for file in all_files:
            if file.lower() == 'clients.csv':
                continue
                
            file_path = os.path.join(data_folder, file)
            
            # Определяем тип файла по названию
            if 'transaction' in file.lower():
                df = pd.read_csv(file_path)
                df['file_type'] = 'transaction'
                transactions_dfs.append(df)
            elif 'transfer' in file.lower():
                df = pd.read_csv(file_path)
                df['file_type'] = 'transfer'
                transfers_dfs.append(df)
        
        # Объединение всех транзакций и переводов
        transactions = pd.concat(transactions_dfs, ignore_index=True) if transactions_dfs else pd.DataFrame()
        transfers = pd.concat(transfers_dfs, ignore_index=True) if transfers_dfs else pd.DataFrame()
        
        return clients, transactions, transfers
    
    def extract_client_id_from_filename(self, filename):
        """Извлечение client_code из имени файла"""
        # Ищем числа в имени файла
        numbers = re.findall(r'\d+', filename)
        return int(numbers[0]) if numbers else None
    
    def preprocess_data(self, clients, transactions, transfers):
        """Предобработка данных"""
        # Обработка транзакций
        if not transactions.empty:
            transactions['date'] = pd.to_datetime(transactions['date'])
            transactions['month'] = transactions['date'].dt.month
            transactions['category_en'] = transactions['category'].map(self.category_mapping)
            transactions['category_en'] = transactions['category_en'].fillna('other')
        
        # Обработка переводов
        if not transfers.empty:
            transfers['date'] = pd.to_datetime(transfers['date'])
            transfers['month'] = transfers['date'].dt.month
            transfers['type_category'] = transfers['type'].map(self.transfer_mapping)
            transfers['type_category'] = transfers['type_category'].fillna('other')
        
        # Агрегация данных по клиентам
        client_features = self._aggregate_client_features(clients, transactions, transfers)
        
        return client_features
    
    def _aggregate_client_features(self, clients, transactions, transfers):
        """Агрегация признаков по клиентам"""
        features = clients.copy()
        
        # Статистика по транзакциям
        if not transactions.empty:
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
        
        # Статистика по переводам
        if not transfers.empty:
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
        
        return features