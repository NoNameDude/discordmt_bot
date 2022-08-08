local ie = minetest.request_insecure_environment()
local conf = Settings(minetest.get_modpath(minetest.get_current_modname()) .. '/bot.conf')
local relay = {messages = {}, reports = {}}
local settings = conf:to_table()
local cooldown = settings["cooldown"] --can be changed if wanted (higher number = less cpu ussage but longer delay. (Need to be > 0))

function send_message_on_discord(msg)
    table.insert(relay["messages"], msg) 
end
 
function send_message_on_discord_reports(msg)
    table.insert(relay["reports"], msg) 
end
 
--Get input string from the discord server
local function get_recent_post()
    local python_file = ie.io.open(settings["python_file_path"], "r")
    if python_file:seek("end") == 0 then
        python_file:close()
        return 
    end
    python_file:close() --dont like this line pre-fix
    local output = false
    for line in ie.io.lines(settings["python_file_path"]) do
        minetest.chat_send_all(minetest.colorize("#4dffe4", line))
        output = true 
    end 
    --erase whatever was inside that file if output returned a full string
    if output == true then
        python_file = ie.io.open(settings["python_file_path"], "w") --dont like this line but pre-fix
        python_file:write("")
        python_file:close()
    end  
end 



local timer = 0
minetest.register_globalstep(function(dtime)
    timer = timer + dtime
    if timer >= tonumber(cooldown) then
        get_recent_post()
        local report_file, msg_file = nil
        --does the table rly have a input?
        if relay["reports"][1] ~= nil then
            report_file = ie.io.open(settings["report_file_path"], "a")
        end
        if relay["messages"][1] ~= nil then
            msg_file = ie.io.open(settings["lua_file_path"], "a")
        end
    
        --make sure file is empty so it dosn't corrupt
        if msg_file ~= nil then
            if msg_file:seek("end") ~= 0 then
                msg_file:close()
                --make it nil so it dosnt corrupt with a future check
                msg_file = nil
            end
        end
        --make sure file is empty so it dosn't corrupt
        if report_file ~= nil then
            if report_file:seek("end") ~= 0 then
                report_file:close()
                --make it nil so it dosnt corrupt with a future check
                report_file = nil
            end
        end
        --
        
        for cat, tab in pairs(relay) do
            for _, message in pairs(tab) do
                if cat == "messages" then
                    --check if file is exists
                    if msg_file ~= nil then 
                        msg_file:write(message.."\n") 
                    end
                    
                elseif cat == "reports" then
                    --check if file is exists
                    if report_file ~= nil then
                        report_file:write(message)
                    end
                end 
            end 
        end
        --empty table for new input
        relay = {messages = {}, reports = {}}
        --close all open files and set timer to 0
        if msg_file ~= nil then
           msg_file:close() 
        end
        if report_file ~= nil then
            report_file:close()
        end
        timer = 0
    end
end)  

minetest.register_on_joinplayer(function(player)
    if not player then return end
    local name = player and player:get_player_name()
    local msg = "[Server] :arrow_up: "..name.." joined the server"
    table.insert(relay["messages"], msg)
end)

minetest.register_on_leaveplayer(function(player)
    local name = player and player:get_player_name()
    local msg = "[Server] :arrow_down: "..name.." left the server"
    table.insert(relay["messages"], msg)
end)

minetest.register_on_shutdown(function()
    local msg = "**Server Shut down**"
    send_message_on_discord(msg)
end) 
--if you got a own chat mod remove minetest.register_on_chat_message and implement this code into yours
minetest.register_on_chat_message(function(name, message)
    local msg = "<"..name.."> "..message
    minetest.chat_send_all(msg)
    send_message_on_discord(msg)
    return true
end)
