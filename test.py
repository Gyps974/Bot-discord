import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
import random
import asyncio

# Intents and Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Global variable to track invites
invites = {}
# Translation dictionary
translations = {
    "en": {
        "welcome": "Welcome to the server, {mention}!",
        "goodbye": "{mention} has left the server.",
        "serverinfo_title": "Server Stats",
        "serverinfo_name": "Server Name",
        "serverinfo_members": "Total Members",
        "serverinfo_online": "Online Members",
        "serverinfo_created": "Created At",
        "ticket_created": "Ticket created: {mention}",
        "giveaway_title": "Giveaway!",
        "giveaway_duration": "Duration: {duration} seconds",
        "giveaway_winner": "Congratulations {mention}, you won the giveaway!",
        "membercount_title": "Member Count",
        "membercount_total": "Total Members",
        "membercount_online": "Online Members",
        "invites_message": "{mention} joined using invite code {invite_code} from {inviter_mention}",
        "help_text": (
            "**Bot Commands:**\n"
            "`!hello` - Greet the bot.\n"
            "`!clear <amount>` - Clear a specified number of messages.\n"
            "`!add_role <member> <role>` - Add a role to a member.\n"
            "`!remove_role <member> <role>` - Remove a role from a member.\n"
            "`!kick <member> [reason]` - Kick a member from the server.\n"
            "`!serverinfo` - Get server statistics.\n"
            "`!poll <question>` - Create a yes/no poll.\n"
            "`!randomuser` - Select a random user from the server.\n"
            "`!server` - Get detailed server info.\n"
            "`!userinfo <user>` - Get detailed information about a user.\n"
            "`!customreact <message>` - Add a custom reaction to a specific message.\n"
            "`!buttons` - Interact with buttons.\n"
            "`!ticket` - Create a support ticket.\n"
            "`!giveaway <duration> <prize>` - Start a giveaway.\n"
            "`!membercount` - Show total and online member count.\n"
            "`!invites` - Track and display user invitations.\n"
        )
    },
    "fr": {
        "welcome": "Bienvenue sur le serveur, {mention} !",
        "goodbye": "{mention} a quitté le serveur.",
        "serverinfo_title": "Statistiques du serveur",
        "serverinfo_name": "Nom du serveur",
        "serverinfo_members": "Nombre total de membres",
        "serverinfo_online": "Membres en ligne",
        "serverinfo_created": "Créé le",
        "ticket_created": "Ticket créé : {mention}",
        "giveaway_title": "Concours !",
        "giveaway_duration": "Durée : {duration} secondes",
        "giveaway_winner": "Félicitations {mention}, vous avez gagné le concours !",
        "membercount_title": "Compte des membres",
        "membercount_total": "Nombre total de membres",
        "membercount_online": "Membres en ligne",
        "invites_message": "{mention} a rejoint en utilisant le code d'invitation {invite_code} de {inviter_mention}",
        "help_text": (
            "**Commandes du bot:**\n"
            "`!hello` - Saluer le bot.\n"
            "`!clear <amount>` - Effacer un nombre spécifié de messages.\n"
            "`!add_role <member> <role>` - Ajouter un rôle à un membre.\n"
            "`!remove_role <member> <role>` - Retirer un rôle d'un membre.\n"
            "`!kick <member> [reason]` - Expulser un membre du serveur.\n"
            "`!serverinfo` - Obtenir des statistiques du serveur.\n"
            "`!poll <question>` - Créer un sondage oui/non.\n"
            "`!randomuser` - Sélectionner un utilisateur au hasard.\n"
            "`!server` - Obtenir des informations détaillées sur le serveur.\n"
            "`!userinfo <user>` - Obtenir des informations détaillées sur un utilisateur.\n"
            "`!customreact <message>` - Ajouter une réaction personnalisée à un message spécifique.\n"
            "`!buttons` - Interagir avec des boutons.\n"
            "`!ticket` - Créer un ticket de support.\n"
            "`!giveaway <duration> <prize>` - Lancer un concours.\n"
            "`!membercount` - Afficher le nombre total et en ligne des membres.\n"
            "`!invites` - Suivre et afficher les invitations des utilisateurs.\n"
        )
    }
}

# Language setting (default is English)
user_languages = {}

# Command to set language
@bot.command()
async def setlanguage(ctx, lang: str):
    if lang in translations:
        user_languages[ctx.author.id] = lang
        await ctx.send(f"Language set to {lang}.")
    else:
        await ctx.send("Language not supported. Available languages are 'en' and 'fr'.")

def get_translation(ctx, key):
    lang = user_languages.get(ctx.author.id, "en")
    return translations[lang].get(key, key)
# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    # Load invites for each guild
    for guild in bot.guilds:
        invites[guild.id] = await guild.fetch_invites()

# Event when a member joins
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='welcome')
    if channel:
        message = get_translation(member, "welcome").format(mention=member.mention)
        await channel.send(message)

# Event when a member leaves
@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.channels, name='goodbye')
    if channel:
        message = get_translation(member, "goodbye").format(mention=member.mention)
        await channel.send(message)

# Event when an invite is created or deleted
@bot.event
async def on_invite_create(invite):
    invites[invite.guild.id] = await invite.guild.fetch_invites()

@bot.event
async def on_invite_delete(invite):
    invites[invite.guild.id] = await invite.guild.fetch_invites()

# Event when a member joins
@bot.event
async def on_member_join(member):
    guild_invites = invites.get(member.guild.id, [])
    new_invites = await member.guild.fetch_invites()
    for invite in new_invites:
        if invite.uses > invites[member.guild.id].get(invite.code, 0):
            inviter = invite.inviter
            message = get_translation(member, "invites_message").format(
                mention=member.mention,
                invite_code=invite.code,
                inviter_mention=inviter.mention
            )
            await member.guild.system_channel.send(message)
    invites[member.guild.id] = new_invites
    # Command to get server stats
@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    online_members = sum(1 for m in guild.members if m.status == discord.Status.online)
    embed = discord.Embed(title=get_translation(ctx, 'serverinfo_title'), color=0x00ff00)
    embed.add_field(name=get_translation(ctx, 'serverinfo_name'), value=guild.name, inline=False)
    embed.add_field(name=get_translation(ctx, 'serverinfo_members'), value=guild.member_count, inline=False)
    embed.add_field(name=get_translation(ctx, 'serverinfo_online'), value=online_members, inline=False)
    embed.add_field(name=get_translation(ctx, 'serverinfo_created'), value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
    await ctx.send(embed=embed)

# Ticket System
@bot.command()
async def ticket(ctx):
    channel = await ctx.guild.create_text_channel(f'ticket-{ctx.author.name}')
    message = get_translation(ctx, "ticket_created").format(mention=ctx.author.mention)
    await channel.send(message)
    await ctx.send(f'Ticket created: {channel.mention}')
    # Giveaway System
@bot.command()
async def giveaway(ctx, duration: int, *, prize: str):
    embed = discord.Embed(
        title=get_translation(ctx, "giveaway_title"),
        description=f'{get_translation(ctx, "giveaway_duration").format(duration=duration)}\nPrize: {prize}',
        color=0x00ff00
    )
    giveaway_message = await ctx.send(embed=embed)
    await giveaway_message.add_reaction('🎉')

    def check(reaction, user):
        return user != bot.user and reaction.emoji == '🎉'

    try:
        reaction, user = await bot.wait_for('reaction_add', timeout=duration, check=check)
    except asyncio.TimeoutError:
        await ctx.send('Giveaway ended with no winner.')
    else:
        winner = user
        await ctx.send(get_translation(ctx, "giveaway_winner").format(mention=winner.mention))