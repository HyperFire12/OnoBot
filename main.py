import os  # Import os dependency
import discord  # Import discord dependency
import requests
import json
import re
import pymongo
# import openai
import random
import string
from OSRSItem import OSRSItem

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
mongoclient = pymongo.MongoClient("mongodb+srv://HyperFire12:"+os.environ.get('PW')+"@profiles.yc6ochs.mongodb.net/?retryWrites=true&w=majority")
db = mongoclient.profiles
# openai.api_key = os.environ.get("AI_TOKEN")

daily = [
  
]

margin = [
  
]

# commands = ["- !price (item)","- !daily {add/remove (item) or list (@User/User ID)}","- !margin {price}", "- !herbs", "- !nuts", "- !image {1-10} {256, 512 or 1024}", "- !recipe (breakfast, lunch, dinner, snack or teatime)"]
commands = ["- !price (item)","- !daily {add/remove (item) or list (@User/User ID)}","- !margin {price}", "- !herbs", "- !nuts", "- !recipe (breakfast, lunch, dinner, snack or teatime)"]
  
error = [7228, 7466, 8624, 8628, 8626, 4595, 22636, 22634, 26602, 2203, 22622, 22613, 22610, 22647]

async def PrintHelp(message):
  s = "```Commands:"
  for x in commands:
    s += "\n" + x
  s += "\n() - mandatory, {} - optional```"
  await message.channel.send(s)

# Returns the ID of the item
def GetItem(name):
  name = name.strip().lower()
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

# Adds or Removes from the daily list
async def ChangeItem(message, name, type):
  await message.channel.send("Processing")
  name = name.strip().lower()
  collection_name = mongoclient["profiles"][str(message.author.id)]
  found = 0
  if(type == "add"):
    for x in collection_name.find({"item":name}):
      found = 1
    if(found == 1):
      await message.channel.send("Already Added")
    else:
      collection_name.insert_one({"item":name.lower()})
      await message.channel.send("Added")
  if(type == "remove"):
    for x in collection_name.find({"item":name}):
      found = 1
    if(found == 1):
      collection_name.delete_one({"item":name.lower()})
      await message.channel.send("Removed")
    else:
      await message.channel.send("Not In The List")

# Prints out the daily array
async def PrintDaily(message, author):
  await message.channel.send("Processing")
  priceUrl = "https://prices.runescape.wiki/api/v1/osrs/latest"
  headers = {
    'User-Agent': 'HyperFire12',
  }
  priceResponse = requests.get(priceUrl, headers=headers)
  priceJson_data = json.loads(priceResponse.text)

  if(str(author) in mongoclient["profiles"].list_collection_names()):
    collection_name = mongoclient["profiles"][str(author)]
  else:
    await message.channel.send("Cannot Find User's List")
    return 
  for r in collection_name.find().sort("item"):
    item = OSRSItem(string.capwords(r["item"]),GetItem(r["item"]))
    item_low = priceJson_data["data"][str(item.id)]["low"]
    item_high = priceJson_data["data"][str(item.id)]["high"]
    item.changePrice(item_low, item_high)
    daily.append(item)
  s = "`"
  i = 0
  x = len(daily)
  while(i < x):
    toAdd = daily[i].name + " - Low Price: " + "{:,}".format(daily[i].low) + ", High Price: " + "{:,}".format(daily[i].high) + "\n"
    if(len(s) + len(toAdd) + 1 > 2000):
      s += "`"
      await message.channel.send(s)
      s = "`"
    s += toAdd
    i += 1
  s += "`"
  await message.channel.send(s)

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

# Prints the margin array with a cap
async def PrintMargins(message, max):
  await message.channel.send("Processing")
  GetMargins()
  s = "`"
  i = 0
  x = 30
  while(i < x):
    if(int(margin[i].low) > max or int(margin[i].high > max)):
      margin.pop(i)
    else:
      toAdd = margin[i].name + " - Low Price: " + "{:,}".format(margin[i].low) + ", High Price: " + "{:,}".format(margin[i].high) + ", Margin: " + "{:,}".format(margin[i].margin) + "\n"
      if(len(s) + len(toAdd) + 1 > 2000):
        s += "`"
        await message.channel.send(s)
        s = "`"
      s += toAdd
      i += 1
  s += "`"
  await message.channel.send(s)

async def PrintHerbs(message):
  await message.channel.send("Processing")
  rs = GetPrice("Ranarr Seed")
  if(rs[1] > rs[0]):
    rseed = rs[0]
  else:
    rseed = rs[1]
  rw = GetPrice("Ranarr Weed")
  if(rw[1] > rw[0]):
    rweed = rw[1]
  else:
    rweed = rw[0]
  ss = GetPrice("Snapdragon Seed")
  if(ss[1] > ss[0]):
    sseed = ss[0]
  else:
    sseed = ss[1]
  sw = GetPrice("Snapdragon")
  if(sw[1] > sw[0]):
    snap = sw[1]
  else:
    snap = sw[0]
  rp = rweed*88 - rseed*9
  sp = snap*88 - sseed*9
  if(rp > sp):
    await message.channel.send("You should plant Ranarr Seeds")
    await message.channel.send("`Ranarr Seed: " + "{:,}".format(rseed) +"`\n`Ranarr Weed: " + 
                                 "{:,}".format(rweed) + "`\n`Ranarr Profitability: " + "{:,}".format(rp) + "`")
    await message.channel.send("---")
    await message.channel.send("`Snapdragon Seed: " + "{:,}".format(sseed) + "`\n`Snapdragon: " + 
                                 "{:,}".format(snap) + "`\n`Snapdragon Profitability: " + "{:,}".format(sp) + "`")
  else:
    await message.channel.send("You should plant Snapdragon Seeds")
    await message.channel.send("`Snapdragon Seed: " + "{:,}".format(sseed) + "`\n`Snapdragon: " + 
                                 "{:,}".format(snap) + "`\n`Snapdragon Profitability: " + "{:,}".format(sp) + "`")
    await message.channel.send("---")
    await message.channel.send("`Ranarr Seed: " + "{:,}".format(rseed) +"`\n`Ranarr Weed: " + 
                                 "{:,}".format(rweed) + "`\n`Ranarr Profitability: " + "{:,}".format(rp) + "`")

# async def PrintImage(message, p, num, size):
#   await message.channel.send("Processing")
#   match size:
#     case 256:
#       s = "256x256"
#     case 512:
#       s = "512x512"
#     case 1024:
#       s = "1024x1024"
#   response = openai.Image.create(
#     prompt = str(p),
#     n = int(num),
#     size = str(s)
#   )
#   i = 0
#   while(i < num):
#     await message.channel.send(response["data"][i]["url"])
#     i += 1

async def PrintRecipe(message, meal):
  await message.channel.send("Processing")
  url = "https://api.edamam.com/api/recipes/v2?type=public&app_id=" + os.environ.get('RECIPE_ID') + "&app_key=" + os.environ.get('RECIPE_API') + "%09&diet=balanced&mealType=" + meal
  response = requests.get(url)
  json_data = json.loads(response.text)
  # option = int(random.random()*int(json_data["count"]))
  option = int(random.random()*100)
  while(option > int(json_data["to"])):
    url = json_data["_links"]["next"]["href"]
    response = requests.get(url)
    json_data = json.loads(response.text)
  option -= int(json_data["from"])
  await message.channel.send(json_data["hits"][option]["recipe"]["shareAs"])

@client.event  # Registers an event
async def on_ready():  # Will be called when bot is ready to be used
  print('We have logged in as {0.user}'.format(client))
  await client.change_presence(activity=discord.Activity(name="!help", type=1))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  if message.content.startswith('!help'):
    await PrintHelp(message)

  if message.content.startswith('!nuts'):
    price = GetPrice("monkey nuts")
    await message.channel.send("Deez Nuts HA Gottem")
    await message.channel.send("`" + "Monkey Nuts" + " - Low Price: " + "{:,}".format(price[0]) +", High Price: " + 
                                 "{:,}".format(price[1]) + "`")

  if message.content.startswith('!price'):
    name = message.content.split("!price")
    price = GetPrice(name[1])
    newname = string.capwords(name[1])
    
    if price == -1:
      await message.channel.send("Unable to find item.")
    else:
      await message.channel.send("`" + newname + " - Low Price: " + "{:,}".format(price[0]) +", High Price: " + 
                                 "{:,}".format(price[1]) + "`")

  if message.content.startswith('!daily'):
    mess = message.content.split()
    if(len(mess) == 1):
      await PrintDaily(message, message.author.id)
      daily.clear()
    else:
      if(mess[1] == "add"):
        m = message.content.removeprefix("!daily add")
        if(GetItem(m) == -1):
          await message.channel.send("Invalid")
        else:
          await ChangeItem(message, m, "add")
      else:
        if(mess[1] == "remove"):
          m = message.content.removeprefix("!daily remove")
          await ChangeItem(message, m, "remove")
        else:
          if(len(mess) == 3):
            m = mess[2].strip("<>@")
            if(mess[1] == "list" and m.isnumeric()):
              await PrintDaily(message, m)
              daily.clear()
            else:
              await message.channel.send("Please Enter a Valid User")
          else:
            await message.channel.send("Invalid")

  if message.content.startswith('!margin'):
    mess = message.content.split()
    if(len(mess) == 1):
      await PrintMargins(message, 2147483647) # 2147483647 is max cash
      margin.clear()
    else:
      if(re.search("^\d+(k|m|b|)$", mess[1])):
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
        margin.clear()
      else:
        await message.channel.send("Invalid")

  if message.content.startswith('!herb'):
    await PrintHerbs(message)
  
  # if message.content.startswith('!image'):
  #   mess = message.content.split()
  #   if(mess[1].isnumeric()):
  #     if(1 <= int(mess[1]) <= 10):
  #       if(mess[2].isnumeric()):
  #         if(int(mess[2]) in (256, 512, 1024)):
  #           n=int(mess[1])
  #           size=int(mess[2])
  #           prompt = message.content.removeprefix("!image " + str(mess[1]) + " " + str(mess[2]) + " ")
  #           await PrintImage(message, prompt, n, size)
  #       else:
  #         n=int(mess[1])
  #         size=256
  #         prompt = message.content.removeprefix("!image " + str(mess[1]) + " ")
  #         await PrintImage(message, prompt, n, size)
  #     else:
  #       if(int(mess[1]) in (256, 512, 1024)):
  #         n=1
  #         size=int(mess[1])
  #         prompt = message.content.removeprefix("!image " + str(mess[1]) + " ")
  #         await PrintImage(message, prompt, n, size)
  #       else:
  #         n=1
  #         size=256
  #         prompt = message.content.removeprefix("!image ")
  #         await PrintImage(message, prompt, n, size)
  #   else:
  #     n=1
  #     size=256
  #     prompt = message.content.removeprefix("!image ")
  #     await PrintImage(message, prompt, n, size)
  
  if message.content.startswith('!recipe'):
    mess = message.content.split()
    if(len(mess) == 2):
      match(mess[1].lower()):
        case "breakfast":
          await PrintRecipe(message, "Breakfast")
        case "lunch":
          await PrintRecipe(message, "Lunch")
        case "dinner":
          await PrintRecipe(message, "Dinner")
        case "snack":
          await PrintRecipe(message, "Snack")
        case "teatime":
          await PrintRecipe(message, "Teatime")
        case _: 
          await message.channel.send("Select either Breakfast, Lunch, Dinner, Snack or Teatime")

my_secret = os.environ.get('TOKEN')  # Environment variables - Hidden Token
client.run(my_secret)  # Run the client
