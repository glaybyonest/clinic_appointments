from django.shortcuts import render
from appointments.db import get_all_appointments, get_appointments_count, DatabaseError


def home_view(request):
    """
    Главная страница приложения (/).
    Получает список приёмов и общее количество записей из SQLite и передаёт в шаблон.
    """
    db_error = None
    appointments = []
    total_appointments = 0

    try:
        appointments = get_all_appointments()
        total_appointments = get_appointments_count()
    except DatabaseError as exc:
        db_error = str(exc)

    context = {
        'app_title': 'Расписание приёмов клиники «МедЛайн»',
        'app_description': (
            'Информационная система для просмотра расписания врачебных приёмов, '
            'контроля загрузки медицинских кабинетов, фильтрации записей по числу '
            'пациентов и анализа статистических показателей клиники.'
        ),
        'appointments': appointments,
        'total_appointments': total_appointments,
        'db_error': db_error,
    }
    return render(request, 'homepage/home.html', context)
