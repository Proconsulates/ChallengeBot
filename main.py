import aiohttp
import random
import discord
from dotenv import load_dotenv
import os
import json
from discord import user, user
import requests
from discord.ext import commands
import time
from operator import index
load_dotenv()

TOKEN = os.getenv("TOKEN")

client = discord.Client()

def addXP(user, amt):
    index = userExists(user.encode('unicode-escape').decode('utf8'))
    if index:
        content = ""
        with open("xp.json", 'r') as f:
            content = json.load(f)
        with open("xp.json", 'w') as f:
            content[index - 1]['xp'] += amt
            json.dump(content, f)
    else:
        content = ""
        with open("xp.json", 'r') as f:
            content = json.load(f)
            f.close()
        with open("xp.json", 'w') as f:
            content.append({
                "name": user.encode('unicode-escape').decode('utf8'),
                "xp": amt
            })
            f.write(json.dumps(content))  

def userExists(username):
    exists = False
    index = 0
    with open("xp.json", 'r') as f:
        res = json.load(f)
        for i in range(0, len(res), 1):
            if res[i]['name'] == username:
                exists = True
                index = i
                break
            print(res[i]['name'], username)
    if exists:
        return index + 1
    else: return False

#gets memes
def get_meme():
        img_response = requests.get("https://meme-api.herokuapp.com/gimme")
        img_json = json.loads(img_response.text)
        return {'image': img_json['preview'][1],
            'author': img_json['author']}

#returns quotes
def get_quote():
    quote_response = requests.get("https://zenquotes.io/api/random")
    quote_json = json.loads(quote_response.text)
    quote = quote_json[0]['q'] + " -" + quote_json[0]['a']
    return quote

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game('$help'))
    print("ChallengeBot is ready!")

@client.event
async def on_message(message):

    if message.content == "$help":
        embed = discord.Embed(title="ChallengeBot", description="{} = optional \n<> = mandatory", color=discord.Color.blue())
        embed.add_field(name="$help", value="Returns this message.", inline=False)
        embed.add_field(name="$showXP {user}", value="Shows a leaderboard from highest to lowest of all the people who have XP. If you have a user after it then it shows the XP of that user.")
        embed.add_field(name="$challenge", value="Posts a random coding challenge from r/dailyprogrammer.", inline=False)
        embed.add_field(name="$addXP <quantity> <user>", value="Adds a specific amount of XP to a user for completing a programming challenge.", inline=False)
        embed.add_field(name="$more", value="Returns another embed filled with random things this bot can do.")
        embed.set_footer(text="Bot created by Proconsulates#7263 and ✨ TeaKe_smAL ✨#4826 \nDM Proconsulates if you wish to use this bot in your server")
        await message.channel.send(embed=embed)
    
    if message.content == "$more":
        embed = discord.Embed(color=discord.Color.blue())
        embed.add_field(name="$meme", value="Returns a random meme.", inline=False)
        embed.add_field(name="$quote", value="Returns a random quote.", inline=False)
        embed.add_field(name="$rickroll {user}", value="Returns a gif with Rick Astley, but if you input user than it rickrolls that user by DM.", inline=False)
        embed.add_field(name="$flip {user}", value="Returns either **Heads** or **Tails**", inline=False)
        embed.add_field(name="$showerthought", value="Returns a random showerthought from reddit.", inline=False)
        embed.add_field(name="$8ball {question}", value="Returns an answer for your question", inline=False)
        embed.add_field(name="$trivia", value="Test your mind to have a chance to win 10 XP for each correct answer", inline=False)
        await message.channel.send(embed=embed)

    if message.content == "$challenge":
        try:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://www.reddit.com/r/dailyprogrammer.json') as r:
                    res = await r.json()
                    embed = discord.Embed(title="ChallengeBot's challenge", description="Your challenge:")
                    challenges = res['data']['children']
                    valid_challenges = []
                    for i in range(0, len(challenges), 1):
                        if len(challenges[i]['data']['selftext']) < 1024:
                            valid_challenges.append(challenges[i]['data']['selftext'])
                    if len(valid_challenges) == 0:
                        embed.add_field(name="Something went wrong", value="Unable to fetch a challenge.", color=discord.Color.blue())
                    else:
                        embed.add_field(name="-----------------------", value=random.choice(valid_challenges))
                    await message.channel.send(embed=embed)
        except:
            await message.channel.send('Sorry, this isn"t working at the moment. YOu could manually get some coding challenges from here though: https://edabit.com/challenges#!')

    if message.content.startswith("$addXP "):
        if message.author.guild_permissions.administrator:
            user = message.mentions[0].name
            c = message.content
            amt = c[7:c.find(" ", 7, len(c))]
            addXP(user, int(amt))
            await message.channel.send('Successfully given ' + amt + 'XP to ' + user + '!')
        else:
            await message.channel.send('Sorry,' + message.author.mention + ' but you don\'t have the permissions to do that!')

    if message.content == "$showXP":
        with open('xp.json', "r") as f:
            users = ""
            for i in sorted(json.load(f), key=lambda k: k["xp"], reverse=True):
                users += f'{i.get("name")} - {str(i.get("xp"))}\n'
            embed = discord.Embed(title=" ", description=users, color=discord.Color.blue())
            await message.channel.send(embed=embed)

    if message.content.startswith("$showXP "):
        user = message.mentions[0].name.encode('unicode-escape').decode('utf-8')
        ux = userExists(user)
        xp = 0
        if ux:
            with open("xp.json", 'r') as f:
                res = json.load(f)
                xp = str(res[ux-1]["xp"])
            embed = discord.Embed(title=" ", description=f"{user} - {xp}", color=discord.Color.blue())
            await message.channel.send(embed=embed)
        else:
            await message.channel.send(f"{user} has 0XP.")

    if message.content.startswith("$quote"):
        quote = get_quote()
        embed = discord.Embed(title=" ", description=quote, color=discord.Color.blue())
        await message.channel.send(embed=embed)

    if message.content.startswith("$meme"):
        try:
            meme = get_meme()['image']
            embed = discord.Embed(title="Memes", color=discord.Color.blue())
            embed.set_image(url=meme)
            embed.set_footer(text="Requested by " + message.author.display_name)
            await message.channel.send(embed=embed)
        except IndexError:
            await message.channel.send('Sorry, try again!')

    if message.content == "$rickroll":
        embed = discord.Embed(title="Get rickrolled!", description=" ", color=discord.Color.blue())
        embed.set_image(url="https://c.tenor.com/d5NnbMG_hh8AAAAM/funnymeme.gif")
        await message.channel.send(embed=embed)
    elif message.content.startswith("$rickroll"):
        dude = message.mentions[0]
        if "VIP" or "moderator" in map(lambda role: role.name, message.author.roles):
            embed = discord.Embed(title="Get rickrolled!", description=" ", color=discord.Color.blue())
            embed.set_image(url="https://c.tenor.com/d5NnbMG_hh8AAAAM/funnymeme.gif")
            embed.set_footer(text="You have been rickrolled by " + message.author.display_name + ". \nUse the command `$rickroll {user}` to get \nthem back!")
            await dude.send(embed=embed)
            await message.channel.send('Successfully rickrolled `' + dude.display_name + '`.')
        else: 
            await message.channel.send("Sorry, you don't have the appropiate roles to do that! You need VIP role or any role with admin capabilities.")

    if message.content == ("$flip"):
        l = ["Heads", "Tails"]
        flip = discord.Embed(title="Flipping!", description="The coin is in the air and flipping...", color=0x3d8bff)
        flip.set_image(url="https://media.tenor.com/images/24dfe486a993882ff8a08e025fb3b755/tenor.gif")
        await message.channel.send(embed=flip)
        time.sleep(3)
        await message.channel.send("It's **" + random.choice(l) + "**")
    elif message.content.startswith("$flip"):
        person = message.mentions[0]
        e = discord.Embed(title="Flipping against " + person.display_name + ".", description="The coin is in the air and flipping...", color=0x3d8bff)
        e.set_image(url="https://media.tenor.com/images/24dfe486a993882ff8a08e025fb3b755/tenor.gif")
        await message.channel.send(embed=e)
        time.sleep(3)
        n = random.randint(1,2)
        if n == 1:
            await message.channel.send(message.author.mention + " got **Heads** and " + person.mention + " got **Tails**.")
        elif n == 2:
            await message.channel.send(message.author.mention + "got **Tails** and " + person.mention + " got **Heads**.")

    if message.content == "$showerthought":
        try:
            embed = discord.Embed(colour=discord.Colour.blue())
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://www.reddit.com/r/showerthoughts.json') as r:
                    res = await r.json()
                    embed.add_field(name="""Here's a showerthought\n‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎‏‏‎ ‎""", value=res['data']['children'] [random.randint(0, 25)]['data']['title'])
                    await message.channel.send(embed=embed)
        except:
            await message.channel.send('Sorry, this isn"t working at the moment. Try again later!')

    if message.content.startswith('$8ball'):
        responses = ["It is certain.", "It is decidedly so.", "Without a doubt.", "Yes - definitely.", "You may rely on it.", "As I see it, yes.","Most likely.", "Outlook good.", "Yes.", "Signs point to yes.", "Reply hazy, try again.", "Ask again later.", "Better not tell you now.", "Cannot predict now.", "Concentrate and ask again.", "Don't count on it.", "My reply is no.", "My sources say no.", "Outlook not so good.", "Very doubtful."]
        embed = discord.Embed(title="Answer:", description=random.choice(responses), color=discord.Color.blue())
        await message.channel.send(embed=embed)

    if message.content.startswith('$trivia'):
        embed = discord.Embed(colour=discord.Colour.blue())
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://trivia-api.aroary.repl.co') as r:
                res = await r.json()
                embed.add_field(name="Trivia", value=f"{res['question']}")
                await message.channel.send(embed=embed)
                def check(m):
                    return m.author == message.author and m.channel == message.channel
                response = await client.wait_for('message', check=check)
                if response.content.lower() in res['answer'].lower():
                    if len(str(response.content)) == 1:
                        await message.channel.send('Don\'t cheat!')
                    else:
                        addXP(message.author.name, 10)
                        await message.channel.send('Correct! +10XP')
                        print('Correct')
                else:
                    await message.channel.send('Incorrect!')
                    print(res['answer'] + '. You got it wrong.')
client.run(TOKEN)