#  Студент: Ензак Темир Александрович
#  Вариант: 22
#
#  Условия варианта:
#  Предметная область «Сеть аптек». В программе только две таблицы, без связей с другими таблицами:
#  1) categories - категории лекарств (только название);
#  2) medicines   лекарства (название, дозировка, количество/объём, производитель, требуется ли рецепт, категория, цена).
#  Условия задания:
#  Скачайте эталонный проект и настройте его для ваших сервера и пользователя СУБД, а также установите нужные библиотеки для языка Python.
#  Замените базовые таблицы people и phone в проекте на указанные в вашем варианте, доработав все проверки целостности данных и соответствия типам данных (не должно при добавлении, и других действиях происходить ошибок PostgreSQL, приводящих к «вылету» программы или действиям программы, не имеющим нормальных объяснений). Интерфейс не должен использовать суррогатных ключей. Только понятные людям нетехнические данные или порядковый номер записи на экране. Таблицы необходимо взять из решенного Вами ранее домашнего задания модуля 1.
#  Доработайте для первой таблицы возможности удаления и редактирования сущностей (должны работать добавление, изменение, удаление с учетом связанных объектов второй таблицы). Интерфейс не должен использовать суррогатных ключей. Только понятные людям нетехнические данные или порядковый номер записи на экране.
#  Доработайте для второй таблицы просмотр списка сущностей по указанному значению ключа из первой таблицы, добавление новых сущностей с этим ключом (включая все проверки целостности данных и соответствия типам данных), удаление сущностей в этом же интерфейсе. Интерфейс не должен использовать суррогатных ключей. Только понятные людям нетехнические данные или порядковый номер записи на экране.
#  Устраните все потенциальные SQL-injection уязвимости.
#  Внимание! Нигде в программе пользователь не должен вводить значения суррогатных ключей (например, значения поля id)!
#  Задание 6 и 7 не являются частью обязательной работы, а приведены для саморазвития.
#  Сделайте постраничный просмотр сущностей.
#  Добавьте для второй таблицы в интерфейсе просмотра списка сущностей по указанному значению ключа из первой таблицы изменение сущностей второй таблицы (UPDATE).
#        Что умеет программа:
#    - постраничный просмотр категорий, добавление, изменение, удаление категории вместе со связанными лекарствами;
#    - просмотр лекарств выбранной категории, добавление, изменение, удаление;
#    - суррогатные ключи (category_id, medicine_id) нигде не вводятся и не показываются: только названия и номера строк на экране;
#    - все значения передаются в SQL через параметры (нет SQL-инъекций);
#    - данные проверяются до обращения к базе, ошибки БД выводятся текстом.

import sys
from decimal import Decimal, InvalidOperation

sys.path.append('tables')

from project_config import *
from dbconnection import *
from categories_table import *
from medicines_table import *

PAGE_SIZE = 10


class Main:

    def __init__(self):
        self.config = ProjectConfig()
        try:
            self.connection = DbConnection(self.config)
        except Exception as exc:
            print("Не удалось подключиться к базе данных:")
            print(exc)
            print("Проверьте параметры в файле config.yaml.")
            sys.exit(1)
        DbTable.dbconn = self.connection



    def db_drop(self):
        MedicinesTable().drop()
        CategoriesTable().drop()

    def db_init(self):
        CategoriesTable().create()
        MedicinesTable().create()

    def db_insert_somethings(self):
        ct = CategoriesTable()
        ct.insert_one({"name": "Обезболивающие и жаропонижающие"})
        ct.insert_one({"name": "Антибиотики"})
        ct.insert_one({"name": "Гастроэнтерологические"})
        ct.insert_one({"name": "Противоаллергические"})
        ct.insert_one({"name": "Сердечно-сосудистые"})
        ct.insert_one({"name": "Витамины"})

        c1 = ct.find_by_name("Обезболивающие и жаропонижающие")["category_id"]
        c2 = ct.find_by_name("Антибиотики")["category_id"]
        c3 = ct.find_by_name("Гастроэнтерологические")["category_id"]
        c4 = ct.find_by_name("Противоаллергические")["category_id"]
        c5 = ct.find_by_name("Сердечно-сосудистые")["category_id"]
        c6 = ct.find_by_name("Витамины")["category_id"]

        mt = MedicinesTable()
        mt.insert_one({"name": "Нурофен", "dosage": "200 мг",
                       "quantity_or_volume": "24 таблетки",
                       "manufacturer": "Reckitt Benckiser",
                       "prescription_required": False,
                       "category_id": c1, "price": Decimal("420.00")})
        mt.insert_one({"name": "Амоксициллин", "dosage": "500 мг",
                       "quantity_or_volume": "20 капсул",
                       "manufacturer": "Синтез",
                       "prescription_required": True,
                       "category_id": c2, "price": Decimal("260.00")})
        mt.insert_one({"name": "Омепразол", "dosage": "20 мг",
                       "quantity_or_volume": "30 капсул",
                       "manufacturer": "Teva",
                       "prescription_required": True,
                       "category_id": c3, "price": Decimal("150.00")})
        mt.insert_one({"name": "Сумамед", "dosage": "500 мг",
                       "quantity_or_volume": "3 таблетки",
                       "manufacturer": "Teva",
                       "prescription_required": True,
                       "category_id": c2, "price": Decimal("450.00")})
        mt.insert_one({"name": "Кларитин", "dosage": "10 мг",
                       "quantity_or_volume": "10 таблеток",
                       "manufacturer": "Bayer",
                       "prescription_required": False,
                       "category_id": c4, "price": Decimal("290.00")})
        mt.insert_one({"name": "Цефтриаксон", "dosage": "1 г",
                       "quantity_or_volume": "1 флакон",
                       "manufacturer": "Биосинтез",
                       "prescription_required": True,
                       "category_id": c2, "price": Decimal("90.00")})
        mt.insert_one({"name": "Аспирин Кардио", "dosage": "100 мг",
                       "quantity_or_volume": "28 таблеток",
                       "manufacturer": "Bayer",
                       "prescription_required": False,
                       "category_id": c5, "price": Decimal("310.00")})
        mt.insert_one({"name": "Эликвис", "dosage": "5 мг",
                       "quantity_or_volume": "60 таблеток",
                       "manufacturer": "Pfizer",
                       "prescription_required": True,
                       "category_id": c5, "price": Decimal("2750.00")})
        mt.insert_one({"name": "Витамин D3", "dosage": "2000 МЕ",
                       "quantity_or_volume": "60 капсул",
                       "manufacturer": "Solgar",
                       "prescription_required": False,
                       "category_id": c6, "price": Decimal("890.00")})
        mt.insert_one({"name": "Флемоксин Солютаб", "dosage": "500 мг",
                       "quantity_or_volume": "20 таблеток",
                       "manufacturer": "Astellas",
                       "prescription_required": True,
                       "category_id": c2, "price": Decimal("380.00")})


    def read_next_step(self):
        return input("=> ").strip()

    def ask_text(self, prompt, max_len, default=None):
        hint = f" [{default}]" if default is not None else ""
        while True:
            value = input(f"  {prompt}{hint} («-» — отмена): ").strip()
            if value == "-":
                return None
            if value == "" and default is not None:
                return default
            if len(value) == 0:
                print("    Поле не может быть пустым!")
                continue
            if len(value) > max_len:
                print(f"    Не более {max_len} символов!")
                continue
            return value

    def ask_price(self, default=None):
        hint = f" [{default}]" if default is not None else ""
        while True:
            value = input(f"  Цена, руб.{hint} («-» — отмена): ").strip()
            value = value.replace(",", ".")
            if value == "-":
                return None
            if value == "" and default is not None:
                return default
            try:
                price = Decimal(value)
            except InvalidOperation:
                print("    Введите число, например 420.50")
                continue
            if price <= 0:
                print("    Цена должна быть больше нуля!")
                continue
            if price > Decimal("99999999.99"):
                print("    Слишком большая цена!")
                continue
            if -price.as_tuple().exponent > 2:
                print("    Не более 2 знаков после запятой!")
                continue
            return price

    def ask_yes_no(self, prompt, default=None):
        hint = ""
        if default is not None:
            hint = " [да]" if default else " [нет]"
        while True:
            value = input(f"  {prompt}{hint} (да/нет, «-» — отмена): ").strip().lower()
            if value == "-":
                return None
            if value == "" and default is not None:
                return default
            if value in ("да", "д", "1", "y", "yes"):
                return True
            if value in ("нет", "н", "0", "n", "no"):
                return False
            print("    Ответьте «да» или «нет».")

    def ask_row(self, total):
        if total <= 0:
            print("  Список пуст.")
            return None
        while True:
            value = input(f"  № строки (1-{total}, 0 - отмена): ").strip()
            if value == "0":
                return None
            if value.isdigit() and 1 <= int(value) <= total:
                return int(value)
            print(f"    Введите число от 1 до {total}.")

    def confirm(self, question):
        while True:
            value = input(f"  {question} (да/нет): ").strip().lower()
            if value in ("да", "д", "1", "y", "yes"):
                return True
            if value in ("нет", "н", "0", "n", "no"):
                return False
            print("    Ответьте «да» или «нет».")

    def cut(self, value, width):
        value = "" if value is None else str(value)
        if len(value) > width:
            return value[:width - 3] + "..."
        return value


    def show_main_menu(self):
        print("""Добро пожаловать!
Основное меню (выберите цифру в соответствии с необходимым действием):
    1 - просмотр категорий лекарств;
    2 - сброс и инициализация таблиц;
    9 - выход.""")

    def main_cycle(self):
        while True:
            self.show_main_menu()
            step = self.read_next_step()
            if step == "2":
                try:
                    self.db_drop()
                    self.db_init()
                    self.db_insert_somethings()
                except Exception as exc:
                    print("Не удалось пересоздать таблицы: " + str(exc))
                    continue
                print("Таблицы созданы заново!")
            elif step == "1":
                if self.categories_menu() == "9":
                    break
            elif step == "9":
                break
            else:
                print("Выбрано неверное число! Повторите ввод!")
        print("До свидания!")


    def categories_menu(self):
        offset = 0
        while True:
            try:
                total = CategoriesTable().count()
                pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
                if total and offset >= total:
                    offset = (pages - 1) * PAGE_SIZE
                rows = CategoriesTable().page(PAGE_SIZE, offset) if total else []
            except Exception as exc:
                print("Ошибка базы данных: " + str(exc))
                return None

            print("\n--- Категории лекарств ---")
            if not rows:
                print("  Список пуст.")
            else:
                print("  №   Название")
                for index, row in enumerate(rows):
                    print(f"  {offset + index + 1}   {row['name']}")
                print(f"\n  Страница {offset // PAGE_SIZE + 1} из {pages}"
                      f" (всего категорий: {total})")
            print("""  3 - добавить категорию
  4 - изменить категорию
  5 - удалить категорию
  6 - лекарства категории
  n - следующая страница, p - предыдущая
  0 - в главное меню
  9 - выход""")

            step = self.read_next_step().lower()
            if step == "n":
                if offset + PAGE_SIZE < total:
                    offset += PAGE_SIZE
                else:
                    print("  Это последняя страница.")
            elif step == "p":
                if offset > 0:
                    offset -= PAGE_SIZE
                else:
                    print("  Это первая страница.")
            elif step == "0":
                return None
            elif step == "3":
                self.add_category()
            elif step == "4":
                self.edit_category(total)
            elif step == "5":
                self.delete_category(total)
            elif step == "6":
                if self.choose_category(total) == "9":
                    return "9"
            elif step == "9":
                return "9"
            else:
                print("  Выбрано неверное число! Повторите ввод!")

    def add_category(self):
        print("\n--- Добавление категории ---")
        name = self.ask_text("Название категории", 100)
        if name is None:
            print("  Добавление отменено.")
            return
        try:
            CategoriesTable().insert_one({"name": name})
        except Exception as exc:
            print("  Не удалось добавить категорию: " + str(exc))
            return
        print(f"  Категория «{name}» добавлена.")

    def edit_category(self, total):
        number = self.ask_row(total)
        if number is None:
            return
        try:
            row = CategoriesTable().find_by_position(number)
        except Exception as exc:
            print("  Ошибка базы данных: " + str(exc))
            return
        if row is None:
            print("  Запись не найдена, обновите список.")
            return
        print(f"\n--- Изменение категории «{row['name']}» ---")
        name = self.ask_text("Новое название", 100, default=row["name"])
        if name is None:
            print("  Изменение отменено.")
            return
        try:
            CategoriesTable().update_one({"name": name},
                                         {"category_id": row["category_id"]})
        except Exception as exc:
            print("  Не удалось изменить категорию: " + str(exc))
            return
        print(f"  Категория переименована в «{name}».")

    def delete_category(self, total):
        number = self.ask_row(total)
        if number is None:
            return
        try:
            row = CategoriesTable().find_by_position(number)
        except Exception as exc:
            print("  Ошибка базы данных: " + str(exc))
            return
        if row is None:
            print("  Запись не найдена, обновите список.")
            return
        try:
            count = MedicinesTable().count_by_category(row["category_id"])
        except Exception as exc:
            print("  Ошибка базы данных: " + str(exc))
            return

        print(f"\n--- Удаление категории «{row['name']}» ---")
        question = f"Удалить категорию «{row['name']}»"
        if count:
            print(f"  В категории {count} лекарств(а) — они будут удалены тоже.")
            question += " вместе с лекарствами"
        if not self.confirm(question + "?"):
            print("  Удаление отменено.")
            return
        try:
            CategoriesTable().delete_with_medicines(row["category_id"])
        except Exception as exc:
            print("  Не удалось удалить категорию: " + str(exc))
            return
        print("  Категория удалена.")
        if count:
            print(f"  Вместе с ней удалено лекарств: {count}.")

    def choose_category(self, total):
        number = self.ask_row(total)
        if number is None:
            return None
        try:
            row = CategoriesTable().find_by_position(number)
        except Exception as exc:
            print("  Ошибка базы данных: " + str(exc))
            return None
        if row is None:
            print("  Запись не найдена, обновите список.")
            return None
        return self.medicines_menu(row)


    def medicines_menu(self, category):
        category_id = category["category_id"]
        offset = 0
        while True:
            try:
                total = MedicinesTable().count_by_category(category_id)
                pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
                if total and offset >= total:
                    offset = (pages - 1) * PAGE_SIZE
                rows = (MedicinesTable().page_by_category(category_id, PAGE_SIZE, offset)
                        if total else [])
            except Exception as exc:
                print("Ошибка базы данных: " + str(exc))
                return None

            print(f"\n--- Лекарства категории «{category['name']}» ---")
            if not rows:
                print("  В этой категории пока нет лекарств.")
            else:
                print(f"  {'№':<4}{'Название':<28}{'Дозировка':<12}"
                      f"{'Кол-во/объём':<16}{'Производитель':<22}"
                      f"{'Рецепт':<8}{'Цена, руб.':>10}")
                for index, row in enumerate(rows):
                    receipt = "да" if row["prescription_required"] else "нет"
                    print(f"  {offset + index + 1:<4}"
                          f"{self.cut(row['name'], 28):<28}"
                          f"{self.cut(row['dosage'], 12):<12}"
                          f"{self.cut(row['quantity_or_volume'], 16):<16}"
                          f"{self.cut(row['manufacturer'], 22):<22}"
                          f"{receipt:<8}"
                          f"{row['price']:>10.2f}")
                print(f"\n  Страница {offset // PAGE_SIZE + 1} из {pages}"
                      f" (всего лекарств: {total})")
            print("""  3 - добавить лекарство
  4 - изменить лекарство
  5 - удалить лекарство
  n - следующая страница, p - предыдущая
  0 - назад к категориям
  9 - выход""")

            step = self.read_next_step().lower()
            if step == "n":
                if offset + PAGE_SIZE < total:
                    offset += PAGE_SIZE
                else:
                    print("  Это последняя страница.")
            elif step == "p":
                if offset > 0:
                    offset -= PAGE_SIZE
                else:
                    print("  Это первая страница.")
            elif step == "0":
                return None
            elif step == "3":
                self.add_medicine(category)
            elif step == "4":
                self.edit_medicine(category, total)
            elif step == "5":
                self.delete_medicine(category, total)
            elif step == "9":
                return "9"
            else:
                print("  Выбрано неверное число! Повторите ввод!")

    def add_medicine(self, category):
        print(f"\n--- Новое лекарство в категории «{category['name']}» ---")
        name = self.ask_text("Название лекарства", 150)
        if name is None:
            print("  Добавление отменено.")
            return
        dosage = self.ask_text("Дозировка (например, 200 мг)", 50)
        if dosage is None:
            print("  Добавление отменено.")
            return
        quantity = self.ask_text("Количество или объём (например, 24 таблетки)", 50)
        if quantity is None:
            print("  Добавление отменено.")
            return
        manufacturer = self.ask_text("Производитель", 150)
        if manufacturer is None:
            print("  Добавление отменено.")
            return
        receipt = self.ask_yes_no("Требуется рецепт?")
        if receipt is None:
            print("  Добавление отменено.")
            return
        price = self.ask_price()
        if price is None:
            print("  Добавление отменено.")
            return

        try:
            MedicinesTable().insert_one({
                "name": name,
                "dosage": dosage,
                "quantity_or_volume": quantity,
                "manufacturer": manufacturer,
                "prescription_required": receipt,
                "category_id": category["category_id"],
                "price": price,
            })
        except Exception as exc:
            print("  Не удалось добавить лекарство: " + str(exc))
            return
        print(f"  Лекарство «{name}» добавлено.")

    def edit_medicine(self, category, total):
        number = self.ask_row(total)
        if number is None:
            return
        try:
            row = MedicinesTable().find_by_position_in_category(
                category["category_id"], number)
        except Exception as exc:
            print("  Ошибка базы данных: " + str(exc))
            return
        if row is None:
            print("  Запись не найдена, обновите список.")
            return

        print(f"\n--- Изменение лекарства «{row['name']}» ---")
        print("  Enter — оставить как есть, «-» — отменить изменение.")
        name = self.ask_text("Название", 150, default=row["name"])
        if name is None:
            print("  Изменение отменено.")
            return
        dosage = self.ask_text("Дозировка", 50, default=row["dosage"])
        if dosage is None:
            print("  Изменение отменено.")
            return
        quantity = self.ask_text("Количество или объём", 50,
                                 default=row["quantity_or_volume"])
        if quantity is None:
            print("  Изменение отменено.")
            return
        manufacturer = self.ask_text("Производитель", 150,
                                     default=row["manufacturer"])
        if manufacturer is None:
            print("  Изменение отменено.")
            return
        receipt = self.ask_yes_no("Требуется рецепт?", default=row["prescription_required"])
        if receipt is None:
            print("  Изменение отменено.")
            return
        price = self.ask_price(default=row["price"])
        if price is None:
            print("  Изменение отменено.")
            return

        try:
            MedicinesTable().update_one({
                "name": name,
                "dosage": dosage,
                "quantity_or_volume": quantity,
                "manufacturer": manufacturer,
                "prescription_required": receipt,
                "price": price,
            }, {"medicine_id": row["medicine_id"]})
        except Exception as exc:
            print("  Не удалось изменить лекарство: " + str(exc))
            return
        print(f"  Лекарство «{name}» изменено.")

    def delete_medicine(self, category, total):
        number = self.ask_row(total)
        if number is None:
            return
        try:
            row = MedicinesTable().find_by_position_in_category(
                category["category_id"], number)
        except Exception as exc:
            print("  Ошибка базы данных: " + str(exc))
            return
        if row is None:
            print("  Запись не найдена, обновите список.")
            return
        if not self.confirm(f"Удалить лекарство «{row['name']}» ({row['dosage']})?"):
            print("  Удаление отменено.")
            return
        try:
            MedicinesTable().delete_one({"medicine_id": row["medicine_id"]})
        except Exception as exc:
            print("  Не удалось удалить лекарство: " + str(exc))
            return
        print(f"  Лекарство «{row['name']}» удалено.")


m = Main()
m.main_cycle()