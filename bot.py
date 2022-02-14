import discord # pip install discord
from discord.ext.commands.core import guild_only
intents = discord.Intents.default()
from discord.ext import commands, tasks
import PIL
from PIL import Image, ImageFont, ImageDraw
import os
import shutil
import time

# pip install -U discord-py-slash-command
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_choice, create_option

import json
import requests
import asyncio

testing_guilds = [926178688247140383]

vbuckemoji = '<:vbuck1:934263403441193030>'

client = commands.Bot(command_prefix='test-', intents=intents)
client.remove_command('help')
slash = SlashCommand(client, sync_commands = True)

headerslmao = {'Authorization': '60bcad5e-fe7c-4734-92a9-986b81f99444'}

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name="/help"))
    print("\nServers: " + str(len(client.guilds)))
    print("Bot is ready")
    client.loop.create_task(looping_status())

async def looping_status():
    while True:
        a_file = open(f"auths.json", "r")
        json_object = json.load(a_file)
        a_file.close()

        users = len(json_object['auths'])
        await client.change_presence(activity=discord.Game(name=f'with {users} Fortnite Accounts!'))
        await asyncio.sleep(15)
        

@slash.slash(name='help', description='Help!')
async def help(ctx):
    await ctx.send('Login to our bot using **/login <auth>**. Type "/" for a list of commands.')

def test_user_auth(DiscordauthorID, data):
    a_file = open(f"auths.json", "r")
    json_object = json.load(a_file)
    a_file.close()

    for i in json_object['auths']:
        if i['DiscordauthorID'] == str(DiscordauthorID):
            data = i
            return(data)

@slash.slash(name='logout', description='Remove your Epic Games account from our system.') # Logout command removes everything except discord author ID
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
    await ctx.send(embed=embed)
    return await ctx.author.send('Sad to see you go!\nWe have removed your tokens from our system. If you wish to use the bot again, please use **/login <auth>**')


@slash.slash(name='login', description='Log into your Epic Games account.', options=[
    create_option(
        name='auth',
        description='32-character Auth Code',
        option_type=3,
        required=False
    )
])
#@commands.cooldown(1, 30, commands.BucketType.user)
async def login(ctx, auth:str = None):
    if auth is None:
        embed = discord.Embed(
            color = discord.Colour.blue(),
            title='Login to your Epic Games account',
            description='[CLICK ME TO GET YOUR AUTH CODE](https://www.epicgames.com/id/login?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Fapi%2Fredirect%3FclientId%3Dec684b8c687f479fadea3cb2ad83f5c6%26responseType%3Dcode)\n\nHow to login to your Epic Games account:\n\n1. Visit the link above to get your login code.\n2. Copy the 32 character code that looks like **aabbccddeeff11223344556677889900**, located after **authorizationCode=**.\n3. Send /login <32 character code> to complete your login.\n\n**Need to switch accounts?**\n[Use this link instead](https://www.epicgames.com/id/login?redirectUrl=https%3A%2F%2Fwww.epicgames.com%2Fid%2Fapi%2Fredirect%3FclientId%3D3f69e56c7649492c8cc29f1af08a8a12%26responseType%3Dcode&prompt=login)'
        )
        embed.set_footer(text='We recommend that you only log into accounts that you have email access to!')
        embed.set_image(url='https://media1.giphy.com/media/LpMNwwVXrKz4KLOFLA/giphy.gif?cid=790b7611f064ad78dc583adf51b84a2e9a9d8b72103503a6&rid=giphy.gif&ct=g')

        await ctx.send(embed=embed)
    else: # The real command

        # Code below generates a epic auth token
        response = requests.post('https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token', headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"basic ZWM2ODRiOGM2ODdmNDc5ZmFkZWEzY2IyYWQ4M2Y1YzY6ZTFmMzFjMjExZjI4NDEzMTg2MjYyZDM3YTEzZmM4NGQ=" # Auth provided by M1
        },
        data={
            "grant_type": "authorization_code",
            "code": auth
        }
        )


        try:
            token = response.json()['access_token']
            print('Generated new token for account')
        except:
            embed = discord.Embed(
                color = discord.Colour.red(),
                title='ERROR',
                description='Invalid access token was entered.'
            )
            return await ctx.send(embed=embed)
        accountID = response.json()['account_id']

        #await ctx.send(f"Generated auth token. Expires at {response.json()['expires_at']}")
        await ctx.author.send(f"I have just generated a new token for you.\nThis token Expires at {response.json()['expires_at']}") # Sends a DM to the author (success)

        a_file = open(f"auths.json", "r")
        json_object = json.load(a_file)
        a_file.close()

        DiscordauthorID = ctx.author.id

        # Checks the auths array to see if discord author ID is in it. If it is, the bot will refresh the token and notice it.
        for x in json_object['auths']:
            if x['DiscordauthorID'] == str(DiscordauthorID):
    
                response = requests.get(f'https://fortnite-api.com/v2/stats/br/v2/{accountID}', headers=headerslmao)
                clientUsername = response.json()['data']['account']['name']
            

                response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/QueryProfile?profileId=athena',  json={"text": {}}, headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }
                )

                try:
                    error = response.json()['errorCode']
                    embed = discord.Embed(
                        color = discord.Colour.red(),
                        title = 'LOGIN FAILED!',
                        description=f'{error}'
                    )
                    return await ctx.send(embed=embed)
                except:
                    pass
                
                #print(response.json())
                created = response.json()['profileChanges'][0]['profile']['created']
                created = created[:10]
                updated = response.json()['profileChanges'][0]['profile']['updated']
                updated = updated[:10]

                embed = discord.Embed(
                    color = discord.Colour.red(),
                    title=f'Welcome back, {clientUsername}!'
                )
                embed.add_field(name='Account ID', value=f'{accountID}')
                embed.add_field(name='Created at', value=created)
                embed.add_field(name='Last updated', value=updated)

                loadoutUUID = response.json()['profileChanges'][0]['profile']['stats']['attributes']['loadouts'][0]
                print(loadoutUUID)
                #for i in profileChanges[0].profile.stats.attributes.loadouts
                for i in json_object['auths']:
                    if i['DiscordauthorID'] == str(DiscordauthorID):
                        #print('a')
                        print('Found client :)') # If this happens, the user is already logged in.
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
        
        # Below is if a user uses the bot for the first time.

        await ctx.author.send('Thank you for using our bot for the first time. You are now added into our system.')

        # Below dumps all data except loadout UUID and account name. We will dump it later.
        json_object['auths'].append({
            "DiscordauthorID": f"{DiscordauthorID}",
            "token": f"{token}",
            #"authCode": f'{auth}',
            "accountID": f"{accountID}",
            "loadoutUUID": "",
            "accountName": ""
        })
        a_file = open(f"auths.json", "w")
        
        # Below grabs the account username with Fortnite-API.
        response = requests.get(f'https://fortnite-api.com/v2/stats/br/v2/{accountID}', headers=headerslmao)
        try:
            clientUsername = response.json()['data']['account']['name']
        except:
            clientUsername = 'error'

        # Accessing Query Profile to get locker data...
        response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/QueryProfile?profileId=athena',  json={"text": {}}, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        )
        
        # Created/Updated
        created = response.json()['profileChanges'][0]['profile']['created']
        created = created[:10]
        updated = response.json()['profileChanges'][0]['profile']['updated']
        updated = updated[:10]

        # Creates embed
        embed = discord.Embed(
            color = discord.Colour.red(),
            title=f'Welcome, {clientUsername}!'
        )
        embed.add_field(name='Account ID', value=f'{accountID}')
        embed.add_field(name='Created at', value=created)
        embed.add_field(name='Last updated', value=updated)

        # Uses query profile to grab UUID
        loadoutUUID = response.json()['profileChanges'][0]['profile']['stats']['attributes']['loadouts'][0]
        
        # Now, we load back into the token array and dump account name and loadout UUID. We do this by finding the author discord ID, which is already in the array.
        for i in json_object['auths']:
            if i['DiscordauthorID'] == str(DiscordauthorID):
                print('Found client :)') # Used to know we found client
                i['loadoutUUID'] = loadoutUUID
                i['accountName'] = clientUsername
                json.dump(json_object, a_file, indent = 4)
        
        # Now, we are grabbing the author's locker data to retreive the current skin.
        # We use the loadout UUID thats in the array.

        lockerdata = response.json()['profileChanges'][0]['profile']['items'][loadoutUUID]['attributes']['locker_slots_data']['slots']
        lockerskinID = lockerdata['Character']['items'][0]
        lockerskinID = lockerskinID.replace('AthenaCharacter:', '')
        response = requests.get(f'https://fortnite-api.com/v2/cosmetics/br/search?id={lockerskinID}')
        url = response.json()['data']['images']['icon']
        embed.set_thumbnail(url=url)

        await ctx.send(embed=embed) # Sends embed, user is logged in and added!

        
@login.error
async def loginerror(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        em = discord.Embed(title=f"Slow it down bro!",description=f"Try again in {error.retry_after:.2f}s.", color=discord.Colour.red())
        await ctx.send(embed=em)

@slash.slash(name='purchaseitem', description='Purchase an item from the current shop!',options=[
    create_option(
        name='offerid',
        description='Enter item Offer ID (Must include v2:/)',
        option_type=3,
        required=True
    )
], guild_ids=testing_guilds)
async def purchaseitem(ctx, offerid:str):
    DiscordauthorID = ctx.author.id
    data = ''
    test = test_user_auth(DiscordauthorID, data)

    s1 = json.dumps(test)
    i = json.loads(s1)
    print(offerid)
    offerid.replace(' ', '')
    #await ctx.send('Loaded auth token!')
    token = i['token']
    accountID = i['accountID']
    accountName = i['accountName']

    valid_ID = False
    
    shop_response = requests.get('https://api.nitestats.com/v1/epic/store')
    for i in shop_response.json()['storefronts']:
        for i in i['catalogEntries']:
            if offerid in i['offerId']:
                print('Found offer ID!')
                devName = i['devName']
                try:
                    finalPrice = i['finalPrice']
                    regularPrice = i['regularPrice']
                except:
                    
                    try:
                        finalPrice = abs(i['dynamicBundleInfo']['discountedBasePrice']) + i['dynamicBundleInfo']['floorPrice']
                    except:
                        finalPrice = "N/A"
                    
                    regularPrice = "N/A"
                items = len(i['itemGrants'])
                valid_ID = True

                embed = discord.Embed(
                    color = discord.Colour.blue(),
                    title='Found Item!',
                    description=f'Dev Name: **{devName}**\n\nItems included in offer: **{items}**\n\nRegular Price: **{regularPrice}** {vbuckemoji}\n\nFinal Price: **{finalPrice}** {vbuckemoji}'
                )
                embed.set_footer(text='Made with the Fortnite Interactions discord bot')
                await ctx.send(embed=embed)

    if valid_ID != True:
        embed = discord.Embed(
            color = discord.Colour.red(),
            title='ERROR',
            description='The offer ID you have entered is not currently in the Epic Store!\n\nType **/offerids** for a list of the current Offer IDs.'
        )
        return await ctx.send(embed=embed)

    response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/PurchaseCatalogEntry?profileId=common_core', json= {
        "offerId": offerid,
        "purchaseQuantity": 1,
        "currency": "MtxCurrency",
        "expectedTotalPrice": finalPrice,
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
            description=f'Successfully purchased *{result} cosmetic(s)** for <:vbuck1:934263403441193030> {vbuckspaid}!\nCode used: **{codeused}**'
        )
        await ctx.send(embed=embed)

@slash.slash(name='sac', description='Change oyour support-a-creator code!',options=[
    create_option(
        name='code',
        description='Support-A-Creator Code',
        option_type=3,
        required=False
    )
], guild_ids=testing_guilds)
async def sac(ctx, code:str=None):
    DiscordauthorID = ctx.author.id
    data = ''
    test = test_user_auth(DiscordauthorID, data)

    s1 = json.dumps(test)
    i = json.loads(s1)

    #await ctx.send('Loaded auth token!')
    token = i['token']
    accountID = i['accountID']
    accountName = i['accountName']

    if code is None:
        response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/QueryProfile?profileId=common_core',  json= {
            
        }, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        )

        current_sac = response.json()['profileChanges'][0]['profile']['stats']['attributes']['mtx_affiliate']

        embed = discord.Embed(
            color = discord.Colour.green(),
            title = f"{accountName}'s Current Support-A-Creator Code",
            description=f'{accountName} is currently supporting code "**{current_sac}**"'
        )
        return await ctx.send(embed=embed)
        
    else:
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
    response = requests.get(f'https://fortnite-api.com/v2/stats/br/v2?name={user}', headers=headerslmao)

    if response.json()['status'] != 200:
        error = response.json()['error']
        embed = discord.Embed(
            color = discord.Colour.red(),
            title='ERROR',
            description=f'{error}'
        )
        return await ctx.send(embed=embed)

    user_name = response.json()['data']['account']['name']
    user_id = response.json()['data']['account']['id']
    

    DiscordauthorID = ctx.author.id
    data = ''
    test = test_user_auth(DiscordauthorID, data)

    s1 = json.dumps(test)
    i = json.loads(s1)
            
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
    DiscordauthorID = ctx.author.id
    data = ''
    test = test_user_auth(DiscordauthorID, data)

    s1 = json.dumps(test)
    i = json.loads(s1)

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
    DiscordauthorID = ctx.author.id
    data = ''
    test = test_user_auth(DiscordauthorID, data)

    s1 = json.dumps(test)
    i = json.loads(s1)

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
        
        amountPurchased = len(response.json()['profileChanges'][0]['profile']['stats']['attributes']['mtx_purchase_history']['purchases'])
        
        embed.description=f'Current Amount: <:vbuck1:934263403441193030> **{Sum}**'
        embed.add_field(
            name='Purchased Items',
            value = f"{amountPurchased}"
        )


        return await ctx.send(
            embed=embed
        )
    

@slash.slash(name='info', description='Account Info', guild_ids=testing_guilds)
async def info(ctx):
    DiscordauthorID = ctx.author.id
    data = ''
    test = test_user_auth(DiscordauthorID, data)

    s1 = json.dumps(test)
    i = json.loads(s1)

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


    loadoutUUID = response.json()['profileChanges'][0]['profile']['stats']['attributes']['loadouts'][0]

    lockerdata = response.json()['profileChanges'][0]['profile']['items'][loadoutUUID]['attributes']['locker_slots_data']['slots']
    lockerskinID = lockerdata['Character']['items'][0]
    lockerskinID = lockerskinID.replace('AthenaCharacter:', '')
    response3 = requests.get(f'https://fortnite-api.com/v2/cosmetics/br/search?id={lockerskinID}')
    url = response3.json()['data']['images']['icon']

    response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/QueryProfile?profileId=common_core',  json= {
        
    }, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    )

    current_sac = response.json()['profileChanges'][0]['profile']['stats']['attributes']['mtx_affiliate']



    embed.set_thumbnail(url=url)
    embed.add_field(name="Main: ", value=f"Level: {level} \n Battle Stars: {stars}")
    embed.add_field(name="Misc: ", value=f"Account Level: {accountlevel} \n XP: {xp} \n Currently Supporting: {current_sac}")
    embed.description=f'Last Updated:  {lastupdated}'


    return await ctx.send(
        embed=embed
    )


@slash.slash(name='equip', description='Equips a item that you currently own to a slot.', guild_ids=testing_guilds, options=[
    create_option(
        name='category',
        description='The catagory of the item that you want to equip',
        option_type=3,
        required=True,
        choices=[
            create_choice(
                name='Character',
                value='Character'
            ),
            create_choice(
                name='Dance',
                value='Dance'
            ),
            create_choice(
                name='Epic',
                value='Epic'
            ),
            create_choice(
                name='Glider',
                value='Glider'
            ),
            create_choice(
                name='Pickaxe',
                value='Pickaxe'
            ),
            create_choice(
                name='Backpack',
                value='Backpack'
            ),
            create_choice(
                name='LoadingScreen',
                value='LoadingScreen'
            ),
            create_choice(
                name='MusicPack',
                value='MusicPack'
            ),
            create_choice(
                name='ItemWrap',
                value='ItemWrap'
            ),
            create_choice(
                name='SkyDiveContrail',
                value='SkyDiveContrail'
            )
        ]
    ),
    create_option(
        name='cosmetic',
        description='The cosmetic that you want to equip',
        option_type=3,
        required=True
    )
],)
async def equip(ctx, category:str, cosmetic:str):
    fresponse = requests.get(f'https://fortnite-api.com/v2/cosmetics/br/search?name={cosmetic}')
    cosmeticID = fresponse.json()['data']['id']
    cosmeticName = fresponse.json()['data']['name']
    cosmeticBT = fresponse.json()['data']['type']['backendValue']

    DiscordauthorID = ctx.author.id
    data = ''
    test = test_user_auth(DiscordauthorID, data)

    s1 = json.dumps(test)
    i = json.loads(s1)
            
    #await ctx.send('Loaded auth token!')
    token = i['token']
    accountID = i['accountID']
    name = i['accountName']
    response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/QueryProfile?profileId=athena',  json= {
        "lockerItem": "",
        "category": f"{category}",
        "itemToSlot": f"{cosmeticBT}:{cosmeticID}",
        "slotIndex": 0,
        "variantUpdates": [],
        "optLockerUseCountOverride": -1
    }, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    )

    embed = discord.Embed(
        color = discord.Colour.green(),
        title = 'Equiped Item!',
        description= f'I have equiped the {cosmeticName} {category}.'
    )
    await ctx.send(embed=embed)

@slash.slash(name='generate_profile',  description='Creates a json file of your current loadout', guild_ids=testing_guilds)
async def generate_profile(ctx):
    DiscordauthorID = ctx.author.id
    data = ''
    test = test_user_auth(DiscordauthorID, data)

    s1 = json.dumps(test)
    i = json.loads(s1)

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
        lockerdata = response.json()['profileChanges'][0]['profile']['items'][loaduuid]['attributes']

        banner_icon_template = lockerdata['banner_icon_template']
        banner_color_template = lockerdata['banner_color_template']
        
        response = requests.get(f'https://fortnite-api.com/v2/stats/br/v2/{accountID}', headers=headerslmao)
        
        clientUsername = response.json()['data']['account']['name']
        embed = discord.Embed(
            color = discord.Colour.green(),
            title=f"{clientUsername}'s current loadout"
        )

        list_ = []
        for i in lockerdata['locker_slots_data']['slots']:
            #print(i)
            backendtype = i
            type = lockerdata['locker_slots_data']['slots'][i]
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

        list_.append({
            "banner_icon_template": banner_icon_template,
            "banner_color_template": banner_color_template,
            "backendType": "Banner"
        })

        result = json.dumps(list_, indent=4, sort_keys=True)
        await ctx.send(f'```json\n{result}```')

@slash.slash(name='generatelocker', description='Generates a custom image of your Fortnite Locker.', guild_ids=testing_guilds)
async def generatelocker(ctx):
    try:
        shutil.rmtree('cache')
        os.makedirs('cache')
    except:
        os.makedirs('cache')

    await ctx.defer()

    start = time.time()

    DiscordauthorID = ctx.author.id
    data = ''
    test = test_user_auth(DiscordauthorID, data)

    s1 = json.dumps(test)
    x = json.loads(s1)

    token = x['token']
    accountID = x['accountID']
    loaduuid = x['loadoutUUID']
    accountName = x['accountName']
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
        
        lockerdata = response.json()['profileChanges'][0]['profile']['items'][loaduuid]['attributes']

        banner_icon_template = lockerdata['banner_icon_template']
        banner_color_template = lockerdata['banner_color_template']
        
        response = requests.get(f'https://fortnite-api.com/v2/stats/br/v2/{accountID}', headers=headerslmao)
        
        clientUsername = response.json()['data']['account']['name']
        embed = discord.Embed(
            color = discord.Colour.green(),
            title=f"{clientUsername}'s current loadout"
        )

        list_ = []
        for i in lockerdata['locker_slots_data']['slots']:
            #print(i)
            backendtype = i
            type = lockerdata['locker_slots_data']['slots'][i]
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

        #list_.append({
        #    "banner_icon_template": banner_icon_template,
        #    "banner_color_template": banner_color_template,
        #    "backendType": "Banner"
        #})
    
    background=Image.open(f'background.png').convert('RGB')
    rarityfile = open(f"auths.json", "r")
    rarityresponse = json.load(rarityfile)
    rarityfile.close()
    for i in list_:
        backendType = i['backendType']
        #print(backendType)

        if backendType == 'Character':
            # Character featured icon:
            characterID = i[backendType][0]
            fresponse = requests.get(f'https://fortnite-api.com/v2/cosmetics/br/search?id={characterID}')
            furl = fresponse.json()['data']['images']['featured']
            iurl = fresponse.json()['data']['images']['icon']
            irarity = fresponse.json()['data']['rarity']['value']
                
            #print(characterID)
            if furl != None:
                r = requests.get(furl, allow_redirects=True)
            else:
                r = requests.get(iurl, allow_redirects=True)
            
            open(f'{backendType}_icontemp.png', 'wb').write(r.content)

            characterImage= Image.open(f'{backendType}_icontemp.png').resize((791,791),PIL.Image.ANTIALIAS).convert('RGBA')
            background.paste(characterImage, (764, 144), characterImage)
            ###############################

            # Character locker icon:
            
            r = requests.get(iurl, allow_redirects=True)
            open(f'{backendType}_icontemp.png', 'wb').write(r.content)
            characterImage= Image.open(f'{backendType}_icontemp.png').convert('RGBA')

            img=Image.new("RGB",(130,160))
            
            # Rarity Paste
            rarityimg = Image.open(f'rarities/{irarity}.png').resize((130,160),PIL.Image.ANTIALIAS).convert('RGBA')
            img.paste(rarityimg, (0,0), rarityimg)
                


            img.paste(Image.open(f'{backendType}_icontemp.png').resize((130,130),PIL.Image.ANTIALIAS).convert('RGBA'), (0,0), Image.open(f'{backendType}_icontemp.png').resize((130,130),PIL.Image.ANTIALIAS).convert('RGBA'))
            img.save(f'cache/{backendType}_Locker.png')
            os.remove(f'{backendType}_icontemp.png')
            ########################
        else:
            num = 1
            for x in i[backendType]:
                if x != "None":
                    #print(x)
                    fresponse = requests.get(f'https://fortnite-api.com/v2/cosmetics/br/search?id={x}')
                    irarity = fresponse.json()['data']['rarity']['value']
                    url = fresponse.json()['data']['images']['icon']
                    r = requests.get(url, allow_redirects=True)
                    open(f'{backendType}_icontemp.png', 'wb').write(r.content)

                    x_value = 130
                    y_value = 160
                    icon_size = 130
                    if backendType == 'Dance' or backendType == 'ItemWrap' or backendType == 'MusicPack' or backendType == 'LoadingScreen':
                        x_value = 88
                        y_value = 110
                        icon_size = 88

                    img=Image.new("RGB",(x_value,y_value))
                    # Rarity Paste
                    rarityimg = Image.open(f'rarities/{irarity}.png').resize((x_value,y_value),PIL.Image.ANTIALIAS).convert('RGBA')
                    img.paste(rarityimg, (0,0), rarityimg)

                    img.paste(Image.open(f'{backendType}_icontemp.png').resize((icon_size,icon_size),PIL.Image.ANTIALIAS).convert('RGBA'), (0,0), Image.open(f'{backendType}_icontemp.png').resize((icon_size,icon_size),PIL.Image.ANTIALIAS).convert('RGBA'))
                    img.save(f'cache/{backendType}_Locker{num}.png')
                    os.remove(f'{backendType}_icontemp.png')
                else:
                    if backendType != 'Backpack':
                        x_value = 130
                        y_value = 160
                        icon_size = 130
                        if backendType == 'Dance' or backendType == 'ItemWrap' or backendType == 'MusicPack' or backendType == 'LoadingScreen':
                            x_value = 88
                            y_value = 110
                            icon_size = 88
                        img=Image.new("RGB",(x_value,y_value))
                        img.save(f'cache/{backendType}_Locker{num}.png')
                    else:
                        x_value = 130
                        y_value = 160
                        icon_size = 130

                        url = 'https://media.discordapp.net/attachments/926178688767258706/935263849811161138/backpack_is_null.png?width=554&height=554'
                        r = requests.get(url, allow_redirects=True)
                        open(f'{backendType}_icontemp.png', 'wb').write(r.content)
                        img=Image.new("RGB",(x_value,y_value))
                        img.paste(Image.open(f'{backendType}_icontemp.png').resize((icon_size,icon_size),PIL.Image.ANTIALIAS).convert('RGBA'), (0,0), Image.open(f'{backendType}_icontemp.png').resize((icon_size,icon_size),PIL.Image.ANTIALIAS).convert('RGBA'))
                        img.save(f'cache/{backendType}_Locker{num}.png')
                        os.remove(f'{backendType}_icontemp.png')
                
                num += 1
    bruhhhhhh = requests.get('https://fortnite-api.com/v1/banners')
    url = None
    for i in bruhhhhhh.json()['data']:
        if i['id'].lower() == banner_icon_template.lower():
            url = i['images']['icon']
        
    #url = banner_icon_template
    r = requests.get(url, allow_redirects=True)
    open(f'cache/Banner_icontemp.png', 'wb').write(r.content)
    img=Image.new("RGB",(88,110))
    img.paste(Image.open(f'cache/Banner_icontemp.png').resize((88,88),PIL.Image.ANTIALIAS).convert('RGBA'), (0,0), Image.open(f'cache/Banner_icontemp.png').resize((88,88),PIL.Image.ANTIALIAS).convert('RGBA'))
    img.save(f'cache/Banner_Locker.png')
    os.remove(f'cache/Banner_icontemp.png')

    img = Image.open(f'cache/Banner_Locker.png').convert('RGBA')
    background.paste(img, (68, 643), img)
    

    for i in list_:
        backendType = i['backendType']

        if backendType == 'Character':
            img = Image.open('cache/Character_Locker.png').convert('RGBA')
            background.paste(img, (68, 238), img)

        elif backendType == 'Backpack':
            num = 1
            for file in os.listdir('cache'):
                if file.startswith(f'{backendType}_Locker'):
                    img = Image.open(f'cache/{backendType}_Locker{num}.png').convert('RGBA')
                    background.paste(img, (203, 238), img)

                    num += 1

        elif backendType == 'Pickaxe':
            num = 1
            for file in os.listdir('cache'):
                if file.startswith(f'{backendType}_Locker'):
                    img = Image.open(f'cache/{backendType}_Locker{num}.png').convert('RGBA')
                    background.paste(img, (340, 238), img)

                    num += 1

        elif backendType == 'Glider':
            num = 1
            for file in os.listdir('cache'):
                if file.startswith(f'{backendType}_Locker'):
                    img = Image.open(f'cache/{backendType}_Locker{num}.png').convert('RGBA')
                    background.paste(img, (476, 238), img)

                    num += 1

        elif backendType == 'SkyDiveContrail':
            num = 1
            for file in os.listdir('cache'):
                if file.startswith(f'{backendType}_Locker'):
                    img = Image.open(f'cache/{backendType}_Locker{num}.png').convert('RGBA')
                    background.paste(img, (611, 238), img)

                    num += 1

        elif backendType == 'ItemWrap':
            num = 1
            x_value = 68
            for file in os.listdir('cache'):
                if file.startswith(f'{backendType}_Locker'):
                    img = Image.open(f'cache/{backendType}_Locker{num}.png').convert('RGBA')
                    background.paste(img, (x_value, 525), img)

                    num += 1
                    x_value += 95


        elif backendType == 'Dance':
            num = 1
            x_value = 68
            for file in os.listdir('cache'):
                if file.startswith(f'{backendType}_Locker'):
                    img = Image.open(f'cache/{backendType}_Locker{num}.png').convert('RGBA')
                    background.paste(img, (x_value, 407), img)

                    num += 1
                    x_value += 95

        elif backendType == 'MusicPack':
            num = 1
            x_value = 163
            for file in os.listdir('cache'):
                if file.startswith(f'{backendType}_Locker'):
                    img = Image.open(f'cache/{backendType}_Locker{num}.png').convert('RGBA')
                    background.paste(img, (x_value, 643), img)

                    num += 1
                    x_value += 95

        elif backendType == 'LoadingScreen':
            num = 1
            x_value = 260
            for file in os.listdir('cache'):
                if file.startswith(f'{backendType}_Locker'):
                    img = Image.open(f'cache/{backendType}_Locker{num}.png').convert('RGBA')
                    background.paste(img, (x_value, 643), img)

                    num += 1
                    x_value += 95

                

    response = requests.post(f'https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/profile/{accountID}/client/QueryProfile?profileId=common_core',  json= {
        
    }, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
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
            #if counter >=2 or counter == 1:
            result.append(quantity)
    
    Sum = sum(result)

    loadFont = 'fonts/BurbankSmall-Bold.otf'
    draw=ImageDraw.Draw(background)

    font=ImageFont.truetype(loadFont,30)
    draw.text((1641,36),f"{Sum}",font=font,fill=(15, 194, 255)) # Writes VBucks sum

    draw.text((126,38),f"{accountName}'s Locker",font=font,fill='white') # Writes name

    background.save('test.png')

    end = time.time()

    embed = discord.Embed(
        title = f"{accountName}'s Fortnite BR Locker"
    )
    file = discord.File(f"test.png", filename="image.png")
    embed.set_image(url="attachment://image.png")
    embed.set_footer(text=f'Generated with the Fortnite Interactions discord bot in {round(end - start, 2)} seconds')
    await ctx.send(embed=embed, file=file)
    #await ctx.send('Heres your generated locker image',file=discord.File('test.png'))
                
@slash.slash(name='addfriend', description='Sends a friend request to a Epic Games account!', guild_ids=testing_guilds, options=[
    create_option(
        name='username',
        description='The username of the friend you want to add',
        option_type=3,
        required=True
    )
])
async def addfriend(ctx, username:str):

    DiscordauthorID = ctx.author.id
    data = ''
    test = test_user_auth(DiscordauthorID, data)

    s1 = json.dumps(test)
    i = json.loads(s1)

    token = i['token']
    accountID = i['accountID']

    response = requests.get(f'https://fortnite-api.com/v2/stats/br/v2?name={username}', headers=headerslmao)
    if response.json()['status'] != 200:
        embed = discord.Embed(
            color = discord.Colour.red(),
            title='ERROR',
            description='This account does not exist.'
        )
        return await ctx.send(embed=embed)

    friendID = response.json()['data']['account']['id']
    friendName = response.json()['data']['account']['name']
    
    
    response = requests.post(f'https://friends-public-service-prod06.ol.epicgames.com/friends/api/public/friends/{accountID}/{friendID}', headers={"Authorization": f"bearer {token}"})

    try:
        errorCode = response.json()['errorCode']

        if "errors.com.epicgames.common.authentication.token_verification_failed" in errorCode:
            embed = discord.Embed(
                color = discord.Colour.red(),
                title='ERROR',
                description='Your token has most likely expired! Type /login <auth> to generate a new one.'
            )
            return await ctx.send(embed=embed)
        elif "errors.com.epicgames.friends.duplicate_friendship" in errorCode:
            embed = discord.Embed(
                color = discord.Colour.red(),
                title='ERROR',
                description='You are already friends with this user!'
            )
            return await ctx.send(embed=embed)
        elif "errors.com.epicgames.friends.account_not_found" in errorCode:
            embed = discord.Embed(
                color = discord.Colour.red(),
                title='ERROR',
                description='This account does not exist.'
            )
            return await ctx.send(embed=embed)
        elif "errors.com.epicgames.friends.cannot_friend_due_to_target_settings" in errorCode:
            embed = discord.Embed(
                color = discord.Colour.red(),
                title='ERROR',
                description='Can not send friend request due to users target settings.'
            )
            return await ctx.send(embed=embed)
        elif "errors.com.epicgames.friends.incoming_friendships_limit_exceeded" in errorCode:
            embed = discord.Embed(
                color = discord.Colour.red(),
                title='ERROR',
                description='Can not send friend request due to users friendships has exceeded the max limit.'
            )
            return await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                color = discord.Colour.red(),
                title='ERROR',
                description=f"UNKNOWN ERROR: *{errorCode}*"
            )
            return await ctx.send(embed=embed)
    except:
        embed = discord.Embed(
            color = discord.Colour.green(),
            title='Success!',
            description=f"Successfully sent a friend request to: **{friendName}**!"
        )
        return await ctx.send(embed=embed)

def check_if_it_is_me(ctx):
    return ctx.author.id == 776811214893875211
    # Fevers, ral, stormzy, nickname, ender, jacobb, deviantionsz

@slash.slash(name='logout_all_users', description='Logs out of all users accounts. ADMIN ONLY', guild_ids=testing_guilds)
@commands.check(check_if_it_is_me)
async def logoutall(ctx):

    new_file = {
        "version": "0.1",
        "auths": []
    }

    a_file = open(f"auths.json", "w")
    json.dump(new_file, a_file, indent = 4)

    await ctx.send('Removed all users data and logged out of all accounts.')
            
@slash.slash(name='verify_token', description='Verify your Fortnite Auth token.', guild_ids=testing_guilds)
async def testauth(ctx):
    DiscordauthorID = ctx.author.id
    data = ''
    test = test_user_auth(DiscordauthorID, data)

    s1 = json.dumps(test)
    i = json.loads(s1)
            
    try:
        token = i['token']
    except:
        embed = discord.Embed(
            color = discord.Colour.red(),
            title='ERROR',
            description='You are not logged in! Make if you want to login, type **/login <auth>**'
        )
        return await ctx.send(embed=embed)

    response = requests.get(f'https://account-public-service-prod.ol.epicgames.com/account/api/oauth/verify',  json={"text": {}}, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    )

    try:
        error = response.json()['errorMessage']
        embed = discord.Embed(
            color = discord.Colour.red(),
            title='ERROR',
            description='Your token has most likely expired! Type **/login <auth>** to generate a new one.'
        )
        return await ctx.send(embed=embed)
    except:
        expires_at = response.json()['expires_at']
        embed = discord.Embed(
            color = discord.Colour.green(),
            title='SUCCESS!',
            description=f'Your token is still valid until **{expires_at}**.\nIf you want to generate a new one, type **/login <auth>**'
        )
        return await ctx.send(embed=embed)

@slash.slash(name='test_command', description='a command to test stuff', guild_ids=testing_guilds)
async def test_command(ctx):
    DiscordauthorID = ctx.author.id
    data = ''
    test = test_user_auth(DiscordauthorID, data)

    s1 = json.dumps(test)
    response = json.loads(s1)
    print(response['token'])

    
    
    # We have now gotten the user auth. Now, we authenticate the auth token.


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
client.run('token')

