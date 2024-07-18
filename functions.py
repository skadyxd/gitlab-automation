import requests

from config import GITLAB_URL, HEADERS, PROJECT_ID


def get_merge_requests_by_users(project_id: int, user_ids: list[int]) -> list[dict]:
    """
    Gets a list of open merge requests for the given project and list of users.

    :param project_id: Id of the project / repository.
    :param user_ids: List of user IDs whose merge requests need to be retrieved.

    :return: List of dictionaries with data about merge requests.
    """
    merge_requests = []

    for user_id in user_ids:
        response = requests.get(
            f'{GITLAB_URL}/api/v4/projects/{project_id}/merge_requests',
            headers=HEADERS,
            params={'author_id': user_id, 'state': 'opened'}  # запрашиваем только открытые MR
        )

        if response.status_code == 200:
            merge_requests.extend(response.json())
        else:
            print(f'Error fetching merge requests for user {user_id}: {response.status_code}')
    return merge_requests


def is_merge_request_approved(merge_requests: dict) -> bool:
    """
    Checks if a merge request is approved.

    :param merge_requests: Dictionary with merge request data.

    :return: True if the merge request is approved, False otherwise.
    """

    approvals_response = requests.get(
        f'{GITLAB_URL}/api/v4/projects/{merge_requests["project_id"]}/merge_requests/{merge_requests["iid"]}/approvals',
        headers=HEADERS
    )

    if approvals_response.status_code != 200:
        print(f'Error fetching approvals for MR {merge_requests["iid"]}: {approvals_response.status_code}')
        return False

    approvals = approvals_response.json()
    if not approvals.get('approved'):
        print(f'MR {merge_requests["iid"]} is not approved')
        return False

    return True


def are_merge_request_pipelines_successful(merge_requests: dict) -> bool:
    """
    Checks if all pipelines are successful.

    :param merge_requests: Dictionary with merge request data.

    :return: True if the pipelines are successful, False otherwise.
    """

    pipelines_response = requests.get(
        f'{GITLAB_URL}/api/v4/projects/{merge_requests["project_id"]}/merge_requests/{merge_requests["iid"]}/pipelines',
        headers=HEADERS
    )

    if pipelines_response.status_code != 200:
        print(f'Error fetching pipelines for MR {merge_requests["iid"]}: {pipelines_response.status_code}')
        return False

    pipelines = pipelines_response.json()
    for pipeline in pipelines:
        if pipeline['status'] != 'success':
            print(f'MR {merge_requests["iid"]} has unsuccessful pipeline: {pipeline["status"]}')
            return False

    return True


def merge_and_close(merge_requests: dict):
    """
    Merges and closes a given merge request.
    """

    merge_response = requests.put(
        f'{GITLAB_URL}/api/v4/projects/{merge_requests["project_id"]}/merge_requests/{merge_requests["iid"]}/merge',
        headers=HEADERS
    )
    if merge_response.status_code == 200:
        print(f'Merged MR {merge_requests["iid"]}')
    else:
        print(f'Error merging MR {merge_requests["iid"]}: {merge_response.status_code}')


def check_conditions(merge_requests: dict) -> bool:
    if not is_merge_request_approved(merge_requests):
        return False
    if not are_merge_request_pipelines_successful(merge_requests):
        return False

    return True
