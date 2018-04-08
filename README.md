# Basic DnD Discord Bot
A basic Discord DnD Bot

Some basic functions to use when playing DnD or similar games through Discord.

Most config is done through a json file for easy modification (this config.json file will need to be filled in for the bot to work)

# Features
Supports dice rolling in the format:
- !roll <#d#> <+#> ( ># )

For example: 
- `!roll 1d10` (roll one 10 sided dice)
- `!roll 3d10 + 2` (roll three 10 sided dice and add 2 to each roll)
- `!roll 5d20 + 1 > 10` (roll five 20 sided dice and add 1 to each roll and separate the rolls greater or equal to 10 from those below)


Supports a basic inventory system.

In format:
- !additem [item name], quantity, value, description

Which will add the item to the players inventory.

The player can see their own inventory by using:
 - !myitems

Which will print to the channel.

The GM/DM can use the command:
- !allitems

To print a list of all player items to their private channel.

Editing and deleting items without directly modifying the database currently is not working.


There is also support for compendium lookup:
- !lookup item_name

This will search the roll20 compendium and format it to print to the channel. This will work for items, but will not always work for other lookups (ex. lookup fighter will display some, but not all of the info of a fighter).

There is also support for a custom compendium in comma separated values:
- !addlookup [item_name],,desc1,desc2,desc3,etc.

For example:
`!addlookup [Khopesh],,Damage: 1d8+4,Damage Type: Slashing,Saving Throw: STR vs DC STR,Weight: 3`

Using `!lookup khopesh` will print:
```
[Khopesh]

Damage: 1d8+4
Damage Type: Slashing
Saving Throw: STR vs DC STR
Weight: 3
```

You can add as many values to the command as you like.

By default, the command `!lookup` will search and return the custom lookup database before searching the roll20 compendium.
Also by default, it will search the 5e compendium, but can be changed.

# Other Features

For picking choices, there is a command that can pick between two:
- !choose choice1 choice2

To print a static invite, you can set and use this command:
- !invite

To logout the bot as an admin, use:
- !disconnectbot

# Setup

Other than actually setting up the bot, there are a few things that will need to be set up on the Discord server.

Your Discord server will need some new channels:
- A general channel
- A bot output channel
- A GM/DM layer channel

The names given to these don't matter. You will also need their channel IDs.

You will also need a new role:
- GM

# TODO

Some features that I plan on adding:
- Editing and deleting of inventory items
- I might eventually hook it up to interact with roll20 (API or web, unsure)
- Have the `!lookup` command work better with the web compendium
- More roles, set it up to work better if there is a Discord server hosting more than one game.