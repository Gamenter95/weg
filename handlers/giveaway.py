
import logging
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database import Database
from keyboards import get_back_keyboard, get_giveaway_type_keyboard, get_dice_count_keyboard, get_draft_set_keyboard, get_main_keyboard
from handlers.giveaway_runner import run_scheduled_giveaway

logger = logging.getLogger(__name__)
db = Database()

CHANNEL, GIVEAWAY_TYPE, DISCUSSION_GROUP, DICE_COUNT, PRIZE_AMOUNT, AFTER_TIME = range(6)

async def start_create_giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎁 Create Giveaway\n\n"
        "Please send the channel username or ID where you want to create the giveaway.\n"
        "Make sure I'm added as an admin in that channel!",
        reply_markup=get_back_keyboard()
    )
    return CHANNEL

async def receive_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Back":
        await update.message.reply_text("Giveaway creation cancelled.", reply_markup=get_main_keyboard())
        return ConversationHandler.END
    
    context.user_data['channel'] = text
    await update.message.reply_text("Great! Now select the giveaway type:", reply_markup=get_giveaway_type_keyboard())
    return GIVEAWAY_TYPE

async def receive_giveaway_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Back":
        await update.message.reply_text("Please send the channel username or ID:", reply_markup=get_back_keyboard())
        return CHANNEL
    
    if text == "Dice Giveaway":
        context.user_data['giveaway_type'] = 'dice'
        await update.message.reply_text(
            "🎲 Dice Giveaway selected!\n\n"
            "Dice giveaways require a discussion group linked to your channel.\n"
            "Please send the discussion group username or ID.\n"
            "Make sure I'm added as an admin there too!",
            reply_markup=get_back_keyboard()
        )
        return DISCUSSION_GROUP
    else:
        await update.message.reply_text("Please select a valid giveaway type:", reply_markup=get_giveaway_type_keyboard())
        return GIVEAWAY_TYPE

async def receive_discussion_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Back":
        await update.message.reply_text("Select giveaway type:", reply_markup=get_giveaway_type_keyboard())
        return GIVEAWAY_TYPE
    
    try:
        chat = await context.bot.get_chat(text)
        discussion_group_id = str(chat.id)
        context.user_data['discussion_group'] = discussion_group_id
        
        await update.message.reply_text("Perfect! Now select how many dices you want (1-10):", reply_markup=get_dice_count_keyboard())
        return DICE_COUNT
    except Exception as e:
        logger.error(f"Failed to get discussion group chat: {e}")
        await update.message.reply_text(
            "❌ Could not find that discussion group.\n"
            "Please make sure:\n"
            "1. The group exists\n"
            "2. I'm added as an admin there\n"
            "3. You provided the correct username or ID\n\n"
            "Please try again:",
            reply_markup=get_back_keyboard()
        )
        return DISCUSSION_GROUP

async def receive_dice_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Back":
        await update.message.reply_text("Please send the discussion group username or ID:", reply_markup=get_back_keyboard())
        return DISCUSSION_GROUP
    
    if text.isdigit() and 1 <= int(text) <= 10:
        context.user_data['dice_count'] = int(text)
        await update.message.reply_text(
            f"Great! {text} dice(s) selected.\n\n"
            "Now, how much money will the winner get? (in ₹)\n"
            "Please send the prize amount:",
            reply_markup=get_back_keyboard()
        )
        return PRIZE_AMOUNT
    else:
        await update.message.reply_text("Please select a valid number between 1 and 10:", reply_markup=get_dice_count_keyboard())
        return DICE_COUNT

async def receive_prize_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Back":
        await update.message.reply_text("Select how many dices you want (1-10):", reply_markup=get_dice_count_keyboard())
        return DICE_COUNT
    
    try:
        amount = float(text)
        if amount <= 0:
            await update.message.reply_text("Prize amount must be greater than 0. Please try again:", reply_markup=get_back_keyboard())
            return PRIZE_AMOUNT
        
        context.user_data['prize_amount'] = amount
        await update.message.reply_text(
            f"Prize amount: ₹{amount:.2f}\n\n"
            "How long after sending should the giveaway start?\n"
            "Please enter time in minutes:\n"
            "Example: 5 (for 5 minutes)",
            reply_markup=get_back_keyboard()
        )
        return AFTER_TIME
    except ValueError:
        await update.message.reply_text("Please enter a valid number for the prize amount:", reply_markup=get_back_keyboard())
        return PRIZE_AMOUNT

async def receive_after_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Back":
        await update.message.reply_text("Please send the prize amount:", reply_markup=get_back_keyboard())
        return PRIZE_AMOUNT
    
    if text in ["Draft", "Set"]:
        return await handle_draft_set_choice(update, context)
    
    try:
        after_minutes = int(text)
        if after_minutes <= 0:
            raise ValueError
        
        context.user_data['after_time'] = after_minutes
        
        user = update.effective_user
        user_data = db.get_user(user.id)
        prize_amount = context.user_data.get('prize_amount', 0)
        balance = user_data.get('balance', 0.0)
        
        summary = (
            "📋 Giveaway Summary:\n\n"
            f"Channel: {context.user_data.get('channel', 'Not set')}\n"
            f"Type: Dice Giveaway\n"
            f"Discussion Group: {context.user_data.get('discussion_group')}\n"
            f"Number of Dices: {context.user_data.get('dice_count')}\n"
            f"Prize Amount: ₹{prize_amount:.2f}\n"
            f"Start After: {after_minutes} minutes\n\n"
            f"Your Balance: ₹{balance:.2f}\n"
        )
        
        if balance >= prize_amount:
            summary += "\n✅ You have sufficient balance!\n\nWhat would you like to do?"
        else:
            summary += (
                f"\n❌ Insufficient balance!\n"
                f"Required: ₹{prize_amount:.2f}\n"
                f"You have: ₹{balance:.2f}\n\n"
                f"Please save as draft and add funds to your balance."
            )
        
        await update.message.reply_text(summary, reply_markup=get_draft_set_keyboard())
        context.user_data['waiting_for_draft_set'] = True
        return AFTER_TIME
    except ValueError:
        await update.message.reply_text("Please enter a valid number of minutes:", reply_markup=get_back_keyboard())
        return AFTER_TIME

async def handle_draft_set_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.effective_user
    
    if text == "Draft":
        draft_data = {
            'channel': context.user_data.get('channel'),
            'giveaway_type': context.user_data.get('giveaway_type'),
            'discussion_group': context.user_data.get('discussion_group'),
            'dice_count': context.user_data.get('dice_count'),
            'prize_amount': context.user_data.get('prize_amount'),
            'after_time': context.user_data.get('after_time')
        }
        
        db.add_draft(user.id, draft_data)
        await update.message.reply_text(
            "✅ Giveaway saved as draft!\n\n"
            "You can access it from the 'Drafts' button.",
            reply_markup=get_main_keyboard()
        )
        context.user_data.clear()
        return ConversationHandler.END
    
    elif text == "Set":
        user_data = db.get_user(user.id)
        prize_amount = context.user_data.get('prize_amount', 0)
        balance = user_data.get('balance', 0.0)
        
        if balance >= prize_amount:
            giveaway_data = {
                'channel': context.user_data.get('channel'),
                'giveaway_type': context.user_data.get('giveaway_type'),
                'discussion_group': context.user_data.get('discussion_group'),
                'dice_count': context.user_data.get('dice_count'),
                'prize_amount': prize_amount,
                'after_time': context.user_data.get('after_time')
            }
            
            giveaway_id = db.add_giveaway(user.id, giveaway_data)
            new_balance = balance - prize_amount
            db.update_user_balance(user.id, new_balance)
            
            await update.message.reply_text(
                f"✅ Giveaway created successfully!\n\n"
                f"₹{prize_amount:.2f} has been deducted from your balance.\n"
                f"New balance: ₹{new_balance:.2f}\n\n"
                f"Sending giveaway to channel now...",
                reply_markup=get_main_keyboard()
            )
            
            await run_scheduled_giveaway(context, giveaway_id)
            
            context.user_data.clear()
            return ConversationHandler.END
        else:
            await update.message.reply_text("❌ Insufficient balance! Please save as draft and add funds first.", reply_markup=get_main_keyboard())
            context.user_data.clear()
            return ConversationHandler.END
    
    elif text == "Back":
        await update.message.reply_text("Please enter time in minutes:", reply_markup=get_back_keyboard())
        return AFTER_TIME

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.", reply_markup=get_main_keyboard())
    context.user_data.clear()
    return ConversationHandler.END
