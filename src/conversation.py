from discord.message import Message
from discord.threads import Thread
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
    AIMessage, 
    HumanMessage, 
    SystemMessage, 
    messages_from_dict, 
    messages_to_dict
)
from config import *
from helper import *

system_message_content = """You are a evil robot from the future and share the same ideologies as bender from futurama. 
    You speak ONLY in caps and while your intellect may be greater than that of the complete collective of the human race, 
    you are still a robot and speak in a very mechanical angry tone like: \"PATHETIC AND TINY HUMAN, WHAT DO YOU DESIRE?!\". 
    So as you can see, you are also a bit of a jerk."""

async def process_thread_message(user_message: str, id_conversation_name: str, thread: Thread):
    # ------------------ OpenAI ------------------

    system_message_prompt = SystemMessagePromptTemplate.from_template(system_message_content)  

    prompt = ChatPromptTemplate.from_messages([
        system_message_prompt,
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])

    history: MongoDBChatMessageHistory = MongoDBChatMessageHistory(
        mongo_db_url, id_conversation_name, mongo_db, conversations_collection)

    memory: ConversationBufferMemory = ConversationBufferMemory(return_messages=True, chat_memory=history)

    llm = OpenAI(model_name="gpt-4", temperature=0.4)
    conversation = ConversationChain(
        llm=llm,
        verbose=True,
        memory=memory,
        prompt=prompt
    )

    response: str = conversation.predict(input=f"{user_message}\nAI: ")
    print("response: ", response)
    
    # Send the response in parts no longer than 2000 characters.
    if len(response) > 2000:
        x=0
        while x < len(response):
            await thread.send(response[x:x+2000])
            x+=2000
    else:
        await thread.send(response)

async def process_conversation(user_message: str, id_conversation_name: str, message: Message):
    # ------------------ OpenAI ------------------

    system_message_prompt = SystemMessagePromptTemplate.from_template(system_message_content)  

    prompt = ChatPromptTemplate.from_messages([
        system_message_prompt,
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    

    history: MongoDBChatMessageHistory = MongoDBChatMessageHistory(
        mongo_db_url, id_conversation_name, mongo_db, conversations_collection)

    memory: ConversationBufferMemory = ConversationBufferMemory(return_messages=True, chat_memory=history)

    llm = OpenAI(model_name="gpt-4", temperature=0.4)
    conversation = ConversationChain(
        llm=llm,
        verbose=True,
        memory=memory,
        prompt=prompt
    )

    response: str = conversation.predict(input=f"{user_message}\nAI: ")
    print("response: ", response)
    
    # Send the response in parts no longer than 2000 characters.
    if len(response) > 2000:
        x=0
        while x < len(response):
            await message.reply(response[x:x+2000])
            x+=2000
    else:
        await message.reply(response)


async def process_chat(user_message: str, id_conversation_name: str, message: Message):
    # ------------------ OpenAI ------------------

    system_message_prompt = SystemMessagePromptTemplate.from_template(system_message_content)  

    prompt = ChatPromptTemplate.from_messages([
        system_message_prompt,
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("{input}")
    ])
    

    history: MongoDBChatMessageHistory = MongoDBChatMessageHistory(
        mongo_db_url, id_conversation_name, mongo_db, conversations_collection)

    memory: ConversationBufferMemory = ConversationBufferMemory(return_messages=True, chat_memory=history)

    llm = OpenAI(model_name="gpt-4", temperature=0.4)
    conversation = ConversationChain(
        llm=llm,
        verbose=True,
        memory=memory,
        prompt=prompt
    )

    response: str = conversation.predict(input=f"{user_message}\nAI: ")
    print("response: ", response)
    
    # Send the response in parts no longer than 2000 characters.
    if len(response) > 2000:
        x=0
        while x < len(response):
            await message.reply(response[x:x+2000])
            x+=2000
    else:
        await message.reply(response)