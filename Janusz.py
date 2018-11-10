import discord, random, json, os, datetime, re, asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from hangman import Hangman

sched = AsyncIOScheduler()
client = discord.Client()
hangman_games = []

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
    await client.send_message(message.channel, get_personal_greeting(get_person_name(message.author)))
    reply = await client.wait_for_message(timeout=15, author=message.author, channel=message.channel)
    if not reply:
        await client.send_message(message.channel, get_person_name(message.author) + " why do you ignore me? :cry:")
                
async def send_single_name(message):
    await client.send_message(message.channel, get_person_name(message.author))
    reply = await client.wait_for_message(timeout=15, author=message.author, channel=message.channel)
    if not reply:
        await client.send_message(message.channel, get_person_name(message.author) + " was there something you meant to tell me? :thinking:")
         
async def send_single_mention(message):
    await client.send_message(message.channel, message.author.mention)
    reply = await client.wait_for_message(timeout=15, author=message.author, channel=message.channel)
    if not reply:
        await client.send_message(message.channel, message.author.mention + " was there something you meant to tell me? :thinking:")
        
async def send_daily_color(message):
    await client.send_message(message.channel, "The color of the day is " + daily_color + " :rainbow:")

async def send_roll_dice(message):
    if random.randint(0, 100) == 77:
        await client.send_message(message.channel, ":scream_cat: Oh no! (void)dice :scream_cat:")
    else:
        await client.send_message(message.channel, "A :game_die: was cast by " + get_person_name(message.author) + " and the result was " + str(random.choice([1,2,3,4,5,6])))
    
async def send_random_member(message):
    if message.channel.type == discord.ChannelType.private:
        if len(message.channel.recipients) == 1:
            await client.send_message(message.channel, "Wait what...! I thought it was just you and me here! :scream:")
        else:
            await client.send_message(message.channel, get_person_name(random.choice(message.channel.recipients)) + ", I choose you!")
    else:
        if len(message.channel.server.members) == 2:
            await client.send_message(message.channel, "Wait what...! I thought it was just you and me here! :scream:")
        else:
            members = []
            for member in message.channel.server.members:
                if member.bot:
                    continue
                members.append(member)
            await client.send_message(message.channel, get_person_name(random.choice(members)) + ", I choose you!")
    
async def process_message(message):
    msg = message.clean_content.lower()
    
    if get_hangman_game(message.channel):
        if len(msg) == 1:
            if msg.isalpha():
                await update_hangman_state(message, msg)
            else:
                await client.send_message(message.channel, get_person_name(message.author) + " this isn't a letter! :rolling_eyes:")
            
    if 'janusz' in msg:
        if 'janusz' == msg:
            await send_single_name(message)
        elif '@janusz' == msg:
            await send_single_mention(message)
        elif is_in_string_as_whole('play', msg) and not get_active_game(message.channel):
            if is_in_string_as_whole('hangman', msg):
                await start_hangman(message)
        elif is_in_string_as_whole('color', msg):
            await send_daily_color(message)
        elif (is_in_string_as_whole('roll', msg) or is_in_string_as_whole('cast', msg)) and is_in_string_as_whole('dice', msg):
            await send_roll_dice(message)
        elif (is_in_string_as_whole('pick', msg) or is_in_string_as_whole('choose', msg) or is_in_string_as_whole('random', msg)) and is_in_string_as_whole('member', msg):
            await send_random_member(message)
        elif is_in_string_as_whole('tip', msg) or is_in_string_as_whole('help', msg):
            await client.send_message(message.channel, random.choice(tips))
        elif is_in_string_as_whole('joke', msg):
            await client.send_message(message.channel, random.choice(jokes))
        elif is_greeting_in_message(msg):
            await send_greet_user(message)
        else:
            if is_in_string_as_whole('play', msg) and get_active_game(message.channel):
                await client.send_message(message.channel, "Sorry " + get_person_name(message.author) + ", there is already an active game in this channel. :call_me:")
            else:
                await client.send_message(message.channel, "Sorry " + get_person_name(message.author) + ", I didn't quite catch that :confused:\nFeel free to ask me for a tip anytime :hugging:")
           
async def start_hangman(message):
    game = Hangman(random.choice(wordlist), message.channel)
    hangman_games.append(game)
    await client.send_message(game.channel, Hangman.rules)
    await client.send_message(game.channel, game.get_life_drawing() + "\n" + game.get_solved())
           
async def update_hangman_state(message, char):
    game = get_hangman_game(message.channel)
    result = game.update(char)
    if result:
        await client.send_message(message.channel, result[0].replace(game.author_sign(), get_person_name(message.author)))
        if result[1]:
            if result[1] == "Lose":
                dead_msg = await client.send_message(message.channel, Hangman.dead)
                await asyncio.sleep(0.1)
                await client.edit_message(dead_msg, Hangman.dead_left)
                await asyncio.sleep(0.1)
                await client.edit_message(dead_msg, Hangman.dead)
                await asyncio.sleep(0.1)
                await client.edit_message(dead_msg, Hangman.dead_right)
                await asyncio.sleep(0.1)
                await client.edit_message(dead_msg, Hangman.dead)
            hangman_games.remove(game)
    
def get_active_game(channel):
    return get_hangman_game(channel)

def get_hangman_game(channel):
    for game in hangman_games:
        if game.get_channel() == channel:
            return game
    return False
           
def get_personal_greeting(author):
    message = ''
    message += random.choice(greetings) + ' ' + author + '! '
    message += random.choice(convo_starters)
    return message
    
def get_person_name(person):
    if type(person) == discord.Member:
        name = person.nick if person.nick else person.name
        return name
    else:
        return person.name.split(" ")[0]
        
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
    
def load_json_file_from_data(filename):
    f = open(os.path.join(data_folder, filename + ".json"), "r")
    json_contents = f.read()
    data = json.loads(json_contents)
    f.close()
    return data

data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Data')
colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']
daily_color = ''
set_daily_color()
    
greetings = load_json_file_from_data("greetings")
convo_starters = load_json_file_from_data("convo_starters")
announcements = load_json_file_from_data("announcements")
holidays = load_json_file_from_data("holidays")
tips = load_json_file_from_data("tips")
jokes = load_json_file_from_data("jokes")
wordlist = load_json_file_from_data("wordlist")

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