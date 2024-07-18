import time

from config import PROJECT_ID, USER_IDS, SLEEP_PAUSE
from functions import get_merge_requests_by_users, check_conditions, merge_and_close


def main_loop():
    while True:

        merge_requests = get_merge_requests_by_users(PROJECT_ID, USER_IDS)

        for mr in merge_requests:
            # Проверяем условия для мержинга и закрытия
            if check_conditions(mr):
                # Если условия выполнены, мержим и закрываем merge request
                merge_and_close(mr)

        # Пауза перед следующей итерацией
        time.sleep(SLEEP_PAUSE)


if __name__ == "__main__":
    main_loop()

