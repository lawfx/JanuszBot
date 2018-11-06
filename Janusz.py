import discord, random, json, os, datetime, re
from apscheduler.schedulers.asyncio import AsyncIOScheduler

sched = AsyncIOScheduler()
client = discord.Client()

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    await process_message(message)
    
@client.event
async def on_message_edit(before, after):
    if after.author == client.user:
        return
    await process_message(after)
    
@client.event
async def on_reaction_add(reaction, user):
    if user == client.user or reaction.message.author == client.user:
        return
    reactions = reaction.message.reactions
    for react in reactions:
        if react.me:
            return
    if random.randint(0, 1) == 1:
        if random.randint(0, 1) == 1:
            await client.add_reaction(reaction.message, random.choice(reactions).emoji)
        else:
            await client.add_reaction(reaction.message, '\U0001f984')

async def send_announcement(announcement):
    if client.is_logged_in:
        for server in client.servers:
            for channel in server.channels:
                if channel.type != discord.ChannelType.text:
                    continue
                if channel.type == discord.ChannelType.text and channel.position == 0:
                    if not announcement['working_day'] or (announcement['working_day'] and not is_holiday()):
                        await client.send_message(channel, random.choice(announcement['message']))
                        break
    
async def send_greet_user(message):
    await client.send_message(message.channel, get_personal_greeting(get_author_name(message.author)))
    reply = await client.wait_for_message(timeout=15, author=message.author, channel=message.channel)
    if not reply:
        await client.send_message(message.channel, get_author_name(message.author) + " why do you ignore me? :cry:")
                
async def send_single_name(message):
    await client.send_message(message.channel, get_author_name(message.author))
    reply = await client.wait_for_message(timeout=15, author=message.author, channel=message.channel)
    if not reply:
        await client.send_message(message.channel, get_author_name(message.author) + " was there something you meant to tell me? :thinking:")
         
async def send_single_mention(message):
    await client.send_message(message.channel, message.author.mention)
    reply = await client.wait_for_message(timeout=15, author=message.author, channel=message.channel)
    if not reply:
        await client.send_message(message.channel, message.author.mention + " was there something you meant to tell me? :thinking:")
        
async def send_daily_color(message):
    await client.send_message(message.channel, "The color of the day is " + daily_color + " :rainbow:")

async def process_message(message):
    msg = message.clean_content.lower()
    if 'janusz' in msg:
        if 'janusz' == msg:
            await send_single_name(message)
        elif '@janusz' == msg:
            await send_single_mention(message)
        elif is_in_string_as_whole('color', msg):
            await send_daily_color(message)
        elif is_greeting_in_message(msg):
            await send_greet_user(message)
        else:
            await client.send_message(message.channel, "Sorry " + get_author_name(message.author) + " I didn't quite catch that :confused:")
            
def get_personal_greeting(author):
    message = ''
    message += random.choice(greetings) + ' ' + author + '! '
    message += random.choice(convo_starters)
    return message
    
def get_author_name(author):
    if type(author) == discord.Member:
        name = author.nick if author.nick else author.name
        return name
    else:
        return author.name.split(" ")[0]
        
def is_holiday():
    day = datetime.date.today().day
    month = datetime.date.today().month
    for holiday in holidays:
        date = holiday.split('-')
        if int(date[0]) == day and int(date[1]) == month:
            return True
    return False
    
def set_daily_color():
    global daily_color
    daily_color = random.choice(colors)
    
def is_in_string_as_whole(word, message):
    return True if re.search(r'\b' + word + r'\b', message) else False
    
def is_greeting_in_message(message):
    for greeting in greetings:
        if is_in_string_as_whole(greeting.lower(), message):
            return True
    return False
    
data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data')
colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']
daily_color = ''
set_daily_color()
    
f = open(os.path.join(data_folder, "greetings.json"), "r")
json_greetings = f.read()
greetings = json.loads(json_greetings)
f.close()

f = open(os.path.join(data_folder, "convo_starters.json"), "r")
json_convo_starters = f.read()
convo_starters = json.loads(json_convo_starters)
f.close()
    
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
sched.add_job(set_daily_color, 'cron', hour=0, minute=0, second=0)
sched.start()

client.run(token)

# python D:\Projects\OtherProjects\JanuszBotPython\Janusz.py