/**
 * Интерактивные элементы интерфейса приложения «Расписание приёмов»:
 * 1. Раскрытие и скрытие дополнительной информации о приёме на карточке (.js-toggle-extra).
 * 2. Переключение компактного/обычного режима отображения карточек (#compact-mode-btn).
 * 3. Подтверждение сброса параметров фильтрации (#reset-filter-link).
 */
document.addEventListener('DOMContentLoaded', function () {
    // 1. Показ / скрытие дополнительной сводки в карточке приёма
    const toggleButtons = document.querySelectorAll('.js-toggle-extra');
    toggleButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            const targetId = btn.getAttribute('data-target');
            const extraBlock = document.getElementById(targetId);
            if (!extraBlock) return;

            const isHidden = extraBlock.hasAttribute('hidden');
            if (isHidden) {
                extraBlock.removeAttribute('hidden');
                btn.textContent = 'Скрыть сводку';
            } else {
                extraBlock.setAttribute('hidden', 'hidden');
                btn.textContent = 'Краткая сводка';
            }
        });
    });

    // 2. Переключение компактного режима отображения страницы
    const compactBtn = document.getElementById('compact-mode-btn');
    if (compactBtn) {
        compactBtn.addEventListener('click', function () {
            document.body.classList.toggle('compact-view');
            const isCompact = document.body.classList.contains('compact-view');
            compactBtn.textContent = isCompact ? 'Компактный вид: ВКЛ' : 'Компактный вид: ВЫКЛ';
        });
    }

    // 3. Подтверждение сброса активного фильтра, если поле фильтра заполнено
    const resetLink = document.getElementById('reset-filter-link');
    const patientsInput = document.getElementById('patients-input');
    if (resetLink && patientsInput) {
        resetLink.addEventListener('click', function (event) {
            if (patientsInput.value.trim() !== '') {
                const confirmed = window.confirm('Сбросить установленный фильтр по количеству пациентов?');
                if (!confirmed) {
                    event.preventDefault();
                }
            }
        });
    }
});
