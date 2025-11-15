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
- November 15, 2025: Initial project setup with database and bot structure
