import pandas as pd
from typing import List, Dict
import os

def save_orders_to_excel(orders: List[Dict[str, str]], file_name: str):

    df_new = pd.DataFrame(orders)

    if os.path.exists(file_name):
        df_existing = pd.read_excel(file_name)

        if 'URL' in df_existing.columns:
            combined_orders = pd.concat([df_existing, df_new])
            combined_orders.drop_duplicates(subset=['URL'], keep='last', inplace=True)
            combined_orders.to_excel(file_name, index=False)
            print(f"Добавлено {len(df_new)} новых заказов в файл '{file_name}'")
        else:
            print("В существующем файле отсутствует столбец 'URL'. Сохранение отменено.")
    else:
        df_new.to_excel(file_name, index=False)
        print(f"Создан новый файл '{file_name}' с {len(df_new)} заказами")

    if df_new.empty:
        print("Новых заказов пока нет.")

