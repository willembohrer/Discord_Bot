from __future__ import print_function
import re
import os
import six
import json
import time
import ffmpeg
import random
import discord
import spotipy
import requests
import linecache
import youtube_dl
import cloudmersive_image_api_client
from enum import Enum
from discord import Intents
from discord.utils import get
from youtube_dl import YoutubeDL
from pprint import PrettyPrinter
from discord.ext import commands
from discord import FFmpegPCMAudio
from datetime import datetime, timedelta, date
from spotipy.oauth2 import SpotifyClientCredentials
from google.cloud import translate_v2 as TextTranslation
from cloudmersive_image_api_client.rest import ApiException

spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
bot = commands.Bot(command_prefix = commands.when_mentioned_or('!'), guild_subscriptions = True, intents = Intents.all())
Doost_Token = os.getenv('Doost_Token')
Image_AI_API_Key = os.getenv('Image_AI_API_Key')

# Globals.
COUNTER = 0
MESSAGE_COUNT = 0
CHAMBER = [False] * 6
CHAMBER[random.randint(0,5)] = True
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FILE_BASE = ROOT_DIR + '\\Sources\\Files\\'
MUSIC_BASE = ROOT_DIR + '\\Sources\\Music\\'
GOOGLE_APPLICATION_CREDENTIALS = FILE_BASE + 'Doost Translator-6ad539c1e4a1.json'

# Dictionary of User Names and IDs.
users = dict([
    ('Andrew', 130115750785581056), ('Ben', 447186033755553802), ('Dalton', 92085284241444864), ('Evan', 221465946240450563),
    ('David', 144675493336055808), ('Dustin', 256983245705445376), ('Kayla', 144969702119047169), ('Peirce', 668675156557824012),
    ('Willem', 144245969846796288), ('Brad', 144213055041961984), ('Rick', 153362738377261057), ('Dennis', 144216413035298816),
    ('Tyler', 144967149373489162), ('Mike', 589970449866424331), ('Sophi', 612145416036941863), ('Kasey', 98234914746433536),
    ('Arrowgantt', 149712965786927105), ('Bluebuddha007', 155164138006511617), ('Doost Bot', 678020824447320095), ('Jackson', 281241298634145795)
    ])

# Dictionary of useful Minecraft Locations.
minecraft = dict([
    ('Ben\'s Base: -188/65/0', 1), ('Brad\'s Base: 4851/50/380', 2), ('David\'s Base: -1545/69/125', 3),
    ('Tyler\'s Base: -1484/60/-404', 4), ('Willem\'s Base: -1494/63/-185', 5),
    ('Ben\'s Nether Portal (OW): -188/65/0', 6), ('Ben\'s Nether Portal (UW): -1504/65/0', 7), ('Jungle Nether Portal (OW): 3025/63/5120', 8), ('Jungle Portal (UW): 378/63/640', 9),
    ('End Portal (UW): -118/55/200', 10), ('Stronghold Portal (UW): -540/55/-52', 11),
    ('Chat Link: https://www.discordapp.com/channels/230070065511268352/689194125014335607', 12),
    ('Minecraft Atlas: http://mineatlas.com/?levelName=6233283774608044292&seed=6233283774608044292&mapCentreX=3096&mapCentreY=4472&mapZoom=15&pos=&Player=true&Spawn=true&Likely+Villages=false&Ocean+Monuments=false&Jungle+Temples=true&Desert+Temples=false&Witch+Huts=false&Slime+Chunks=false', 13)
    ])

# Dictionary of Channels and IDs.
channels = dict([
    ('Inconspicuous Test Server', 678102033664049166), ('The Wild West', 542515361296285698), ('Bot Spam', 682720294649069568),
    ('Kick', 708583511392780338), ('Horny Jail', 782458247352156190), ('Peepo Chat', 721882866858066021)
    ])

# Roulette functions.
def newChamber():
    CHAMBER = [False]*6
    CHAMBER[random.randint(0,5)] = True
    return CHAMBER

# Gets Name from User Dictionary
def get_Key(user_id):
    for key, value in users.items():
         if user_id == value:
             return key

# Function definitions for the detection of Authors:
def is_me(message):
    return message.author == bot.user
def is_Command(message):
    return message.content.startswith('!')
def getRandMember():
    members = message.guild.members
    return random.choice(members)
def is_Sender(message):
    return message.author.id == users.get(get_Key(message.author.id))
def is_author(message):
    return message.author == message.author

async def kick(ctx, member : discord.Member, reason = None):
    await member.kick(reason = reason)
    return
async def ban(ctx, member : discord.Member, reason = None):
    await member.ban(reason = reason)
    return
async def deletecommand(ctx):
    deleted = await ctx.channel.purge(limit = 5, check = is_Command)
    return
async def connectmessage(ctx):
    await ctx.channel.send('{}, connect to a voice channel to use this command.'.format(ctx.message.author.mention))
    return
async def soundplayingmessage(ctx):
    await ctx.channel.send('{}, Doost is currently playing something.'.format(ctx.message.author.mention))
    return
async def exceptionprint(exception):
    print('Fun Facts:')
    print(exception)
    return

# Message to Terminal to let you know Doost is running.
@bot.event
async def on_ready():
    print('Doost Bot Logged in as: {0.user}'.format(bot))

@bot.command(pass_context = True, help = "Stops Doost.")
async def stop(ctx):
    await deletecommand(ctx)
    await bot.logout()
    await bot.cleanup()
    await bot.disconnect()
    return

@bot.command(pass_context = True, help = "REALLY Stops Doost.")
async def hardstop(ctx):
    await deletecommand(ctx)
    await bot.logout()
    await bot.close()
    await bot.cleanup()
    await bot.disconnect()
    return

@bot.command(pass_context = True, help = "Prompts Doost to join your current Voice Channel.")
async def join(ctx):
    try:
        channel = ctx.message.author.voice.channel
        voice_client = await channel.connect()
        await deletecommand(ctx)
        return
    except Exception as exception:
        print(exception)
        await deletecommand(ctx)
        await exceptionprint(exception)
        await connectmessage(ctx)
        return

@bot.command(pass_context = True, help = "Prompts Doost to leave your current Voice Channel.")
async def leave(ctx):
    try:
        await ctx.voice_client.disconnect()
        await deletecommand(ctx)
        return
    except Exception as exception:
        await exceptionprint(exception)
        await deletecommand(ctx)
        await connectmessage(ctx)
        return

@bot.command(pass_context = True, help = "Prompts Doost to translate the given text to the specified language code.")
async def translate(ctx, target):
    translate_client = TextTranslation.Client()
    message = ctx.message.content
    message = message[13:]
    languages = translate_client.get_languages()
    if isinstance(message, six.binary_type):
        message = message.decode("utf-8")
    languageList = []
    for lang in languages:
        languageList.append(lang.get('language'))
    if target in languageList:
        result = translate_client.translate(message, target_language=target)
        await ctx.send(u"Text translation to {} from {}:\n{}".format(target, result["detectedSourceLanguage"], result["translatedText"]))

# API call to get Zalcano Hiscore from Runescsape
@bot.command(pass_context = True, help = "Sends Willem's Zalcano Hiscore record to chat.")
async def zalcano(ctx):
    URL = "https://secure.runescape.com/m=hiscore_oldschool_ironman/index_lite.ws?"
    searchParameter = "GertrudeSimp"
    PARAMS = {"player": searchParameter}
    response = (requests.get(url = URL, params = PARAMS)).text
    file = open("{}runescapeHiscore.txt".format(FILE_BASE),"w")
    file.write(response)
    file.close()
    file = open("{}runescapeHiscore.txt".format(FILE_BASE),"r")
    zalcano = file.readlines()
    file.close()
    zalcano = (zalcano[78]).split(',')
    start = date(2020, 11, 23)
    end = date(2021, 1, 29)
    delta = (end - start)
    days = (int(zalcano[1].strip('\n'))/delta.days)
    chance = round(((1-((2249/2250)**int(zalcano[1].strip('\n'))))*100), 3)
    await ctx.send("Player: {}\nRank: {} with {} KC\nAvg. KC/Day: {}\nChance of Smolcano: {}%\nStart date: {}\nEnd date: {}".format(searchParameter, zalcano[0], zalcano[1].strip('\n'), round(days), chance, start, end))
    await deletecommand(ctx)

@bot.command(pass_context = True, help = "Prompts Doost to send you a message containing all languages they can translate from/to.")
async def languages(ctx):
    translate_client = TextTranslation.Client()
    languages = translate_client.get_languages()
    languageList = []
    for language in languages:
        languageList.append(u"{name} ({language})".format(**language))
    await ctx.author.send('\n'.join(map(str, languageList)))

@bot.command(pass_context = True, help = "Prompts Doost to play a youtube video in your current Voice Channel.")
async def youtube(ctx, url):
    await deletecommand(ctx)
    if get(bot.voice_clients, guild = ctx.message.guild) is None:
        await join(ctx)
    YDL_OPTIONS = {'format': 'bestaudio', 'noplaylist':'True'}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    voice_client = get(bot.voice_clients, guild = ctx.message.guild)
    if not voice_client.is_playing():
        with YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
        URL = info['formats'][0]['url']
        voice_client.play(FFmpegPCMAudio(URL, **FFMPEG_OPTIONS))
        voice_client.is_playing()
    else:
        await soundplayingmessage(ctx)
        return

@bot.command(pass_context = True, help = "Plays the sounds of our people.")
async def comrade(ctx):
    try:
        if get(bot.voice_clients, guild = ctx.message.guild) is None:
            channel = ctx.message.author.voice.channel
            voice_client = await channel.connect()
            voice_client.play(discord.FFmpegPCMAudio('{}anthem.mp3'.format(MUSIC_BASE)), after=lambda e: print('"comrade" was called. Errors:', e))
            await deletecommand(ctx)
        else:
            channel = ctx.message.author.voice.channel
            get(bot.voice_clients, guild = ctx.message.guild).play(discord.FFmpegPCMAudio('{}anthem.mp3'.format(MUSIC_BASE)), after=lambda e: print('"comrade" was called. Errors:', e))
            await deletecommand(ctx)
        return
    except AttributeError as exception:
        await deletecommand(ctx)
        await exceptionprint(exception)
        await connectmessage(ctx)
        return
    except Exception as exception:
        await deletecommand(ctx)
        await exceptionprint(exception)
        await soundplayingmessage(ctx)
        return

async def heyman(channel):
    try:
        if get(bot.voice_clients, guild = channel.guild) is None:
            voice_client = await channel.connect()
            voice_client.play(discord.FFmpegPCMAudio('{}heyman.mp3'.format(MUSIC_BASE)), after=lambda e: print('"heyman" was called. Errors:', e))
            time.sleep(3)
            await voice_client.disconnect()
        else:
            voice_client = get(bot.voice_clients, guild = channel.guild)
            voice_client.play(discord.FFmpegPCMAudio('{}heyman.mp3'.format(MUSIC_BASE)), after=lambda e: print('"heyman" was called. Errors:', e))
            time.sleep(3)
        return
    except AttributeError as exception:
        await exceptionprint(exception)
        return
    except Exception as exception:
        await exceptionprint(exception)
        return

@bot.command(pass_context = True, help = "Plays some music to your ears.")
async def pogchamp(ctx):
    try:
        if get(bot.voice_clients, guild = ctx.message.guild) is None:
            channel = ctx.message.author.voice.channel
            await ctx.channel.send(file = discord.File('{}pogchamp.gif'.format(FILE_BASE)))
            voice_client = await channel.connect()
            voice_client.play(discord.FFmpegPCMAudio('{}pogchamp.mp3'.format(MUSIC_BASE)), after=lambda e: print('"pogchamp" was called. Errors:', e))
            await deletecommand(ctx)
            time.sleep(4)
            await leave(ctx)
            await doostdelete(ctx)
        else:
            await ctx.channel.send(file = discord.File('{}pogchamp.gif'.format(FILE_BASE)))
            channel = ctx.message.author.voice.channel
            get(bot.voice_clients, guild = ctx.message.guild).play(discord.FFmpegPCMAudio('{}pogchamp.mp3'.format(MUSIC_BASE)), after=lambda e: print('"pogchamp" was called. Errors:', e))
            await deletecommand(ctx)
            time.sleep(4)
            await leave(ctx)
            await doostdelete(ctx)
        return
    except AttributeError as exception:
        await exceptionprint(exception)
        await deletecommand(ctx)
        await connectmessage(ctx)
        return
    except Exception as exception:
        await exceptionprint(exception)
        await deletecommand(ctx)
        await soundplayingmessage(ctx)
        return

@bot.command(pass_context = True, help = "Alters the mentioned Member's nickname.")
async def nickname(ctx, member: discord.Member, name):
    await member.edit(nick = name)
    return

@bot.command(pass_context = True, help = "Pings mentioned User 10 times that the pizza rolls are dones.")
async def pizzarolls(ctx, member: discord.Member):
    await deletecommand(ctx)
    i = 1
    while i <= 10:
        await member.send('Pizza wowwls awe done')
        i += 1
    return

@bot.command(pass_context = True, help = "Six bullets in the chamber, one will kick.")
async def bang(ctx):
    global CHAMBER
    member = ctx.message.author
    if(True not in CHAMBER):
        CHAMBER = newChamber()
    if(CHAMBER.pop() == True):
        await comrade(ctx)
        await ctx.message.channel.send("{} pulls the trigger...\nBANG!".format(get_Key(ctx.message.author.id)))
        time.sleep(5)
        await ctx.message.author.send(await ctx.message.channel.create_invite(reason=None))
        await kick('Bit the bullet', member)
        await leave(ctx)
        await deletecommand(ctx)
        return
    else:
        print(CHAMBER)
        await ctx.message.channel.send("{} pulls the trigger...\n*click*".format(get_Key(ctx.message.author.id)))
        await deletecommand(ctx)

@bot.command(pass_context = True, help = "Deletes the last 100 of Doost\'s Messages")
async def doostdelete(ctx):
    deleted = await ctx.channel.purge(limit = 100, check = is_me)
    await deletecommand(ctx)
    return

@bot.command(pass_context = True, help = "Deletes the last 1000 messages from the Channel.")
async def nuke(ctx):
    if (ctx.author.id == users.get('Willem') or ctx.author.id == users.get('David')):
        deleted = await ctx.channel.purge(limit = 1000, check = is_author)
        await ctx.channel.send('*Snap*\n{} message(s) have been removed'.format(len(deleted)))
        return

@bot.command(pass_context = True, help = "Deletes last 1000 messages with the \'!\' prefix.")
async def deletecommands(ctx):
    deleted = await ctx.channel.purge(limit = 1000, check = is_Command)
    return

@bot.command(pass_context = True, help = "Sends you a list of Minecraft information.")
async def mine(ctx):
    craftInformation = []
    for item in minecraft:
        craftInformation.append(item)
    await ctx.author.send('\n\n'.join(map(str, craftInformation)))
    await deletecommand(ctx)
    return

@bot.command(pass_context = True, help = "Sends the specified Member to Horny Jail.")
async def bonk(ctx, member: discord.Member):
    try:
        toChannel = bot.get_channel(channels.get('Horny Jail'))
        fromChannel = bot.get_channel(channels.get('Peepo Chat'))
        await member.move_to(toChannel)
        await ctx.channel.send('{} has been sentenced to 5 seconds in Horny Jail.'.format(member.display_name))
        time.sleep(5)
        await member.move_to(fromChannel)
        await ctx.channel.send('{} leaves Horny Jail a little less hot and bothered.'.format(member.display_name))
        await deletecommand(ctx)
        return
    except Exception as exception:
        print(exception)
        await deletecommand(ctx)
        await exceptionprint(exception)
        await ctx.channel.send('{} is not connected to a voice channel and cannot be bonked.'.format(member.display_name))
        return

@bot.command(pass_context = True, help = "Sends you a list of the Server's members.")
async def members(ctx):
    members = ctx.guild.members
    membersList = []
    for member in members:
        membersList.append(member)
    await ctx.author.send('\n\n'.join(map(str, membersList)))
    await deletecommand(ctx)
    return

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None and member.id == users.get('Andrew'):
        await heyman(after.channel)

# Detects when a User updates their Status, Activity, or Roles (returns as enumerator values):
@bot.event
async def on_member_update(before, after):
    today = datetime.now()
    day = today.strftime("%d")
    month = today.strftime("%m")
    # Status change greetings:
    if(before.name == "Bodied" and before.status.name == "offline"):
        if(day == 2 and month == 4):
            await bot.get_channel(channels.get('The Wild West')).send("Happy Birthday, David!")
        else:
            await bot.get_channel(channels.get('Bot Spam')).send("Hello, Senpai David! :3")
        return
    if(before.name == "WillemBohrer" and before.status.name == "offline"):
        if(day == 20 and month == 2):
            await bot.get_channel(channels.get('The Wild West')).send("Birthday Boy is here!! HBD :D")
        else:
            await bot.get_channel(channels.get('Bot Spam')).send("Oh no, Willem is here, everyone act casual")
        return
    if(before.name == "Tyler" and before.status.name == "offline"):
        if (day == 15 and month == 5):
            await bot.get_channel(channels.get('The Wild West')).send("Happy Birthday Tyler!!")
        else:
            await bot.get_channel(channels.get('Bot Spam')).send("Yay! Papa Tyler is online again :3")
        return
    if(before.name == "Beamisx" and before.status.name == "offline"):
        if (day == 7 and month == 2):
            await bot.get_channel(channels.get('The Wild West')).send("Brad is the birthday boy! Have a great day :)")
        else:
            await bot.get_channel(channels.get('Bot Spam')).send("God damn it, Brads here, that's a bummer")
        return
    if(before.name == "Kayla" and before.status.name == "offline"):
        if (day == 8 and month == 2):
            await bot.get_channel(channels.get('The Wild West')).send("An E-Girl Birthday?? In this discord? HBD KAYLA")
        return

# Detects when a User is typing:
@bot.event
async def on_typing(channel, user, when):
    if (channel.id == channels.get('Kick')):
        try:
            message = ''
            await user.send(await bot.get_channel(channels.get('The Wild West')).create_invite(reason=None))
            await kick(message, user)
            await bot.get_channel(channels.get('Kick')).purge(limit = 100, check = None)
            return
        except Exception as exception:
            await exceptionprint(exception)
            await channel.send('{} is an abusive admin.'.format(user.mention))
            await bot.get_channel(channels.get('Kick')).purge(limit = 100, check = None)

# Detects when a Message is sent to a Channel:
@bot.event
async def on_message(message):
    # Split Message into individual words and Print to Terminal.
    messageContent = message.content.lower()
    messageWords = messageContent.split()
    print(messageWords)

    # Doost guesses what is within your image.
    if (len(message.attachments) > 0 and message.channel.id == channels.get('Bot Spam')):
        attachment = message.attachments[0]
        imageURL = attachment.url
        with open('{}picture.jpg'.format(FILE_BASE), 'wb') as handle:
            response = requests.get(imageURL, stream=True)
            if not response.ok:
                print(response)
            for block in response.iter_content(1024):
                if not block:
                    break
                handle.write(block)
        configuration = cloudmersive_image_api_client.Configuration()
        configuration.api_key['Apikey'] = Image_AI_API_Key
        api_instance = cloudmersive_image_api_client.FaceApi(cloudmersive_image_api_client.ApiClient(configuration))
        image_file = '{}picture.jpg'.format(FILE_BASE)
        try:
            pprinter = PrettyPrinter()
            api_response = api_instance.face_detect_age(image_file)
            api_response2 = api_instance.face_detect_gender(image_file)
            print(api_response)
            await message.channel.send(api_response)
            await message.channel.send(api_response2)
            #await message.channel.send('Is that ' + (str(pprinter.pformat(api_response))[str(pprinter.pformat(api_response)).find('description')+15:str(pprinter.pformat(api_response)).find('highconfidence')-7]).lower().strip()+'?')
        except ApiException as e:
            print("Exception when calling RecognizeApi->recognize_describe: %s\n" % e)

    # User-specified User and ammount of Messages to delete.
    if('delete' in messageWords):
        name = get_Key(message.author.id)
        int_list = [int(word) for word in messageWords if word.isdigit()]
        if(len(int_list) == 0):
            return
        messageList = await message.channel.history(limit = 200).flatten()
        length = int_list[0]
        for m in messageList:
            if(name == get_Key(m.author.id) and length >= 0):
                await message.channel.purge(limit = 1, check = is_author)
                length -= 1
        return
    await bot.process_commands(message)

    # Automatically downvotes a specified User's Image Attachment:
    if (message.author.id == users.get('Jackson') and len(message.attachments) > 0):
        file = open("{}downvoteCount.txt".format(FILE_BASE),"r")
        numbers = file.readline()
        downvotes = ''
        for number in numbers:
            downvotes = downvotes + number
        print(downvotes)
        file.close()
        file = open("{}downvoteCount.txt".format(FILE_BASE),"w")
        file.write(str(int(downvotes) + 1).rstrip())
        file.close()
        await message.add_reaction('👎')
        await message.channel.send('{} of Jackson\'s images(s) have been automatically downvoted'.format(downvotes))
        return

# Detects when a Member joins the Server:
@bot.event
async def on_member_join(member):
    role = get(member.guild.roles, name="comrade")
    await member.add_roles(role)
    nickname = get_Key(member.id)
    await member.edit(nick = nickname)
    await bot.get_channel(channels.get('Bot Spam')).send("Welcome to Ram Ranch, {}, lets see how long you make it before being purged".format(member.mention))

# Detects when a User is removed from the Server:
@bot.event
async def on_member_remove(member):
    joined = member.joined_at
    left = datetime.now()
    delta = (left - joined)
    await bot.get_channel(channels.get('Bot Spam')).send("{} has been purged".format(member.name))
    await bot.get_channel(channels.get('Bot Spam')).send("They lasted {} days before being purged".format(delta.days))

# Unique Token for Doost:
bot.run(Doost_Token)
