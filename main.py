import logging
from config import PROJECT_ID, USER_IDS, SLEEP_PAUSE, APPROVERS_IDS
from gitlab_merge_request_checker import GitLabMergeRequestChecker

import discord
from discord.ext import tasks
from config import DISCORD_TOKEN, DISCORD_CHANNEL_ID

client = discord.Client(intents=discord.Intents.all())

# Настройка логирования
logging.basicConfig(level=logging.INFO, filename='main.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s')


@tasks.loop(seconds=SLEEP_PAUSE)
async def main_task():

    await client.wait_until_ready()
    channel = client.get_channel(DISCORD_CHANNEL_ID)

    checker = GitLabMergeRequestChecker(PROJECT_ID, APPROVERS_IDS, channel)

    merge_requests = await checker.get_merge_requests_by_users(USER_IDS)

    for mr in merge_requests:
        # Проверяем условия для мержинга и закрытия
        if await checker.check_conditions(mr):
            # Если условия выполнены, мержим и закрываем merge request
            message = await checker.merge_and_close(mr)

            await channel.send(message)


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    main_task.start()


client.run(DISCORD_TOKEN)
