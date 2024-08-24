import time
from atlassian import Jira

from config import JIRA_TOKEN
from jira_automation.reports import StatusByDeveloperReport, StatusByTeamReport, PriorityReport
from jira_automation.sprint import Sprint

jira = Jira(
    url='https://jira.zyfra.com',
    token=JIRA_TOKEN
)


# sprint = Sprint(jira, 530, 'Grey')
# jql_request = 'project = VItemp/StatusByDeveloperReportSTV8 AND Sprint = {}'.format(sprint.id)
# jql_response = jira.jql(jql_request)
# sprint_issues = jql_response.get('issues')
# print(StatusByTeamReport.build(sprint_issues, sprint))


def save_tmp(file, data):
    with open('jira_automation/temp/{}'.format(file), 'w') as f:
        f.write(data)


def generate_jira_report():
    sprint = Sprint(jira, 530, 'Grey')
    jql_request = 'project = VISTV8 AND Sprint = {}'.format(sprint.id)
    jql_response = jira.jql(jql_request)
    sprint_issues = jql_response.get('issues')

    save_tmp(StatusByDeveloperReport.tmp_prefix_name,
             StatusByDeveloperReport.build(sprint_issues, sprint))

    save_tmp(StatusByTeamReport.tmp_prefix_name,
             StatusByTeamReport.build(sprint_issues, sprint))

    save_tmp(PriorityReport.tmp_prefix_name,
             PriorityReport.build(sprint_issues, sprint))


def run():
    while True:
        generate_jira_report()
        time.sleep(300)


if __name__ == "__main__":
    run()

# class JiraProcessor:
#     jql_request = 'project = VISTV8 AND Sprint = {}'
#
#     def build_cache(self):
#         time_now = datetime.datetime.now()
#         if not self.cache_up_time or time_now - self.cache_up_time > self.cache_lifetime:
#             self.sprint = Sprint(self.jira, self.board, self.team)
#             jql_response = self.jira.jql(self.jql_request.format(self.sprint.id))
#             self.sprint_issues = jql_response.get('issues')
#             self.cache_up_time = time_now
#
#     def __init__(self, jira, board, team):
#         self.jira = jira
#         self.board = board
#         self.team = team
#         self.sprint = None
#         self.sprint_issues = None
#         self.cache_lifetime = datetime.timedelta(minutes=5)
#         self.cache_up_time = None
#         self.build_cache()
#
#     def run(self):
#         while True:
#             self.build_cache()
#             time.sleep(1)


# StatusByDeveloperReport.build(sprint_issues, sprint)
# StatusByTeamReport.build(sprint_issues, sprint)
