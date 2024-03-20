import asyncio
from pymongo import MongoClient
from cog import Get
from config import KEY_DATABASE 
cluster = MongoClient(KEY_DATABASE)
database=cluster["wotblitz"]
collection=database["state_machine"]
gen=database["state"]
tank=database["tank"]
player=database["user"]


async def output(user,state_tank,general):
    collection.replace_one(filter={"id":user},replacement=state_tank,upsert=True)
    gen.replace_one(filter={"id":user},replacement=general,upsert=True)

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
    