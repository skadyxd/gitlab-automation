import re


def get_jira_mr_link(merge_request_title: str) -> str:
    """
    Создает ссылку на Jira с тэгом MR, взятым из названия merge request.

    :param merge_request_title: Название merge request, из которого будет извлекаться тэг.
    :return: Ссылка на Jira.
    """
    task_tag = extract_first_bracket_content(input_string=merge_request_title)

    link = f'https://jira.zyfra.com/browse/{task_tag}'

    return link


def extract_first_bracket_content(input_string: str) -> str | None:
    """
    Извлекает содержимое первых квадратных скобок из заданной строки.

    :param input_string: Заданная строка.
    :return: Содержимое находящееся в первых квадратных скобках ([])
    """

    # Регулярное выражение для поиска содержимого первых квадратных скобок
    pattern = r'\[([^\[\]]+)\]'

    # Поиск совпадений
    match = re.search(pattern, input_string)

    # Если совпадение найдено, вернуть содержимое первых скобок
    if match:
        return match.group(1)
    else:
        return None
