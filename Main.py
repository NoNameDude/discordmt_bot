import configparser
import os  
import discord
from discord.ext import commands, tasks 
from discord.ext.commands import bot
#array to send messages to minetest from discord  
minetest_messages = []
  
config = configparser.ConfigParser()
#you may need to path to bot.conf
config.read('bot.conf')    
#settings 
bot = commands.Bot(command_prefix=config["BOT"]["command_prefix"], help_command=None)   
lua_file = config["RELAY"]["lua_file_path"]
python_file = config["RELAY"]["python_file_path"]
python_report_file = config["RELAY"]["report_file_path"]
relay_channel = config["RELAY"]["relay_channel"] 
report_channel = config["RELAY"]["report_channel"]
cooldown = config["RELAY"]["cooldown"]
debug_channel = config["RELAY"]["debug_channel"]
debug_file = config["RELAY"]["debug_action_file_path"]

def get_reports_msg():
    if os.path.getsize(python_report_file) != 0: 
        messages = []
        with open(python_report_file, 'r') as filehandle:
            for message in filehandle: 
                messages.append(message)  
                #configs.append(currentPlace)
                
            #once readed empty file's input
            file = open(python_report_file, 'w')
            file.write("")
            file.close()     
                
        return messages
      
      
def get_messages(): 
    #check if file has input or is empty
    if os.path.getsize(lua_file) != 0:   
        messages = []
        with open(lua_file, 'r') as filehandle:
            for message in filehandle: 
                messages.append(message) 
                #configs.append(currentPlace)
                
            #once readed empty file's input
            file = open(lua_file, 'w')
            file.write("")
            file.close()     
                
        return messages 
  
def get_debug_message(): 
    #check if file has input or is empty
    if os.path.getsize(debug_file) != 0:   
        messages = []
        with open(debug_file, 'r') as filehandle:
            for message in filehandle: 
                messages.append(message) 
                #configs.append(currentPlace)
                
            #once readed empty file's input
            file = open(debug_file, 'w')
            file.write("")
            file.close()     
                
        return messages 
  
def write_messages():
    #check if discord has messages to send and if so empty the array and send 
    if os.path.getsize(python_file) == 0:
        #once readed empty file's input
        file = open(python_file, 'a')
        for dmsg in (minetest_messages):
            file.write("{} \n".format(dmsg))
                        
        file.close()
        minetest_messages.clear()


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
        
    
#loop to check if file has input or not
@tasks.loop(seconds=int(cooldown))
async def task_loop():
    channel = await bot.fetch_channel(relay_channel)
    rep_channel = await bot.fetch_channel(report_channel)
    deb_channel = await bot.fetch_channel(debug_channel)
    #check if channel exists
    if channel is None:
        print("Error: Channel id {}, dosn't exists".format(channel)) 
    elif rep_channel is None:
        print("Error: Channel id {}, dosn't exists".format(rep_channel))
    elif debug_channel is None:
        print("Error: Channel id {}, dosn't exists".format(debug_channel))
        
     
    #get messages from lua.txt
    messages = get_messages() 
    report_msg = get_reports_msg()
    debug_msg = get_debug_message()
    
    #Read / send messages
    if messages != None:    
        for msg in (messages):  
            await channel.send(msg) 
    
    if report_msg != None:
        for rmsg in (report_msg):
            await rep_channel.send(rmsg)    

    if debug_msg != None:
        for dmsg in (debug_msg):
            await deb_channel.send(dmsg)  
            
    #only write if array isn't emtpy
    if len(minetest_messages) != 0:
        write_messages() 
    

#bot token to run
bot.run(config["BOT"]["bot_token"]) 

