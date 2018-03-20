# this is a test instance of Dire Wolf while trying to implement multiple search sources
import discord
import asyncio
import os
import aiohttp
from discord.ext.commands import Bot
from discord.ext import commands
from discord.ext.commands import CommandInvokeError
import platform
import random
from funcs import *

client = Bot(description="Dire Wolf by Marcus#3244", command_prefix=";", pm_help = False)

@client.event
async def on_ready():
    print('Logged in as '+client.user.name+' (ID:'+client.user.id+') | Connected to '+str(len(client.servers))+' servers | Connected to '+str(len(set(client.get_all_members())))+' users')
    print('--------')
    print('Current Discord.py Version: {} | Current Python Version: {}'.format(discord.__version__, platform.python_version()))
    print('--------')
    print('https://discordapp.com/oauth2/authorize?client_id={}&scope=bot&permissions=8'.format(client.user.id))
    print('--------')
    print('Support Discord Server: https://discord.gg/FNNNgqb')
    print('Github Link: https://github.com/Marc5567/dire-wolf')
    print('--------')
    print('You are running Dire Wolf v1.0.1')
    print('Created by Marcus#3244')
    print('--------')
    client.loop.create_task(update_sources_loop())
    return await client.change_presence(game=discord.Game(name='Dungeon World'))

@client.command()
async def hack(*args):
    """Rolls Hack and Slash""" # to be rewritten as move with subcommands for individual moves
    try:
        mod = int(args[0])
    except:
        mod = 0
    try:
        dmgmod = int(args[1])
    except:
        dmgmod = 0
    roll1 = random.randint(1,6)
    roll2 = random.randint(1,6)
    dmg = random.randint(1,10)
    total = (roll1 + roll2 + mod)
    finalresult = "2d6 (%i, %i) + %i = %i" % (roll1, roll2, mod, roll1 + roll2 + mod)
    finaldamage = "1d10 (%i) + %i = %i" % (dmg, dmgmod, dmg + dmgmod)
    result = "On a 10+, you deal your damage to the enemy and avoid their attack. At your option, you may choose to do +1d6 damage but expose yourself to the enemy’s attack." if int(total) >= 10 else "On a 7–9, you deal your damage to the enemy and the enemy makes an attack against you." if 9 >= int(total) >= 7 else "Miss!"
    embed=discord.Embed(title="Hack and Slash", description="*When you attack an enemy in melee, roll+Str.*" "\n\n**Roll:** " + finalresult + "\n**Damage:** " + finaldamage + "\n", color=0xd6d136)
    embed.add_field(name="Results:", value=result, inline=False)
    embed.set_footer(text="Basic Move, 58")
    await client.say(embed=embed)

UPDATE_DELAY = 60 * 60  # update every hour

ITEM_SOURCE = "https://raw.githubusercontent.com/Marc5567/dire-wolf/master/items.txt"
MONSTER_SOURCE = "https://raw.githubusercontent.com/Marc5567/dire-wolf/master/monsters"
ITEM_DIVIDER = "***"  # a string that divides distinct items.
META_LINES = 0  # the number of lines of meta info each item has

items = []
monsters = []

@client.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, CommandInvokeError):
        error = error.original
    await client.send_message(ctx.message.channel, error)


async def update_sources_loop():
    try:
        await client.wait_until_ready()
        while not client.is_closed:
            await update_sources()
            await asyncio.sleep(UPDATE_DELAY)
    except asyncio.CancelledError:
        pass


async def update_sources():
    ITEM_SOURCE = "https://raw.githubusercontent.com/Marc5567/dire-wolf/master/items.txt"
    MONSTER_SOURCE = "https://raw.githubusercontent.com/Marc5567/dire-wolf/master/monsters"
    async with aiohttp.ClientSession() as session:
        async with session.get(ITEM_SOURCE) as resp:
            print(ITEM_SOURCE)
            text = await resp.text()
            if 399 < resp.status < 600:  # 4xx, 5xx errors
                raise Exception(f"Failed to update items: {text}")

            raw_items = [t.strip() for t in text.split(ITEM_DIVIDER)]  # filter out index

            for item in raw_items:
                lines = item.split('\n')
                name = lines[0].strip('### ')
                meta = '\n'.join(lines[1::])
                desc = '\n'.join(lines)

                items.append({'name': name, 'meta': meta, 'desc': desc})
                print(f"Indexed item {name}.")

            print("Updated items!")

    async with aiohttp.ClientSession() as session:
        async with session.get(MONSTER_SOURCE) as resp:
            print(MONSTER_SOURCE)
            text = await resp.text()
            if 399 < resp.status < 600:  # 4xx, 5xx errors
                raise Exception(f"Failed to update monsters: {text}")

            raw_monsters = [t.strip() for t in text.split(ITEM_DIVIDER)]  # filter out index

            for monster in raw_monsters:
                lines = monster.split('\n')
                name = lines[0].strip('### ')
                meta = '\n'.join(lines[1::])
                desc = '\n'.join(lines)

                monsters.append({'name': name, 'meta': meta, 'desc': desc})
                print(f"Indexed monster {name}.")

            print("Updated monsters!")

@client.command(pass_context=True)
async def item(ctx, *, name=''):
    """Looks up a Dungeon World item."""
    result = search(items, 'name', name)
    if result is None:
        return await client.say('Item not found.')
    strict = result[1]
    results = result[0]
    if strict:
        result = results
    else:
        if len(results) == 1:
            result = results[0]
        else:
            result = await get_selection(ctx, [(r['name'], r) for r in results])
            if result is None: return await client.say('Selection timed out or was cancelled.')
    embed = EmbedWithAuthor(ctx)
    embed.title = result['name']
    meta = result['meta']
    meta2 = [meta[i:i + 1024] for i in range(2048, len(meta), 1024)]
    embed.description = meta[0:2048]
    for piece in meta2:
        embed.add_field(name="\u200b", value=piece)
    await client.say(embed=embed)

@client.command(pass_context=True)
async def monster(ctx, *, name=''):
    """Looks up a Dungeon World monster."""
    result = search(monsters, 'name', name)
    if result is None:
        return await client.say('Monster not found.')
    strict = result[1]
    results = result[0]
    if strict:
        result = results
    else:
        if len(results) == 1:
            result = results[0]
        else:
            result = await get_selection(ctx, [(r['name'], r) for r in results])
            if result is None: return await client.say('Selection timed out or was cancelled.')
    embed = EmbedWithAuthor(ctx)
    embed.title = result['name']
    meta = result['meta']
    meta2 = [meta[i:i + 1024] for i in range(2048, len(meta), 1024)]
    embed.description = meta[0:2048]
    for piece in meta2:
        embed.add_field(name="\u200b", value=piece)
    await client.say(embed=embed)

client.run('NDIwMDkxNDE2Mzc1NDU5ODcw.DX5p3A.s7Qla8wABEvNhaHP-AO2gvV3UKE')

# Please join this Discord server if you need help: https://discord.gg/FNNNgqb
# The help command is currently set to be not be Direct Messaged.
# If you would like to change that, change "pm_help = False" to "pm_help = True" on line 9.
