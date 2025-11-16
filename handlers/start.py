
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import CHANNEL_USERNAME, ADMIN_USER_ID, DEVELOPER_CONTACT
from database import Database
from keyboards import get_main_keyboard, get_join_channel_keyboard

logger = logging.getLogger(__name__)
db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Check if user is banned
    if db.is_user_banned(user.id):
        await update.message.reply_text("❌ You are banned from using this bot.")
        return
    
    # Handle prize claim
    if context.args and context.args[0].startswith('prize'):
        await handle_prize_claim(update, context)
        return
    
    # Check channel membership
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user.id)
        if member.status in ['left', 'kicked']:
            await update.message.reply_text(
                f"⚠️ Please join our channel first:\n{CHANNEL_USERNAME}",
                reply_markup=get_join_channel_keyboard()
            )
            return
    except Exception as e:
        logger.error(f"Error checking channel membership: {e}")
    
    # Initialize user
    db.get_user(user.id)
    db.set_channel_joined(user.id, True)
    
    await update.message.reply_text(
        f"👋 Welcome {user.first_name}!\n\n"
        f"🎁 Create and manage giveaways easily\n"
        f"💰 Track your balance and withdrawals\n"
        f"📝 Save drafts for later\n\n"
        f"Use the buttons below to get started:",
        reply_markup=get_main_keyboard()
    )

async def handle_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db.get_user(user.id)
    balance = user_data.get('balance', 0.0)
    
    await update.message.reply_text(
        f"💰 Your Balance\n\n"
        f"Current Balance: ₹{balance:.2f}",
        reply_markup=get_main_keyboard()
    )

async def handle_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"💳 Add Funds\n\n"
        f"To add funds to your account, please contact the developer:\n"
        f"{DEVELOPER_CONTACT}\n\n"
        f"Provide your User ID: {update.effective_user.id}",
        reply_markup=get_main_keyboard()
    )

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "📖 Help & Instructions\n\n"
        "🎁 Create Giveaway:\n"
        "- Click 'Create Giveaway'\n"
        "- Choose your channel\n"
        "- Select Dice Giveaway\n"
        "- Set discussion group\n"
        "- Choose dice count (1-10)\n"
        "- Enter prize amount\n"
        "- Set start time\n\n"
        "💰 Balance:\n"
        "- View your current balance\n"
        "- Contact admin to add funds\n\n"
        "💸 Withdraw (Out):\n"
        "- Minimum: ₹5\n"
        "- Enter amount and UPI ID\n"
        "- Admin will process your request\n\n"
        "📝 Drafts:\n"
        "- Save incomplete giveaways\n"
        "- Activate when ready\n\n"
        "📊 My Giveaways:\n"
        "- View all your giveaways\n"
        "- Check status and details\n"
        "- Cancel scheduled ones"
    )
    
    await update.message.reply_text(help_text, reply_markup=get_main_keyboard())

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"📞 Contact Developer\n\n"
        f"For support, questions, or to add funds:\n"
        f"{DEVELOPER_CONTACT}\n\n"
        f"Your User ID: {update.effective_user.id}",
        reply_markup=get_main_keyboard()
    )

async def handle_prize_claim(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle prize claim from deep link"""
    user = update.effective_user
    args = context.args
    
    if not args or not args[0].startswith('prize'):
        return
    
    giveaway_id = args[0].replace('prize', '')
    giveaway = db.get_giveaway(giveaway_id)
    
    if not giveaway:
        await update.message.reply_text("❌ Invalid giveaway link.", reply_markup=get_main_keyboard())
        return
    
    winner_id = giveaway.get('winner_id')
    
    if not winner_id:
        await update.message.reply_text("❌ This giveaway hasn't been completed yet.", reply_markup=get_main_keyboard())
        return
    
    if user.id != winner_id:
        await update.message.reply_text("❌ You are not the winner of this giveaway!", reply_markup=get_main_keyboard())
        return
    
    if giveaway.get('prize_claimed'):
        await update.message.reply_text("❌ Prize has already been claimed!", reply_markup=get_main_keyboard())
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
