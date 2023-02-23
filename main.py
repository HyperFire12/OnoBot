import os  # Import os dependency
import discord  # Import discord dependency
import requests
import json
import string
from OSRSItem import OSRSItem

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

daily = [
  
]

margin = [
  
]
  
error = [7228, 7466, 8624, 8628, 8626, 4595, 22636, 22634, 26602, 2203, 22622, 22613, 22610, 22647]

#TODO:Watchlist
#!add [id] [nickname]
#returns [Full name] [low price]
#!remove [nickname]
#removes nicknamed item from watchlist

# Returns the ID of the item
def GetItem(name):
  url = "https://prices.runescape.wiki/api/v1/osrs/mapping"
  headers = {
    'User-Agent': 'HyperFire12',
  }
  response = requests.get(url, headers=headers)
  json_data = json.loads(response.text)
  i = 0
  while i < len(json_data):
    if json_data[i]["name"].lower() == name:
      return json_data[i]["id"]
    i += 1
  return -1

# Returns the low and high price of the item
def GetPrice(name):
  id = GetItem(name)
  if id == -1:
    return -1
  else:
    url = "https://prices.runescape.wiki/api/v1/osrs/latest?id=" + str(id) + "/1m"
    headers = {
      'User-Agent': 'HyperFire12',
    }
    response = requests.get(url, headers=headers)
    json_data = json.loads(response.text)
    item_low = json_data["data"][str(id)]["low"]
    item_high = json_data["data"][str(id)]["high"]
    item = [item_low,item_high]
    return(item)

# Adds the name and price to the daily array
def AddPrice(name):
  price = GetPrice(name.lower())
  daily.append(name)
  daily.append(price[0])
  daily.append(price[1])

# Prints out the daily array
async def PrintPrice(message):
  str = "`"
  i = 0
  x = len(daily)
  while(i < x):
    str += daily[i] + " - Low Price: " + "{:,}".format(daily[i+1]) + ", High Price: " + "{:,}".format(daily[i+2]) + "\n"
    i += 3
  str += "`"
  await message.channel.send(str)

# Adds margins to the margin array
def GetMargins():
  url = "https://prices.runescape.wiki/api/v1/osrs/mapping"
  priceUrl = "https://prices.runescape.wiki/api/v1/osrs/latest"
  headers = {
    'User-Agent': 'HyperFire12',
  }
  priceResponse = requests.get(priceUrl, headers=headers)
  priceJson_data = json.loads(priceResponse.text)
  response = requests.get(url, headers=headers)
  json_data = json.loads(response.text)
  i = 0

  # Inserts the item based on its margin 
  while(i < len(json_data)-1):
    if(int(json_data[i]["value"]) != 0):
      for x in error:
        if(int(json_data[i]["id"]) == x):
          i += 1
      item = OSRSItem(json_data[i]["name"],json_data[i]["id"])
      item_low = priceJson_data["data"][str(item.id)]["low"]
      item_high = priceJson_data["data"][str(item.id)]["high"]
      item.changePrice(item_low, item_high)
      
      j = 0
      inserted = 0
      if(len(margin) == 0):
        margin.append(item)
      else:
        while(j < len(margin)):
          if(margin[j].margin < item.margin):
            margin.insert(j, item)
            inserted = 1
            break
          j += 1
        if(inserted == 0):
          margin.append(item)
    i += 1

# Prints the margin array
async def PrtMargins(message):
  await message.channel.send("Processing")
  GetMargins()
  str = "`"
  i = 0
  x = 20
  while(i < x):
    str += margin[i].name + " - Low Price: " + "{:,}".format(margin[i].low) + ", High Price: " + "{:,}".format(margin[i].high) + ", Margin: " + "{:,}".format(margin[i].margin) + "\n"
    i += 1
  str += "`"
  await message.channel.send(str)

# Prints the margin array with a cap
async def PrintMargins(message, max):
  await message.channel.send("Processing")
  GetMargins()
  str = "`"
  i = 0
  x = 20
  while(i < x):
    if(int(margin[i].low) > max or int(margin[i].high > max)):
      margin.pop(i)
    else:
      str += margin[i].name + " - Low Price: " + "{:,}".format(margin[i].low) + ", High Price: " + "{:,}".format(margin[i].high) + ", Margin: " + "{:,}".format(margin[i].margin) + "\n"
      i += 1
  str += "`"
  await message.channel.send(str)

@client.event  # Registers an event
async def on_ready():  # Will be called when bot is ready to be used
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('!nuts'):
    price = GetPrice("monkey nuts")
    await message.channel.send("Deez Nuts HA Gottem")
    await message.channel.send("`" + "Monkey Nuts" + " - Low Price: " + "{:,}".format(price[0]) +", High Price: " + 
                                 "{:,}".format(price[1]) + "`")

  if message.content.startswith('!price'):
    name = message.content.split("!price")
    pricename = name[1].strip().lower()
    price = GetPrice(pricename)
    newname = string.capwords(pricename)
    
    if price == -1:
      await message.channel.send("Unable to find item.")
    else:
      await message.channel.send("`" + newname + " - Low Price: " + "{:,}".format(price[0]) +", High Price: " + 
                                 "{:,}".format(price[1]) + "`")

  if message.content.startswith('!daily'):
    await message.channel.send("Processing")
    AddPrice("Old School Bond")
    AddPrice("Scythe of Vitur (Uncharged)")
    AddPrice("Dragon Hunter Lance")
    AddPrice("Revenant Cave Teleport")
    AddPrice("Christmas Cracker")
    AddPrice("Mort Myre Fungus")
    AddPrice("Bone Fragments")
    AddPrice("Dragon Claws")
    AddPrice("Ancestral Robe Top")
    AddPrice("Ancestral Robe Bottom")
    AddPrice("Imbued Heart")
    AddPrice("Osmumten's Fang")
    AddPrice("Ghrazi Rapier")
    AddPrice("Red Spiders' Eggs")
    AddPrice("Snapdragon")
    print(daily)
    await PrintPrice(message)
    daily.clear()

  if message.content.startswith('!margin'):
    mess = message.content.split()
    if(len(mess) == 1):
      await PrtMargins(message)
      margin.clear()
    else:
      if(mess[1].isnumeric()):
        await PrintMargins(message, int(mess[1]))
      else:
        if(mess[1][len(mess[1])-1] in ("k","m","b") and (mess[1][:len(mess[1])-1].isnumeric())):
          deg = mess[1][len(mess[1])-1]
          m = mess[1].rstrip("kmb")
          match deg:
            case "k":
              m += "000"
            case "m":
              m += "000000"
            case "b":
              m += "000000000"
          await PrintMargins(message, int(m))
        else:
          await message.channel.send("Invalid")
      margin.clear()
         
my_secret = os.environ.get('TOKEN')  # Environment variables - Hidden Token
client.run(my_secret)  # Run the client
