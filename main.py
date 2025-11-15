import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
import asyncio
from database import Database
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "8480692956:AAHzyBn2PYOG8EI2NEsqg4a8WMORgj3LT-M"
CHANNEL_USERNAME = "@WeooBots"
DEVELOPER_CONTACT = "@Weoo_Weox"
MIN_AMOUNT = 5
ADMIN_USER_ID = 6186511950

db = Database()
scheduler = AsyncIOScheduler()

CHANNEL, GIVEAWAY_TYPE, DISCUSSION_GROUP, DICE_COUNT, PRIZE_AMOUNT, AFTER_TIME = range(6)
BROADCAST_MESSAGE = 0

def get_main_keyboard():
    keyboard = [
        [KeyboardButton("Create Giveaway")],
        [KeyboardButton("Add"), KeyboardButton("Balance"), KeyboardButton("Out")],
        [KeyboardButton("My Giveaways"), KeyboardButton("Drafts")],
        [KeyboardButton("Help"), KeyboardButton("Contact")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard():
    keyboard = [[KeyboardButton("Back")]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_giveaway_type_keyboard():
    keyboard = [
        [KeyboardButton("Dice Giveaway")],
        [KeyboardButton("Back")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_dice_count_keyboard():
    keyboard = [
        [KeyboardButton("1"), KeyboardButton("2"), KeyboardButton("3")],
        [KeyboardButton("4"), KeyboardButton("5"), KeyboardButton("6")],
        [KeyboardButton("7"), KeyboardButton("8"), KeyboardButton("9")],
        [KeyboardButton("10"), KeyboardButton("Back")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_draft_set_keyboard():
    keyboard = [
        [KeyboardButton("Draft"), KeyboardButton("Set"), KeyboardButton("Back")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db.get_user(user.id)
    
    if db.is_user_banned(user.id):
        await update.message.reply_text(
            "⛔ You have been banned from using this bot.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    if context.args:
        await handle_prize_claim(update, context)
        return
    
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user.id)
        if member.status in ['member', 'administrator', 'creator']:
            db.set_channel_joined(user.id, True)
        else:
            await update.message.reply_text(
                f"Welcome to Weoo Giveaway Bot! 🎉\n\n"
                f"Please join our channel {CHANNEL_USERNAME} first and then send /start again.",
                reply_markup=ReplyKeyboardRemove()
            )
            return
    except Exception as e:
        await update.message.reply_text(
            f"Welcome to Weoo Giveaway Bot! 🎉\n\n"
            f"Please join our channel {CHANNEL_USERNAME} first and then send /start again.",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    welcome_message = (
        f"Welcome {user.first_name}! 🎉\n\n"
        f"I'm Weoo Giveaway Bot, your assistant for creating and managing dice giveaways!\n\n"
        f"Use the buttons below to navigate:"
    )
    
    await update.message.reply_text(
        welcome_message,
        reply_markup=get_main_keyboard()
    )

async def handle_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db.get_user(user.id)
    balance = user_data.get('balance', 0.0)
    
    await update.message.reply_text(
        f"💰 Your Balance: ₹{balance:.2f}",
        reply_markup=get_main_keyboard()
    )

async def handle_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"💵 Add Funds\n\n"
        f"To add funds to your balance, please contact {DEVELOPER_CONTACT}\n\n"
        f"Minimum add amount: ₹{MIN_AMOUNT}",
        reply_markup=get_main_keyboard()
    )

async def handle_out(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"💸 Withdraw Funds\n\n"
        f"To withdraw funds from your balance, please contact {DEVELOPER_CONTACT}\n\n"
        f"Minimum withdraw amount: ₹{MIN_AMOUNT}",
        reply_markup=get_main_keyboard()
    )

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📚 Help - Weoo Giveaway Bot\n\n"
        "🎲 Create Giveaway: Create dice giveaways for your channel\n"
        "💰 Balance: Check your current balance\n"
        "💵 Add: Add funds to your balance\n"
        "💸 Out: Withdraw funds from your balance\n"
        "📋 My Giveaways: View and manage your giveaways\n"
        "📝 Drafts: View and continue your draft giveaways\n"
        "📞 Contact: Get bot and developer information\n\n"
        "How to create a giveaway:\n"
        "1. Click 'Create Giveaway'\n"
        "2. Provide your channel (bot must be admin)\n"
        "3. Select 'Dice Giveaway'\n"
        "4. Provide discussion group (bot must be admin)\n"
        "5. Select number of dices (1-10)\n"
        "6. Enter prize amount\n"
        "7. Set send time and after time\n"
        "8. Save as draft or set to schedule\n\n"
        f"Minimum balance for transactions: ₹{MIN_AMOUNT}\n\n"
        f"For support, contact {DEVELOPER_CONTACT}"
    )
    
    await update.message.reply_text(
        help_text,
        reply_markup=get_main_keyboard()
    )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact_text = (
        "📞 Contact Information\n\n"
        "🤖 Bot: @WeooGiveawayBot\n"
        f"📢 Channel: {CHANNEL_USERNAME}\n"
        f"👤 Developer: {DEVELOPER_CONTACT}\n\n"
        "About this bot:\n"
        "Weoo Giveaway Bot helps you create and manage dice giveaways "
        "for your Telegram channels. With balance management, scheduling, "
        "and an easy-to-use interface, running giveaways has never been easier!\n\n"
        f"For support, questions, or to add/withdraw funds, contact {DEVELOPER_CONTACT}"
    )
    
    await update.message.reply_text(
        contact_text,
        reply_markup=get_main_keyboard()
    )

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
        await update.message.reply_text(
            "Giveaway creation cancelled.",
            reply_markup=get_main_keyboard()
        )
        return ConversationHandler.END
    
    context.user_data['channel'] = text
    await update.message.reply_text(
        "Great! Now select the giveaway type:",
        reply_markup=get_giveaway_type_keyboard()
    )
    return GIVEAWAY_TYPE

async def receive_giveaway_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Back":
        await update.message.reply_text(
            "Please send the channel username or ID:",
            reply_markup=get_back_keyboard()
        )
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
        await update.message.reply_text(
            "Please select a valid giveaway type:",
            reply_markup=get_giveaway_type_keyboard()
        )
        return GIVEAWAY_TYPE

async def receive_discussion_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Back":
        await update.message.reply_text(
            "Select giveaway type:",
            reply_markup=get_giveaway_type_keyboard()
        )
        return GIVEAWAY_TYPE
    
    context.user_data['discussion_group'] = text
    await update.message.reply_text(
        "Perfect! Now select how many dices you want (1-10):",
        reply_markup=get_dice_count_keyboard()
    )
    return DICE_COUNT

async def receive_dice_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Back":
        await update.message.reply_text(
            "Please send the discussion group username or ID:",
            reply_markup=get_back_keyboard()
        )
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
        await update.message.reply_text(
            "Please select a valid number between 1 and 10:",
            reply_markup=get_dice_count_keyboard()
        )
        return DICE_COUNT

async def receive_prize_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Back":
        await update.message.reply_text(
            "Select how many dices you want (1-10):",
            reply_markup=get_dice_count_keyboard()
        )
        return DICE_COUNT
    
    try:
        amount = float(text)
        if amount <= 0:
            await update.message.reply_text(
                "Prize amount must be greater than 0. Please try again:",
                reply_markup=get_back_keyboard()
            )
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
        await update.message.reply_text(
            "Please enter a valid number for the prize amount:",
            reply_markup=get_back_keyboard()
        )
        return PRIZE_AMOUNT

async def handle_giveaway_participation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    
    # Check if message is from a discussion group with an active giveaway
    chat_id = str(update.message.chat.id)
    user = update.effective_user
    text = update.message.text
    
    if not text:
        return
    
    # Find active giveaway for this discussion group
    active_giveaway = None
    for giveaway in db.get_all_giveaways():
        if giveaway.get('discussion_group') == chat_id and giveaway.get('status') == 'scheduled':
            active_giveaway = giveaway
            break
    
    if not active_giveaway:
        return
    
    try:
        number = int(text)
        dice_count = active_giveaway.get('dice_count', 1)
        min_num = dice_count
        max_num = dice_count * 6
        
        if min_num <= number <= max_num:
            # Check if user already participated
            participants = db.get_giveaway_participants(active_giveaway.get('giveaway_id'))
            already_participated = any(p.get('user_id') == user.id for p in participants)
            
            if not already_participated:
                db.add_participant(
                    active_giveaway.get('giveaway_id'),
                    user.id,
                    user.username or user.first_name,
                    number
                )
            else:
                error_msg = await update.message.reply_text(
                    "You have already participated!"
                )
                await asyncio.sleep(5)
                try:
                    await error_msg.delete()
                except Exception:
                    pass
        else:
            error_msg = await update.message.reply_text(
                f"Please choose a number between {min_num}-{max_num}"
            )
            await asyncio.sleep(5)
            try:
                await error_msg.delete()
            except Exception:
                pass
    except ValueError:
        pass




async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ You don't have permission to use this command.")
        return
    
    all_users = db.get_all_users()
    all_giveaways = db.get_all_giveaways()
    active_giveaways = [g for g in all_giveaways if g.get('status') == 'scheduled']
    completed_giveaways = [g for g in all_giveaways if g.get('status') == 'completed']
    
    total_balance = sum(u.get('balance', 0) for u in all_users.values())
    
    panel_text = (
        "🎛️ Admin Panel\n\n"
        f"👥 Total Users: {len(all_users)}\n"
        f"🎁 Total Giveaways: {len(all_giveaways)}\n"
        f"⏳ Active Giveaways: {len(active_giveaways)}\n"
        f"✅ Completed Giveaways: {len(completed_giveaways)}\n"
        f"💰 Total Balance in System: ₹{total_balance:.2f}\n\n"
        "Available Commands:\n"
        "/ban <user_id> - Ban a user\n"
        "/unban <user_id> - Unban a user\n"
        "/add <user_id> <amount> - Add balance\n"
        "/remove <user_id> <amount> - Remove balance\n"
        "/say <user_id> <message> - Send message to user\n"
        "/broadcast - Broadcast message to all users"
    )
    
    await update.message.reply_text(panel_text)

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ You don't have permission to use this command.")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /ban <user_id>")
        return
    
    try:
        user_id = int(context.args[0])
        db.ban_user(user_id)
        await update.message.reply_text(f"✅ User {user_id} has been banned.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ You don't have permission to use this command.")
        return
    
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /unban <user_id>")
        return
    
    try:
        user_id = int(context.args[0])
        db.unban_user(user_id)
        await update.message.reply_text(f"✅ User {user_id} has been unbanned.")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID.")

async def add_balance_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ You don't have permission to use this command.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /add <user_id> <amount>")
        return
    
    try:
        user_id = int(context.args[0])
        amount = float(context.args[1])
        user_data = db.get_user(user_id)
        new_balance = user_data.get('balance', 0) + amount
        db.update_user_balance(user_id, new_balance)
        await update.message.reply_text(f"✅ Added ₹{amount:.2f} to user {user_id}. New balance: ₹{new_balance:.2f}")
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Invalid user ID or amount.")

async def remove_balance_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ You don't have permission to use this command.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /remove <user_id> <amount>")
        return
    
    try:
        user_id = int(context.args[0])
        amount = float(context.args[1])
        user_data = db.get_user(user_id)
        new_balance = max(0, user_data.get('balance', 0) - amount)
        db.update_user_balance(user_id, new_balance)
        await update.message.reply_text(f"✅ Removed ₹{amount:.2f} from user {user_id}. New balance: ₹{new_balance:.2f}")
    except (ValueError, IndexError):
        await update.message.reply_text("❌ Invalid user ID or amount.")

async def say_to_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ You don't have permission to use this command.")
        return
    
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /say <user_id> <message>")
        return
    
    try:
        user_id = int(context.args[0])
        message = ' '.join(context.args[1:])
        await context.bot.send_message(chat_id=user_id, text=f"📢 Message from Admin:\n\n{message}")
        await update.message.reply_text(f"✅ Message sent to user {user_id}.")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send message: {str(e)}")

async def start_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ You don't have permission to use this command.")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "📢 Broadcast Message\n\n"
        "Please send the message you want to broadcast to all users:",
        reply_markup=get_back_keyboard()
    )
    return BROADCAST_MESSAGE

async def receive_broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Back":
        await update.message.reply_text("Broadcast cancelled.", reply_markup=get_main_keyboard())
        return ConversationHandler.END
    
    message = update.message.text
    all_users = db.get_all_users()
    
    success_count = 0
    fail_count = 0
    
    await update.message.reply_text(f"📤 Broadcasting to {len(all_users)} users...")
    
    for user_id in all_users.keys():
        try:
            await context.bot.send_message(
                chat_id=int(user_id),
                text=f"📢 Broadcast Message:\n\n{message}"
            )
            success_count += 1
        except Exception:
            fail_count += 1
    
    await update.message.reply_text(
        f"✅ Broadcast completed!\n\n"
        f"✔️ Sent: {success_count}\n"
        f"❌ Failed: {fail_count}",
        reply_markup=get_main_keyboard()
    )
    return ConversationHandler.END

async def handle_prize_claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    
    if not args or not args[0].startswith('prize'):
        return
    
    giveaway_id = args[0].replace('prize', '')
    giveaway = db.get_giveaway(giveaway_id)
    
    if not giveaway:
        await update.message.reply_text("❌ Invalid giveaway link.")
        return
    
    winner_id = giveaway.get('winner_id')
    
    if not winner_id:
        await update.message.reply_text("❌ This giveaway hasn't been completed yet.")
        return
    
    if user.id != winner_id:
        await update.message.reply_text("❌ You are not the winner of this giveaway!")
        return
    
    if giveaway.get('prize_claimed'):
        await update.message.reply_text("❌ Prize has already been claimed!")
        return
    
    prize_amount = giveaway.get('prize_amount', 0)
    user_data = db.get_user(user.id)
    new_balance = user_data.get('balance', 0) + prize_amount
    
    db.update_user_balance(user.id, new_balance)
    db.mark_prize_claimed(giveaway_id)
    
    await update.message.reply_text(
        f"🎉 Congratulations!\n\n"
        f"You won ₹{prize_amount:.2f}!\n"
        f"Your new balance: ₹{new_balance:.2f}",
        reply_markup=get_main_keyboard()
    )

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
            text=f"🎲 Dice Giveaway!\n\nPlease send a number between {min_number}-{max_number} ✅\nComment Down ❤️"
        )
        
        db.update_giveaway_message(giveaway_id, message.message_id)
        
        context.job_queue.run_once(
            start_giveaway_rolling,
            when=after_time * 60,
            data=giveaway_id,
            name=f"roll_{giveaway_id}"
        )
        
    except Exception as e:
        logger.error(f"Failed to send giveaway message: {e}")

async def start_giveaway_rolling(context: ContextTypes.DEFAULT_TYPE):
    giveaway_id = context.job.data
    giveaway = db.get_giveaway(giveaway_id)
    
    if not giveaway:
        return
    
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
        
        db.set_giveaway_winner(giveaway_id, winner_id)
        
        await context.bot.send_message(
            chat_id=channel,
            text=f"🎉 Giveaway Result!\n\n"
                 f"Number: {total}\n"
                 f"Winner: @{winner_username}\n\n"
                 f"Winner, please click here to grab the prize:\n"
                 f"[Click Here](https://t.me/WeooGiveawayBot?start=prize{giveaway_id})",
            parse_mode='Markdown'
        )
        
        db.update_giveaway_status(giveaway_id, 'completed')
    else:
        # No winner - refund creator and mark as completed
        creator_id = giveaway.get('user_id')
        prize_amount = giveaway.get('prize_amount', 0)
        
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



async def receive_after_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Back":
        await update.message.reply_text(
            "Please send the prize amount:",
            reply_markup=get_back_keyboard()
        )
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
                f"Please save as draft and add funds to your balance.\n"
                f"Contact {DEVELOPER_CONTACT} to add funds."
            )
        
        await update.message.reply_text(
            summary,
            reply_markup=get_draft_set_keyboard()
        )
        
        context.user_data['waiting_for_draft_set'] = True
        return AFTER_TIME
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number of minutes:",
            reply_markup=get_back_keyboard()
        )
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
            'send_time': context.user_data.get('send_time'),
            'after_time': context.user_data.get('after_time')
        }
        
        draft_id = db.add_draft(user.id, draft_data)
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
            await update.message.reply_text(
                "❌ Insufficient balance! Please save as draft and add funds first.",
                reply_markup=get_main_keyboard()
            )
            context.user_data.clear()
            return ConversationHandler.END
    
    elif text == "Back":
        await update.message.reply_text(
            "Please enter time in minutes for when the giveaway should start after being sent:",
            reply_markup=get_back_keyboard()
        )
        return AFTER_TIME

async def handle_my_giveaways(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    giveaways = db.get_user_giveaways(user.id)
    
    if not giveaways:
        await update.message.reply_text(
            "📋 My Giveaways\n\n"
            "You haven't created any giveaways yet.\n"
            "Use 'Create Giveaway' to get started!",
            reply_markup=get_main_keyboard()
        )
        return
    
    message = "📋 My Giveaways\n\n"
    for idx, giveaway in enumerate(giveaways, 1):
        message += (
            f"{idx}. {giveaway.get('giveaway_type', 'Unknown').title()} Giveaway\n"
            f"   Prize: ₹{giveaway.get('prize_amount', 0):.2f}\n"
            f"   Status: {giveaway.get('status', 'Unknown')}\n"
            f"   Send Time: {giveaway.get('send_time', 'Not set')}\n\n"
        )
    
    await update.message.reply_text(
        message,
        reply_markup=get_main_keyboard()
    )

async def handle_drafts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    drafts = db.get_user_drafts(user.id)
    
    if not drafts:
        await update.message.reply_text(
            "📝 Drafts\n\n"
            "You don't have any draft giveaways.",
            reply_markup=get_main_keyboard()
        )
        return
    
    message = "📝 Draft Giveaways\n\n"
    for idx, draft in enumerate(drafts, 1):
        message += (
            f"{idx}. {draft.get('giveaway_type', 'Unknown').title()} Giveaway\n"
            f"   Prize: ₹{draft.get('prize_amount', 0):.2f}\n"
            f"   Channel: {draft.get('channel', 'Not set')}\n\n"
        )
    
    await update.message.reply_text(
        message,
        reply_markup=get_main_keyboard()
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    
    # Only handle text in private chats, ignore group messages
    if update.message.chat.type != 'private':
        return
    
    text = update.message.text
    
    if text == "Balance":
        await handle_balance(update, context)
    elif text == "Add":
        await handle_add(update, context)
    elif text == "Out":
        await handle_out(update, context)
    elif text == "Help":
        await handle_help(update, context)
    elif text == "Contact":
        await handle_contact(update, context)
    elif text == "My Giveaways":
        await handle_my_giveaways(update, context)
    elif text == "Drafts":
        await handle_drafts(update, context)
    else:
        await update.message.reply_text(
            "🚧 Coming soon...\n\n"
            "This feature is under development!",
            reply_markup=get_main_keyboard()
        )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Cancelled.",
        reply_markup=get_main_keyboard()
    )
    context.user_data.clear()
    return ConversationHandler.END

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Create Giveaway$"), start_create_giveaway)],
        states={
            CHANNEL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_channel)],
            GIVEAWAY_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_giveaway_type)],
            DISCUSSION_GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_discussion_group)],
            DICE_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_dice_count)],
            PRIZE_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_prize_amount)],
            AFTER_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_after_time)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        allow_reentry=True
    )
    
    broadcast_handler = ConversationHandler(
        entry_points=[CommandHandler("broadcast", start_broadcast)],
        states={
            BROADCAST_MESSAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_broadcast_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("panel", admin_panel))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("add", add_balance_admin))
    application.add_handler(CommandHandler("remove", remove_balance_admin))
    application.add_handler(CommandHandler("say", say_to_user))
    application.add_handler(broadcast_handler)
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_giveaway_participation))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info("Bot started successfully!")
    
    async def post_init(application):
        scheduler.start()
        logger.info("Scheduler started successfully!")
    
    application.post_init = post_init
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
