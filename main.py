from config import PROJECT_ID, USER_IDS, GITLAB_LOOP_SLEEP_PAUSE, JIRA_LOOP_SLEEP_PAUSE, APPROVERS_IDS, DISCORD_TOKEN, DISCORD_CHANNEL_ID

import discord
from discord.ext import tasks, commands

from gitlab_automation.gitlab_merge_request_checker import GitLabMergeRequestChecker
from teamlead_bot.jira import generate_jira_report
from teamlead_bot.reports import StatusByTeamReport, StatusByDeveloperReport, PriorityReport

# Настройки бота
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='>', intents=intents)


# Основные команды и задачи первого проекта (GitLab)
@tasks.loop(seconds=GITLAB_LOOP_SLEEP_PAUSE)
async def gitlab_task():
    await bot.wait_until_ready()
    channel = bot.get_channel(DISCORD_CHANNEL_ID)

    checker = GitLabMergeRequestChecker(PROJECT_ID, APPROVERS_IDS, channel)
    merge_requests = await checker.get_merge_requests_by_users(USER_IDS)

    for mr in merge_requests:
        if await checker.check_conditions(mr):
            message = await checker.merge_and_close(mr)
            await channel.send(message)


# Основные команды и задачи второго проекта (Jira)
@tasks.loop(seconds=JIRA_LOOP_SLEEP_PAUSE)
async def jira_task():
    try:
        generate_jira_report()
    except Exception as e:
        print('ERROR:', e)


@bot.command()
async def ping(ctx):
    await ctx.send('pong')


# @bot.command()
# async def sprint(ctx, arg):
#     if arg == 'team':
#         result = open(f'teamlead_bot/temp/{StatusByTeamReport.tmp_prefix_name}').read()
#     elif arg == 'dev':
#         result = open(f'teamlead_bot/temp/{StatusByDeveloperReport.tmp_prefix_name}').read()
#     elif arg == 'priority':
#         result = open(f'teamlead_bot/temp/{PriorityReport.tmp_prefix_name}').read()
#     await ctx.send(result)

@bot.command()
async def sprint(ctx, arg):
    if arg == 'team':
        result = open(f'teamlead_bot/temp/{StatusByTeamReport.tmp_prefix_name}').read()
    elif arg == 'dev':
        result = open(f'teamlead_bot/temp/{StatusByDeveloperReport.tmp_prefix_name}').read()
    elif arg == 'priority':
        result = open(f'teamlead_bot/temp/{PriorityReport.tmp_prefix_name}').read()

    # Разделяем сообщение на части длиной не более 2000 символов
    for i in range(0, len(result), 2000):
        await ctx.send(result[i:i+2000])


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} (ID: {bot.user.id})')
    gitlab_task.start()
    jira_task.start()


bot.run(DISCORD_TOKEN)
