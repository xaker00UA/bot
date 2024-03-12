import aiohttp
async def search(name,region):

    params={"application_id":"6645d2ba41b7ded38e934bd6fdd48d05","search":name,"type":"exact","fields":"account_id"}
    if region=="eu":
        api="https://api.wotblitz.eu/wotb/account/list/"
    elif region=="na":
        api="https://api.wotblitz.com/wotb/account/list/"
    elif region=="asia":
        api="https://api.wotblitz.asia/wotb/account/list/"
    else:
        raise ValueError("Invalid region")
    try:
        async with aiohttp.ClientSession()as session:
            async with session.get(api,params=params)as response:
               
                results=await response.json()
                
                if "data" in results and results["data"]:
                    
                    return results["data"][0]["account_id"]
                else:
                    return None
               
    except aiohttp.ClientError as err:
        print("AIOHTTP client error occurred:", err)
    except Exception as err:
        print("Error occurred:", err)
