import datetime
import discord
from collections import defaultdict
import nhl

def get_player_stats(first_name: str, last_name: str) -> discord.Embed:
    player_id = nhl.get_player_id(first_name, last_name)
    if isinstance(player_id, discord.Embed):
        return player_id
    player_info = nhl.get_specific_player_info(player_id)
    if "careerTotals" not in player_info:
        embed = discord.Embed(color=discord.Color.lighter_grey())
        embed.add_field(name = "", value="No stats available for this player", inline=False)
        return embed
    
    if "regularSeason" in player_info["careerTotals"]:
        regular_season_stats = player_info["careerTotals"]["regularSeason"]
    else:
        regular_season_stats = {}
    
    if "playoffs" in player_info["careerTotals"]:
        playoffs_stats = player_info["careerTotals"]["playoffs"]
    else:
        playoffs_stats = {}

    table = [
        "```",
        f"{"Stat":<10}{"RegSe":>7}{"PlOff":>7}{"Total":>7}\n",
    ]

    if player_info.get("position", "?") == "G":
        stats = [
            ("GP:", regular_season_stats.get("gamesPlayed", 0), playoffs_stats.get("gamesPlayed", 0), True),
            ("GS:", regular_season_stats.get("gamesStarted", 0), playoffs_stats.get("gamesStarted", 0), True),
            ("W:", regular_season_stats.get("wins", 0), playoffs_stats.get("wins", 0), True),
            ("L:", regular_season_stats.get("losses", 0), playoffs_stats.get("losses", 0), True),
            ("OT:", regular_season_stats.get("otLosses", 0), playoffs_stats.get("otLosses", 0), True),
            ("SA:", regular_season_stats.get("shotsAgainst", 0), playoffs_stats.get("shotsAgainst", 0), True),
            ("GA:", regular_season_stats.get("goalsAgainst", 0), playoffs_stats.get("goalsAgainst", 0), True),
            ("SO:", regular_season_stats.get("shutouts", 0), playoffs_stats.get("shutouts", 0), True),
            ("A:", regular_season_stats.get("assists", 0), playoffs_stats.get("assists", 0), True),
            ("GAA:", round(regular_season_stats.get("goalsAgainstAvg", 0), 2), round(playoffs_stats.get("goalsAgainstAvg", 0), 2), False),
            ("SV%:", round(regular_season_stats.get("savePctg", 0), 3), round(playoffs_stats.get("savePctg", 0), 3), False),
        ]
    else: 
        stats = [
            ("GP:", regular_season_stats.get("gamesPlayed", 0), playoffs_stats.get("gamesPlayed", 0), True),
            ("G:", regular_season_stats.get("goals", 0), playoffs_stats.get("goals", 0), True),
            ("A:", regular_season_stats.get("assists", 0), playoffs_stats.get("assists", 0), True),
            ("P:", regular_season_stats.get("points", 0), playoffs_stats.get("points", 0), True),
            ("+/-:", regular_season_stats.get("plusMinus", 0), playoffs_stats.get("plusMinus", 0), False),
            ("PIM:", regular_season_stats.get("pim", 0), playoffs_stats.get("pim", 0), True),
            ("PPG:", regular_season_stats.get("powerPlayGoals", 0), playoffs_stats.get("powerPlayGoals", 0), True),
            ("PPP:", regular_season_stats.get("powerPlayPoints", 0), playoffs_stats.get("powerPlayPoints", 0), True),
            ("SHG:", regular_season_stats.get("shorthandedGoals", 0), playoffs_stats.get("shorthandedGoals", 0), True),
            ("SHP:", regular_season_stats.get("shorthandedPoints", 0), playoffs_stats.get("shorthandedPoints", 0), True),
            ("TOI/G:", regular_season_stats.get("avgToi", 0), playoffs_stats.get("avgToi", 0), False),
            ("GWG:", regular_season_stats.get("gameWinningGoals", 0), playoffs_stats.get("gameWinningGoals", 0), True),
            ("OTG:", regular_season_stats.get("otGoals", 0), playoffs_stats.get("otGoals", 0), True),
            ("S:", regular_season_stats.get("shots", 0), playoffs_stats.get("shots", 0), True),
            ("S%:", round(regular_season_stats.get("shootingPctg", 0) * 100, 1), round(playoffs_stats.get("shootingPctg", 0) * 100, 1), False),
            ("FO%:", round(regular_season_stats.get("faceoffWinningPctg", 0) * 100, 1), round(playoffs_stats.get("faceoffWinningPctg", 0) * 100, 1), False)
        ]
    print("5")
    for stat, regular_season, playoffs, add in stats:
        if add:
            total = regular_season + playoffs
        else:
            total = "-"
        table.append(f"{stat:<10}{regular_season:>7}{playoffs:>7}{total:>7}")

    table.append("```")
    formatted_table = "\n".join(table)
    print("6")

    embed = discord.Embed(
        title=f"{player_info["firstName"]["default"]} {player_info["lastName"]["default"]}",
        color = discord.Color(int(nhl.teams_colors.get(player_info.get("currentTeamAbbrev", "???"), "#FFFFFF").lstrip("#"), 16))
    )
    embed.set_author(name=f"#{player_info.get("sweaterNumber", "?")} [{player_info.get("position", "?")}]", icon_url=player_info.get("headshot"))
    embed.add_field(name="Career Statistics", value=formatted_table, inline=False)
    if "fullTeamName" in player_info:
        team_name = player_info["fullTeamName"].get("default", "Unknown Team")
    else:
        team_name = "No NHL Team"
    embed.set_footer(text=f"{team_name}{"PID: " + str(player_info["playerId"]):>50}")
    return embed

def get_standings(season: str) -> discord.Embed:
    if season == "":
        standings = nhl.get_current_standings()
        pre_title = "Current"
    else:
        end_date = nhl.get_standings_end(season)
        standings = nhl.get_standings_by_date(end_date)
        pre_title = season[:4] + "-" + season[4:]
    divisions = defaultdict(list)
    
    for team in standings["standings"]:
        division_name = team["divisionName"]
        divisions[division_name].append(team)
    divisions = dict(divisions)
    
    for division in divisions:
        divisions[division] = sorted(divisions[division], key=lambda x: x.get("points", 0), reverse=True)
    
    embed = discord.Embed(
        title = pre_title + " Standings",
        color = discord.Color(0xFFFFFF)    
    )
    
    for division, teams in divisions.items():
        table = [
            "```",
            f"{"Team":<15}{"W":>5}{"L":>5}{"P":>5}\n",
        ]
        for team in teams:
            teamname = f"{team["teamAbbrev"]["default"]} {team.get("clinchIndicator", "")}"
            table.append(f"{teamname:<15}{team.get("wins", 0):>5}{team.get("losses", 0):>5}{team.get("points", 0):>5}")
        table.append("```")
        formatted_table = "\n".join(table)
        embed.add_field(name=division, value=formatted_table[:1024], inline=False)
        embed.set_footer(text=f"p - Clinched President\'s Trophy \nx - Clinched Playoff Spot \ny - Clinched Division \nz - Clinched Conference")

    return embed

def get_leaders(position: str, category: str) -> discord.Embed:
    category = category.lower()
    if category ==("savepctg"):
        category = "savePctg"
    position = position.lower()
    try:
        if position == ("skater"):
            results = nhl.get_current_skaters_stats_leaders(category, 10)
        elif position == ("goalie"):
            results = nhl.get_current_goalie_stats_leaders(category, 10)
        else:
            embed = discord.Embed(color=discord.Color.red())
            embed.add_field(name="Error", value="Position doesnt exist.", inline=False)
            return embed
    except Exception:
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="Error", value="Category doesnt exist.", inline=False)
        return embed
    
    embed = discord.Embed(
        title = "Leaders for " + category,
        color = discord.Color(0xFFFFFF)    
    )
    
    table = [
        "```",
        f"{"Name":<20}{"Team":>5}{"Val":>5}\n",
    ]
    for player in results[category]:
        playername = f"{player["firstName"]["default"]} {player["lastName"]["default"]}"
        table.append(f"{playername:<20}{player.get("teamAbbrev", "NUL"):>5}{player.get("value", 0):>5}")
    table.append("```")
    formatted_table = "\n".join(table)
    embed.add_field(name="",value=formatted_table[:1024], inline=False)

    return embed

def get_team_roster(team: str, season: str) -> discord.Embed:
    team_stats = nhl.get_team_roster_by_season(team, season)
    if season == "current":
        pre_title = "Current"
    else:
        pre_title = season[:4] + "-" + season[4:]
    embed = discord.Embed(
        title = pre_title + " Roster For " + team,
        color = discord.Color(int(nhl.teams_colors.get(team, "#FFFFFF").lstrip("#"), 16))    
    )

    if "goalies" not in team_stats:
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name="Error", value="No roster available", inline=False)
        embed.set_footer(text="Check your paramters")
        return embed
    
    table = [
        "```",
        f"{"#":<3}{"Name":<25}{"Ht":>3}{"Wt":>4}\n",
    ]
    for player in team_stats["goalies"]:
        playername = f"{player["firstName"]["default"]} {player["lastName"]["default"]}"
        table.append(f"{player.get("sweaterNumber", "-"):<3}{"[" + player.get("positionCode","-") + "]" + playername:<25}{player.get("heightInInches","-"):>3}{player.get("weightInPounds","-"):>4}")
    table.append("```")
    goalie_table = "\n".join(table)
    embed.add_field(name="Goalies", value=goalie_table[:1024], inline=False)

    table = [
        "```",
        f"{"#":<3}{"Name":<25}{"Ht":>3}{"Wt":>4}\n",
    ]
    for player in team_stats["forwards"]:
        playername = f"{player["firstName"]["default"]} {player["lastName"]["default"]}"
        table.append(f"{player.get("sweaterNumber", "-"):<3}{"[" + player.get("positionCode","-") + "]" + playername:<25}{player.get("heightInInches","-"):>3}{player.get("weightInPounds","-"):>4}")
    table.append("```")
    forward_table = "\n".join(table)
    embed.add_field(name="Forwards", value=forward_table[:1024], inline=False)

    table = [
        "```",
        f"{"#":<3}{"Name":<25}{"Ht":>3}{"Wt":>4}\n",
    ]
    for player in team_stats["defensemen"]:
        playername = f"{player["firstName"]["default"]} {player["lastName"]["default"]}"
        table.append(f"{player.get("sweaterNumber", "-"):<3}{"[" + player.get("positionCode","-") + "]" + playername:<25}{player.get("heightInInches","-"):>3}{player.get("weightInPounds","-"):>4}")
    table.append("```")
    defense_table = "\n".join(table)
    embed.add_field(name="Defensemen", value=defense_table[:1024], inline=False)

    return embed

def get_playoff_bracket() -> discord.Embed:
    brackets = nhl.get_playoff_carousel(nhl.get_current_season())
    if 'rounds' not in brackets:
        embed = discord.Embed(color=discord.Color.red())
        embed.add_field(name='Error', value='No playoff information available', inline=False)
        return embed

    embed = discord.Embed(color=discord.Color(0xFFFFFF))

    for round_data in brackets['rounds']:
        round_number = round_data['roundNumber']
        series_list = round_data['series']
        
        table = ['```', f'{'Top':<8}{'Score'}{'Btm':>8}\n']

        for series in series_list:
            top_seed = series['topSeed']
            bottom_seed = series['bottomSeed']
            table.append(f'{top_seed['abbrev']:<8}{top_seed['wins']} - {bottom_seed['wins']}{bottom_seed['abbrev']:>8}')
        
        table.append('```')
        table = "\n".join(table)
        embed.add_field(name=f"Round {round_number}", value=table, inline=False)
         
    return embed

def get_team_schedule(team: str) -> discord.Embed:
    schedule = nhl.get_week_schedule_now(team)
    embed = discord.Embed(color = discord.Color(int(nhl.teams_colors.get(team, "#FFFFFF").lstrip("#"), 16)))
    if 'games' in schedule and not schedule['games']:
        embed.add_field(name=f"{team} Week Schedule", value=f"There are no games scheduled for {team} this week")
        return embed
    
    table = ['```']

    for game in schedule['games']:
        venue = game['venue']['default']
        dt = datetime.datetime.strptime(game['startTimeUTC'], "%Y-%m-%dT%H:%M:%SZ")
        updated_datetime_obj = dt - datetime.timedelta(hours=4)
        est_date = str(updated_datetime_obj.strftime("%m/%d"))
        est_time = str(updated_datetime_obj.strftime("%I:%M %p"))
        home_team = game['awayTeam']['abbrev']
        away_team = game['homeTeam']['abbrev']

        table.append(f'{away_team} @ {home_team} [{est_date} {est_time} EST] Arena: {venue}')
    
    table.append('```')
    table = "\n".join(table)
    embed.add_field(name=f'{team} Week Schedule', value=table, inline=False)
    return embed

def get_league_schedule() -> discord.Embed:
    schedule = nhl.get_current_schedule()
    games_today = schedule['gameWeek'][0]['games']
    table = ['```']
    for game in games_today:
        away_team = game['awayTeam']['abbrev']
        home_team = game['homeTeam']['abbrev']
        venue = game['venue']['default']
        home_team = game['awayTeam']['abbrev']
        away_team = game['homeTeam']['abbrev']

        dt = datetime.datetime.strptime(game['startTimeUTC'], "%Y-%m-%dT%H:%M:%SZ")
        updated_datetime_obj = dt - datetime.timedelta(hours=4)
        est_date = str(updated_datetime_obj.strftime("%m/%d"))
        est_time = str(updated_datetime_obj.strftime("%I:%M %p"))
        
        table.append(f'{away_team} @ {home_team} [{est_date} {est_time} EST] {venue}')
    if table == ['```']:
        embed.add_field(name=f'No Games Scheduled Today', value="")
        return embed
    table.append('```')
    table = "\n".join(table)
    embed = discord.Embed(color=discord.Color(0xFFFFFF))
    embed.add_field(name=f'Today\'s Games', value=table, inline=False)
    return embed