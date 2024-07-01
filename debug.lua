--More debug comming soon [WIP]
--localize for performance
local send_message_on_discord_debugs = discord_mt.send_message_on_discord_debugs
minetest.register_on_dignode(function(pos, oldnode, digger)
    if not digger then return end
    if not oldnode then return end
    local name = digger and digger:get_player_name()
    local msg = "[Server] Player "..name.." digged "..oldnode.name.. " at pos **[x="..pos.x..", y="..pos.y..", z="..pos.z.."]** \n"
    send_message_on_discord_debugs(msg)
end)

minetest.register_on_placenode(function(pos, newnode, placer, oldnode, itemstack, pointed_thing)
    if not placer then return end
    if not newnode then return end
    local name = placer and placer:get_player_name()
    local msg = "[Server] Player "..name.." placed "..newnode.name.. " at pos **[x="..pos.x..", y="..pos.y..", z="..pos.z.."]** \n"
    send_message_on_discord_debugs(msg)
end)

 
