import os
import discord
from discord.message import Message
from discord.threads import Thread
from discord.ext import commands
from db import *
from commands import *
from config import *
from conversation import process_conversation

# Set up the discord bot
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Set bot commands
bot.add_command(new)
bot.add_command(list)
bot.add_command(active)
bot.add_command(delete)
# bot.add_command(help)
bot.add_command(jumpto)
bot.add_command(q) # q for query.
bot.add_command(clear) # Clears the active conversation


# Events
@bot.event
async def on_ready():
    print(f'Bot is ready, logged in as {bot.user} with an id of {bot.user.id}')

@bot.event
async def on_thread_create(thread: Thread):
    parent_channel_name = thread.parent.name
    if parent_channel_name != 'gpt-4-deus':
        return
    # Process first message (somehow)
    message_reference = thread.starter_message
    if message_reference:
        # start_message = await thread.fetch_message(message_reference.message_id)
        # async for message in thread.history(oldest_first=True, limit=1):
        #     first_message = message
        #     break
        print(f'Thread created: {thread.name}')
        print(f'First message: {message_reference.content}')
        await thread.send('Hello, I am a bot. \
                          I will be assisting you in this conversation, someday.')
    return

# @bot.event
# async def on_message(message: Message):
#     # Ignore messages from the bot itself and messages from other channels.
#     if message.author == bot.user or message.channel.name != 'gpt-4-deus':
#         return

#     # Process commands
#     content: str = message.content
#     if content.startswith('?'):
#         await bot.process_commands(message)
#         return

#     # Continue or create a conversation.
#     userid = message.author.id
#     username = message.author.name
#     print(f'User: {username}\n {content}')

#     user_conversations_document = await get_user_conversation_list(userid)
#     if user_conversations_document is None or \
#         user_conversations_document['active_conversation'] is None or \
#             user_conversations_document['active_conversation'] == '':
#         await message.channel.send(
#             'Please create a new conversation instance using the `?new` command. \
#                 or jump to an existing conversation using the `?jumpto` command. \
#                     You can list all your conversations using the `?list` command.'
#         )
#         return
    
#     # Get the active conversation. formated as userid_conversationname
#     id_conversation_name = str(user_conversations_document['active_conversation'])
#     print(f'Active conversation found: {id_conversation_name}')

#     await process_conversation(content, id_conversation_name, message)

# TODO: finish working on the threads functionality.
@bot.event
async def on_command_error(content, exception):
    print(f"An error occurred: {str(exception)}")

@bot.event
async def on_message(message: Message):
    if isinstance(message.channel, discord.threads.Thread):
        # thread_channel_name: str = message.channel.name
        parent_channel_name = message.channel.parent.name
        if message.author == bot.user or parent_channel_name != 'gpt-4-deus':
            return
        # Process text in thread.
    else:
        # Create a new thread.
        content: str = message.content
        # id_conversation_name: str = get_id_conversation(ctx.author.id, content[0:10])
        # print(f"Creating a new thread for the new conversation for user [{ctx.author.name}: {ctx.author.id}]")
        # await store_in_user_conversation_list(ctx.author.id, username, name)
        # await ctx.send(f'Created a new conversation instance with name `{name}`')
        thread: Thread = await message.create_thread(name=content[:10])
        print(f'# Does this every hit?  \nCreated a new thread: {thread.name}')
    return
    # Ignore messages from the bot itself and messages from other channels.
    if message.author == bot.user or message.channel.name != 'gpt-prime':
        return

    # Process commands
    content: str = message.content
    print(f'Content: {content}')
    if content.startswith('!'):
        await bot.process_commands(message)
        return

    #TODO Create thread if no active conversation

    # Continue or create a conversation.
    userid = message.author.id
    username = message.author.name
    print(f'User: {username}\n {content}')

    user_conversations_document = await get_user_conversation_list(userid)
    if user_conversations_document is None or \
        user_conversations_document['active_conversation'] is None or \
            user_conversations_document['active_conversation'] == '':
        await message.channel.send(
"""Please create a new conversation instance using the `?new` command.
or jump to an existing conversation using the `?jumpto` command.
You can list all your conversations using the `?list` command."""
        )
        return
    
    # Get the active conversation. formated as userid_conversationname
    id_conversation_name = str(user_conversations_document['active_conversation'])
    print(f'Active conversation found: {id_conversation_name}')

    await process_conversation(content, id_conversation_name, message)


        
# Run the bot
bot.run(discord_bot_token)