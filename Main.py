import configparser
import os  
import discord
from discord.ext import commands, tasks 
from discord.ext.commands import bot
import asyncio
#array to send messages to minetest from discord  
minetest_messages = []

config = configparser.ConfigParser()
#you may need to path to bot.conf
config.read('bot.conf')    
#settings 
bot = commands.Bot(
  command_prefix=config["BOT"]["command_prefix"], 
  help_command=None, 
  intents=discord.Intents(messages=True, message_content=True)
)   

lua_file = config["RELAY"]["lua_file_path"]
python_file = config["RELAY"]["python_file_path"]
python_report_file = config["RELAY"]["report_file_path"]
relay_channel = config["RELAY"]["relay_channel"] 
report_channel = config["RELAY"]["report_channel"]
cooldown = config["RELAY"]["cooldown"]
debug_channel = config["RELAY"]["debug_channel"]
debug_file = config["RELAY"]["debug_action_file_path"]


class Queue:
    def __init__(self):
        self.msg = []
    
    def get(self, path): 
        if os.path.getsize(path) != 0: 
            with open(path, 'r') as filehandle:
                for message in filehandle: 
                    self.msg.append(message.strip())  # Use strip to remove newline characters
                
            # Once read, empty the file's input
            with open(path, 'w') as file:
                file.write("")     
                 
            return self.msg  # Return the messages, not a method reference
    
    def write(self, path):
        if os.path.getsize(path) == 0:
            with open(path, 'a') as file: 
                for dmsg in minetest_messages:
                    file.write("{}\n".format(dmsg))
            minetest_messages.clear()

queue = Queue()

            
 
@bot.event      
async def on_ready():  
    print('Connected!')
    #start the loop   
    task_loop.start()
     

#fetch messages in the channel 
@bot.event
async def on_message(message):
    #make sure the channel is the right one and the bot messages getting ignored
    if (message.channel.id == int(relay_channel)) and (message.author.id != bot.user.id):
        author = message.author.name
        if config["RELAY"]["use_nicknames"] == True:
            author = message.author.display_name
        
        msg = "[Discord] <{}> {}".format(author, message.content)
        minetest_messages.append(msg)  
        
    
#loop to check if file has input or 
@tasks.loop(seconds=int(cooldown))
async def task_loop():
    # In case of a timeout
    try: 
        channel = await bot.fetch_channel(relay_channel)
        rep_channel = await bot.fetch_channel(report_channel)
        deb_channel = await bot.fetch_channel(debug_channel)
        
        # Check if channel exists
        if channel is None:
            print(f"Error: Channel id {relay_channel} doesn't exist")
        elif rep_channel is None:
            print(f"Error: Channel id {report_channel} doesn't exist") 
        elif deb_channel is None:
            print(f"Error: Channel id {debug_channel} doesn't exist")

        # Get messages from files
        messages = queue.get(lua_file)
        report_msg = queue.get(python_report_file)
        debug_msg = queue.get(debug_file) 

        # Read / send messages
        if messages:
            for msg in messages:  
                await channel.send(msg)

        if report_msg:
            for rmsg in report_msg:
                await rep_channel.send(rmsg)    

        if debug_msg:
            for dmsg in debug_msg: 
                await deb_channel.send(dmsg)  

        # Only write if array isn't empty
        if minetest_messages:
            queue.write(python_file)  
    except discord.HTTPException as e:
        print(f'HTTPException: {e}')
        await asyncio.sleep(60)  # wait before retrying

    except discord.DiscordServerError as e:
        print(f'DiscordServerError: {e}')
        await asyncio.sleep(60)  # wait before retrying

    except Exception as e:
        print(f'Unexpected error: {e}')
        await asyncio.sleep(60)  # wait before retrying
     

#bot token to run
bot.run(config["BOT"]["bot_token"]) 
