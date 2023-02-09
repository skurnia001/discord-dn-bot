# Dragon Nest Dragon Jade Query Discord Bot
![CD Status](https://github.com/skurnia001/discord-dn-bot/actions/workflows/main.yml/badge.svg)

[Dragon Nest](https://en.wikipedia.org/wiki/Dragon_Nest)

Dragon Jade is a special item in Dragon Nest which is useful for increasing damage of a character. 
Each class in Dragon Nest has their own skills which is upgraded by dragon jade. 
There are also multiple variants of dragon jade.

This version of bot is using skill naming for SEA server, other server might differ in skill naming, 
so the bot might not work.

As per this recurring joke in Computer Science.
![Solving 1 minute routine task by making script that takes 20 minutes to develop](https://imgs.xkcd.com/comics/the_general_problem.png)

## Notes
Required Discord bot permission: 414464683072 

## Requirements 
* Python 3.8
* MongoDB Instance (for database storing purposes, some modules must be disabled otherwise)

## Setting up the envrionment
### Linux
```bash
# Run from project root directory
python3.8 -m venv $(pwd)/venv
source $(pwd)/venv/activate
```
### Windows 
```cmd
# Ensure python 3.8 is installed and configured to the PATH variables
python -m venv c:\path\to\myenv
<venv>\Scripts\activate.bat
```

## Starting the bot
```bash
python bot.py
```
