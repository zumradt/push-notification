import json
import random
from datetime import datetime

class PushGenerator:
    def __init__(self, templates_path):
        try:
            with open(templates_path, 'r', encoding='utf-8') as f:
                self.templates = json.load(f)
        except:
            self.templates = self._create_default_templates()
        
        self.month_names = {
            1: "январе", 2: "феврале", 3: "марте", 4: "апреле",
            5: "мае", 6: "июне", 7: "июле", 8: "августе",
            9: "сентябре", 10: "октябре", 11: "ноябре", 12: "декабре"
        }
    
    def _create_default_templates(self):
        """Создание шаблонов по умолчанию"""
        return {
            "Карта для путешествий": {
                "template": "{name}, в {month} у вас много поездок. С тревел-картой вернули бы до 4% кешбэка на такси и отели. Оформить карту?"
            },
            "Премиальная карта": {
                "template": "{name}, с вашим остатком можно получать до 4% кешбэка на все покупки. Премиальная карта также даёт бесплатные переводы. Подключить?"
            },
            "Кредитная карта": {
                "template": "{name}, ваши основные траты — {cat1}, {cat2} и {cat3}. С кредитной картой получите до 10% кешбэка в этих категориях. Оформить?"
            }
        }
    
    def generate_push(self, product_name, client_data, client_profile):
        """Генерация персонализированного пуш-уведомления"""
        template_info = self.templates.get(product_name, {})
        template = template_info.get('template', '')
        
        if not template:
            return self._generate_fallback_push(product_name, client_profile.get('name', 'Клиент'))
        
        # Подготовка параметров для шаблона
        params = {
            'name': client_profile.get('name', 'Клиент'),
            'month': self.month_names.get(datetime.now().month, 'этом месяце')
        }
        
        # Генерация текста
        try:
            push_text = template.format(**params)
        except:
            push_text = self._generate_fallback_push(product_name, client_profile.get('name', 'Клиент'))
        
        # Применение TOV правил
        push_text = self._apply_tov_rules(push_text)
        
        return push_text
    
    def _apply_tov_rules(self, text):
        """Применение правил Tone of Voice"""
        # Убедимся, что текст не слишком длинный
        if len(text) > 220:
            words = text.split()
            # Сохраняем первые 180 символов
            truncated = ''
            for word in words:
                if len(truncated + ' ' + word) <= 180:
                    truncated += ' ' + word
                else:
                    break
            text = truncated.strip() + '...'
        
        return text
    
    def _generate_fallback_push(self, product_name, client_name):
        """Резервный шаблон для неизвестных продуктов"""
        templates = [
            f"{client_name}, у нас есть специальное предложение по {product_name.lower()}. Посмотреть детали?",
            f"{client_name}, подобрали для вас выгодный вариант — {product_name.lower()}. Оформить сейчас?",
            f"{client_name}, персональное предложение: {product_name.lower()} с преимуществами для вас. Узнать больше?"
        ]
        
        return random.choice(templates)