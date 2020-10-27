import discord
from discord.ext import commands
import asyncio
import requests
import datetime

TOKEN = "<insert discord token here>"
API_KEY = "<insert nasa api key here>"
DAILY_CHANNEL = "<insert the channel id (integer) where the daily apod should be posted>"

PREFIX = "s!"
COLOUR = discord.Colour.from_rgb(51, 51, 86)


async def wait_until(dt):
    # sleep until the specified datetime
    now = datetime.datetime.now()
    await asyncio.sleep((dt - now).total_seconds())

async def get_apod_embed(date :str):
    # using synchronous requests is a poor idea, but who cares
    apod = requests.get("https://api.nasa.gov/planetary/apod?date={}&api_key={}".format(date, API_KEY)).json()
    if 'code' in apod:
        raise Exception("APOD returned error code {}: {}".format(apod['code'], apod['msg']))
    embed = discord.Embed()
    embed.colour = COLOUR
    embed.title = "Astronomy Picture Of the Day"
    embed.url = "https://apod.nasa.gov/apod/ap{}.html".format("".join(date[2:].split("-")))
    embed.add_field(name="Title", value=apod['title'])
    embed.add_field(name="Date", value=date)
    embed.set_footer(text="All rights to their respective owners!")
    if apod['media_type'] == "image":
        embed.set_image(url = apod['hdurl'] if 'hdurl' in apod else apod['url'])
    elif apod['media_type'] == "video":
        embed.video = apod['url']
    return embed


bot = commands.Bot(PREFIX)

@bot.command()
async def apod(ctx, date: str = ""):
    if not date:
        date = datetime.datetime.now().strftime("%Y-%m-%d")
    embed = await get_apod_embed(date)
    await ctx.channel.send(embed=embed)

async def post_daily():
    if not (channel := bot.get_channel(DAILY_CHANNEL)):
        raise ValueError("DAILY_CHANNEL could not be resolved to a channel") 
    # post daily at 7 AM UTC
    next_post_time = datetime.datetime.utcnow().replace(hour=7,minute=0,second=0,microsecond=0)
    while True:
        next_post_time += datetime.timedelta(days = 1)
        await wait_until(next_post_time)
        date = next_post_time.strftime("%Y-%m-%d")
        embed = await get_apod_embed(date)
        await channel.send(embed=embed)
        
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

    bot.loop.create_task(post_daily())

bot.run(TOKEN)