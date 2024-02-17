import discord
from discord.ext import commands
from discord import Intents, Embed
import requests
from bs4 import BeautifulSoup
import re

intents = Intents.all()  # Enable all intents
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():   
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    print('------')

def normalize_rank(rank):
    # Remove Roman numerals (IV, III, II, I) and convert to uppercase
    rank = re.sub(r'(?i)(IV|III|II|I)$', '', rank).strip().upper()
    return rank

def get_rank_color(rank):
    # Define a mapping between ranks and colors
    rank_colors = {
        'BRONZE': discord.Color(0xCD7F32),       # Bronze color
        'SILVER': discord.Color(0xC0C0C0),       # Silver color
        'GOLD': discord.Color(0xFFD700),         # Gold color
        'PLATINUM': discord.Color(0x00CED1),     # Platinum color
        'DIAMOND': discord.Color(0x6495ED),      # Diamond color
        'MASTER': discord.Color(0x800080),       # Master color
        'GRANDMASTER': discord.Color(0xFF0000),  # Grandmaster color
        'CHALLENGER': discord.Color(0xFFD700),   # Challenger color (using Gold color for example)
        # Add more ranks and colors as needed
    }

    # Print the extracted rank for debugging
    print("Extracted Rank for Color Assignment:", repr(rank))

    # Normalize the rank by removing Roman numerals and converting to uppercase
    normalized_rank = normalize_rank(rank)

    # Return the color based on the direct comparison of rank names
    return rank_colors.get(normalized_rank, discord.Color.default())

@bot.command(name='profile', help='Get profile info from tracker.gg')
async def profile(ctx, riot_id: str, tag_id: str, region: str):
    url = f"https://tracker.gg/lol/profile/riot/{region}/{riot_id}%23{tag_id}/overview?playlist=RANKED_SOLO_5x5"
    
    try:
        profile = requests.get(url)
        profile.raise_for_status()
    except requests.exceptions.RequestException as e:
        await ctx.send(f"Error retrieving profile: {e}")
        return
    
    try:
        src = profile.content
        soup = BeautifulSoup(src, "lxml")
        
        rank_element = soup.find("span", {"class": "stat__label"})
        lp_element = soup.find("span", {"class": "stat__value"})
        img_element = soup.find("img", {"class": "trn-profile-highlighted-content__icon"})
        win_lose_element = soup.find("span", {"class": "stat__subtext"})

        # Check if any of the required elements is missing
        if not rank_element or not lp_element or not img_element or not win_lose_element:
            raise ValueError("Required elements not found in the HTML content.")

        # Extract text content from HTML elements
        rank = rank_element.text.strip()
        lp = lp_element.text.strip()
        img_link = img_element.get("src")
        win_lose = win_lose_element.text.strip()

        # Get the color based on the direct comparison of rank names
        embed_color = get_rank_color(rank)

        embed = Embed(
            title="Profile Info", 
            description=f"**Rank:** {rank}\n**LP:** {lp}\n**Win-Lose:** {win_lose}", 
            color=embed_color
        )
        
        if img_link:
            embed.set_thumbnail(url=img_link)  # Set thumbnail image if URL is available

        # Add a footer with the developer information
        embed.set_footer(text="Developed By: OmarKadry") 

        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Error parsing profile data: {e}")


bot.run('MTE3NjEyNjE1NTgxNjk3MjI4OA.GwZmHU.4iCsheUhDwaPVAxWUE7qlbcHxDQDTXJJ0mQm7Q')
