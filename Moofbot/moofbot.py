import discord
from discord.ext import commands

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------
# Config
# -------------------
MOOF_CHANNEL_ID = 1411912372074975272  # put your moof channel ID here
LEADERBOARD_CHANNEL_ID = 1411880703553179739  # leaderboard channel you gave me
MOOF_EMOJI = "🐮"

# Dictionary to track moof counts
moof_counts = {}
leaderboard_message_id = None
last_moof_user = None  # track who last moofed


# -------------------
# Helper: Update leaderboard
# -------------------
async def update_leaderboard():
    global leaderboard_message_id

    channel = bot.get_channel(LEADERBOARD_CHANNEL_ID)
    if channel is None:
        return

    if not moof_counts:
        leaderboard_text = "**🐮 Moof Leaderboard 🐮**\n\nNobody has moofed yet!"
    else:
        sorted_counts = sorted(moof_counts.items(), key=lambda x: x[1], reverse=True)
        leaderboard_text = "**🐮 Moof Leaderboard 🐮**\n\n"
        for i, (user_id, count) in enumerate(sorted_counts, 1):
            user = await bot.fetch_user(user_id)
            leaderboard_text += f"{i}. {user.display_name}: {count} {MOOF_EMOJI}\n"

    try:
        if leaderboard_message_id:  # update existing
            msg = await channel.fetch_message(leaderboard_message_id)
            await msg.edit(content=leaderboard_text)
        else:  # send new one and pin it
            msg = await channel.send(leaderboard_text)
            await msg.pin()
            leaderboard_message_id = msg.id
    except discord.NotFound:
        msg = await channel.send(leaderboard_text)
        await msg.pin()
        leaderboard_message_id = msg.id


# -------------------
# Count moofs
# -------------------
@bot.event
async def on_message(message):
    global last_moof_user

    if message.author.bot:
        return

    if message.channel.id == MOOF_CHANNEL_ID and message.content.lower() == "moof":
        if message.author.id == last_moof_user:
            # same user moofing twice in a row → ignore
            await message.channel.send(
                f"⚠️ {message.author.display_name}, you can’t moof twice in a row!"
            )
        else:
            user_id = message.author.id
            moof_counts[user_id] = moof_counts.get(user_id, 0) + 1
            last_moof_user = user_id
            await update_leaderboard()

    await bot.process_commands(message)


# -------------------
# Admin commands
# -------------------
@bot.command(name="addmoof")
@commands.has_permissions(administrator=True)
async def addmoof(ctx, member: discord.Member, amount: int):
    moof_counts[member.id] = moof_counts.get(member.id, 0) + amount
    await ctx.send(f"✅ Added {amount} moofs to {member.display_name}")
    await update_leaderboard()


@bot.command(name="submoof")
@commands.has_permissions(administrator=True)
async def submoof(ctx, member: discord.Member, amount: int):
    if member.id in moof_counts:
        moof_counts[member.id] = max(0, moof_counts[member.id] - amount)
        await ctx.send(f"✅ Subtracted {amount} moofs from {member.display_name}")
        await update_leaderboard()
    else:
        await ctx.send(f"{member.display_name} has no moofs.")


@bot.command(name="resetuser")
@commands.has_permissions(administrator=True)
async def resetuser(ctx, member: discord.Member):
    moof_counts[member.id] = 0
    await ctx.send(f"✅ {member.display_name}'s moofs have been reset")
    await update_leaderboard()


@bot.command(name="resetboard")
@commands.has_permissions(administrator=True)
async def resetboard(ctx):
    moof_counts.clear()
    await ctx.send("✅ The moof leaderboard has been reset")
    await update_leaderboard()


@bot.command(name="leaderboard")
async def leaderboard(ctx):
    await update_leaderboard()


# -------------------
# Run the bot
# -------------------
bot.run("MTQxMTg4ODcyNDQ1ODk5OTkwOA.GXwy_m.7ppxamMO3lWyyHbdmVpPrXtQBlxZXunFnrki8w")