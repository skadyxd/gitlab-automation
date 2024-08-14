import aiohttp
import logging

from config import GITLAB_URL, HEADERS
from gitlab_automation.jira_utils import get_jira_mr_link
from gitlab_automation.messages import MESSAGES
from gitlab_automation.persons_json_functions import get_discord_id_by_gitlab_id

# Настройка логирования
logging.basicConfig(level=logging.INFO, filename='gitlab_merge_request_checker.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')


class GitLabMergeRequestChecker:
    def __init__(self, project_id: int, approvers_ids: list[int], channel_for_messaging):
        self.project_id = project_id
        self.approvers_ids = approvers_ids
        self.channel_for_messaging = channel_for_messaging

    async def get_project_details(self):
        url = f'{GITLAB_URL}/api/v4/projects/{self.project_id}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS) as response:
                if response.status == 200:
                    project_details = await response.json()
                else:
                    logging.error(f"Ошибка получения деталей проекта: {response.status} - {await response.text()}")

        return project_details

    async def construct_merge_request_url(self, merge_request_iid: str) -> str | None:
        """
        Создает URL для merge request на основе сохраненных деталей проекта.

        :param merge_request_iid: IID merge request.

        :return: URL merge request.
        """
        project_details = await self.get_project_details()

        if project_details:
            namespace = project_details['namespace']['full_path']
            project_name = project_details['name']
            return f"{GITLAB_URL}{namespace}/{project_name}/-/merge_requests/{merge_request_iid}"
        return None

    async def get_merge_requests_by_users(self, user_ids: list[int]) -> list[dict]:
        """
        Gets a list of open merge requests for the given project and list of users.

        :param user_ids: List of user IDs whose merge requests need to be retrieved.

        :return: List of dictionaries with data about merge requests.
        """
        merge_requests = []

        async with aiohttp.ClientSession() as session:
            for user_id in user_ids:
                async with session.get(
                        f'{GITLAB_URL}/api/v4/projects/{self.project_id}/merge_requests',
                        headers=HEADERS,
                        params={'author_id': user_id, 'state': 'opened'}
                ) as response:
                    if response.status == 200:
                        merge_requests.extend(await response.json())
                    else:
                        logging.error(f'Error fetching merge requests for user {user_id}: {response.status}')

        return merge_requests

    async def is_merge_request_approved(self, merge_request: dict) -> bool:
        """
        Checks if a merge request is approved and the approver is valid.

        :param merge_request: Dictionary with merge request data.

        :return: True if the merge request is approved and the approver is valid, False otherwise.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'{GITLAB_URL}/api/v4/projects/{merge_request["project_id"]}/merge_requests/{merge_request["iid"]}/approvals',
                    headers=HEADERS
            ) as response:
                if response.status != 200:
                    logging.error(f'Error fetching approvals for MR {merge_request["iid"]}: {response.status}')
                    return False

                approvals = await response.json()
                approved_by = approvals.get('approved_by', [])

                if not approvals.get('approved'):
                    logging.info(f'MR {merge_request["iid"]} is not approved')
                    return False

                valid_approver = any(approver['user']['id'] in self.approvers_ids for approver in approved_by)
                if not valid_approver:
                    logging.info(f'MR {merge_request["iid"]} is not approved by a valid approver')
                    return False

                return True

    async def are_merge_request_pipelines_successful(self, merge_request: dict) -> bool:
        """
        Checks if all pipelines are successful.

        :param merge_request: Dictionary with merge request data.

        :return: True if the pipelines are successful, False otherwise.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f'{GITLAB_URL}/api/v4/projects/{merge_request["project_id"]}/merge_requests/{merge_request["iid"]}/pipelines',
                    headers=HEADERS
            ) as response:
                if response.status != 200:

                    logging.error(
                        MESSAGES["pipeline_fetch_error"].format(
                            mr_link=await self.construct_merge_request_url(merge_request["iid"]),
                            status=response.status
                        )
                    )

                    return False

                pipelines = await response.json()
                failed_pipelines = [pipeline for pipeline in pipelines if pipeline['status'] != 'success']

                if failed_pipelines:
                    for pipeline in failed_pipelines:
                        logging.info(
                            MESSAGES["pipeline_unsuccessful"].format(
                                mr_link=await self.construct_merge_request_url(merge_request["iid"]),
                                pipeline_status=pipeline["status"]
                            )
                        )

                    # failure_messages = [
                    #     f'Pipeline ID: {pipeline["id"]}, Status: {pipeline["status"]}'
                    #     for pipeline in failed_pipelines
                    # ]

                    message = MESSAGES["pipeline_failed_message"].format(
                        mr_title=merge_request["title"],
                        mr_link=await self.construct_merge_request_url(merge_request["iid"]),
                        jira_link=get_jira_mr_link(
                            merge_request_title=merge_request["title"]
                        ),
                        user_id_discord=await get_discord_id_by_gitlab_id(
                            gitlab_id=merge_request["author"]["id"]
                        ),
                        target_branch=merge_request["target_branch"],
                    )

                    await self.channel_for_messaging.send(message)
                    return False

                return True

    async def merge_and_close(self, merge_request: dict):
        """
        Merges and closes a given merge request.
        """
        async with aiohttp.ClientSession() as session:
            async with session.put(
                    f'{GITLAB_URL}/api/v4/projects/{merge_request["project_id"]}/merge_requests/{merge_request["iid"]}/merge',
                    headers=HEADERS
            ) as response:
                if response.status == 200:
                    logging.info(f'Merged MR {merge_request["iid"]}')

                    await self.channel_for_messaging.send(
                        MESSAGES["merge_successful"].format(
                            mr_title=merge_request["title"],
                            mr_link=await self.construct_merge_request_url(merge_request["iid"]),
                            jira_link=get_jira_mr_link(
                                merge_request_title=merge_request["title"]
                            ),
                            user_id_discord=await get_discord_id_by_gitlab_id(
                                gitlab_id=merge_request["author"]["id"]
                            ),
                            target_branch=merge_request["target_branch"]
                        )
                    )

                else:
                    logging.error(f'Error merging MR {merge_request["iid"]}: {response.status}')

                    await self.channel_for_messaging.send(
                        MESSAGES["merge_failed"].format(
                            mr_title=merge_request["title"],
                            mr_link=await self.construct_merge_request_url(merge_request["iid"]),
                            jira_link=get_jira_mr_link(
                                merge_request_title=merge_request["title"]
                            ),
                            user_id_discord=await get_discord_id_by_gitlab_id(
                                gitlab_id=merge_request["author"]["id"]
                            ),
                            target_branch=merge_request["target_branch"]
                        )
                    )

    async def check_conditions(self, merge_request: dict) -> bool:
        """
        Checks if all conditions are met for a merge request.

        :param merge_request: Dictionary with merge request data.

        :return: True if all conditions are met, False otherwise.
        """
        if not await self.is_merge_request_approved(merge_request):
            return False
        if not await self.are_merge_request_pipelines_successful(merge_request):
            return False

        return True
