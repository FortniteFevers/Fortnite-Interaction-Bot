from cgi import test
from re import template
import discord
from discord.ext.commands.core import guild_only
intents = discord.Intents.default()
from discord.ext import commands, tasks

from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option
from discord.ext.commands import bot
from discord_slash.utils.manage_commands import create_option, create_permission, create_choice
from discord_slash.model import ButtonStyle, SlashCommandPermissionType
from discord_slash.utils import manage_components
import json
import interactions
import requests

testing_guilds = [926178688247140383]

client = commands.Bot(command_prefix='test-', intents=intents)
client.remove_command('help')
slash = SlashCommand(client, sync_commands = True)

headerslmao = {'Authorization': '60bcad5e-fe7c-4734-92a9-986b81f99444'}

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="/help"))
    print("\nServers: " + str(len(client.guilds)))
    print("Bot is ready")

@slash.slash(name='help', description='Help!')
async def help(ctx):
    await ctx.send('Login to our bot using **/login <auth>**. Type "/" for a list of commands.')


@slash.slash(name='logout', description='Remove your Epic Games account from our system.', guild_ids=testing_guilds)
async def logout(ctx):
    a_file = open(f"auths.json", "r")
    json_object = json.load(a_file)
    a_file.close()

    for element in json_object['auths']:
        try:
            if element['DiscordauthorID'] == str(ctx.author.id):
                #del element['DiscordauthorID']
                del element['token']
                del element['accountID']
                del element['loadoutUUID']
                del element['accountName']
        except:
            embed = discord.Embed(
                color = discord.Colour.red(),
                title='ERROR',
                description='You are not logged-in to an account! Please use **/login <auth>**'
            )
            return await ctx.send(embed=embed)
    a_file = open(f"auths.json", "w")
    json.dump(json_object, a_file, indent = 4)

    embed = discord.Embed(
        color = 0x00ff44,
        title='SUCCESS!',
        description='Your account has successfully been removed within our system. If you wish to use the bot again, please use **/login <auth>**'
    )
    await ctx.send('Logged out of your account.')
    return await ctx.author.send('Sad to see you go!\nWe have removed your tokens from our system. If you wish to use the bot again, please use **/login <auth>**')


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
    else: # The real command
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

        for x in json_object['auths']:
            if x['DiscordauthorID'] == str(DiscordauthorID):
    
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
                #await ctx.send('test')
                await ctx.send(embed=embed)

                x['loadoutUUID'] = f"{loadoutUUID}"
                x['token'] = f"{token}"
                x['accountID'] = f"{accountID}"
                x['accountName'] = f"{clientUsername}"


                a_file = open(f"auths.json", "w")
                json.dump(json_object, a_file, indent = 4)
                return await ctx.author.send('It looks like you are already logged in, or you are using the bot again after logging out!\nI changed your token anyways, its now updated with a new one.')
        
        list_ = []
        try:
            for i in json_object['auths']:
                accountidlol = i['accountID']
                list_.append(f'{accountidlol}')
        except:
            pass
        
        authornum = list_.count(accountID)
        if authornum == 0:
            await ctx.author.send('Thank you for using our bot for the first time. You are now added into our system.')
            json_object['auths'].append({
                "DiscordauthorID": f"{DiscordauthorID}",
                "token": f"{token}",
                #"authCode": f'{auth}',
                "accountID": f"{accountID}",
                "loadoutUUID": "",
                "accountName": ""
            })
            a_file = open(f"auths.json", "w")
            json.dump(json_object, a_file, indent = 4)
        else:
            json_object['token'] = str(token)
            for i in json_object['auths']:
                if i['DiscordauthorID'] == str(DiscordauthorID):
                    print('Found client :)')
                    i['token'] = token
                    i['accountID'] = f"{accountID}"
                    await ctx.author.send('Welcome back! I have just added the tokens to your new account.')

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
                i['accountName'] = clientUsername

        lockerdata = response.json()['profileChanges'][0]['profile']['items'][loadoutUUID]['attributes']['locker_slots_data']['slots']
        lockerskinID = lockerdata['Character']['items'][0]
        lockerskinID = lockerskinID.replace('AthenaCharacter:', '')
        response = requests.get(f'https://fortnite-api.com/v2/cosmetics/br/search?id={lockerskinID}')
        url = response.json()['data']['images']['icon']
        embed.set_thumbnail(url=url)
    
        #profileChanges[0].profile.items["b085ba91-2bdb-43c8-9a1a-01949ca040f9"]
        #await ctx.send('test')
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
                        try:
                            id = i.split(":").pop()
                        except:
                            i = ''
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


@slash.slash(name='purchaseitem', description='Purchase an item from the current shop!',options=[
    create_option(
        name='offerid',
        description='Enter item Offer ID (Must include v2:/)',
        option_type=3,
        required=True
    ),
    create_option(
        name='price',
        description='Enter the correct price for the item.',
        option_type=3,
        required=True
    )
], guild_ids=testing_guilds)
async def purchaseitem(ctx, offerid:str, price:int):
    print('hello')
    a_file = open(f"auths.json", "r")
    json_object = json.load(a_file)
    a_file.close()

    DiscordauthorID = ctx.author.id

    for i in json_object['auths']:
        if i['DiscordauthorID'] == str(DiscordauthorID):
            print(offerid)
            offerid.replace(' ', '')
            #await ctx.send('Loaded auth token!')
            token = i['token']
            accountID = i['accountID']
            accountName = i['accountName']
            response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/PurchaseCatalogEntry?profileId=common_core', json= {
                "offerId": offerid,
                "purchaseQuantity": 1,
                "currency": "MtxCurrency",
                "expectedTotalPrice": price,
                "gameContext": "",
                "currencySubType": ""
            }, headers={
                "Authorization": f"bearer {token}",
                "Content-Type": "application/json"

            })

            #print(response.json())
            try:
                error = response.json()['errorMessage']
                embed = discord.Embed(
                    color = discord.Colour.red(),
                    title='ERROR',
                    description=error
                )
                return await ctx.send(embed=embed)
            except:
                data = response.json()['profileChanges'][0]['profile']['stats']['attributes']['mtx_purchase_history']['purchases']
                for i in data:
                    if i['offerId'] == offerid:
                      result = len(i['lootResult'])
                      vbuckspaid = i['totalMtxPaid']
                      
                    try:
                        codeused = i['metadata']['mtx_affiliate']
                    except:
                        codeused = None
                    

                embed = discord.Embed(
                    color = discord.Colour.blue(),
                    title="{accountName}'s Purchases",
                    description='Successfully purchased *{result} cosmetic(s)** for <:vbuck1:934263403441193030> {vbuckspaid}!\nCode used: **{codeused}**'
                )
                await ctx.send(embed=embed)

@slash.slash(name='sac', description='Change your support-a-creator code!',options=[
    create_option(
        name='code',
        description='Support-A-Creator Code',
        option_type=3,
        required=True
    )
], guild_ids=testing_guilds)
async def sac(ctx, code:str):
    a_file = open(f"auths.json", "r")
    json_object = json.load(a_file)
    a_file.close()

    DiscordauthorID = ctx.author.id

    for i in json_object['auths']:
        if i['DiscordauthorID'] == str(DiscordauthorID):
            #await ctx.send('Loaded auth token!')
            token = i['token']
            accountID = i['accountID']
            response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/SetAffiliateName?profileId=common_core',  json= {
                "affiliateName": f"{code}"
            }, headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            )

            #print(response.json())
            try:
                error = response.json()['errorMessage']
                if 'Sorry, the affiliate cannot be found' in error:
                    embed = discord.Embed(
                        color = discord.Colour.red(),
                        title='ERROR',
                        description='This code does not exist! Try another code.'
                    )
                    return await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        color = discord.Colour.red(),
                        title='ERROR',
                        description='Your token has most likely expired! Type /login <auth> to generate a new one.'
                    )
                    return await ctx.send(embed=embed)
            except:
                sac = response.json()['profileChanges'][0]['profile']['stats']['attributes']['mtx_affiliate']
                #print(sac)
                #profileChanges[0].profile.stats.attributes.mtx_affiliate
                if sac.lower() != code.lower():
                    embed = discord.Embed(
                        color = discord.Colour.red(),
                        title='ERROR',
                        description='Could not change Support-A-Creator code.'
                    )
                    return await ctx.send(embed=embed)
                embed = discord.Embed(
                    color = discord.Colour.green(),
                    title = 'Changed Code!',
                    description=f'Successfully changed your Support-A-Creator Code to **"{sac}"**!'
                )
                print(f'Changed [{accountID}] SAC to {sac}')
                await ctx.send(embed=embed)


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
            
            response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/GiftCatalogEntry?profileId=common_core',  json= {
                "offerId": f"{offerid}",
                "purchaseQuantity": 1,
                "currency": "MtxCurrency",
                "expectedTotalPrice": price,
                "gameContext": "",
                "receiverAccountIds": [f"{user_id}"],
                "giftWrapTemplateId": "GiftBox:gb_default",
                "currencySubType": "",
                "personalMessage": ""
            }, headers={
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
                embed = discord.Embed(
                    color = discord.Colour.green(),
                    title = 'Gifted item!',
                    description=f'Successfully gifted item to "{user_name}"!'
                )
                await ctx.send(embed=embed)
                print(f'Gifted {offerid} to {user_id} - from {accountID}')

@slash.slash(name='changeplatform', description='Changes the Mtx Platform used for purchases in the item shop.', options=[
    create_option(
        name='platform',
        description='The platform that will be used for purchases.',
        option_type=3,
        required=True,
        choices=[
            create_choice(
                name='Epic',
                value='Epic'
            ),
            create_choice(
                name='PSN',
                value='PSN'
            ),
            create_choice(
                name='Epic',
                value='Epic'
            ),
            create_choice(
                name='Live',
                value='Live'
            ),
            create_choice(
                name='Shared',
                value='Shared'
            ),
            create_choice(
                name='EpicPC',
                value='EpicPC'
            ),
            create_choice(
                name='EpicPCKorea',
                value='EpicPCKorea'
            ),
            create_choice(
                name='IOSAppStore',
                value='IOSAppStore'
            ),
            create_choice(
                name='EpicAndroid',
                value='EpicAndroid'
            ),
            create_choice(
                name='Nintendo',
                value='Nintendo'
            ),
            create_choice(
                name='WeGame',
                value='WeGame'
            ),
            create_choice(
                name='Samsung',
                value='Samsung'
            )     
        ]
    )
], guild_ids=testing_guilds)
async def changeplatform(ctx, platform:str):
    a_file = open(f"auths.json", "r")
    json_object = json.load(a_file)
    a_file.close()

    DiscordauthorID = ctx.author.id

    for i in json_object['auths']:
        if i['DiscordauthorID'] == str(DiscordauthorID):
            #await ctx.send('Loaded auth token!')
            token = i['token']
            accountID = i['accountID']
            response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/SetMtxPlatform?profileId=common_core',  json= {
                "newPlatform": f'{platform}'
            }, headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            )
            #print(response.json())
            embed = discord.Embed(
                color = discord.Colour.green(),
                title = 'MTX platform',
                description=f'Changed Mtx Platform to "**{platform}**"!'
            )
            return await ctx.send(
                embed=embed
            )

@slash.slash(name='offerids', description='Returns with a list of the current Offer IDs. Used to purchase/gift a cosmetic.', guild_ids=testing_guilds)
async def offerids(ctx):
    sectionjson = 'name'

    response = requests.get('https://fortnite-api.com/v2/shop/br/combined')
    current_date = response.json()['data']['date'][:10]
    await ctx.send(f'Heres the shop for {current_date}!\n*please note that you have a limited amount of time to use this embed before it closes.*\n\nAll the offer IDs are in **bold**.')

    sections_list = []
    result = []

    for i in response.json()['data']['featured']['entries']:
        sectionID = i['section'][sectionjson]
        sections_list.append(sectionID)
        for i in sections_list: 
            if i not in result: 
                result.append(sectionID) 

    for i in response.json()['data']['daily']['entries']:
        sectionID = i['section'][sectionjson]
        sections_list.append(sectionID)
        for i in sections_list: 
            if i not in result: 
                result.append(sectionID) 

    #print(f'Someone ran the shop command. There are {len(result)} sections in this shop.')

    from disputils import BotEmbedPaginator, BotConfirmation, BotMultipleChoice
    
    number = 0
    embed = []
    
    for i in result:
        section_count = sections_list.count(i)
        number = number + 1
        currentEmbed = discord.Embed(
            title = f'Page {number} - {i}',
            description=f'**{section_count}** Items are in the *{i}* section.'
        )
        currentEmbed.set_author(name=f'FortniteInteractions - {current_date} Shop')

        for x in response.json()['data']['featured']['entries']:
            if x['section'][sectionjson] == i:
                try:
                    offerid = x['offerId']
                except:
                    offerid = 'N/A'
                itemname = f"{x['items'][0]['name']} {x['items'][0]['type']['displayValue']}"

                # IF ITEM BUNDLE, REPLACE NAME HERE
                try:
                    itemname = f"{x['bundle']['name']} *{x['bundle']['info']}*"
                except:
                    pass
                ####

                price = x['finalPrice']
                currentEmbed.add_field(
                    name=f'{itemname}',
                    value=f'Price: {price} V-Bucks\n\n**{offerid}**'
                )

        for x in response.json()['data']['daily']['entries']:
            if x['section'][sectionjson] == i:
                try:
                    offerid = x['offerId']
                except:
                    offerid = 'N/A'
                itemname = f"{x['items'][0]['name']} {x['items'][0]['type']['displayValue']}"
                try:
                    itemname = f"{x['bundle']['name']}\n*{x['bundle']['info']}*"
                except:
                    pass
                price = x['finalPrice']
                currentEmbed.add_field(
                    name=f'{itemname}',
                    value=f'Price: {price} V-Bucks\n\n**{offerid}**'
                )
        
        currentEmbed.set_thumbnail(url='https://i.ibb.co/VwBbn2K/IMG-0754.png')
        embed.append(currentEmbed)


    paginator = BotEmbedPaginator(ctx, embed)
    
    #await ctx.send(f'Hey there {ctx.message.author.mention}, here ya go!')
    await paginator.run()

    #await ctx.send(embed=embed)

@slash.slash(name='vbucks', description='View your current Fortnite V-Bucks amount and where it has came from', guild_ids=testing_guilds)
async def vbucks(ctx):
    a_file = open(f"auths.json", "r")
    json_object = json.load(a_file)
    a_file.close()

    DiscordauthorID = ctx.author.id

    for i in json_object['auths']:
        if i['DiscordauthorID'] == str(DiscordauthorID):
            #await ctx.send('Loaded auth token!')
            token = i['token']
            accountID = i['accountID']
            name = i['accountName']
            response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/QueryProfile?profileId=common_core',  json= {
                
            }, headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            )

            embed = discord.Embed(
                color = discord.Colour.blue(),
                title = f"{name}'s V-Bucks"
            )

            list_ = []
            result = []
            for i in response.json()['profileChanges'][0]['profile']['items']:
                #print(i)
                list_.append(i)
            
            for i in list_:
                idlol = i

                templateID = response.json()['profileChanges'][0]['profile']['items'][idlol]['templateId']
                if templateID.startswith('Currency:'):
                    #print(idlol)
                    platform = response.json()['profileChanges'][0]['profile']['items'][idlol]['attributes']['platform']
                    quantity = response.json()['profileChanges'][0]['profile']['items'][idlol]['quantity']
                    counter = list_.count(idlol)
                    if counter >=2 or counter == 1:
                        #print(f'Found {quantity} on {platform}')
                        embed.add_field(
                            name=f'{platform}',
                            value=f'<:vbuck1:934263403441193030> {quantity} '
                        )
                        result.append(quantity)
            
            Sum = sum(result)

            embed.description=f'Current Amount: <:vbuck1:934263403441193030> **{Sum}**'


            return await ctx.send(
                embed=embed
            )
    
@slash.slash(name='info', description='Account Info', guild_ids=testing_guilds)
async def info(ctx):
    a_file = open(f"auths.json", "r")
    json_object = json.load(a_file)
    a_file.close()

    DiscordauthorID = ctx.author.id

    for i in json_object['auths']:
        if i['DiscordauthorID'] == str(DiscordauthorID):
            #await ctx.send('Loaded auth token!')
            token = i['token']
            accountID = i['accountID']
            name = i['accountName']
            response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/QueryProfile?profileId=athena',  json= {
                
            }, headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            )
            print(response.json)
            embed = discord.Embed(
                color = discord.Colour.blue(),
                title = f"{name}'s Account Info"
            )

            list_ = []
            result = []
            for i in response.json()['profileChanges'][0]['profile']['stats']:
                #print(i)
                list_.append(i)
            
            for i in list_:
                idlol = i

            #print(idlol)
            level = response.json()['profileChanges'][0]['profile']['stats']['attributes']['book_level']
            stars = response.json()['profileChanges'][0]['profile']['stats']['attributes']['battlestars']
            accountlevel = response.json()['profileChanges'][0]['profile']['stats']['attributes']['accountLevel']
            xp = response.json()['profileChanges'][0]['profile']['stats']['attributes']['xp']
            lastupdated = response.json()['profileChanges'][0]['profile']['updated']

            response2 = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/QueryProfile?profileId=athena',  json={"text": {}}, headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            )
            loadoutUUID = response2.json()['profileChanges'][0]['profile']['stats']['attributes']['last_applied_loadout']
            #for i in profileChanges[0].profile.stats.attributes.loadouts
            for i in json_object['auths']:
                if i['DiscordauthorID'] == str(DiscordauthorID):
                    print('Found client :)')
                    i['loadoutUUID'] = loadoutUUID

            lockerdata = response.json()['profileChanges'][0]['profile']['items'][loadoutUUID]['attributes']['locker_slots_data']['slots']
            lockerskinID = lockerdata['Character']['items'][0]
            lockerskinID = lockerskinID.replace('AthenaCharacter:', '')
            response3 = requests.get(f'https://fortnite-api.com/v2/cosmetics/br/search?id={lockerskinID}')
            url = response3.json()['data']['images']['icon']



            embed.set_thumbnail(url=url)
            embed.add_field(name="Main: ", value=f"Level: {level} \n Battle Stars: {stars}")
            embed.add_field(name="Misc: ", value=f"Account Level: {accountlevel} \n XP: {xp}")
            embed.description=f'Last Updated:  {lastupdated}'


            return await ctx.send(
                embed=embed
            )


@slash.slash(name="createbutton",
    description='Create a manage account button in your server.',
    guild_ids=testing_guilds)
async def createbutton(ctx):

  try:

    buttons = [
      manage_components.create_button(
        style=ButtonStyle.blurple,
        label="Manage your account",
        custom_id='account_button'
      )
    ]

    action_row = manage_components.create_actionrow(*buttons)

    channel = client.get_channel(ctx.channel.id)

    embed = discord.Embed(
        title='Manage your Clash Utils Account',
        description='Click the button below to get a DM from me to manage your **Clash Utils** account.\nMake sure you have DM\'s **enabled** as the next steps will continue in DM\'s',
        colour=discord.Colour(0x2f3136)
        )

    await channel.send(embed=embed, components=[action_row])

    await ctx.send('Embed created!', hidden=True)

  except Exception as e:
    await ctx.send(f'An error occurred: `{e}`', hidden=True)



#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
client.run('')

