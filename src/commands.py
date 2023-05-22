from discord.ext import commands
from db import *
from helper import *

# Define your bot commands here
@commands.command()
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

@commands.command()
async def jumpto(ctx, name=None):
    if name is None:
        await ctx.send('Please provide a `NAME` for the conversation instance you wish to jump back to. \nExample: `?jumpto NAME`')
        return
    else: 
        username: str = str(ctx.author.name)
        userid = ctx.author.id
        id_conversation_name = str(f"{userid}_{name}")
        print(f"Jumping back conversation instance with name: {name} for user [{userid} : {username}]")
        users_conversations = await get_user_conversation_list(userid)
        if users_conversations is None:
            await ctx.send('Please create a new conversation instance using the `?new` command.')
            return
        elif id_conversation_name in users_conversations['conversations']:
            await change_active_conversation(userid, name)
            await ctx.send(f'Jumped back to conversation: `{name}`')
        else: 
            await ctx.send(f'You do not have a conversation instance with the name: `{name}`')
            return
    
    pass

@commands.command()
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

@commands.command()
async def list(ctx):
    print(ctx.author.id)
    users_conversations = await get_user_conversation_list(ctx.author.id)
    if users_conversations is None:
        await ctx.send('Please create a new conversation instance using the `?new` command.')
        return
    else:
        conversation_names: list[str] = \
            [f"{conversation.split('_')[1]}" for conversation in users_conversations['conversations']]
        await ctx.send(f'Your conversation instances: {conversation_names}')
    pass

@commands.command()
async def active(ctx):
    print(ctx.author.id)
    users_conversations = await get_user_conversation_list(ctx.author.id)
    if users_conversations is None:
        await ctx.send('Please create a new conversation instance using the `?new` command.')
        return
    else:
        id_conversation_name = users_conversations['active_conversation']
        if id_conversation_name is None or id_conversation_name == '':
            await ctx.send('You do not have an active conversation instance.')
            return
        active_conversation = id_conversation_name.split('_')[1]
        await ctx.send(f'Your active conversation instance is: {active_conversation}')
    pass

@commands.command()
async def delete(ctx, name=None):  
    if name is None:
        await ctx.send('Please provide a `NAME` for the conversation instance you wish to delete. \nExample: `?delete NAME`')
        return
    else: 
        username: str = str(ctx.author.name)
        userid = ctx.author.id
        id_conversation_name = get_id_conversation(userid, name)
        print(f"Deleting conversation instance with name: {name} for user [{userid} : {username}]")
        users_conversations = await get_user_conversation_list(userid)
        if users_conversations is None:
            await ctx.send('Please create a new conversation instance using the `?new` command.')
            return
        elif id_conversation_name in users_conversations['conversations']:
            await delete_conversation(userid, name)
            await ctx.send(f'Deleted conversation: `{name}`')
        else: 
            await ctx.send(f'You do not have a conversation instance with the name: `{name}`')
            return
    pass

@commands.command()
async def clear(ctx):
    print(ctx.author.id)
    userid = ctx.author.id
    users_conversations = await get_user_conversation_list(ctx.author.id)
    if users_conversations is None:
        await ctx.send('There is no active conversation')
        return
    else:
        id_conversation_name = users_conversations['active_conversation']
        if id_conversation_name is None or id_conversation_name == '':
            await ctx.send('You do not have an active conversation instance.')
            return
        await clear_active_conversation(userid)
        await ctx.send(f'Active conversation cleared')
    pass


# TODO - Help command