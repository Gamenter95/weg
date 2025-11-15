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
- November 15, 2025: **CRITICAL FIX** - Fixed participants being cleared before winner detection. Participants now persist through the entire giveaway lifecycle
- November 15, 2025: Added emoji reactions (✅) to confirm when users successfully submit their number
- November 15, 2025: Users can now update their number by sending a new one (instead of being blocked)
- November 15, 2025: Fixed discussion group ID resolution - usernames are now properly converted to numeric IDs
- November 15, 2025: Added debug logging for dice rolls and participant choices
- November 15, 2025: Initial project setup with database and bot structure

## Bug Fixes
- **Participants Cleared Bug**: Fixed critical bug where participants were being cleared when the giveaway message was sent. The `update_giveaway_message` function was resetting the participants array, causing all submissions to be lost before the dice rolled. Now participants persist correctly.
- **Winner Detection Issue**: Fixed bug where discussion group usernames weren't being converted to numeric IDs, preventing participant matching. The bot now resolves usernames to IDs during setup.
- **Duplicate Submissions**: Users can now update their chosen number by sending a new one, instead of being blocked after their first submission.
- **Better Error Handling**: Added validation when setting up discussion groups to ensure the bot can access them.
- **Debug Logging**: Added detailed logs showing dice roll totals and participant numbers for easier troubleshooting.

## Features
- ✅ Emoji reactions confirm successful number submissions
- 🔄 Users can change their number by sending a new one
- 🎲 Winner detection now works correctly
- 📝 Better error messages and validation
