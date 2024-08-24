import datetime


class Sprint:
    hours_in_day = 8
    estimate = 4.5

    def __init__(self, jira, board, team):
        sprints = jira.get_all_sprints_from_board(board, state='ACTIVE', start=0, limit=50)
        self.sprint = [i for i in sprints['values'] if team in i['name']][0]

    @staticmethod
    def _get_working_days(start, end):
        count = 0
        while start.date() != end.date():
            if start.isoweekday() not in (6, 7):
                count += 1
            start += datetime.timedelta(days=1)

        # TODO: https://xmlcalendar.ru/ добавить производственный календарь

        return count

    def _get_all_days(self):
        end = datetime.datetime.fromisoformat(self.sprint['endDate'])
        start = datetime.datetime.fromisoformat(self.sprint['startDate'])
        days = (end - start).days
        return days

    def _get_active_days(self):
        end = datetime.datetime.fromisoformat(self.sprint['endDate'])
        start = datetime.datetime.fromisoformat(self.sprint['startDate'])
        return self._get_working_days(start, end)

    @property
    def original_hours_all(self):
        days = self._get_active_days()
        hours = days * self.hours_in_day * self.estimate
        return hours

    @property
    def remaining_hours_all(self):
        end = datetime.datetime.fromisoformat(self.sprint['endDate'])
        start = datetime.datetime.now()
        days = self._get_working_days(start, end)
        hours = days * self.hours_in_day * self.estimate
        return hours

    @property
    def remaining_hours_by_one(self):
        end = datetime.datetime.fromisoformat(self.sprint['endDate'])
        start = datetime.datetime.now()
        days = self._get_working_days(start, end)
        hours = days * self.hours_in_day
        return hours

    @property
    def id(self):
        return self.sprint['id']


# class Sprint:
#
#     def status(self):
#         return 'status done'
#
#     def tasks(self):
#         return 'tasks done'
#
#     @classmethod
#     def call(cls, command: str):
#         func = getattr(cls(), command)
#         return func()


# print(Sprint.call('tasks'))