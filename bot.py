import json
import discord
from discord.ext import commands
from discord import app_commands
from tabulate import tabulate

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!',intents=intents)
mod_role_id = 1359262214208622923  # moderator role id

# challenges data file
with open('challenges.json', 'r') as chlngs:
        challenges = json.load(chlngs)

#teams data file
with open('teams-data.json', 'r') as datafile:
        teamsData = json.load(datafile)


@bot.event
async def on_ready():
    await bot.tree.sync()  # Sync slash commands with Discord
    print(f'Logged in as {bot.user}! Slash commands are ready.')


# command to add ctf challenges
@bot.tree.command(name="add_challenge", description="add_new_ctf_challenge")
@app_commands.describe(ctf_name="add_challenge_name",ctf_flag="add_challenge_flag",score="score",description="description")
async def add_challenge(interaction: discord.Interaction, ctf_name: str, ctf_flag: str,score: int, description: str):
    user_roles = [role.id for role in interaction.user.roles]
    obj = {
        "ctf_flag": ctf_flag.lower(),
        "score": score,
        "description": description
    }

    #to check if user is moderator
    if mod_role_id not in user_roles:
        await interaction.response.send_message("Forbidden! your are not a moderator",ephemeral=True)
        return

    challenges.update({ctf_name:obj})

    with open('challenges.json', 'w') as chlngsfile:
        chlngsfile.write(json.dumps(challenges,indent=4))

    await interaction.response.send_message(f"✅ NEW **{ctf_name}** CTF challenge has been added.")



# command to show avilable challenges
@bot.tree.command(name="challenges", description="Show available challenges")
async def show_challenges(interaction=discord.Interaction):
    headers = ["Name", "score", "Description"]
    result=[]

    for x in challenges:
        result.append([x,challenges[x]["score"],challenges[x]["description"]])

    await interaction.response.send_message(f"```{tabulate(result, headers=headers, tablefmt="simple")}```")



#score board
@bot.tree.command(name="scoreboard", description="View the top scores")
async def scoreboard(interaction: discord.Interaction):

    # Sort scores in descending order
    sorted_scores = sorted(teamsData.items(), key=lambda x: x[1]["score"], reverse=True)
    headers = ["Rank", "Team", "Scores"]
    lines =[]

    for i, (team, data) in enumerate(sorted_scores, start=1):
        lines.append([i,team,data["score"]])

    await interaction.response.send_message(f"```{tabulate(lines, headers=headers, tablefmt="simple")}```")



@bot.tree.command(name="add_team", description="append a new team to the database")
@app_commands.describe(add_team="Enter team role name")
async def add_team(interaction: discord.Interaction,add_team:str):
    user_roles = [role.id for role in interaction.user.roles]
    if mod_role_id not in user_roles:
        await interaction.response.send_message("Forbidden! your are not a moderator",ephemeral=True)
        return

    teamsData.update({add_team:{"score":0,"flags":[]}})

    with open('teams-data.json', 'w') as teamdata:
        teamdata.write(json.dumps(teamsData,indent=4))

    await interaction.response.send_message(f"✅ NEW **{add_team}** Team added to the CTF battle.")



#submitting the flag
@bot.tree.command(name="answer", description="Submit your answer")
@app_commands.describe(ctf_name="enter the challenge name",user_answer="Your answer to the current question")
async def slash_answer(interaction: discord.Interaction,ctf_name:str, user_answer: str):
    leader_role = "team-leader"  # or use the role ID if preferred
    user_roles = [role.name.lower() for role in interaction.user.roles]
    teams = [teamName.lower() for teamName in teamsData]

    # check if user is a team leader
    if leader_role not in user_roles:
        await interaction.response.send_message("You must have the **Leader** role to use this command.",ephemeral=True )
        return

    total_teams = len(teams)
    current_team = 1

    for team in teams:
        if team in user_roles: # check the team of the users
            if challenges[ctf_name]["ctf_flag"] == user_answer.lower() and user_answer.lower() not in teamsData[team]["flags"]: #flag validation
                teamsData[team]["score"] = teamsData[team]["score"] + challenges[ctf_name]["score"]
                teamsData[team]["flags"].append(user_answer.lower())

                with open('teams-data.json','w') as teamdata:
                    teamdata.write(json.dumps(teamsData,indent=4))

                await interaction.response.send_message(f"✅ Correct! \n Team **{team}** catched the flag \n now they have {teamsData[team]["score"]} point(s).")

            elif user_answer.lower() in teamsData[team]["flags"]:
                await interaction.response.send_message("This answer has been used by your team before")
            else:
                await interaction.response.send_message("❌ Incorrect answer.",ephemeral=True)
        elif current_team >= total_teams:
            await interaction.response.send_message("Amm! there is a problem in team name",ephemeral=True)
            return
        current_team += 1


# Run the bot 
# enter your token below
bot.run('')
