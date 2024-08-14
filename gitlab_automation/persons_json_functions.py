from config import PERSONS_DATA


async def get_discord_id_by_gitlab_id(gitlab_id: str) -> str | None:
    """
    Получить discord_name пользователя по его gitlab_id

    :return: discord name (@example)
    """
    # Поиск пользователя по gitlab_id
    for person in PERSONS_DATA['persons']:
        if person['gitlab_id'] == gitlab_id:
            return person['discord_id']

    # Если пользователь не найден
    return None
