from django.shortcuts import render
from appointments.db import get_all_cabinets, DatabaseError


def cabinet_list_view(request):
    """
    Страница списка кабинетов (/cabinets/).
    Извлекает список кабинетов из SQLite через SQL-запрос и передаёт в шаблон.
    """
    db_error = None
    cabinets = []

    try:
        cabinets = get_all_cabinets()
    except DatabaseError as exc:
        db_error = str(exc)

    context = {
        'cabinets': cabinets,
        'db_error': db_error,
    }
    return render(request, 'cabinets/cabinet_list.html', context)
