class IssueManager:
    def __init__(self, issues):
        self.active_statuses = ['Код-ревью', 'Бэклог продукта', 'В работе']
        self.done_statuses = ['Готово', 'Тестирование']
        self.waiting_statuses = ['On Pause', 'Отклонено']
        self.backend_developers = ['Aleksandra Yakupova', 'Andrey U Popov', 'Pavel Lazarev']
        self.team_lead = 'Artem Zaykov'
        self.frontend_developers = ['Vadim Popov']
        self.issue_list = [Issue(i) for i in issues]

    def get_issues_by_assignee(self, assignee) -> list:
        return [i for i in self.issue_list if i.assignee == assignee]

    def get_sum_remaining_estimate(self):
        return sum([i.remaining_estimate for i in self.issue_list])

    def get_sum_original_estimate(self):
        return sum([i.original_estimate for i in self.issue_list])

    def get_active_sum_remaining_estimate(self):
        return sum([i.remaining_estimate for i in self.issue_list if i.status in self.active_statuses])

    def get_active_sum_original_estimate(self):
        return sum([i.original_estimate for i in self.issue_list if i.status in self.active_statuses])

    def _get_status(self, type_status):
        """
        Фильтр задачь по статусам
        """
        if type_status == 'active':
            types = self.active_statuses
        elif type_status == 'non_active':
            types = self.done_statuses + self.waiting_statuses
        elif type_status == 'done':
            types = self.done_statuses
        else:
            types = self.non_active_statuses + self.active_statuses
        return types

    def _get_developers(self, competence=None):
        """
        Определяем разработчиков по компетенциям
        """
        if competence == 'backend':
            developers = self.backend_developers
        elif competence == 'frontend':
            developers = self.frontend_developers
        else:
            developers = self.frontend_developers + self.backend_developers
        return developers

    def calculate_original_estimate(self, competence=None, developer=None, type_status=None):
        """
        Сумма оценок времени в задачах
        """
        types = self._get_status(type_status)
        developers = self._get_developers(competence)
        return sum([
            i.original_estimate
            for i in self.issue_list
            if i.status in types and i.assignee in developers and i.assignee == developer
        ])

    def calculate_remaining_estimate(self, competence=None, developer=None, type_status=None):
        """
        Сумма оставшегося времени в задачах
        """
        types = self._get_status(type_status)
        developers = self._get_developers(competence)
        return sum([
            i.remaining_estimate
            for i in self.issue_list
            if i.status in types and i.assignee in developers and i.assignee == developer
        ])

    def calculate_spent_time(self, competence=None, developer=None, type_status=None):
        """
        Сумма списанного времени в задачах
        """
        types = self._get_status(type_status)
        developers = self._get_developers(competence)
        return sum([
            i.spent_time
            for i in self.issue_list
            if i.status in types and i.assignee in developers and i.assignee == developer
        ])

    def calculate_speed_by_developer(self, developer):
        """
        Расчет скорости работы разработчика, на основании разницы оценки и списанного времени всех закрытых задач.
        """
        sum_active_original_estimate = self.calculate_original_estimate(developer=developer, type_status='done')
        sum_spent_time = self.calculate_spent_time(developer=developer, type_status='done')
        if sum_active_original_estimate and sum_spent_time:
            return sum_active_original_estimate / sum_spent_time
        else:
            return None

    def developer_generate(self, competence=None):
        """
        Генератор, для перебора разработчиков
        """
        developers = self._get_developers(competence)
        for dev in developers:
            yield dev


class Issue:
    def __init__(self, issue_dict):
        self.id = issue_dict['id']
        self.key = issue_dict['key']
        self.data = issue_dict['fields']

    @property
    def assignee(self):
        return self.data['assignee']['displayName'] if self.data['assignee'] else 'Не назначен'

    @property
    def status(self):
        return self.data['status']['name']

    @property
    def name(self):
        return self.data['summary']

    @property
    def original_estimate(self):
        estimate = self.data['timetracking'].get('originalEstimateSeconds') or 0
        return estimate / 3600

    @property
    def remaining_estimate(self):
        estimate = self.data['timetracking'].get('remainingEstimateSeconds') or 0
        return estimate / 3600

    @property
    def spent_time(self):
        time = self.data['timetracking'].get('timeSpentSeconds') or 0
        return time / 3600

    @property
    def priority(self):
        priority = self.data.get('priority', {}).get('name', 'Нет приоритета')
        priority_mapping = {
            'Критичный': 1,
            'Высокий': 2,
            'Средний': 3,
            'Низкий': 4,
            'Планируемый': 5,
            'Блокирующий': 6,
            'Минор': 7
        }
        return priority_mapping.get(priority, 8)

