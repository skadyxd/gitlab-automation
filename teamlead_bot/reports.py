from abc import abstractmethod, ABC

from teamlead_bot.Issue import IssueManager
from teamlead_bot.sprint import Sprint


class IReport(ABC):
    manager = IssueManager

    @classmethod
    @abstractmethod
    def build(cls, *args):
        pass


class PriorityReport(IReport):
    tmp_prefix_name = 'PriorityReport'

    raw = (
        "- {} | {} | {} | {} | {} | {}"  # Формат строки для задачи
    )

    @classmethod
    def build(cls, issues, sprint: Sprint):
        manager = cls.manager(issues)
        result = []

        # Порядок статусов, который вам нужен
        status_order = ['В работе', 'Назначено', 'Бэклог продукта', 'Пауза']

        for dev in manager.developer_generate():
            dev_issues = manager.get_issues_by_assignee(dev)

            if not dev_issues:
                continue

            # Фильтруем задачи по статусам (берем только те, которые нам нужны)
            filtered_issues = [i for i in dev_issues if i.status in status_order]

            # Сортируем задачи сначала по статусу, затем по приоритету
            sorted_issues = sorted(
                filtered_issues,
                key=lambda i: (status_order.index(i.status), i.priority)
            )

            # Добавляем разработчика в начало
            if sorted_issues:
                result.append(f"👤 {dev}:")

            for issue in sorted_issues:
                priority_name = cls.get_priority_name(issue.priority)
                result.append(cls.raw.format(
                    issue.status,  # Название статуса
                    priority_name,  # Название приоритета
                    issue.name,  # Название задачи
                    f"https://jira.zyfra.com/browse/{issue.key}",  # Ссылка на задачу в Jira
                    f"{issue.original_estimate}ч",  # Исходная оценка времени
                    f"{issue.remaining_estimate}ч"  # Оставшееся время
                ))

            if sorted_issues:
                result.append("")

        final_result = "\n".join(result)
        if not final_result.strip():
            final_result = "Нет задач для отображения."

        return final_result

    @staticmethod
    def get_priority_name(priority):
        priority_mapping = {
            1: 'Критичный',
            2: 'Высокий',
            3: 'Средний',
            4: 'Низкий',
            5: 'Планируемый',
            6: 'Блокирующий',
            7: 'Минор'
        }
        return priority_mapping.get(priority, 'Неизвестный')


class StatusByDeveloperReport(IReport):
    tmp_prefix_name = 'StatusByDeveloperReport'
    raw = (
        "------------------- \n"
        "Разработчик: {} \n"
        "Скорость работы: {} \n"
        "Доступный остаток в спринте: {} часов"
    )

    @classmethod
    def build(cls, issues, sprint: Sprint):
        manager = cls.manager(issues)
        result = []

        for dev in manager.developer_generate():
            _speed = manager.calculate_speed_by_developer(dev)
            speed = round(_speed, 1) if _speed else "Нет данных"

            available_hours_in_sprint = sprint.remaining_hours_by_one
            remaining_estimate = manager.calculate_remaining_estimate(developer=dev, type_status='active')
            available = round(available_hours_in_sprint - remaining_estimate)

            result.append(cls.raw.format(
                dev, speed, available
            ))
        return "\n".join(result)


class StatusByTeamReport(IReport):
    tmp_prefix_name = 'StatusByTeamReport'
    raw = (
        # "_________________________________ \n"
        "План выполнения:: {}% \n"
        "Факт выполнения:: {}% \n"
        "Доступный остаток backend: {} \n"
        "Доступный остаток fronend: {}"
    )

    @classmethod
    def build(cls, issues, sprint: Sprint):
        manager = cls.manager(issues)
        plan_percent = 100 - sprint.remaining_hours_all / sprint.original_hours_all * 100
        backend_available = 0
        frontend_available = 0

        sum_original_estimate = 0
        sum_remaining_estimate = 0

        for dev in manager.developer_generate('backend'):
            available_hours_in_sprint = sprint.remaining_hours_by_one

            remaining_estimate = manager.calculate_remaining_estimate(developer=dev, type_status='active')
            original_estimate = manager.calculate_original_estimate(developer=dev, type_status='active')

            sum_original_estimate += original_estimate
            sum_remaining_estimate += remaining_estimate
            backend_available += available_hours_in_sprint - remaining_estimate

        for dev in manager.developer_generate('frontend'):
            available_hours_in_sprint = sprint.remaining_hours_by_one

            remaining_estimate = manager.calculate_remaining_estimate(developer=dev, type_status='active')
            original_estimate = manager.calculate_original_estimate(developer=dev, type_status='active')

            sum_original_estimate += original_estimate
            sum_remaining_estimate += remaining_estimate
            frontend_available += available_hours_in_sprint - remaining_estimate

        fact_percent = round(100 - sum_remaining_estimate / sum_original_estimate * 100)

        return cls.raw.format(
            plan_percent,
            fact_percent,
            backend_available,
            frontend_available
        )
