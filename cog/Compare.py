
from cog import DataBase



async def name_tank(tank_id):
    result = await DataBase.name_tank(tank_id=tank_id)
    if result is None:
        return {"name":"unknown","tier":"unknown"}
    del result["tank_id"]
    del result["_id"]
    return result
async def Calculate(now:dict,old:dict)  ->dict:
    result={}
    a={}
    for key in now:
        a[key]  = now[key]-old[key]
    if a["battles"]==0:
        return None
    else:
        result["battles"] = a["battles"]
        result["wins"] = round(a["wins"]/a["battles"]*100,2)
        result["damag"] = round(a["damage_dealt"]/a["battles"],2) 
        result["accuracy"] = round(a["hits"]/a["shots"]*100,2)
        result["survived"] = round(a["survived_battles"]/a["battles"]*100,2)
        result["kkd"] = round(result["damag"]/(a["damage_received"]/a["battles"]),2)
        return result

async def Com(data:dict)  ->dict:
    result={}
    for key,val in data["stata"]["statistics"]["all"].items():
        result[key] = val
    return result
async def com(now:list,old:list)  ->list:
    
    now_results={} 
    old_results={}
    summ=[]
    n=len(now)-len(old)    
    if n!=0:
        old_id={item["tank_id"] for item in old}
        now_id={item["tank_id"] for item in now}
        tank_id=now_id-old_id
        elevents=[item for item in now if item["tank_id"] in tank_id]
        now=[d for d in now if d.get("tank_id") not in tank_id]
        now=sorted(now,key=lambda x: x["tank_id"])
        old=sorted(old,key=lambda x: x["tank_id"])
        for i in range(len(old)):
            if now[i]!=old[i] and old[i]["tank_id"]==now[i]["tank_id"]:
                a = await name_tank(now[i]["tank_id"])
                for j in now[i]["all"]:
                    now_results[j]=(now[i]["all"][j])
                for j in old[i]["all"]:
                    old_results[j]=(old[i]["all"][j])
                b = await Calculate(now=now_results,old=old_results)
                a.update(b)
                summ.append(a)
        for i in range(len(elevents)):
            a = await name_tank(elevents[i]["tank_id"])
            for j in now[i]["all"]:
                now_results[j]=(elevents[i]["all"][j])
            old_results=now_results.copy()
            for j in old_results:
                old_results[j]=0
            b = await Calculate(now=now_results,old=old_results)
            a.update(b)
            summ.append(a) 
        return summ
    else:
        for i in range(len(old)):
       
            if now[i]!=old[i]:
                a = await name_tank(now[i]["tank_id"])
                for j in now[i]["all"]:
                    now_results[j]=((now[i]["all"][j]))
                for j in old[i]["all"]:
                    old_results[j]=((old[i]["all"][j]))
                b = await Calculate(now=now_results,old=old_results)
                a.update(b)
                summ.append(a)  
           
    return summ


async def examination(general_now,general_old,tank_old,tank_now)  ->set:
    x= await Com(general_old)
    y= await Com(general_now)
    a= await Calculate(now=y,old=x)
    if a is not None:

        b= await com(now=tank_now["stata"],old=tank_old["stata"])
        return a,b
    else:
        return None







    

