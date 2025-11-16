
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import ADMIN_USER_ID
from database import Database
from keyboards import get_back_keyboard, get_main_keyboard

logger = logging.getLogger(__name__)
db = Database()

BROADCAST_MESSAGE = 0

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
            await context.bot.send_message(chat_id=int(user_id), text=f"📢 Broadcast Message:\n\n{message}")
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

async def handle_withdraw_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    withdrawal_id = query.data.replace("withdraw_done_", "")
    withdrawal = db.get_withdrawal_request(withdrawal_id)
    
    if not withdrawal:
        await query.edit_message_text("❌ Withdrawal request not found!")
        return
    
    if withdrawal.get('status') != 'pending':
        await query.edit_message_text(f"❌ This request has already been {withdrawal.get('status')}!")
        return
    
    db.update_withdrawal_status(withdrawal_id, 'completed')
    
    user_id = withdrawal.get('user_id')
    amount = withdrawal.get('amount')
    
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ Withdrawal Completed!\n\n"
                 f"Request ID: #{withdrawal_id}\n"
                 f"Amount: ₹{amount:.2f}\n"
                 f"UPI ID: {withdrawal.get('upi_id')}\n\n"
                 f"Your withdrawal has been processed successfully!"
        )
    except Exception as e:
        logger.error(f"Failed to notify user about withdrawal completion: {e}")
    
    await query.edit_message_text(
        f"✅ Withdrawal request #{withdrawal_id} marked as completed!\n\n"
        f"User has been notified.",
        reply_markup=None
    )

async def handle_withdraw_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Please send the rejection reason as a message.")
    
    withdrawal_id = query.data.replace("withdraw_reject_", "")
    withdrawal = db.get_withdrawal_request(withdrawal_id)
    
    if not withdrawal:
        await query.edit_message_text("❌ Withdrawal request not found!")
        return
    
    if withdrawal.get('status') != 'pending':
        await query.edit_message_text(f"❌ This request has already been {withdrawal.get('status')}!")
        return
    
    context.user_data['rejecting_withdrawal'] = withdrawal_id
    
    await context.bot.send_message(
        chat_id=ADMIN_USER_ID,
        text=f"Please send the rejection reason for withdrawal #{withdrawal_id}:"
    )

async def handle_rejection_reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        return
    
    withdrawal_id = context.user_data.get('rejecting_withdrawal')
    
    if not withdrawal_id:
        return
    
    reason = update.message.text
    withdrawal = db.get_withdrawal_request(withdrawal_id)
    
    if not withdrawal:
        await update.message.reply_text("❌ Withdrawal request not found!")
        context.user_data.pop('rejecting_withdrawal', None)
        return
    
    db.update_withdrawal_status(withdrawal_id, 'rejected', reason)
    
    user_id = withdrawal.get('user_id')
    amount = withdrawal.get('amount')
    
    user_data = db.get_user(user_id)
    new_balance = user_data.get('balance', 0) + amount
    db.update_user_balance(user_id, new_balance)
    
    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=f"❌ Withdrawal Rejected\n\n"
                 f"Request ID: #{withdrawal_id}\n"
                 f"Amount: ₹{amount:.2f}\n\n"
                 f"Reason: {reason}\n\n"
                 f"₹{amount:.2f} has been refunded to your balance.\n"
                 f"New balance: ₹{new_balance:.2f}"
        )
    except Exception as e:
        logger.error(f"Failed to notify user about withdrawal rejection: {e}")
    
    await update.message.reply_text(
        f"✅ Withdrawal request #{withdrawal_id} rejected!\n\n"
        f"User has been notified and amount refunded."
    )
    
    context.user_data.pop('rejecting_withdrawal', None)
