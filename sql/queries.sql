-- =========================================================================
-- Контрольная работа № 2. Вариант 3. «Расписание приёмов»
-- Файл SQL-запросов: sql/queries.sql
-- =========================================================================

-- 1. Создание таблицы кабинетов (cabinets)
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS cabinets;

CREATE TABLE cabinets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    capacity INTEGER NOT NULL,
    cabin_type TEXT NOT NULL
);

-- 2. Создание таблицы приёмов (appointments) со связью по cabin_id
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    visit_type TEXT NOT NULL,
    visit_date TEXT NOT NULL,
    duration INTEGER NOT NULL,
    patients INTEGER NOT NULL,
    status TEXT NOT NULL,
    cabin_id INTEGER,
    FOREIGN KEY (cabin_id) REFERENCES cabinets (id) ON DELETE SET NULL
);

-- 3. Наполнение таблицы cabinets (не менее 4 кабинетов разных типов)
INSERT INTO cabinets (id, name, capacity, cabin_type) VALUES
    (1, 'Кабинет 101', 15, 'терапевтический'),
    (2, 'Кабинет 204', 10, 'терапевтический'),
    (3, 'Кабинет 305', 6, 'хирургический'),
    (4, 'Кабинет 410', 12, 'диагностический'),
    (5, 'Кабинет 412', 8, 'диагностический');

-- 4. Наполнение таблицы appointments (10 приёмов разных типов, дат, статусов и кабинетов)
INSERT INTO appointments (id, title, slug, visit_type, visit_date, duration, patients, status, cabin_id) VALUES
    (1, 'Первичный осмотр терапевта', 'primary-checkup', 'терапия', '2026-10-15 09:00', 30, 8, 'запланирован', 1),
    (2, 'Комплексная диспансеризация и расширенная консультация врача', 'comprehensive-dispensary-checkup', 'терапия', '2026-10-15 10:30', 45, 12, 'идёт', 2),
    (3, 'Повторный приём и коррекция схемы лечения пациента', 'follow-up-therapy', 'терапия', '2026-10-16 11:00', 25, 5, 'завершён', 1),
    (4, 'Вакцинация и профилактический осмотр перед прививкой', 'vaccination-checkup', 'терапия', '2026-10-17 14:00', 20, 14, 'запланирован', 2),
    (5, 'УЗИ органов брюшной полости и почек', 'abdominal-ultrasound', 'диагностика', '2026-10-18 09:30', 40, 9, 'запланирован', 4),
    (6, 'ЭКГ с расшифровкой и функциональной нагрузочной пробой', 'ecg-diagnostics', 'диагностика', '2026-10-18 12:00', 35, 7, 'идёт', 5),
    (7, 'Суточное мониторирование артериального давления и пульса', 'holter-monitoring', 'диагностика', '2026-10-19 08:30', 30, 4, 'завершён', NULL),
    (8, 'Малая амбулаторная хирургическая операция и перевязка', 'minor-surgery', 'хирургия', '2026-10-20 10:00', 60, 3, 'идёт', 3),
    (9, 'Хирургическая перевязка и снятие послеоперационных швов', 'post-op-dressing', 'хирургия', '2026-10-21 15:00', 25, 6, 'завершён', 3),
    (10, 'Консультация хирурга-травматолога перед плановой операцией', 'surgeon-consultation', 'хирургия', '2026-10-22 16:00', 40, 2, 'запланирован', 3);

-- =========================================================================
-- Запросы для работы приложения (используются в модуле appointments/db.py)
-- =========================================================================

-- Запрос 1: Подсчёт общего количества приёмов с помощью COUNT (для главной страницы)
SELECT COUNT(*) AS total_count FROM appointments;

-- Запрос 2: Получение списка всех кабинетов (для страницы /cabinets/)
SELECT id, name, capacity, cabin_type
FROM cabinets
ORDER BY name ASC;

-- Запрос 3: Получение списка приёмов со сведениями о связанных кабинетах через LEFT JOIN
SELECT
    a.id,
    a.title,
    a.slug,
    a.visit_type,
    a.visit_date,
    a.duration,
    a.patients,
    a.status,
    a.cabin_id,
    c.name AS cabin_name,
    c.capacity AS cabin_capacity,
    c.cabin_type AS cabin_type
FROM appointments a
LEFT JOIN cabinets c ON a.cabin_id = c.id
ORDER BY a.visit_date ASC;

-- Запрос 4: Выборка приёмов по условию (GET-фильтрация по минимальному числу пациентов, параметризованный запрос)
SELECT
    a.id,
    a.title,
    a.slug,
    a.visit_type,
    a.visit_date,
    a.duration,
    a.patients,
    a.status,
    a.cabin_id,
    c.name AS cabin_name,
    c.capacity AS cabin_capacity,
    c.cabin_type AS cabin_type
FROM appointments a
LEFT JOIN cabinets c ON a.cabin_id = c.id
WHERE a.patients >= ?
ORDER BY a.patients DESC
LIMIT ?;

-- Запрос 5: Сортировка (ORDER BY) и ограничение выборки (LIMIT)
SELECT
    a.id,
    a.title,
    a.slug,
    a.visit_type,
    a.visit_date,
    a.duration,
    a.patients,
    a.status,
    a.cabin_id,
    c.name AS cabin_name
FROM appointments a
LEFT JOIN cabinets c ON a.cabin_id = c.id
ORDER BY a.patients DESC
LIMIT 5;

-- Запрос 6: Получение данных конкретного приёма и связанного кабинета по slug (параметризованный запрос)
SELECT
    a.id,
    a.title,
    a.slug,
    a.visit_type,
    a.visit_date,
    a.duration,
    a.patients,
    a.status,
    a.cabin_id,
    c.name AS cabin_name,
    c.capacity AS cabin_capacity,
    c.cabin_type AS cabin_type
FROM appointments a
LEFT JOIN cabinets c ON a.cabin_id = c.id
WHERE a.slug = ?;

-- Запрос 7: Статистический запрос по типам приёмов с использованием COUNT, GROUP BY и HAVING
SELECT
    visit_type,
    COUNT(*) AS appointment_count,
    SUM(patients) AS total_patients,
    ROUND(AVG(duration), 1) AS avg_duration
FROM appointments
GROUP BY visit_type
HAVING COUNT(*) >= ?
ORDER BY appointment_count DESC;
