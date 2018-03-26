# BlueMist
# Python 3.5.2
# Basic Discord Bot for DnD


import discord
from discord.ext import commands
import random
import asyncio
import aiohttp
from bs4 import BeautifulSoup

description = 'Basic DnD bot'
bot = commands.Bot(command_prefix='!', description=description)
# making our own help command
bot.remove_command("help")
bot.server = bot.servers


# =for the dnd server=
BOTTOKEN = 'TOKEN'
GENERAL_CHANNEL = 'HERE'
BOT_OUTPUT_CHANNEL = 'HERE'
GM_LAYER_CHANNEL = 'HERE'

# ================================================= When joining ==================================================
# will post a welcome message in the general channel when someone joins
@bot.event
async def on_member_join(member):
    welcomeMessage = '{0.mention} just joined {1.name}! Welcome!'.format(member, bot.server)
    # will send it to the general channel
    await bot.send_message(discord.Object(id=GENERAL_CHANNEL), welcomeMessage)


# ======================================= based on specific chat sequences ==========================================
# runs when a message is posted in the chat
@bot.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == bot.user:
        return

    elif 'good bot' in message.content.lower():
        msg = 'Thank you.'
        await bot.send_message(message.channel, msg)

    # will allow commands to also run while it checks in this message block
    await bot.process_commands(message)


# ========================================= initialize =======================================================
bot.all_ready = False
bot._is_all_ready = asyncio.Event(loop=bot.loop)
async def wait_until_all_ready():
    """Wait until the entire bot is ready."""
    await bot._is_all_ready.wait()
bot.wait_until_all_ready = wait_until_all_ready


@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    bot.server = bot.servers
    for server in bot.servers:
        bot.server = server
        if bot.all_ready:
            break

        print("Something went wrong and {} had to restart! But I'm back here in {} now!"
              .format(bot.user.name, server.name))
    # sets which game the bot is playing
    await bot.change_presence(game=discord.Game(name='Rolling the Dice'))

# ===================================================================================================================
#
#                                               =HELP=
#
# ===================================================================================================================
@bot.command(pass_context=True)
async def help(ctx):
    say =  '```'\
           '!roll #d# +# > #\n'\
           '!additem \"<item name>, <quantity>, <value>, <desc>\"\n'\
           '!myitems\n'\
           '!lookup <name>\n'\
           '!choose <choice1> <choice2>\n'\
           '!invite'\
           '```'
    await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), say)


# ===================================================================================================================
#
#                                            =ROLLING DICE=
#
# ===================================================================================================================

@bot.command()
async def roll(dice : str, *, add=''):
    try:
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await bot.say('Format has to be in #d#!')
            return

        greaterSet = False
        if add != '':
            try:
                add = add.replace(' ', '')
                ToAdd = add.split('+')
                if '>' in add:
                    greaterThan = add.split('>')
                    greaterThan = int(greaterThan[1])
                    greaterSet = True
                try:
                    ToAdd = ToAdd[1].split('>')
                    ToAdd = int(ToAdd[0])
                except IndexError:
                    ToAdd = 0
                    pass

            except IndexError:
                await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL),
                                       'Format must be: ```!roll <#d#> <+#> ( ># )```')
                return

        else:
            ToAdd = 0

        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        result = result.split(', ')
        list = []
        greaterList = ''
        greaterCount = 0
        lowerList = ''
        rejectedCount = 0
        for value in result:
            value = int(value) + ToAdd
            if greaterSet == True:
                if int(value) < greaterThan:
                    rejectedCount += 1
                    lowerList += (str(value) + ', ')
                    continue
                else:
                    greaterCount += 1
                    greaterList += (str(value) + ', ')
                    continue
            list.append(str(value))
        if greaterSet == True:
            await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), 'Greater({}): {} | Lower({}): {}'
                                   .format(str(greaterCount), greaterList, str(rejectedCount), lowerList))
        else:
            result = ', '.join(list)
            await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), result)
        return

    except Exception:
        await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), 'Format must be: ```!roll <#d#> <+#> ( ># )```')
        return


# ===================================================================================================================
#
#                                            =INVENTORY=
#
# ===================================================================================================================
inventoryList = []
@bot.command(pass_context=True, hidden=True)
async def additem(ctx, *, fullItem=''):
    member = ctx.message.author
    message = ctx.message
    channel = message.channel

    try:
        # ====== deletes the message, RAISES AN EXCEPTION==========
        if fullItem == '':
            await bot.delete_message(ctx.message)
            raise ValueError

        # ======= deletes the message ================
        if str(channel) != 'bot-output':
            await bot.delete_message(ctx.message)

        # ==========if the list is empty, try to repopulate it============
        if not inventoryList:
            print('Inventory memory database is empty, attempting to repopulate.')
            inventoryFile = open('dndPlayerInventory.txt', 'r', encoding='utf-8')
            read = inventoryFile.readlines()
            for thisline in read:
                inventoryList.append(thisline)
            print('Repopulated inventory memory database.\n')

        max = 3
        current = 0
        fullItem = fullItem.replace('\"', '')
        fullItem = fullItem.split(',')

        # for item quantity
        try:
            if int(fullItem[1]) <= 0:
                raise ValueError

        except ValueError:
            await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), 'Value <quantity> must be:'
                                                                            '```Greater than 0```')
            return

        # for item value
        try:
            if int(fullItem[2]) < 0:
                raise ValueError

        except ValueError:
            await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), 'Value <value> must be:'
                                                                            '```0 or greater```')
            return
        # make sure that commas in the description are handled properly and don't act as new value in the list
        for value in fullItem:
            if current > max:
                fullItem[3] = str(fullItem[3]) + ',' + value
                del fullItem[current]
            else:
                current += 1

        # check if the item already exists in the players inventory
        for value in inventoryList:
            if member.name in value:
                if str(fullItem[0]) in value:
                    await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), 'This item is already in your '
                                                                                    'inventory.')
                    return

        inventory = open('dndPlayerInventory.txt', 'a', encoding='utf-8')
        data = member.name + '<|>' + fullItem[0] + '<|>' + fullItem[1] + '<|>' + fullItem[2] + '<|>' + fullItem[3] + '\n'
        inventory.write(data)
        inventory.close()
        inventoryList.append(data)
        await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL),
                               'Added item \"{}\" to {}\'s inventory'.format(fullItem[0], member.nick))
        return

    except Exception:
        await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), 'Please add quotes around the item information '
                                                                        'and separate values with commas in format:\n'
                      '```!additem \"<item name>, <quantity>, <value>, <desc>\"```')
        return


@bot.command(pass_context=True)
async def myitems(ctx):
    member = ctx.message.author
    message = ctx.message
    channel = message.channel

    # ======= deletes the message ================
    if str(channel) != 'bot-output':
        await bot.delete_message(ctx.message)

    # ==========if the list is empty, try to repopulate it============
    if not inventoryList:
        print('Inventory memory database is empty, attempting to repopulate.')
        inventoryFile = open('dndPlayerInventory.txt', 'r', encoding='utf-8')
        read = inventoryFile.readlines()
        for thisline in read:
            inventoryList.append(thisline)
        print('Repopulated inventory memory database.\n')

    say = ''
    for value in inventoryList:
        if member.name in value:
            value = value.split('<|>')
            say += 'item *{}* with amount:{} value:{} and description:{}\n'\
                .format(value[1], value[2], value[3], value[4])

    if say == '':
        await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), '=Inventory Empty=')
    else:
        await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), '```{}```'.format(say))
    return


@commands.has_role('GM')
@bot.command(pass_context=True)
async def allitems(ctx):
    member = ctx.message.author
    message = ctx.message
    channel = message.channel

    # ======= deletes the message ================
    if str(channel) != 'bot-output':
        await bot.delete_message(ctx.message)

    # ==========if the list is empty, try to repopulate it============
    if not inventoryList:
        print('Inventory memory database is empty, attempting to repopulate.')
        inventoryFile = open('dndPlayerInventory.txt', 'r', encoding='utf-8')
        read = inventoryFile.readlines()
        for thisline in read:
            inventoryList.append(thisline)
        print('Repopulated inventory memory database.\n')

    say = ''
    for value in inventoryList:
        value = value.split('<|>')
        say += '{}: item *{}* with amount:{} value:{} and description:{}' \
            .format(value[0], value[1], value[2], value[3], value[4])

    if say == '':
        await bot.send_message(discord.Object(id=GM_LAYER_CHANNEL), '=Inventory Empty=')
    else:
        await bot.send_message(discord.Object(id=GM_LAYER_CHANNEL), '```{}```'.format(say))
    return

# ======================= editing items broken from previous version ===========================

# @bot.command(pass_context=True)
# async def edititems(ctx, use='', *, new=''):
#     member = ctx.message.author
#     message = ctx.message
#     channel = message.channel
#
#     # ======= deletes the message ================
#     if str(channel) != 'bot-output':
#         await bot.delete_message(ctx.message)
#
#     if use == '' or (new == '' and use != 'del'):
#         pass
#
#     # ==========if the list is empty, try to repopulate it============
#     if not inventoryList:
#         print('Inventory memory database is empty, attempting to repopulate.')
#         inventoryFile = open('inventory.txt', 'r', encoding='utf-8')
#         read = inventoryFile.readlines()
#         for thisline in read:
#             inventoryList.append(thisline)
#         print('Repopulated inventory memory database.\n')
#
#
#
#
# @bot.command(pass_context=True)
# async def delitem(ctx, item):
#     try:
#         await bot.delete_message(ctx.message)
#         member = ctx.message.author
#         itemSplit = item.split(',')
#         item = itemSplit[0]
#         quantity = itemSplit[1]
#         if 'all' in quantity:
#             quantity = 'all'
#         else:
#             quantity = int(quantity)
#             if quantity <= 0:
#                 await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), 'Zero and negative numbers cannot be used.')
#                 return
#         tempList = []
#         for player in playerList:
#             if member.nick == player:
#                 inventory = open(member.nick + '_inv.txt', 'r', encoding='utf-8')
#                 inventoryRead = inventory.readlines()
#                 for line in inventoryRead:
#                     if item in line:
#                         lineSplit = line.split(',')
#                         origQuantity = int(lineSplit[1])
#                         if quantity == 'all':
#                             newQuantity = origQuantity - origQuantity
#                         else:
#                             newQuantity = origQuantity - quantity
#                         if newQuantity < 0:
#                             await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), 'You don\'t have this many of that item, you have {}'.format(str(origQuantity)))
#                             return
#                         elif newQuantity == 0:
#                             line = ''
#                         else:
#                             lineSplit[1] = str(quantity)
#                             line = ','.join(lineSplit)
#                         tempList.append(line)
#                         inventory = open(member.nick + '_inv.txt', 'w', encoding='utf-8')
#                         for value in tempList:
#                             inventory.write(value)
#                         inventory.close()
#                         await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), 'Removed {} {} from your inventory.'.format(quantity, item))
#                         return
#                     else:
#                         pass
#                 await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), 'This item is not in your inventory.')
#             else:
#                 pass
#     except Exception:
#         await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), 'Please add quotes around the item information in format:\n'
#                       '!delitem \"<item name>, <quantity/all>\".')
#
#
# @bot.command(pass_context=True, hidden=True)
# async def listcommands(ctx):
#     await bot.delete_message(ctx.message)
#     await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), '```!choose <choice1> <choice2> | !membercount | '
#                                                                     '!roll <#d#> <+#>  | !invite | !joined <name> | '
#                   '!additem \"<item> , <#> , <$> , <desc>\" | !myitems | !delitem arg1```')


# ===================================================================================================================
#
#                                            =COMPENDIUM LOOKUP=
# will find most info on items and such, won't find everything
# ===================================================================================================================
HEADERS = {
    'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/45.0.2454.101 Safari/537.36'),
}

customList = []
@bot.command(pass_context=True)
async def lookup(ctx, *, name):

    async def fetch(session, url):
        async with session.get(url) as response:
            return await response.text()

    async with aiohttp.ClientSession() as session:
        html = await fetch(session, 'https://roll20.net/compendium/dnd5e/{}'.format(name))

    soup = BeautifulSoup(html, 'html.parser')
    title = soup.find("h1", {'class': 'page-title'})
    if title == None:

        if not customList:
            print('dndCustomLookup memory database is empty, attempting to repopulate.')
            customFile = open('dndCustomLookup.txt', 'r', encoding='utf-8')
            read = customFile.readlines()
            for thisline in read:
                customList.append(thisline)
            print('Repopulated dndCustomLookup memory database.\n')

        say = ''
        for value in customList:
            values = value.split('<|>')
            if name in values[0].lower():
                for value in values:
                    say += value + '\n'
                break

        if say == '':
            await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), 'Could not find: `{}`'.format(name))
            return

        await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), '```asciidoc\n' + say + '```')
        return

    title = title.string
    desc = soup.find("div", {'id': 'pagecontent'}).text
    if desc != '':
        desc = '= ' + desc + ' ='
    # for details
    rownames = soup.find_all("div", {'class': 'col-md-3 attrName'})
    rowvalues = soup.find_all("div", {'class': 'value'})

    valueList = []
    id = 0
    for row in rownames:
        if 'Components' in row or 'School' in row or 'Source' in row or 'Category' in row:
            id += 1
            continue
        name = row.text
        value = rowvalues[id].text
        valueList.append(name +': '+value)
        id += 1

    # will only work with items and spells
    if valueList is None:
        await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), 'Could not find: `{}`'.format(name))
        return

    say = '[' + title+ ']' + '\n\n' + '\n'.join(valueList) + '\n\n' + desc
    charmax = 1700
    currentCount = 0
    localCount = 0
    messageLast = True
    currentMessage = ''
    messageList = say.split('\n')
    for line in messageList:
        messageLast = True
        currentCount += len(line)
        localCount += len(line)
        if currentCount > charmax:
            await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), '```asciidoc\n' + say + '```')
            currentMessage = ''
            currentCount = localCount
            messageLast = False
        currentMessage += line + '\n'
        localCount = 0
    if messageLast == True:
        await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), '```asciidoc\n' + say + '```')

    return


@bot.command(pass_context=True, hidden=True)
async def addlookup(ctx, *, fullItem=''):
    member = ctx.message.author
    message = ctx.message
    channel = message.channel

    # ==========if the list is empty, try to repopulate it============
    if not customList:
        print('dndCustomLookup memory database is empty, attempting to repopulate.')
        inventoryFile = open('dndPlayerInventory.txt', 'r', encoding='utf-8')
        read = inventoryFile.readlines()
        for thisline in read:
            inventoryList.append(thisline)
        print('Repopulated dndCustomLookup memory database.\n')

    if fullItem == '':
        await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), 'You must enter at least one value.')
        return

    fullItem = fullItem.split(',')
    newCustom = '<|>'.join(fullItem)
    newCustom = newCustom + '\n'

    inventory = open('dndCustomLookup.txt', 'a', encoding='utf-8')
    inventory.write(newCustom)
    inventory.close()
    customList.append(newCustom)
    await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), 'Custom item added to database.')
    return


# ===================================================================================================================
#
#                                            =EXTRA=
#
# ===================================================================================================================

# ======================================== will randomly pick a string of choices ===============================
@bot.command(description='For when you want to settle a debate')
async def choose(*choices : str):
    """Chooses between multiple choices."""
    await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), 'I declare it to be '+random.choice(choices))


# ================================================ Prints a static invite ========================================
@bot.command()
async def invite():
    await bot.send_message(discord.Object(id=BOT_OUTPUT_CHANNEL), 'Here you go: SOME INVITE')

# ================================================== disconnect =================================================
@bot.command()
async def disconnectbot():
    await bot.logout()


# ===================================================================================================================
#
#                                            =RUNNING THE BOT=
#
# ===================================================================================================================
# runs the bot with its ticket
bot.run(BOTTOKEN)
