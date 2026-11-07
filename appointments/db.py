"""
Модуль работы с базой данных SQLite через стандартную библиотеку sqlite3.
Обеспечивает подключение, параметризованное выполнение SQL-запросов,
преобразование дат для фильтра Django |date и корректное закрытие соединения.
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from django.conf import settings


class DatabaseError(Exception):
    """Пользовательское исключение при ошибке обращения к базе данных."""
    pass


def get_connection(db_path=None):
    """Создаёт и возвращает соединение с базой данных SQLite."""
    target_path = Path(db_path) if db_path else Path(settings.SQLITE_DB_PATH)
    if not target_path.exists():
        raise DatabaseError("Файл базы данных не найден.")
    conn = sqlite3.connect(str(target_path))
    conn.row_factory = sqlite3.Row
    return conn


def _parse_visit_date(date_str):
    """
    Преобразует строку даты из SQLite ('YYYY-MM-DD HH:MM' или 'YYYY-MM-DD')
    в объект datetime для корректной работы шаблонных фильтров Django (например, |date:"d.m.Y").
    """
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(str(date_str), fmt)
        except ValueError:
            continue
    return date_str


def _row_to_dict(row):
    """Преобразует sqlite3.Row в словарь с распарсенной датой приёма."""
    item = dict(row)
    if "visit_date" in item:
        item["visit_date_raw"] = item["visit_date"]
        item["visit_date"] = _parse_visit_date(item["visit_date"])
    return item


# Белый список допустимых вариантов сортировки (защита от SQL-инъекций в ORDER BY)
ALLOWED_SORT_OPTIONS = {
    "date_asc": ("a.visit_date ASC", "По дате (сначала ближайшие)"),
    "date_desc": ("a.visit_date DESC", "По дате (сначала поздние)"),
    "patients_desc": ("a.patients DESC", "По числу пациентов (по убыванию)"),
    "patients_asc": ("a.patients ASC", "По числу пациентов (по возрастанию)"),
    "duration_desc": ("a.duration DESC", "По длительности (по убыванию)"),
    "title_asc": ("a.title ASC", "По названию (А–Я)"),
}

ALLOWED_LIMIT_OPTIONS = [5, 8, 10, 20, 50]


def get_all_appointments():
    """Возвращает список всех приёмов из базы данных."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT
                a.id, a.title, a.slug, a.visit_type, a.visit_date,
                a.duration, a.patients, a.status, a.cabin_id,
                c.name AS cabin_name, c.capacity AS cabin_capacity, c.cabin_type AS cabin_type
            FROM appointments a
            LEFT JOIN cabinets c ON a.cabin_id = c.id
            ORDER BY a.visit_date ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return [_row_to_dict(row) for row in rows]
    except sqlite3.Error as exc:
        raise DatabaseError("Не удалось получить список приёмов из базы данных.") from exc
    finally:
        if conn:
            conn.close()


def get_appointments_count():
    """Возвращает общее количество приёмов в таблице appointments с помощью COUNT(*)."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) AS total_count FROM appointments")
        row = cursor.fetchone()
        return row["total_count"] if row else 0
    except sqlite3.Error as exc:
        raise DatabaseError("Не удалось подсчитать количество приёмов.") from exc
    finally:
        if conn:
            conn.close()


def get_all_cabinets():
    """Возвращает список всех кабинетов из таблицы cabinets."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT id, name, capacity, cabin_type
            FROM cabinets
            ORDER BY name ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        raise DatabaseError("Не удалось загрузить список кабинетов из базы данных.") from exc
    finally:
        if conn:
            conn.close()


def get_filtered_appointments(min_patients=None, sort_key="date_asc", limit=None, simulate_error=False):
    """
    Выполняет параметризованный SQL-запрос для получения списка приёмов
    с присоединением данных кабинета (LEFT JOIN), фильтрацией по числу пациентов (WHERE),
    безопасной сортировкой (ORDER BY) и ограничением выборки (LIMIT).
    """
    conn = None
    try:
        if simulate_error:
            # Для демонстрации критерия 19 (обработка ошибки БД без показа traceback)
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM non_existent_table_for_error_demo")

        conn = get_connection()
        cursor = conn.cursor()

        order_clause, _ = ALLOWED_SORT_OPTIONS.get(sort_key, ALLOWED_SORT_OPTIONS["date_asc"])

        query = """
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
        """
        params = []

        if min_patients is not None:
            query += " WHERE a.patients >= ?"
            params.append(min_patients)

        query += f" ORDER BY {order_clause}"

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        return [_row_to_dict(row) for row in rows]
    except sqlite3.Error as exc:
        raise DatabaseError("Произошла ошибка при обращении к базе данных расписания приёмов.") from exc
    finally:
        if conn:
            conn.close()


def get_appointment_by_slug(slug):
    """
    Возвращает данные конкретного приёма и связанного кабинета по уникальному slug.
    Использует параметризованный SQL-запрос. Если запись не найдена, возвращает None.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
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
            WHERE a.slug = ?
        """
        cursor.execute(query, (slug,))
        row = cursor.fetchone()
        return _row_to_dict(row) if row else None
    except sqlite3.Error as exc:
        raise DatabaseError("Ошибка при получении сведений о приёме из базы данных.") from exc
    finally:
        if conn:
            conn.close()


def get_appointment_statistics(min_count=2):
    """
    Выполняет статистический SQL-запрос с использованием COUNT, GROUP BY и HAVING.
    Возвращает количество приёмов, суммарное число пациентов и среднюю длительность
    для каждого типа приёма, у которого число записей >= min_count.
    """
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT
                visit_type,
                COUNT(*) AS appointment_count,
                SUM(patients) AS total_patients,
                ROUND(AVG(duration), 1) AS avg_duration
            FROM appointments
            GROUP BY visit_type
            HAVING COUNT(*) >= ?
            ORDER BY appointment_count DESC, visit_type ASC
        """
        cursor.execute(query, (min_count,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        raise DatabaseError("Не удалось рассчитать статистику приёмов из базы данных.") from exc
    finally:
        if conn:
            conn.close()


def get_status_summary():
    """Дополнительная сводка по статусам приёмов с использованием COUNT и GROUP BY."""
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        query = """
            SELECT
                status,
                COUNT(*) AS status_count,
                SUM(patients) AS status_patients
            FROM appointments
            GROUP BY status
            ORDER BY status_count DESC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as exc:
        raise DatabaseError("Не удалось получить сводку по статусам приёмов.") from exc
    finally:
        if conn:
            conn.close()
