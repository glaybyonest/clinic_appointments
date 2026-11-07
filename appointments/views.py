from django.shortcuts import render
from django.http import Http404
from .db import (
    get_filtered_appointments,
    get_appointment_by_slug,
    get_appointment_statistics,
    get_status_summary,
    get_appointments_count,
    ALLOWED_SORT_OPTIONS,
    ALLOWED_LIMIT_OPTIONS,
    DatabaseError,
)


def appointment_list_view(request):
    """
    Страница списка приёмов (/appointments/).
    Поддерживает:
    - GET-фильтрацию по минимальному количеству пациентов (?patients=5);
    - сортировку по заранее определённым безопасным вариантам (?sort=patients_desc);
    - ограничение количества выводимых записей (?limit=5);
    - безопасную обработку ошибок базы данных (?simulate_db_error=1 для демонстрации).
    """
    db_error = None
    filter_warning = None
    appointments = []

    raw_patients = request.GET.get('patients', '').strip()
    raw_sort = request.GET.get('sort', 'date_asc').strip()
    raw_limit = request.GET.get('limit', '').strip()
    simulate_error = request.GET.get('simulate_db_error') == '1'

    min_patients = None
    if raw_patients != '':
        try:
            parsed_patients = int(raw_patients)
            if parsed_patients < 0:
                filter_warning = 'Количество пациентов не может быть отрицательным. Показаны все записи.'
            else:
                min_patients = parsed_patients
        except ValueError:
            filter_warning = 'Введите корректное целое число для фильтра по количеству пациентов.'

    sort_key = raw_sort if raw_sort in ALLOWED_SORT_OPTIONS else 'date_asc'

    limit_val = None
    if raw_limit != '':
        try:
            parsed_limit = int(raw_limit)
            if parsed_limit > 0:
                limit_val = parsed_limit
        except ValueError:
            pass

    try:
        appointments = get_filtered_appointments(
            min_patients=min_patients,
            sort_key=sort_key,
            limit=limit_val,
            simulate_error=simulate_error,
        )
    except DatabaseError as exc:
        db_error = str(exc)

    sort_choices = [
        {'key': k, 'label': v[1]}
        for k, v in ALLOWED_SORT_OPTIONS.items()
    ]

    context = {
        'appointments': appointments,
        'current_patients': raw_patients if min_patients is not None else '',
        'min_patients_applied': min_patients,
        'current_sort': sort_key,
        'current_limit': limit_val or '',
        'sort_choices': sort_choices,
        'limit_choices': ALLOWED_LIMIT_OPTIONS,
        'filter_warning': filter_warning,
        'db_error': db_error,
    }
    return render(request, 'appointments/appointment_list.html', context)


def appointment_detail_view(request, slug):
    """
    Страница конкретного приёма (/appointments/<slug>/).
    При обращении к несуществующему slug вызывает Http404 (корректная страница 404).
    """
    db_error = None
    appointment = None

    try:
        appointment = get_appointment_by_slug(slug)
    except DatabaseError as exc:
        db_error = str(exc)
        return render(
            request,
            'appointments/appointment_detail.html',
            {'appointment': None, 'db_error': db_error},
            status=503,
        )

    if appointment is None:
        raise Http404(f"Приём с адресом '{slug}' не найден в расписании.")

    context = {
        'appointment': appointment,
        'db_error': db_error,
    }
    return render(request, 'appointments/appointment_detail.html', context)


def statistics_view(request):
    """
    Страница статистики приёмов (/appointments/statistics/).
    Выполняет SQL-запрос с COUNT, GROUP BY и HAVING COUNT(*) >= min_count.
    """
    db_error = None
    stats_by_type = []
    status_summary = []
    total_appointments = 0

    raw_min_count = request.GET.get('min_count', '2').strip()
    try:
        min_count = max(1, int(raw_min_count))
    except ValueError:
        min_count = 2

    try:
        stats_by_type = get_appointment_statistics(min_count=min_count)
        status_summary = get_status_summary()
        total_appointments = get_appointments_count()
    except DatabaseError as exc:
        db_error = str(exc)

    context = {
        'stats_by_type': stats_by_type,
        'status_summary': status_summary,
        'min_count': min_count,
        'total_appointments': total_appointments,
        'db_error': db_error,
    }
    return render(request, 'appointments/statistics.html', context)
