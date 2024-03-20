
import discord
from discord.ext import commands
from pymongo import MongoClient
from cog import DataBase,Search,Compare,Get
from config import TOKEN, KEY_DATABASE
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler




async def create_embed(general, state,name,time):



   gen = '\n'.join(f"{key.ljust(15)}: {value}" for key, value in general.items())

   embed=discord.Embed(title=f"Статистика игрока {name}",description=f"Сесия длиться {time}",colour=discord.Color.from_str("#7CFC00"))
   embed.add_field(name="Общая",value=f"```{gen} ```",inline=False)
   for i in state:
      embed.add_field(name=f"{i["name"]}",value=f"```{"\n".join(f"{key.ljust(15)}: {value}" for key,value in i.items() if key !="name" )} ```",inline=False)
   return embed




cluster = MongoClient(KEY_DATABASE)
database=cluster["wotblitz"]
collection=database["user"]

TOKEN = TOKEN 
PREFIX = '!'
intents = discord.Intents().all()


bot = commands.Bot(command_prefix=PREFIX, intents=intents)
bot.remove_command("help")

async def power():
   await DataBase.update()

@bot.event
async def on_ready():
   print(f'{bot.user} has connected to Discord!')
   if cluster.server_info():
      print("Connected to MongoDB")
   else:
      print("Failed to connect to MongoDB")
   scheduler = AsyncIOScheduler()
   scheduler.add_job(power, "cron", hour=5, minute=00)
   scheduler.start()
   

@bot.command(name = "set_player")
async def player(ctx,name=1,region="eu"): 
  
   result = await Search.search(name=name,region=region)
  
   if name ==1:
       await ctx.send("Вы не указали обезательный аргумент никнейм")
   elif result is None:
      await ctx.send("Ник не найден")
   else:
      a={} 
      y = await Get.session(user=result,region=region)
      x = await Get.general(user=result,region=region)  
      userds=ctx.author.id 
      a["discord_id"]=userds
      a["region"]=region
      a["name"]=name
      a["id"]=result    
      await DataBase.set_users(a)
      await DataBase.output(state_tank=y,general=x,user=result)
      await ctx.send(f"Сесия начата для {name}")
   
   

@bot.command(name = "get")
async def get(get,name=None):
  
   if name is not None:
      b=collection.find_one({"name":name})      
   else:       
      userds=get.author.id
      b=collection.find_one({"discord_id":userds})      
   if b is not None:
      user =b.get("id")
      region =b.get("region")
      us = b.get("name")      
      gen1= await Get.general(user=user,region=region)
      tank1= await Get.session(user=user,region=region)
      tank,gen = await DataBase.input(user=user)
      result = await Compare.examination(general_now=gen1,general_old=gen,tank_now=tank1,tank_old=tank)
      time=datetime.datetime.strptime(gen1.get("data"),"%d-%m-%Y %H:%M:%S")-datetime.datetime.strptime(gen.get("data"),"%d-%m-%Y %H:%M:%S")
      if result is not None:
         general, state = result
         a = await create_embed(general=general,state=state,name=us,time=time)
         await get.send(embed=a)

      else:
         await get.send("Вы не сыграли ни одного боя с начала сессии")
   else:
      await get.send("Пользователь не отслежуеться")


@bot.command(name = "start")
async def start(start,name=1,region="eu"):
   result = await Search.search(name=name,region=region)
  
   if name ==1:
       await start.send("Вы не указали обезательный аргумент никнейм")
   elif result is None:
      await start.send("Ник не найден")
   else:
      a={}
      y = await Get.general(user=result,region=region)
      x = await Get.session(user=result,region=region)   
      a["region"]=region
      a["name"]=name
      a["id"]=result    
      await DataBase.users(a)
      await DataBase.output(state_tank=x,general=y,user=result) 
      await start.send(f"Сесия начата для {name}")
   

@bot.command(name = "help")
async def help(ctx):
   with open("help.txt","r",encoding="utf-8")as file:
      a=file.read()
      await ctx.send(embed=discord.Embed(title="Команды",description=a,colour=discord.Color.from_str("#9400D3")))
bot.run(TOKEN)