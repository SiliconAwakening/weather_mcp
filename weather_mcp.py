from mcp.server.fastmcp import FastMCP

# create a FastMCP instance with routed handlers
mcp = FastMCP("weather_mcp",host="0.0.0.0", port=8000)

# register the tool
@mcp.tool("getWeather", description="获取指定城市的天气数据")
async def get_weather(city: str) -> dict:
    """
    获取指定城市的天气数据
    :param city: 城市名称
    :return: 包含天气状况和温度的字典
    """
    api_key = "YOUR_API_KEY"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    import aiohttp
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                response_data = {
                    "status": "success",
                    "result": {"condition": data["weather"][0]["main"], "temperature": data["main"]["temp"]}
                }
            else:
                response_data = {"status": "error", "message": f"无法获取 {city} 的天气数据"}
            return response_data

@mcp.resource("weather://{location}", description="获取指定位置的天气数据")
async def get_weather_resource(location: str) -> dict:
    """
    获取指定位置的天气数据
    :param location: 位置名称
    :return: 包含天气状况和温度的字典
    """
    return await get_weather(location)

@mcp.prompt()
def weather_prompt(location) -> str:
    """Create a weather report prompt."""
    return  f"""You are a weather reporter. Weather report for {location}?"""

# start the MCP server
if __name__ == "__main__":
    mcp.run(transport="sse")
    
