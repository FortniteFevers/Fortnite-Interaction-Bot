import discord
from discord.ext.commands.core import guild_only
intents = discord.Intents.default()
from discord.ext import commands, tasks

from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from discord.ext.commands import bot
import json
import requests

testing_guilds = [926178688247140383]

client = commands.Bot(command_prefix='............', intents=intents)
client.remove_command('help')
slash = SlashCommand(client, sync_commands = True)

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="/help"))
    print("\nServers: " + str(len(client.guilds)))
    print("Bot is ready")

@slash.slash(name='login', description='Log into your Epic Games account.', options=[
    create_option(
        name='auth',
        description='32-character Auth Code',
        option_type=3,
        required=False
    )
])
async def login(ctx, auth:str = None):
    if auth is None:
        embed = discord.Embed(
            color = discord.Colour.blue(),
            title='Login to your Epic Games account',
            description='[CLICK ME TO GET YOUR AUTH CODE](https://www.epicgames.com/id/api/redirect?clientId=3446cd72694c4a4485d81b77adbb2141&responseType=code)\n\nHow to login to your Epic Games account:\n\n1. Visit the link above to get your login code.\n2. Copy the 32 character code that looks like **aabbccddeeff11223344556677889900**, located after **authorizationCode=**.\n3. Send /login <32 character code> to complete your login.'
        )
        embed.set_footer(text='We recommend that you only log into accounts that you have email access to!')

        await ctx.send(embed=embed)
    else:
        response = requests.post('https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token', headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"basic MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE="
        },
        data={
            "grant_type": "authorization_code",
            "code": auth
        }
        )
        try:
            token = response.json()['access_token']
        except:
            embed = discord.Embed(
                color = discord.Colour.red(),
                title='ERROR',
                description='Invalid access token was entered.'
            )
            return await ctx.send(embed=embed)
        accountID = response.json()['account_id']

        #await ctx.send(f"Generated auth token. Expires at {response.json()['expires_at']}")
        await ctx.author.send(f"Auth Token: {token}\nExpires at {response.json()['expires_at']}")

        a_file = open(f"auths.json", "r")
        json_object = json.load(a_file)
        a_file.close()

        DiscordauthorID = ctx.author.id
        
        list_ = []
        for i in json_object['auths']:
            list_.append(f'{accountID}')
        
        authornum = list_.count(accountID)
        if authornum == 0:
            await ctx.author.send('Thank you for using our bot for the first time. You are now added into our system.')
            json_object['auths'].append({
                "DiscordauthorID": f"{DiscordauthorID}",
                "token": f"{token}",
                "authCode": f'{auth}',
                "accountID": f"{accountID}",
                "accountUsername": ""
            })
        else:
            json_object['token'] = str(token)
            for i in json_object['auths']:
                if i['DiscordauthorID'] == str(DiscordauthorID):
                    print('Found client :)')
                    i['token'] = token

        a_file = open(f"auths.json", "w")
        json.dump(json_object, a_file, indent = 4)

        headerslmao = {'Authorization': '60bcad5e-fe7c-4734-92a9-986b81f99444'}
        
        response = requests.get(f'https://fortnite-api.com/v2/stats/br/v2/{accountID}', headers=headerslmao)
        clientUsername = response.json()['data']['account']['name']
        for i in json_object['auths']:
            if i['DiscordauthorID'] == str(DiscordauthorID):
                i['accountUsername'] = clientUsername

        response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/QueryProfile?profileId=athena',  json={"text": {}}, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        )
        
        #print(response.json())
        created = response.json()['profileChanges'][0]['profile']['created']
        updated = response.json()['profileChanges'][0]['profile']['updated']

        embed = discord.Embed(
            color = discord.Colour.red(),
            title=f'Welcome, {clientUsername}!'
        )
        embed.add_field(name='Account ID', value=f'{accountID}')
        embed.add_field(name='Created at', value=created)
        embed.add_field(name='Last updated', value=updated)

        lockerdata = response.json()['profileChanges'][0]['profile']['items']['83dbbcea-d579-45b4-bfa7-24c19bc6d9fc']['attributes']['locker_slots_data']['slots']
        lockerskinID = lockerdata['Character']['items'][0]
        lockerskinID = lockerskinID.replace('AthenaCharacter:', '')
        response = requests.get(f'https://fortnite-api.com/v2/cosmetics/br/search?id={lockerskinID}')
        url = response.json()['data']['images']['icon']
        embed.set_thumbnail(url=url)
    
        #profileChanges[0].profile.items["b085ba91-2bdb-43c8-9a1a-01949ca040f9"]
        await ctx.send(embed=embed)

def authenticate():
    a_file = open(f"auths.json", "r")
    json_object = json.load(a_file)
    a_file.close()

@slash.slash(name='showlocker', description='Shows the skins in your Fortnite locker', guild_ids=testing_guilds)
async def showlocker(ctx):
    print('nrij')
    a_file = open(f"auths.json", "r")
    json_object = json.load(a_file)
    a_file.close()

    DiscordauthorID = ctx.author.id

    for i in json_object['auths']:
        if i['DiscordauthorID'] == str(DiscordauthorID):
            token = i['token']
            accountID = i['accountID']
            response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/QueryProfile?profileId=athena',  json={"text": {}}, headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
            )
            #print(response.json())
            try:
                error = response.json()['errorMessage']
                embed = discord.Embed(
                    color = discord.Colour.red(),
                    title='ERROR',
                    description='Your token has most likely expired! Type /login <auth> to generate a new one.'
                )
                return await ctx.send(embed=embed)
            except:
                lockerdata = response.json()['profileChanges'][0]['profile']['items']['83dbbcea-d579-45b4-bfa7-24c19bc6d9fc']['attributes']['locker_slots_data']['slots']

                embed = discord.Embed(
                    title='Your locker'
                )
                await ctx.send('Sucesfully got into the API!')

client.run('OTI5Nzk4NTQ5NTQ0MjQzMjMw.YdskYQ.aCfwzLhE8XTcyOidJ767fgLjcW4')