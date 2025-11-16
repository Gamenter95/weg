
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import ADMIN_USER_ID, MIN_AMOUNT, DEVELOPER_CONTACT
from database import Database
from keyboards import get_back_keyboard, get_main_keyboard

logger = logging.getLogger(__name__)
db = Database()

WITHDRAW_AMOUNT, WITHDRAW_UPI = range(2)

async def start_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_data = db.get_user(user.id)
    balance = user_data.get('balance', 0.0)
    
    await update.message.reply_text(
        f"💸 Withdraw Funds\n\n"
        f"Your Balance: ₹{balance:.2f}\n"
        f"Minimum withdraw amount: ₹{MIN_AMOUNT}\n\n"
        f"Please enter the amount you want to withdraw:",
        reply_markup=get_back_keyboard()
    )
    return WITHDRAW_AMOUNT

async def receive_withdraw_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Back":
        await update.message.reply_text("Withdrawal cancelled.", reply_markup=get_main_keyboard())
        return ConversationHandler.END
    
    try:
        amount = float(text)
        user = update.effective_user
        user_data = db.get_user(user.id)
        balance = user_data.get('balance', 0.0)
        
        if amount < MIN_AMOUNT:
            await update.message.reply_text(
                f"❌ Minimum withdrawal amount is ₹{MIN_AMOUNT}\n\n"
                f"Please enter a valid amount:",
                reply_markup=get_back_keyboard()
            )
            return WITHDRAW_AMOUNT
        
        if amount > balance:
            await update.message.reply_text(
                f"❌ Insufficient balance!\n\n"
                f"Your balance: ₹{balance:.2f}\n"
                f"Requested: ₹{amount:.2f}\n\n"
                f"Please enter a valid amount:",
                reply_markup=get_back_keyboard()
            )
            return WITHDRAW_AMOUNT
        
        context.user_data['withdraw_amount'] = amount
        await update.message.reply_text(
            f"✅ Amount: ₹{amount:.2f}\n\n"
            f"Please enter your UPI ID:",
            reply_markup=get_back_keyboard()
        )
        return WITHDRAW_UPI
    except ValueError:
        await update.message.reply_text("❌ Please enter a valid number:", reply_markup=get_back_keyboard())
        return WITHDRAW_AMOUNT

async def receive_withdraw_upi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Back":
        await update.message.reply_text("Please enter the amount you want to withdraw:", reply_markup=get_back_keyboard())
        return WITHDRAW_AMOUNT
    
    upi_id = text
    user = update.effective_user
    amount = context.user_data.get('withdraw_amount', 0)
    
    withdrawal_id = db.add_withdrawal_request(user.id, amount, upi_id)
    
    user_data = db.get_user(user.id)
    new_balance = user_data.get('balance', 0) - amount
    db.update_user_balance(user.id, new_balance)
    
    keyboard = [
        [
            InlineKeyboardButton("✅ Done", callback_data=f"withdraw_done_{withdrawal_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"withdraw_reject_{withdrawal_id}")
        ]
    ]
    
    try:
        await context.bot.send_message(
            chat_id=ADMIN_USER_ID,
            text=f"💸 New Withdrawal Request\n\n"
                 f"Request ID: #{withdrawal_id}\n"
                 f"User: {user.first_name} (@{user.username or 'No username'})\n"
                 f"User ID: {user.id}\n"
                 f"Amount: ₹{amount:.2f}\n"
                 f"UPI ID: {upi_id}\n"
                 f"Status: Pending",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"Failed to send withdrawal request to admin: {e}")
    
    await update.message.reply_text(
        f"✅ Withdrawal request submitted!\n\n"
        f"Amount: ₹{amount:.2f}\n"
        f"UPI ID: {upi_id}\n"
        f"Request ID: #{withdrawal_id}\n\n"
        f"₹{amount:.2f} has been deducted from your balance.\n"
        f"New balance: ₹{new_balance:.2f}\n\n"
        f"Your request is being reviewed by the admin.\n"
        f"You will be notified once it's processed.",
        reply_markup=get_main_keyboard()
    )
    
    context.user_data.clear()
    return ConversationHandler.END
