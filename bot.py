import discord
from discord.ext.commands.core import guild_only
intents = discord.Intents.default()
from discord.ext import commands, tasks

from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from discord.ext.commands import bot
import json
import requests

testing_guilds = []

client = commands.Bot(command_prefix='............', intents=intents)
client.remove_command('help')
slash = SlashCommand(client, sync_commands = True)

headerslmao = {'Authorization': AUTH_TOKEN}

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
            description='[CLICK ME TO GET YOUR AUTH CODE](https://www.epicgames.com/id/login?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Fapi%2Fredirect%3FclientId%3Dec684b8c687f479fadea3cb2ad83f5c6%26responseType%3Dcode)\n\nHow to login to your Epic Games account:\n\n1. Visit the link above to get your login code.\n2. Copy the 32 character code that looks like **aabbccddeeff11223344556677889900**, located after **authorizationCode=**.\n3. Send /login <32 character code> to complete your login.\n\n**Need to switch accounts?**\n[Use this link instead](https://www.epicgames.com/id/login?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Fapi%2Fredirect%3FclientId%3D3f69e56c7649492c8cc29f1af08a8a12%26responseType%3Dcode&prompt=login)'
        )
        embed.set_footer(text='We recommend that you only log into accounts that you have email access to!')

        await ctx.send(embed=embed)
    else:
        response = requests.post('https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token', headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"basic ZWM2ODRiOGM2ODdmNDc5ZmFkZWEzY2IyYWQ4M2Y1YzY6ZTFmMzFjMjExZjI4NDEzMTg2MjYyZDM3YTEzZmM4NGQ="
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
        await ctx.author.send(f"I have just generated a new token for you.\nThis token Expires at {response.json()['expires_at']}")

        a_file = open(f"auths.json", "r")
        json_object = json.load(a_file)
        a_file.close()

        DiscordauthorID = ctx.author.id
        
        list_ = []
        for i in json_object['auths']:
            accountidlol = i['accountID']
            list_.append(f'{accountidlol}')
        
        authornum = list_.count(accountID)
        if authornum == 0:
            await ctx.author.send('Thank you for using our bot for the first time. You are now added into our system.')
            json_object['auths'].append({
                "DiscordauthorID": f"{DiscordauthorID}",
                "token": f"{token}",
                "authCode": f'{auth}',
                "accountID": f"{accountID}",
                "loadoutUUID": ""
            })
            a_file = open(f"auths.json", "w")
            json.dump(json_object, a_file, indent = 4)
        else:
            json_object['token'] = str(token)
            for i in json_object['auths']:
                if i['DiscordauthorID'] == str(DiscordauthorID):
                    print('Found client :)')
                    i['token'] = token

        response = requests.get(f'https://fortnite-api.com/v2/stats/br/v2/{accountID}', headers=headerslmao)
        try:
            clientUsername = response.json()['data']['account']['name']
        except:
            clientUsername = 'error'

        response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/QueryProfile?profileId=athena',  json={"text": {}}, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        )
        
        #print(response.json())
        created = response.json()['profileChanges'][0]['profile']['created']
        created = created[:10]
        updated = response.json()['profileChanges'][0]['profile']['updated']
        updated = updated[:10]

        embed = discord.Embed(
            color = discord.Colour.red(),
            title=f'Welcome, {clientUsername}!'
        )
        embed.add_field(name='Account ID', value=f'{accountID}')
        embed.add_field(name='Created at', value=created)
        embed.add_field(name='Last updated', value=updated)

        loadoutUUID = response.json()['profileChanges'][0]['profile']['stats']['attributes']['last_applied_loadout']
        #for i in profileChanges[0].profile.stats.attributes.loadouts
        for i in json_object['auths']:
            if i['DiscordauthorID'] == str(DiscordauthorID):
                print('Found client :)')
                i['loadoutUUID'] = loadoutUUID

        lockerdata = response.json()['profileChanges'][0]['profile']['items'][loadoutUUID]['attributes']['locker_slots_data']['slots']
        lockerskinID = lockerdata['Character']['items'][0]
        lockerskinID = lockerskinID.replace('AthenaCharacter:', '')
        response = requests.get(f'https://fortnite-api.com/v2/cosmetics/br/search?id={lockerskinID}')
        url = response.json()['data']['images']['icon']
        embed.set_thumbnail(url=url)
    
        #profileChanges[0].profile.items["b085ba91-2bdb-43c8-9a1a-01949ca040f9"]
        await ctx.send(embed=embed)
        a_file = open(f"auths.json", "w")
        json.dump(json_object, a_file, indent = 4)
        

def authenticate():
    a_file = open(f"auths.json", "r")
    json_object = json.load(a_file)
    a_file.close()

@slash.slash(name='loadout', description='Shows your current Fortnite loadout', guild_ids=testing_guilds)
async def showlocker(ctx):
    a_file = open(f"auths.json", "r")
    json_object = json.load(a_file)
    a_file.close()

    DiscordauthorID = ctx.author.id

    for i in json_object['auths']:
        if i['DiscordauthorID'] == str(DiscordauthorID):
            token = i['token']
            accountID = i['accountID']
            loaduuid = i['loadoutUUID']
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
                lockerdata = response.json()['profileChanges'][0]['profile']['items'][loaduuid]['attributes']['locker_slots_data']['slots']
                
                response = requests.get(f'https://fortnite-api.com/v2/stats/br/v2/{accountID}', headers=headerslmao)
                
                clientUsername = response.json()['data']['account']['name']
                embed = discord.Embed(
                    color = discord.Colour.green(),
                    title=f"{clientUsername}'s current loadout"
                )
                message = await ctx.send('Loading locker...')

                list_ = []
                for i in lockerdata:
                    #print(i)
                    backendtype = i
                    type = lockerdata[i]
                    list_.append({
                        f'{i}': [],
                        "backendType": backendtype
                    })
                    for i in type['items']:
                        
                        id = i.split(":").pop()
                        if i == '':
                            id = 'None'
                        
                        for i in list_:
                            if backendtype in i:
                                i[backendtype].append(id)


                for i in list_:
                    backendtype = i['backendType']
                    cosmetics = ''
                    for i in i[backendtype]:
                        if i != 'None':
                            #print(i)
                            response = requests.get(f'https://fortnite-api.com/v2/cosmetics/br/search?id={i}')
                            i = response.json()['data']['name']
                            url = response.json()['data']['images']['icon']
                        cosmetics += f'[{i}]({url})\n'
                    if i != 'None':
                        embed.add_field(
                            name=backendtype,
                            value=cosmetics
                        )
                    else:
                        embed.add_field(
                            name=backendtype,
                            value='N/A'
                        )
                    

                await message.delete()
                await ctx.send(embed=embed)


@slash.slash(name='purchaceitem', description='Purchace an item from the current shop!',options=[
    create_option(
        name='offerid',
        description='Enter item Offer ID (Must include v2:/)',
        option_type=3,
        required=True
    )
], guild_ids=testing_guilds)
async def purchaceitem(ctx, offerid:str):
    print('hello')
    a_file = open(f"auths.json", "r")
    json_object = json.load(a_file)
    a_file.close()

    DiscordauthorID = ctx.author.id

    for i in json_object['auths']:
        if i['DiscordauthorID'] == str(DiscordauthorID):
            #await ctx.send('Loaded auth token!')
            token = i['token']
            accountID = i['accountID']
            response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/PurchaseCatalogEntry?profileId=common_core',  json={"text": {
                "offerId": "v2:/fcd259b7616f9e189a4d9dc5a2e75c20370823b1b9983f034e46738662ee18bd",
                "purchaseQuantity": 1,
                "currency": "MtxCurrency",
                "expectedTotalPrice": 0,
                "gameContext": "",
                "currencySubType": ""
            }}, headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            )

            print(response.json())
            try:
                error = response.json()['errorMessage']
                embed = discord.Embed(
                    color = discord.Colour.red(),
                    title='ERROR',
                    description=error
                )
                return await ctx.send(embed=embed)
            except:
                await ctx.send('Purchased item!')

@slash.slash(name='sac', description='Change your support-a-creator code!',options=[
    create_option(
        name='code',
        description='Support-A-Creator Code',
        option_type=3,
        required=True
    )
], guild_ids=testing_guilds)
async def purchaceitem(ctx, code:str):
    a_file = open(f"auths.json", "r")
    json_object = json.load(a_file)
    a_file.close()

    DiscordauthorID = ctx.author.id

    for i in json_object['auths']:
        if i['DiscordauthorID'] == str(DiscordauthorID):
            #await ctx.send('Loaded auth token!')
            token = i['token']
            accountID = i['accountID']
            response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/SetAffiliateName?profileId=common_core',  json={"text": {
                "affiliateName": f"{code}"
            }}, headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            )

            print(response.json())
            try:
                error = response.json()['errorMessage']
                embed = discord.Embed(
                    color = discord.Colour.red(),
                    title='ERROR',
                    description='Your token has most likely expired! Type /login <auth> to generate a new one.'
                )
                return await ctx.send(embed=embed)
            except:

                await ctx.send(f'Successfully changed Support-A-Creator Code to "{code}"!')


@slash.slash(name='gift', description='Gift an item thats currently in the shop!',options=[
    create_option(
        name='offerid',
        description='Item OfferID',
        option_type=3,
        required=True
    ),
    create_option(
        name='price',
        description='The price of the item (MUST ENTER REAL PRICE OR IT WILL NOT WORK)',
        option_type=3,
        required=True
    ),
    create_option(
        name='user',
        description='The username of the account you want to gift to',
        option_type=3,
        required=True
    )
], guild_ids=testing_guilds)
async def gift(ctx, offerid:str, user:str, price:int):
    a_file = open(f"auths.json", "r")
    json_object = json.load(a_file)
    a_file.close()

    DiscordauthorID = ctx.author.id
    response = requests.get(f'https://fortnite-api.com/v2/stats/br/v2?name={user}', headers=headerslmao)
    user_name = response.json()['data']['account']['name']
    user_id = response.json()['data']['account']['id']

    if response.json()['status'] != 200:
        error = response.json()['error']
        embed = discord.Embed(
            color = discord.Colour.red(),
            title='ERROR',
            description=f'{error}'
        )
        return await ctx.send(embed=embed)
    

    for i in json_object['auths']:
        if i['DiscordauthorID'] == str(DiscordauthorID):
            #await ctx.send('Loaded auth token!')
            token = i['token']
            accountID = i['accountID']
            response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/GiftCatalogEntry?profileId=common_core',  json={"text": {
                "offerId": f"{offerid}",
                "purchaseQuantity": 1,
                "currency": "MtxCurrency",
                "expectedTotalPrice": price,
                "gameContext": "",
                "receiverAccountIds": [f"{user_id}"],
                "giftWrapTemplateId": "GiftBox:gb_default",
                "currencySubType": ""
            }}, headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            )

            print(response.json())
            try:
                error = response.json()['errorMessage']
                embed = discord.Embed(
                    color = discord.Colour.red(),
                    title='ERROR',
                    description='Your token has most likely expired! Type /login <auth> to generate a new one.'
                )
                return await ctx.send(embed=embed)
            except:

                await ctx.send(f'Successfully gifted item to "{user_name}"!')



client.run(TOKEN)
