import pytextnow

import discord
from discord.ext.commands import Bot

import pymongo
from pymongo import MongoClient

import os

import dotenv
from dotenv import load_dotenv

onlineannouncements = [952019407465480292] #952019407465480292]
instoreannouncements = [952019354806022185,967639841330307133] #952019354806022185]
test = [967639841330307133]

privateverify = 967621988728320030
logid = 967612380857110619

verifyid =  967621837582376961


load_dotenv()

#logging into textnow
tnclient = pytextnow.Client(os.getenv("TN_USER"), sid_cookie=os.getenv("TN_SID"), csrf_cookie=os.getenv("TN_CSRF"))
print("logged onto textnow")

#logging into database
cluster = MongoClient(os.getenv("CLUSTER_URL"))
db = cluster["FlockDepot"]
members = db["members"]
print("logged in to mongodb")

#logging into discord
bot = Bot(command_prefix='$')
@bot.event
async def on_ready():
  print(f'Bot connected as {bot.user}')


@bot.event
async def on_message(message):
  logchannel = bot.get_channel(int(logid))
  msg = message.content.lower()
  if msg[0:8] == "!verify ":
    try:
      print("trying")
      number = int(msg[8:])
      myquery = {"_id":message.author.id}
      print("made query")
      if message.channel.id == privateverify:
        print("in private verify")
        print(members.count_documents(myquery))
        if members.count_documents(myquery)==0:
          print("creating new")
          try:
            print("try 2")
            tnclient.send_sms(str(number),"verified for instore and online notifications")
            post = {"_id": message.author.id, "number":number,"online":True,"instore":True}
            members.insert_one(post)
            await message.author.send("Please check your texts for a message. If there is nothing reverify")
            await logchannel.send(f"<@{str(message.author.id)}> verified for instore and online, {str(number)}")
            await message.delete()
          except:
            await message.author.send("not a valid phone number")
            await message.delete()
        else:
          try:
            tnclient.send_sms(str(number),"verified for instore and online notifications")
            post = {"$set":{"number":number},"$set":{"online":True},"$set":{"instore":True}}
            members.update_one({"_id": message.author.id},{"$set":{"online":True}})
            members.update_one({"_id": message.author.id},{"$set":{"instore":True}})
            await message.author.send("Please check your texts for a message. If there is nothing reverify")
            await logchannel.send(f"<@{str(message.author.id)}> verified for instore and online, {str(number)}")
            await message.delete()
          except:
            await message.author.send("not a valid phone number")
            await message.delete()
      else:
        if members.count_documents(myquery) ==0:
          try:
            tnclient.send_sms(str(number),"verified for online notifications")
            post = {"_id": message.author.id, "number":number,"online":True}
            members.insert_one(post)
            await message.author.send("Please check your texts for a message. If there is nothing reverify")
            await logchannel.send(f"<@{str(message.author.id)}> verified for online, {str(number)}")
            await message.delete()
          except:
            await message.author.send("not a valid phone number")
            await message.delete()
        else:
          try:
            tnclient.send_sms(str(number),"verified for online notifications")
            post = {"$set":{"number":number},"$set":{"online":True}}
            members.update_one({"_id": message.author.id},{"$set":{"online":True}})
            await message.author.send("Please check your texts for a message. If there is nothing reverify")
            await logchannel.send(f"<@{str(message.author.id)}> verified for online, {str(number)}")
            await message.delete()
          except:
            await message.author.send("not a valid phone number")
            await message.delete()
    except:
      await message.author.send("not a number")
      await message.delete()
  elif message.channel.id in onlineannouncements:
    data = members.find()
    for i in data:
      try:
        tnclient.send_sms(str(i["number"]),msg)
        await logchannel.send(f"message sent to <@{i['_id']}>")
      except:
        print(f"message could not be sent to <@{i['_id']}>")
        await logchannel.send(f"message could not be sent to <@{i['_id']}>")
  elif message.channel.id in instoreannouncements:
    data = members.find({"instore":True})
    for i in data:
      try:
        tnclient.send_sms(str(i["number"]),msg)
        await logchannel.send(f"message sent to <@{i['_id']}>")
      except:
        print((f"message could not be sent to <@{i['_id']}>"))
        await logchannel.send(f"message could not be sent to <@{i['_id']}>")


bot.run(os.getenv("DISCORD_KEY"))
