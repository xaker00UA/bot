
import disnake as discord
from disnake.ext import commands
from pymongo import MongoClient
from cog import DataBase,Search,Compare,Get
from config import TOKEN,KEY_DATABASE
import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler




async def create_embed(general, name,time,state=None):



   gen = '\n'.join(f"{key.ljust(15)}: {value}" for key, value in general.items())

   embed=discord.Embed(title=f"Статистика игрока {name}",description=f"Сесия длиться {time}",colour=discord.Color.from_rgb(124,252,0))
   embed.add_field(name="Общая",value=f"```{gen} ```",inline=False)
   if state is not None:
      for i in state:
         embed.add_field(name=f"{i["name"]}",value=f"```{"\n".join(f"{key.ljust(15)}: {value}" for key,value in i.items() if key !="name" )} ```",inline=False)
   return embed




cluster = MongoClient(KEY_DATABASE)
database=cluster["wotblitz"]
collection=database["user"]

TOKEN = TOKEN
PREFIX = '.'
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
   




@bot.slash_command(name = "set_player",description="Подвязать ДС к акаунту в игре")
async def player(ctx, name:str, region:str=commands.Param (choices={"eu":"eu","na":"com","asia":"asia"})): 
   
   result = await Search.search(name=name,region=region)
  

   if result is None:
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
   
   

@bot.slash_command(name = "get",description="Полуить текущую активную сессию")
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


@bot.slash_command(name = "start",description="Начать снова сессию или зарегестрировать акаунт")
async def start(start,name:str,region:str=commands.Param (choices={"eu":"eu","na":"com","asia":"asia"})):
   result = await Search.search(name=name,region=region)
  
   
   if result is None:
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
   

@bot.slash_command(name="day_sesssion",description="Сессию можно получить за определенное количство дней")
async def day_sesssion(ctx,days:int,name:str=None):
   if days < 0:
      await ctx.send("Введите положительное число")
      return
   elif days>30:
      await ctx.send("Сесиию можно получить только за 30 дней")
      return
   if name is not None:
      b=collection.find_one({"name":name})
   else:
      userds=ctx.author.id
      b=collection.find_one({"discord_id":userds})
   if b is not None:
      user =b.get("id")
      region =b.get("region")
      us = b.get("name")      
      general_now= await Get.general(user=user,region=region)
      general_old = await DataBase.day(user=user,cout_day=days)
      if general_old is None:
         await ctx.send(f"Вы не отслеживаетесь {days} дней")
      result = await Compare.examination(general_now=general_now,general_old=general_old)
      time=datetime.datetime.strptime(general_now.get("data"),"%d-%m-%Y %H:%M:%S")-datetime.datetime.strptime(general_old.get("data"),"%d-%m-%Y %H:%M:%S")
      if result is not None:
         a=await create_embed(general=result,time=time,name=us)
         await ctx.send(embed=a)
      else:
         await ctx.send(f"Вы не сыграли ни одного боя за {days} дней")
   else:
      await ctx.send("Пользователь не отслежуеться")
   



@bot.slash_command(name = "help",description="Инструкция к командам")
async def help(ctx):
   with open("help.txt","r",encoding="utf-8")as file:
      a=file.read()
      await ctx.send(embed=discord.Embed(title="Команды",description=a,colour=discord.Color.from_str("#9400D3")))
bot.run(TOKEN)