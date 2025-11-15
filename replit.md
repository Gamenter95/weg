# Weoo Giveaway Bot

## Overview
A Telegram bot for managing dice giveaways with balance management, scheduled messaging, and draft system.

**Bot Information:**
- Name: Weoo Giveaway Bot
- Username: @WeooGiveawayBot
- Token: 8480692956:AAHzyBn2PYOG8EI2NEsqg4a8WMORgj3LT-M
- Channel: @WeooBots (users must join)
- Developer Contact: @Weoo_Weox

## Features
- User balance system (default ₹0.00, min add/withdraw ₹5)
- Channel join verification (@WeooBots)
- Dice giveaway creation with scheduling
- Draft system for incomplete giveaways
- Custom keyboard navigation (not inline buttons)
- Giveaway management dashboard

## Project Structure
- `main.py` - Main bot application with all handlers
- `database.py` - JSON-based database for user data, balances, and giveaways
- `bot_data.json` - Data storage (created automatically)

## Technologies
- Python 3.11
- python-telegram-bot library
- APScheduler for scheduling

## Recent Changes
- November 15, 2025: Fixed critical winner detection bug - Discussion group IDs are now properly resolved from usernames, enabling participant matching to work correctly
- November 15, 2025: Added debug logging for dice rolls and participant choices to help troubleshoot giveaways
- November 15, 2025: Initial project setup with database and bot structure

## Bug Fixes
- **Winner Detection Issue**: Fixed bug where discussion group usernames weren't being converted to numeric IDs, causing the bot to never find participants when checking for winners. The bot now resolves usernames to IDs when you set up a giveaway.
- **Better Error Handling**: Added validation when setting up discussion groups to ensure the bot can access them.
- **Debug Logging**: Added detailed logs showing dice roll totals and participant numbers for easier troubleshooting.
