import asyncio
from pymongo import MongoClient
from cog import Get
import datetime
from config import KEY_DATABASE
cluster = MongoClient(KEY_DATABASE) 
database=cluster["wotblitz"]
collection=database["state_machine"]
gen=database["state"]
tank=database["tank"]
player=database["user"]
daydatabase=database["day"]


async def date(day=31):
    data_30day=datetime.datetime.now().replace(second=0,microsecond=0)-datetime.timedelta(days=day)
    start =data_30day.replace(hour=0, minute=0, second=0)
    end=(start+datetime.timedelta(days=1)).strftime("%d-%m-%Y %H:%M:%S")
    start=start.strftime("%d-%m-%Y %H:%M:%S")
    query={"data":{"$gte":start,"$lte":end}}
    return query
async def output(user,state_tank,general):
    filter=await date()
    collection.replace_one(filter={"id":user},replacement=state_tank,upsert=True)
    gen.replace_one(filter={"id":user},replacement=general,upsert=True)
    daydatabase.replace_one(filter=filter,replacement=general,upsert=True)



async def day(user,cout_day):
    filters= await date(cout_day)
    filters["id"]=user
    try:
        a = daydatabase.find_one(filter=filters)
        del a["_id"]
    except TypeError:
        return None        
    return a
async def input(user):  
    a = collection.find_one(filter={"id":user})
    b = gen.find_one(filter={"id":user})
    del a["_id"]
    del b["_id"]
    return a,b


async def name_tank(tank_id):
    return tank.find_one(filter={"tank_id":tank_id})

async def a(doc):
        user=doc.get("id")
        region=doc.get("region")
        y = await Get.general(user=user,region=region)
        x = await Get.session(user=user,region=region)
        await output(user=user,state_tank=x,general=y)

async def update():
    tasks=[]
    for doc in player.find({}):
        tasks.append(a(doc))
        if len(tasks)==10:
            await asyncio.gather(*tasks)
            tasks=[]
    await asyncio.gather(*tasks)

    
        

async def users(file:dict):
    name = file.get("name")
    player.replace_one(filter={"name":name},replacement=file,upsert=True)

async def set_users(file:dict):
    discord_id = file.get("discord_id")
    player.replace_one(filter={"discord_id":discord_id},replacement=file,upsert=True)
    