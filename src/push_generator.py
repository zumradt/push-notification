import json
import random
from datetime import datetime

class PushGenerator:
    def __init__(self, template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            self.templates = json.load(f)
        
        self.month_names = {
            1: "январе", 2: "феврале", 3: "марте", 4: "апреле",
            5: "мае", 6: "июне", 7: "июле", 8: "августе",
            9: "сентябре", 10: "октябре", 11: "ноябре", 12: "декабре"
        }
    
    def generate_push(self, product_name, client_data, client_profile):
        """Генерация персонализированного пуш-уведомления"""
        template = self.templates.get(product_name, {}).get('template')
        
        if not template:
            return self._generate_fallback_push(product_name, client_profile['name'])
        
        # Подготовка параметров для шаблона
        params = {
            'name': client_profile['name'],
            'month': self.month_names.get(datetime.now().month, 'этом месяце')
        }
        
        # Добавление специфических параметров в зависимости от продукта
        if product_name == "Кредитная карта":
            top_categories = self._get_top_categories_russian(client_data)
            params.update({
                'cat1': top_categories[0] if len(top_categories) > 0 else "покупки",
                'cat2': top_categories[1] if len(top_categories) > 1 else "услуги",
                'cat3': top_categories[2] if len(top_categories) > 2 else "развлечения"
            })
        
        elif product_name == "Обмен валют":
            main_currency = self._get_main_currency(client_data)
            params['fx_curr'] = main_currency
        
        # Генерация текста
        push_text = template.format(**params)
        
        # Применение TOV правил
        push_text = self._apply_tov_rules(push_text)
        
        return push_text
    
    def _get_top_categories_russian(self, client_data):
        """Получение топ-категорий на русском языке"""
        category_mapping_ru = {
            'fashion': "одежда", 'groceries': "продукты", 'restaurants': "рестораны",
            'healthcare': "медицина", 'auto': "авто", 'sports': "спорт",
            'entertainment': "развлечения", 'fuel': "АЗС", 'movies': "кино",
            'pets': "питомцы", 'books': "книги", 'flowers': "цветы",
            'food_delivery': "доставка еды", 'streaming': "стриминги",
            'gaming': "игры", 'cosmetics': "косметика", 'gifts': "подарки",
            'home_improvement': "ремонт", 'furniture': "мебель", 'spa': "спа",
            'jewelry': "украшения", 'taxi': "такси", 'hotels': "отели",
            'travel': "путешествия"
        }
        
        # Здесь должна быть логика определения топ-категорий
        # Для примера возвращаем фиктивные значения
        return ["рестораны", "развлечения", "онлайн-покупки"]
    
    def _get_main_currency(self, client_data):
        """Определение основной валюты для FX"""
        # Здесь должна быть логика определения основной валюты
        return "долларах"
    
    def _apply_tov_rules(self, text):
        """Применение правил Tone of Voice"""
        # Удаление лишних знаков препинания
        text = text.replace('!!', '!').replace('??', '?')
        
        # Проверка длины
        if len(text) > 220:
            words = text.split()
            while len(' '.join(words)) > 220 and len(words) > 5:
                words = words[:-1]
            text = ' '.join(words) + '...'
        
        # Добавление эмодзи (0-1 по смыслу)
        emoji_map = {
            'путешестви': '✈️',
            'карт': '💳',
            'кешбэк': '💰',
            'ресторан': '🍽️',
            'инвест': '📈',
            'кредит': '🤝'
        }
        
        for keyword, emoji in emoji_map.items():
            if keyword in text.lower() and random.random() < 0.3:
                text += f" {emoji}"
                break
        
        return text
    
    def _generate_fallback_push(self, product_name, client_name):
        """Резервный шаблон для неизвестных продуктов"""
        templates = [
            f"{client_name}, у нас есть специальное предложение по {product_name.lower()}. Посмотреть детали?",
            f"{client_name}, подобрали для вас выгодный вариант — {product_name.lower()}. Оформить сейчас?",
            f"{client_name}, персональное предложение: {product_name.lower()} с преимуществами для вас. Узнать больше?"
        ]
        
        return random.choice(templates)