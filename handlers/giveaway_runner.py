
import logging
import asyncio
from telegram import Update, ReactionTypeEmoji
from telegram.ext import ContextTypes
from database import Database

logger = logging.getLogger(__name__)
db = Database()

async def handle_giveaway_participation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    
    if update.message.chat.type not in ['group', 'supergroup']:
        return
    
    chat_id = str(update.message.chat.id)
    user = update.effective_user
    text = update.message.text
    
    if not text:
        return
    
    active_giveaway_id = db.get_active_giveaway_for_discussion(chat_id)
    
    if not active_giveaway_id:
        return
    
    active_giveaway = db.get_giveaway(active_giveaway_id)
    
    if not active_giveaway or active_giveaway.get('status') != 'scheduled':
        return
    
    try:
        number = int(text)
        dice_count = active_giveaway.get('dice_count', 1)
        min_num = dice_count
        max_num = dice_count * 6
        
        if min_num <= number <= max_num:
            participants = db.get_giveaway_participants(active_giveaway.get('giveaway_id'))
            user_participant = next((p for p in participants if p.get('user_id') == user.id), None)
            
            if user_participant:
                db.update_participant(active_giveaway.get('giveaway_id'), user.id, number)
            else:
                db.add_participant(active_giveaway.get('giveaway_id'), user.id, user.username or user.first_name, number)
            
            try:
                await update.message.set_reaction(reaction=[ReactionTypeEmoji(emoji="👍")], is_big=False)
            except Exception:
                pass
        else:
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"@{user.username or user.first_name}, please choose a number between {min_num}-{max_num}",
                    message_thread_id=update.message.message_thread_id
                )
            except Exception as e:
                logger.error(f"Failed to send invalid number message: {e}")
    except ValueError:
        pass

async def run_scheduled_giveaway(context: ContextTypes.DEFAULT_TYPE, giveaway_id=None):
    if giveaway_id is None:
        giveaway_id = context.job.data
    giveaway = db.get_giveaway(giveaway_id)
    
    if not giveaway:
        return
    
    channel = giveaway.get('channel')
    discussion_group = giveaway.get('discussion_group')
    dice_count = giveaway.get('dice_count', 1)
    after_time = giveaway.get('after_time', 5)
    
    min_number = dice_count
    max_number = dice_count * 6
    
    try:
        message = await context.bot.send_message(
            chat_id=channel,
            text=f"🎲 Dice Giveaway #{giveaway_id.split('_')[-1]}!\n\nPlease send a number between {min_number}-{max_number} ✅\nComment Down ❤️"
        )
        
        db.update_giveaway_message(giveaway_id, message.message_id)
        db.set_active_giveaway_for_discussion(discussion_group, giveaway_id)
        
        context.job_queue.run_once(start_giveaway_rolling, when=after_time * 60, data=giveaway_id, name=f"roll_{giveaway_id}")
        
    except Exception as e:
        logger.error(f"Failed to send giveaway message: {e}")

async def start_giveaway_rolling(context: ContextTypes.DEFAULT_TYPE):
    giveaway_id = context.job.data
    giveaway = db.get_giveaway(giveaway_id)
    
    if not giveaway:
        return
    
    discussion_group = giveaway.get('discussion_group')
    db.clear_active_giveaway_for_discussion(discussion_group)
    
    channel = giveaway.get('channel')
    dice_count = giveaway.get('dice_count', 1)
    prize_amount = giveaway.get('prize_amount', 0)
    
    total = 0
    
    for i in range(dice_count):
        dice_msg = await context.bot.send_dice(chat_id=channel, emoji="🎲")
        total += dice_msg.dice.value
        await asyncio.sleep(3)
    
    participants = db.get_giveaway_participants(giveaway_id)
    
    winner = None
    for participant in participants:
        if participant.get('number') == total:
            winner = participant
            break
    
    if winner:
        winner_id = winner.get('user_id')
        winner_username = winner.get('username', 'Unknown')
        
        if winner_username.startswith('@'):
            winner_display = winner_username
        elif winner_username and winner_username != 'Unknown':
            winner_display = f"@{winner_username}"
        else:
            try:
                user_info = await context.bot.get_chat(winner_id)
                winner_display = user_info.first_name
            except:
                winner_display = winner_username
        
        db.set_giveaway_winner(giveaway_id, winner_id)
        
        await context.bot.send_message(
            chat_id=channel,
            text=f"🎉 Giveaway Result!\n\n"
                 f"Number: {total}\n"
                 f"Winner: {winner_display}\n\n"
                 f"Winner, please click here to grab the prize:\n"
                 f"[Click Here](https://t.me/WeooGiveawayBot?start=prize{giveaway_id})",
            parse_mode='Markdown'
        )
        
        db.update_giveaway_status(giveaway_id, 'completed')
    else:
        creator_id = giveaway.get('user_id')
        
        user_data = db.get_user(creator_id)
        new_balance = user_data.get('balance', 0) + prize_amount
        db.update_user_balance(creator_id, new_balance)
        
        await context.bot.send_message(
            chat_id=channel,
            text=f"😔 Giveaway Result\n\n"
                 f"Number: {total}\n"
                 f"Winner: No one\n"
                 f"Reason: No one chose the correct number\n\n"
                 f"Prize amount refunded to creator."
        )
        
        db.update_giveaway_status(giveaway_id, 'completed')
