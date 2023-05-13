import os
import discord
from discord.ext import commands
from db import *
from commands import *
from config import *
from conversation_processor import process_conversation

# Set up the discord bot
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='?', intents=intents)

# Set bot commands
bot.add_command(new)
bot.add_command(list)
bot.add_command(active)
bot.add_command(delete)
# bot.add_command(help)
bot.add_command(jumpto)
bot.add_command(q) # q for query.


# Events
@bot.event
async def on_ready():
    print(f'Bot is ready, logged in as {bot.user}')

@bot.event
async def on_thread_create(thread):
    print(f'Thread created: {thread.name}')

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself and messages from other channels.
    if message.author == bot.user or message.channel.name != 'gpt-4-deus':
        return

    # Process commands
    content = message.content
    if content.startswith('?'):
        await bot.process_commands(message)
        return

    # Continue or create a conversation.
    userid = message.author.id
    username = message.author.name
    print(f'User: {username}\n {content}')

    user_conversations_document = await get_user_conversation_list(userid)
    if user_conversations_document is None or \
        user_conversations_document['active_conversation'] is None or \
            user_conversations_document['active_conversation'] == '':
        await message.channel.send(
            'Please create a new conversation instance using the `?new` command. \
                or jump to an existing conversation using the `?jumpto` command. \
                    You can list all your conversations using the `?list` command.'
        )
        return
    
    # Get the active conversation. formated as userid_conversationname
    refined_conversation_name = str(user_conversations_document['active_conversation'])
    print(f'Active conversation found: {refined_conversation_name}')

    await process_conversation(content, refined_conversation_name, message)


# Run the bot
bot.run(discord_bot_token)