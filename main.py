import requests
import time
import csv,json
import threading
from discord_webhook import *
from utils import log,log_error_p,log_info,log_success,get_proxy


Query = []

with open('query.csv','r') as file:
    reader = csv.reader(file)
    header = next(reader)
    if header != None:
        for line in reader:
            skinName,Exterior,isStatTrack = line[0].lower(),line[1].lower(),line[2].lower()
            if isStatTrack == "no":
                isStatTrack = "not_stattrak_tm"
            else:
                isStatTrack = "stattrak_tm"
                
            Query.append([skinName,Exterior,isStatTrack])

with open('config.json','r',encoding='UTF-8') as f:
    configData = json.load(f)
    auth = configData['AuthToken']
    webhookUrl = configData['WebhookUrl']

def Monitor(data):
    title = data[0].replace(' ','%20')
    exterior = data[1].replace(' ','%20')
    isStatTrack = data[2].replace(' ','%20')

    headers = {
        'Host': 'api.dmarket.com',
        'Language': 'PL',
        'Authorization': auth,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 OPR/102.0.0.0',
        'Accept': 'application/json, text/plain, */*',
        'Origin': 'https://dmarket.com',
        'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    while True:
        try:
            responseNew = requests.get(f"https://api.dmarket.com/exchange/v1/market/items?side=market&orderBy=price&orderDir=asc&title={title}&priceFrom=0&priceTo=0&treeFilters=exterior%5B%5D={exterior},category_0%5B%5D={isStatTrack}&gameId=a8db&types=dmarket&limit=100&currency=USD",headers=headers)
            
            newLowestItemId = responseNew.json()['objects'][0]['itemId']
            itemPrice = responseNew.json()['objects'][0]['price']['USD']
            itemTitle = responseNew.json()['objects'][0]['title']
            itemImage = responseNew.json()['objects'][0]['image']
            itemDiscount = responseNew.json()['objects'][0]['discount']
            itemFloatValue = responseNew.json()['objects'][0]['extra']['floatValue']
            itemFloatValueFormatted = round(itemFloatValue,6)
            link = f"https://dmarket.com/pl/ingame-items/item-list/csgo-skins?exchangeTab=exchange&title={str(itemTitle.replace(' ','-'))}"
            itemPriceFormatted = str(int(itemPrice)/100).replace('.',',')

            with open("offers.json","r") as f:
                data = json.load(f)
            
            if newLowestItemId in data['Offers']:
                savedPriceForOffer = data['Offers'][newLowestItemId]['Price']
                if int(savedPriceForOffer) == int(itemPrice):
                    log_info(f"Same lowestOffer | Same price for this Offer")
                    time.sleep(60)
                    continue
                if int(savedPriceForOffer) != int(itemPrice):
                    log_success(f"New price for LowestOffer")
                    
                    webhook = DiscordWebhook(url=webhookUrl, username = 'Dmarket',avatar_url='https://i.imgur.com/fkxcL1b.jpg')
                    embed = DiscordEmbed(title=itemTitle,url=link, color='0x1f4acc',description=f"New Lowest Offer | ID: {newLowestItemId} | Experimental")
                    embed.set_thumbnail(url = itemImage)
                    embed.add_embed_field(name='Price:', value=f"{itemPriceFormatted} USD",inline=True)
                    embed.add_embed_field(name='Discount:', value=f"-{itemDiscount}%",inline=True)
                    embed.add_embed_field(name='FloatValue:', value=f"{str(itemFloatValueFormatted)}",inline=True)
                    embed.set_footer(text=f'by rafał6750',icon_url = 'https://i.imgur.com/fkxcL1b.jpg')
                    embed.set_timestamp()
                    webhook.add_embed(embed)
                    webhook.execute()
                    log_success(f"Webhook sent!")
                    data['Offers'][newLowestItemId]['Price'] = itemPrice

                    with open("offers.json","w") as f:
                        json.dump(data,f,indent=4)

                    continue
            if newLowestItemId not in data['Offers']:
                log_success(f"Found new LowestOffer")
                webhook = DiscordWebhook(url=webhookUrl, username = 'Dmarket',avatar_url='https://i.imgur.com/fkxcL1b.jpg')
                embed = DiscordEmbed(title=itemTitle,url=link, color='0x1f4acc',description=f"New Lowest Offer | ID: {newLowestItemId} | Experimental")
                embed.set_thumbnail(url = itemImage)
                embed.add_embed_field(name='Price:', value=f"{itemPriceFormatted} USD",inline=True)
                embed.add_embed_field(name='Discount:', value=f"-{itemDiscount}%",inline=True)
                embed.add_embed_field(name='FloatValue:', value=f"{str(itemFloatValueFormatted)}",inline=True)
                embed.set_footer(text=f'by rafał6750',icon_url = 'https://i.imgur.com/fkxcL1b.jpg')
                embed.set_timestamp()
                webhook.add_embed(embed)
                webhook.execute()
                log_success(f"Webhook sent!")
                data['Offers'][newLowestItemId] = {"Price":itemPrice}

                with open("offers.json","w") as f:
                    json.dump(data,f,indent=4)

                continue

        except Exception as er:
            raise er
            #log_error_p(str(er))

if __name__ == "__main__":
    if len(auth) >= 40:
        for q in Query:
            thread = threading.Thread(target=Monitor,args=(q,)).start()
    else:
        log_error_p(f"Put your Dmarket auth token in config.json")