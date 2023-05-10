import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import openai
import langchain
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain, OpenAI, PromptTemplate
from langchain.memory import ChatMessageHistory
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories.mongodb import MongoDBChatMessageHistory
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import (
    AIMessage, HumanMessage, SystemMessage, messages_from_dict, messages_to_dict
)
from pymongo import MongoClient

# Load environment variables from .env file
load_dotenv()

# Get environment variables
openai_api_key = os.environ.get('OPENAI_API_KEY')
discord_bot_token = os.environ.get('DISCORD_BOT_TOKEN')
mongo_db_url = os.environ.get('MONGO_DB_URL')
mongo_db = os.environ.get('MONGO_DB')
conversation_list_collection = os.environ.get('CONVERSATION_LIST_COLLECTION')
conversations_collection = os.environ.get('CONVERSATIONS_COLLECTION')

# Connect to MongoDB
mongo_client = MongoClient(mongo_db_url)
deus_db = mongo_client[mongo_db]
user_conversation_list = deus_db[conversation_list_collection]
conversations = deus_db[conversations_collection]

# Set up the discord bot
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='?', intents=intents)


# Bot Command functions.s
@bot.command()
async def new(ctx, name=None):
    if name is None:
        await ctx.send('Please provide a `NAME` for the conversation instance. \nExample: `?new NAME`')
        return
    else: 
        print(f"Creating a new conversation instance with name: {name} for user [{ctx.author.id} : {ctx.author.name}]")
        username: str = str(ctx.author.name)
        await store_in_user_conversation_list(ctx.author.id, username, name)
        await ctx.send(f'Created a new conversation instance with name `{name}`')
    pass

@bot.command()
async def jumpto(ctx, name=None):
    if name is None:
        await ctx.send('Please provide a `NAME` for the conversation instance you wish to jump back to. \nExample: `?jumpto NAME`')
        return
    else: 
        username: str = str(ctx.author.name)
        userid = ctx.author.id
        refined_conversation_name = str(f"{userid}_{name}")
        print(f"Jumping back conversation instance with name: {name} for user [{userid} : {username}]")
        users_conversations = await get_user_conversation_list(userid)
        if users_conversations is None:
            await ctx.send('Please create a new conversation instance using the `?new` command.')
            return
        elif refined_conversation_name in users_conversations['conversations']:
            await change_active_conversation(userid, name)
            await ctx.send(f'Jumped back to conversation: `{name}`')
        else: 
            await ctx.send(f'You do not have a conversation instance with the name: `{name}`')
            return
    
    pass

@bot.command()
async def q(ctx, question=None):
    if question is None:
        await ctx.send('Please provide a `MESSAGE`. \nExample: `?q MESSAGE`')
        return
    else:
        question = ctx.message.content[3:]
        print(f"Question from {ctx.author.name}: {question}") 
        chat = OpenAI(model_name="gpt-4", temperature=0.4)
        chat.model_name = "gpt-4"
        chat.openai_api_key = openai_api_key
        result = chat(question)
        print(f"Response: {result}")
        await ctx.send(result)
    pass

@bot.command()
async def list(ctx):
    print(ctx.author.id)
    users_conversations = await get_user_conversation_list(ctx.author.id)
    if users_conversations is None:
        await ctx.send('Please create a new conversation instance using the `?new` command.')
        return
    else:
        conversation_names = [f"{conversation.split('_')[1]}" for conversation in users_conversations['conversations']]
        await ctx.send(f'Your conversation instances: {conversation_names}')
    pass

@bot.command()
async def active(ctx):
    print(ctx.author.id)
    users_conversations = await get_user_conversation_list(ctx.author.id)
    if users_conversations is None:
        await ctx.send('Please create a new conversation instance using the `?new` command.')
        return
    else:
        active_conversation = users_conversations['active_conversation'].split('_')[1]
        await ctx.send(f'Your active conversation instance is: {active_conversation}')
    pass

# DB functions
async def change_active_conversation(userid, conversation_name):
    refined_conversation_name = await get_conversation(userid, conversation_name)
    user_conversation_list.update_one(
        filter={'user_id': userid}, 
        update={'$set': {'active_conversation': refined_conversation_name}}, 
        upsert=True)

async def store_in_user_conversation_list(user_id, username, conversation_name):
    refined_conversation_name = await get_conversation(user_id, conversation_name)
    user_conversation_list.update_one(
        filter={'user_id': user_id, 'username': username}, 
        update={"$set": {"active_conversation": refined_conversation_name}, '$addToSet': {'conversations': refined_conversation_name}}, 
        upsert=True)

async def get_user_conversation_list(user_id):
    return user_conversation_list.find_one({'user_id': user_id})

# Basic helper functions
async def get_conversation(userid, conversation_name):
    return f"{userid}_{conversation_name}"


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
    if user_conversations_document is None:
        await message.channel.send('Please create a new conversation instance using the `?new` command.')
        return
    
    # Get the active conversation. formated as userid_conversationname
    refined_conversation_name = str(user_conversations_document['active_conversation'])
    print(f'Active conversation found: {refined_conversation_name}')

    # ------------------ OpenAI ------------------
    
    # system_message_content = "You are a helpful assistant that translates English to French."

    # system_message_prompt = SystemMessagePromptTemplate.from_template(system_message_content)  

    # prompt = ChatPromptTemplate.from_messages([
    #     system_message_prompt,
    #     MessagesPlaceholder(variable_name="history"),
    #     HumanMessagePromptTemplate.from_template("{input}")
    # ])
    

    history: MongoDBChatMessageHistory = MongoDBChatMessageHistory(
        mongo_db_url, refined_conversation_name, mongo_db, conversations_collection)

    memory: ConversationBufferMemory = ConversationBufferMemory(return_messages=True, chat_memory=history)

    llm = OpenAI(model_name="gpt-4", temperature=0.4)
    conversation = ConversationChain(
        llm=llm,
        verbose=True,
        memory=memory,
        # prompt=prompt
    )

    response: str = conversation.predict(input=content)

    # # Get the conversation history
    # history: MongoDBChatMessageHistory = MongoDBChatMessageHistory(mongo_db_url, refined_conversation_name, mongo_db, conversations_collection)
    # # Create a memory object
    # memory: ConversationBufferMemory = ConversationBufferMemory(return_messages=True, chat_memory=history)
    # # Create a conversation chain
    # llm = OpenAI(model_name="gpt-4")
    # conversation = ConversationChain(
    #     llm=llm,
    #     verbose=True,
    #     memory=memory
    # )
    # response: str = conversation.predict(input=content)
    
    print(response)
    if len(response) > 2000:
        x=0
        while x < len(response):
            await message.reply(response[x:x+2000])
            x+=2000
    else:
        await message.reply(response)

# Run the bot
bot.run(discord_bot_token)