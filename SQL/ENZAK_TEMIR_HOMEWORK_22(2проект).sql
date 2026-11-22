-- Домашнее задание: проектирование базы данных «Сеть аптек»
--
-- ФИО студента: Ензак Темир Александрович
-- Вариант: 22
--
-- Описание предметной области
-- Описание сети аптек. Включает в себя: аптеки, лекарства, категории лекарств, провизоров, информацию о наличии и продажах лекарств. 
-- Аптеки описываются: адресом, номером, ближайшей станцией метро. 
-- Лекарства характеризуются: названием, дозировкой, количеством (или объёмом), производителем, указанием, требуется ли рецепт для приобретения или нет, указанием категорий, к которым данное лекарство относится, ценой. 
-- Категория лекарства описывается только названием. Провизоры характеризуются: фамилией, именем, отчеством, датой рождения, ИНН, серией и номером паспорта, указанием аптеки, в которой работают. 
-- Информация о наличии лекарств состоит из: указания аптеки, указания лекарства, количества упаковок. 
-- Информация о продаже лекарства состоит из: указания аптеки, указания лекарства, указания провизора, который продал лекарство, даты продажи, количества упаковок.
-- Одно и то же лекарство не может принадлежать разным категориям.
--
-- Заполнить таблицы не менее чем 5 осмысленными записями (SQL-запросы INSERT); данные взяты из реальных аптечных каталогов;
-- Выберите название и дозировку лекарств стоимостью менее 1000 рублей за упаковку, требующих наличие рецепта. 
-- Выберите для каждого номера или идентификатора провизора, продавшего более 5 упаковок лекарств, общее число проданных упаковок лекарств.


DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS availability;
DROP TABLE IF EXISTS pharmacists;
DROP TABLE IF EXISTS medicines;
DROP TABLE IF EXISTS pharmacies;
DROP TABLE IF EXISTS categories;


CREATE TABLE categories (
    category_id SERIAL       PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE
);


CREATE TABLE pharmacies (
    pharmacy_id   SERIAL       PRIMARY KEY,
    number        VARCHAR(20)      NOT NULL UNIQUE,
    address       VARCHAR(200) NOT NULL,
    metro_station VARCHAR(100)
);

CREATE TABLE medicines (
    medicine_id           SERIAL        PRIMARY KEY,
    name                  VARCHAR(150)  NOT NULL,
    dosage                VARCHAR(50)   NOT NULL,
    quantity_or_volume    VARCHAR(50)   NOT NULL,
    manufacturer          VARCHAR(150)  NOT NULL,
    prescription_required BOOLEAN       NOT NULL DEFAULT FALSE,
    category_id           INTEGER       NOT NULL
        REFERENCES categories (category_id),
    price                 NUMERIC(10, 2) NOT NULL
        CHECK (price > 0)
);


CREATE TABLE pharmacists (
    pharmacist_id   SERIAL      PRIMARY KEY,
    last_name       VARCHAR(50) NOT NULL,
    first_name      VARCHAR(50) NOT NULL,
    patronymic      VARCHAR(50),
    birth_date      DATE        NOT NULL CHECK (birth_date < CURRENT_DATE),
    inn             VARCHAR(12) NOT NULL UNIQUE CHECK (inn ~ '^[0-9]{12}$'),
    passport_series VARCHAR(4)  NOT NULL
        CHECK (passport_series ~ '^[0-9]{4}$'), passport_number VARCHAR(6)  NOT NULL
        CHECK (passport_number ~ '^[0-9]{6}$'), pharmacy_id     INTEGER     NOT NULL
        REFERENCES pharmacies (pharmacy_id),
        UNIQUE (pharmacist_id, pharmacy_id)
);

CREATE TABLE availability (
    pharmacy_id INTEGER NOT NULL REFERENCES pharmacies (pharmacy_id),
    medicine_id INTEGER NOT NULL REFERENCES medicines (medicine_id),
    quantity    INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    PRIMARY KEY (pharmacy_id, medicine_id)
);

CREATE TABLE sales (
    sale_id       SERIAL  PRIMARY KEY,
    pharmacy_id   INTEGER NOT NULL
        REFERENCES pharmacies (pharmacy_id),
    medicine_id   INTEGER NOT NULL
        REFERENCES medicines (medicine_id),
    pharmacist_id INTEGER NOT NULL,
    sale_date     DATE    NOT NULL DEFAULT CURRENT_DATE,
    quantity      INTEGER NOT NULL
        CHECK (quantity > 0),
    FOREIGN KEY (pharmacist_id, pharmacy_id)
        REFERENCES pharmacists (pharmacist_id, pharmacy_id)
);



INSERT INTO categories (category_id, name) VALUES
    (1, 'Обезболивающие и жаропонижающие'),
    (2, 'Антибиотики'),
    (3, 'Гастроэнтерологические'),
    (4, 'Противоаллергические'),
    (5, 'Сердечно-сосудистые'),
    (6, 'Витамины');

INSERT INTO pharmacies (pharmacy_id, number, address, metro_station) VALUES
    (1, '1', 'ул. Тверская, 18, корп. 1',       'Пушкинская'),
    (2, '2', 'Ленинградский пр-т, 74, корп. 1', 'Сокол'),
    (3, '3', 'ул. Новый Арбат, 28',             'Смоленская'),
    (4, '4', 'просп. Мира, 26, стр. 1',         'Проспект Мира'),
    (5, '5', 'Кутузовский пр-т, 12',            'Кутузовская');

INSERT INTO medicines (medicine_id, name, dosage, quantity_or_volume,
                       manufacturer, prescription_required, category_id, price) VALUES
    (1, 'Нурофен', '200 мг', '24 таблетки', 'Reckitt Benckiser', FALSE, 1, 420.00),
    (2, 'Амоксициллин', '500 мг', '20 капсул', 'Синтез', TRUE, 2, 260.00),
    (3, 'Омепразол', '20 мг', '30 капсул', 'Teva', TRUE, 3, 150.00),
    (4, 'Сумамед', '500 мг', '3 таблетки', 'Teva', TRUE, 2, 450.00),
    (5, 'Кларитин', '10 мг', '10 таблеток', 'Bayer', FALSE, 4, 290.00),
    (6, 'Цефтриаксон', '1 г', '1 флакон', 'Биосинтез', TRUE, 2, 90.00),
    (7, 'Аспирин Кардио', '100 мг', '28 таблеток', 'Bayer', FALSE, 5, 310.00),
    (8, 'Эликвис', '5 мг', '60 таблеток', 'Pfizer', TRUE, 5, 2750.00),
    (9, 'Витамин D3', '2000 МЕ', '60 капсул', 'Solgar', FALSE, 6, 890.00),
    (10, 'Флемоксин Солютаб', '500 мг', '20 таблеток', 'Astellas', TRUE, 2, 380.00);

INSERT INTO pharmacists (pharmacist_id, last_name, first_name, patronymic,
                         birth_date, inn, passport_series, passport_number,
                         pharmacy_id) VALUES
    (1, 'Иванова', 'Мария', 'Петровна', '1985-03-14', '770123456789', '4508', '123456', 1),
    (2, 'Смирнов', 'Алексей', 'Николаевич', '1990-07-22', '770234567890', '4510', '234567', 2),
    (3, 'Кузнецова', 'Елена', 'Владимировна', '1988-11-05', '770345678901', '4512', '345678', 3),
    (4, 'Попов', 'Дмитрий', 'Сергеевич', '1992-01-30', '770456789012', '4514', '456789', 4),
    (5, 'Соколова', 'Анна', 'Игоревна', '1987-09-17', '770567890123', '4516', '567890', 5);

INSERT INTO availability (pharmacy_id, medicine_id, quantity) VALUES
    (1, 1, 25), (1, 2, 10), (1, 10, 20),
    (2, 3, 7), (2, 4, 12),
    (3, 4, 15), (3, 5, 30), (3, 10, 10),
    (4, 6, 8),
    (5, 7, 15), (5, 9, 4);

INSERT INTO sales (sale_id, pharmacy_id, medicine_id, pharmacist_id,
                   sale_date, quantity) VALUES
    (1, 1, 1, 1, '2026-10-12', 3),
    (2, 1, 2, 1, '2026-10-20', 3),
    (3, 2, 3, 2, '2026-10-15', 2),
    (4, 3, 5, 3, '2026-10-18', 2),
    (5, 3, 4, 3, '2026-10-25', 2),
    (6, 3, 10, 3, '2026-10-28', 2),
    (7, 4, 6, 4, '2026-11-01', 1),
    (8, 5, 7, 5, '2026-11-05', 3),
    (9, 5, 9, 5, '2026-11-07', 2);


SELECT name, dosage
FROM medicines
WHERE price < 1000
  AND prescription_required = TRUE
ORDER BY name;


SELECT pharmacist_id, SUM(quantity) AS total_packages
FROM sales
GROUP BY pharmacist_id
HAVING SUM(quantity) > 5
ORDER BY pharmacist_id;
