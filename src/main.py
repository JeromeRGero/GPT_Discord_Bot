import os
import discord
from discord.message import Message
from discord.threads import Thread
from discord.ext import commands
from db import *
from commands import *
from config import *
from conversation import process_conversation, process_thread_message

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
    assert bot.user is not None
    print(f'Bot is ready, logged in as {bot.user} with an id of {bot.user.id}')

@bot.event
async def on_thread_create(thread: Thread):
    assert thread.parent is not None
    parent_channel_name = thread.parent.name
    assert bot.user is not None
    if thread.owner_id != bot.user.id or parent_channel_name != 'gpt-prime':
        return
    # Process first message (somehow)
    message_reference = thread.starter_message
    id_conversation_name = f'thread_{thread.id}_{thread.name}'
    assert message_reference is not None
    await process_thread_message(message_reference.content, id_conversation_name, thread)
    return

# TODO: finish working on the threads functionality.
@bot.event
async def on_command_error(content, exception):
    print(f"An error occurred: {str(exception)}")

@bot.event
async def on_message(message: Message):
    #If message is in a thread
    if isinstance(message.channel, discord.threads.Thread):
        thread_channel_name: str = message.channel.name
        thread_channel_id = message.channel.id
        assert message.channel.parent is not None
        parent_channel_name = message.channel.parent.name
        #If message is in the correct channel
        if message.author == bot.user or parent_channel_name != 'gpt-prime':
            return
        await process_conversation(message.content, f'thread_{message.channel.id}_{message.channel.name}', message)
        return
        # Process commands in the thread
    else:
        # Ignore messages from the bot itself and messages from other channels.
        if message.author == bot.user or isinstance(message.channel, discord.DMChannel) or \
              isinstance(message.channel, discord.PartialMessageable) or message.channel.name != 'gpt-prime':
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
        # Create a new thread.
        convoName: str = content[0:10]
        id_conversation_name: str = get_id_conversation(message.author.id, convoName)
        print(f"Creating a new thread for the new conversation for user [{message.author.name}: {message.author.id}]")
        thread: Thread = await message.create_thread(name=convoName)
        print(f'# Does this every hit?  \nCreated a new thread: {thread.name}')
        return
    
    # Get the active conversation. formated as userid_conversationname
    id_conversation_name = str(user_conversations_document['active_conversation'])
    print(f'Active conversation found: {id_conversation_name}')

    await process_conversation(content, id_conversation_name, message)


        
# Run the bot
bot.run("discord_bot_token")