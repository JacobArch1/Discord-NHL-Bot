import os
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from typing import Final, Optional
from responses import get_response

load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='help')
    async def help_command(self, interaction: discord.Interaction):
        response = get_response('help', None)
        await interaction.response.send_message(embed=response, ephemeral=True)

    @app_commands.command(name='glossary')
    async def glossary_command(self, interaction: discord.Interaction):
        response = get_response('glossary', None)
        await interaction.response.send_message(embed=response, ephemeral=True)

    @app_commands.command(name='playerstats')
    @app_commands.describe(player="Enter first and last name, capitalize each.")
    async def playerstats_command(self, interaction: discord.Interaction, player: str):
        response = get_response('playerstats', player)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name='standings')
    @app_commands.describe(season="Get standings by year. Format: YYYY-YYYY")
    async def standings_command(self, interaction: discord.Interaction, season: Optional[str] = None):
        if season:
            response = get_response('standings', season)
        else:
            response = get_response('currentstandings', None)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name='leaders')
    @app_commands.describe(position="Skater or goalie")
    @app_commands.describe(category="Use /glossary for list of categories")
    async def leaders_command(self, interaction: discord.Interaction, position: str, category: str):
        params = f'{position} {category}'
        response = get_response('leaders', params)
        await interaction.response.send_message(embed=response)
    
    @app_commands.command(name="teamroster")
    @app_commands.describe(team="Enter the team you want the roster for")
    @app_commands.describe(season="Get team roster by year. Format: YYYY-YYYY")
    async def teamroster_command(self, interaction: discord.Interaction, team: str, season: Optional[str] = 'current'):
        params = f'{team} {season}'
        response = get_response('teamroster', params)
        await interaction.response.send_message(embed=response)

    @app_commands.command(name="playoffbracket")
    async def playoffbracket_command(self, interaction: discord.Interaction):
        response = get_response('playoffbracket', None)
        await interaction.response.send_message(embed=response)

async def setup(bot):
    if 'Commands' not in bot.cogs:
        await bot.add_cog(Commands(bot))
    else:
        print('Cog named "Commands" is already loaded')
    await bot.tree.sync()

@bot.event
async def on_ready() -> None:
    print(f'{bot.user} is now running')
    await setup(bot)

def main() -> None:
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
