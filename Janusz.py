import discord, random, json, os, datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sched = AsyncIOScheduler()
client = discord.Client()

data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data')

greetings = ['Hey', 'Hello', 'Greetings', 'Good day']
personal_greetings = ['Nice to see you here!', 'Productive day?', 'How are you?', 'Great weather today!\nUnless it\'s raining, in which case I\'m just a bot, so... Great weather!']

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    msg = message.content;
    if msg.lower() == 'hi janusz' or msg.lower() == 'hey janusz':
        await client.send_message(message.channel, get_personal_greeting(message.author.nick if message.author.nick else message.author.name))

@client.event
async def on_message_edit(before, after):
    if after.author == client.user:
        return
    msg = after.content;
    if msg.lower() == 'hi janusz' or msg.lower() == 'hey janusz':
        await client.send_message(after.channel, get_personal_greeting(after.author.nick if after.author.nick else after.author.name))

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

async def send_announcement(announcement):
    if client.is_logged_in:
        for server in client.servers:
            for channel in server.channels:
                if channel.type == discord.ChannelType.text:
                    if not announcement['working_day'] or (announcement['working_day'] and not isHoliday()):
                        await client.send_message(channel, random.choice(announcement['message']))
                        break
    
def get_personal_greeting(author):
    message = ''
    message += random.choice(greetings) + ' ' + author + '! '
    message += random.choice(personal_greetings)
    return message
    
def isHoliday():
    day = datetime.date.today().day
    month = datetime.date.today().month
    for holiday in holidays:
        date = holiday.split('-')
        if int(date[0]) == day and int(date[1]) == month:
            return True
    return False
    
f = open(os.path.join(data_folder, "announcements.json"), "r")
json_announcements = f.read()
announcements = json.loads(json_announcements)
f.close()

f = open(os.path.join(data_folder, "holidays.json"), "r")
json_holidays = f.read()
holidays = json.loads(json_holidays)
f.close()

f = open(os.path.join(data_folder, "token.txt"), "r")
token = f.read()
f.close()
#print(json.dumps(announcements, sort_keys=False, indent=4))

for announcement in announcements:
    sched.add_job(send_announcement, 'cron', year=announcement['year'], month=announcement['month'], day=announcement['day'], week=announcement['week'], day_of_week=announcement['day_of_week'], hour=announcement['hour'], minute=announcement['minute'], second=announcement['second'], args=[announcement])
sched.start()

client.run(token)

# python D:\Projects\OtherProjects\JanuszBotPython\Janusz.py