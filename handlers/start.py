
import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import CHANNEL_USERNAME, DEVELOPER_CONTACT
from database import Database
from keyboards import get_main_keyboard

logger = logging.getLogger(__name__)
db = Database()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if db.is_user_banned(user.id):
        await update.message.reply_text("⛔ You have been banned from using this bot.")
        return
    
    if context.args:
        from handlers.prize import handle_prize_claim
        await handle_prize_claim(update, context)
        return
    
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user.id)
        if member.status in ['member', 'administrator', 'creator']:
            db.set_channel_joined(user.id, True)
        else:
            await update.message.reply_text(
                f"Welcome to Weoo Giveaway Bot! 🎉\n\n"
                f"Please join our channel {CHANNEL_USERNAME} first and then send /start again."
            )
            return
    except Exception:
        await update.message.reply_text(
            f"Welcome to Weoo Giveaway Bot! 🎉\n\n"
            f"Please join our channel {CHANNEL_USERNAME} first and then send /start again."
        )
        return
    
    welcome_message = (
        f"Welcome {user.first_name}! 🎉\n\n"
        f"I'm Weoo Giveaway Bot, your assistant for creating and managing dice giveaways!\n\n"
        f"Use the buttons below to navigate:"
    )
    
    await update.message.reply_text(welcome_message, reply_markup=get_main_keyboard())

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
        f"Minimum add amount: ₹5",
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
        "7. Set after time\n"
        "8. Save as draft or set to schedule\n\n"
        f"For support, contact {DEVELOPER_CONTACT}"
    )
    
    await update.message.reply_text(help_text, reply_markup=get_main_keyboard())

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
    
    await update.message.reply_text(contact_text, reply_markup=get_main_keyboard())
