
import aiohttp
import datetime
async def session(user,region):  #функция для среза статистики по танкам
    fild="all.battles, all.damage_received, all.damage_dealt, all.hits, all.shots, all.survived_battles, all.wins, tank_id, account_id"
    params={"application_id":"6645d2ba41b7ded38e934bd6fdd48d05","account_id":user,"fields":fild}
    if region=="eu":
        api="https://api.wotblitz.eu/wotb/tanks/stats/"
    elif region=="na":
        api="https://api.wotblitz.com/wotb/tanks/stats/"
    elif region=="asia":
        api="https://api.wotblitz.asia/wotb/tanks/stats/"
    else:
        raise ValueError("Invalid region")
    try:
        async with aiohttp.ClientSession()as session:
            async with session.get(api,params=params)as response:
               
                results=await response.json()
                a={}
                a["id"]=user 
                a["data"]= datetime.datetime.now().replace(microsecond=0).strftime("%d-%m-%Y %H:%M:%S")
                a["stata"]=results["data"][str(user)]                                                          
                return a
               
               
               
    except aiohttp.ClientError as err:
        print("AIOHTTP client error occurred:", err)
    except Exception as err:
        print("Error occurred:", err)

async def general(user,region):  #функция для среза общей статистики 
    fild="statistics.all.battles, statistics.all.damage_dealt, statistics.all.damage_received, statistics.all.hits, statistics.all.shots, statistics.all.survived_battles, statistics.all.wins"
    params={"application_id":"6645d2ba41b7ded38e934bd6fdd48d05","account_id":user,"fields":fild}
    if region=="eu":
        api="https://api.wotblitz.eu/wotb/account/info/"
    elif region=="na":
        api="https://api.wotblitz.com/wotb/account/info/"
    elif region=="asia":
        api="https://api.wotblitz.asia/wotb/account/info/"
    else:
        raise ValueError("Invalid region")
    try:
        async with aiohttp.ClientSession()as session:
            async with session.get(api,params=params)as response:
               
                results=await response.json()
                a={}
                a["id"]=user 
                a["data"]= datetime.datetime.now().replace(microsecond=0).strftime("%d-%m-%Y %H:%M:%S")
                a["stata"]=results["data"][str(user)]             
                return a
               
               
               
    except aiohttp.ClientError as err:
        print("AIOHTTP client error occurred:", err)
    except Exception as err:
        print("Error occurred:", err)






