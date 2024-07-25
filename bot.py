import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import threading

# Initialize the bot
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Replace with your bot token
TOKEN = 'YOUR_BOT_TOKEN'

# Flask app
app = Flask(__name__)

@app.route('/setstatus', methods=['POST'])
def set_status():
    data = request.json
    status = data.get('status')
    if status:
        bot.loop.create_task(bot.change_presence(activity=discord.Game(name=status)))
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'error'}), 400

@app.route('/sendmessage', methods=['POST'])
def send_message():
    data = request.json
    channel_id = data.get('channel_id')
    message = data.get('message')
    if channel_id and message:
        channel = bot.get_channel(int(channel_id))
        bot.loop.create_task(channel.send(message))
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'error'}), 400

@app.route('/createrole', methods=['POST'])
def create_role():
    data = request.json
    role_name = data.get('role_name')
    guild = bot.guilds[0]  # Assumes the bot is only in one server
    if role_name and guild:
        bot.loop.create_task(guild.create_role(name=role_name))
        return jsonify({'status': 'success'}), 200
    return jsonify({'status': 'error'}), 400

@app.route('/serverinfo')
def server_info():
    guild = bot.guilds[0]  # Assumes the bot is only in one server
    info = {
        'name': guild.name,
        'member_count': guild.member_count,
        'roles': [role.name for role in guild.roles],
        'channels': [channel.name for channel in guild.channels]
    }
    return jsonify(info), 200

def run_flask():
    app.run(host='0.0.0.0', port=5000)

# Bot events and commands
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

# Run Flask app in a separate thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# Run the bot
bot.run(TOKEN)
