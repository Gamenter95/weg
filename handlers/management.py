
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import Database
from keyboards import get_main_keyboard
from handlers.giveaway_runner import run_scheduled_giveaway

logger = logging.getLogger(__name__)
db = Database()

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
    
    message = "📋 My Giveaways\n\nSelect a giveaway to manage:\n\n"
    keyboard = []
    
    for idx, giveaway in enumerate(giveaways, 1):
        giveaway_id = giveaway.get('giveaway_id')
        status = giveaway.get('status', 'Unknown')
        
        status_emoji = "⏳" if status == "scheduled" else "✅" if status == "completed" else "❓"
        
        message += (
            f"{idx}. {giveaway.get('giveaway_type', 'Unknown').title()} Giveaway\n"
            f"   Prize: ₹{giveaway.get('prize_amount', 0):.2f}\n"
            f"   Status: {status_emoji} {status.title()}\n"
            f"   Participants: {len(giveaway.get('participants', []))}\n\n"
        )
        
        buttons = [InlineKeyboardButton(f"📊 Details #{idx}", callback_data=f"view_giveaway_{giveaway_id}")]
        
        if status == "scheduled":
            buttons.append(InlineKeyboardButton(f"❌ Cancel #{idx}", callback_data=f"cancel_giveaway_{giveaway_id}"))
        
        keyboard.append(buttons)
    
    keyboard.append([InlineKeyboardButton("« Back", callback_data="close_menu")])
    
    await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_drafts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    drafts = db.get_user_drafts(user.id)
    
    if not drafts:
        await update.message.reply_text("📝 Drafts\n\nYou don't have any draft giveaways.", reply_markup=get_main_keyboard())
        return
    
    message = "📝 Draft Giveaways\n\nSelect a draft to manage:\n\n"
    keyboard = []
    
    for idx, draft in enumerate(drafts, 1):
        draft_id = draft.get('draft_id')
        message += (
            f"{idx}. {draft.get('giveaway_type', 'Unknown').title()} Giveaway\n"
            f"   Prize: ₹{draft.get('prize_amount', 0):.2f}\n"
            f"   Channel: {draft.get('channel', 'Not set')}\n\n"
        )
        keyboard.append([
            InlineKeyboardButton(f"✅ Activate #{idx}", callback_data=f"activate_draft_{draft_id}"),
            InlineKeyboardButton(f"🗑️ Delete #{idx}", callback_data=f"delete_draft_{draft_id}")
        ])
    
    keyboard.append([InlineKeyboardButton("« Back", callback_data="close_menu")])
    
    await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_draft_activate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    draft_id = query.data.replace("activate_draft_", "")
    draft = db.get_draft(draft_id)
    
    if not draft:
        await query.edit_message_text("❌ Draft not found!")
        return
    
    user = update.effective_user
    user_data = db.get_user(user.id)
    prize_amount = draft.get('prize_amount', 0)
    balance = user_data.get('balance', 0.0)
    
    if balance < prize_amount:
        await query.edit_message_text(
            f"❌ Insufficient balance!\n\n"
            f"Required: ₹{prize_amount:.2f}\n"
            f"Your balance: ₹{balance:.2f}\n\n"
            f"Please add funds first."
        )
        return
    
    giveaway_data = {
        'channel': draft.get('channel'),
        'giveaway_type': draft.get('giveaway_type'),
        'discussion_group': draft.get('discussion_group'),
        'dice_count': draft.get('dice_count'),
        'prize_amount': prize_amount,
        'after_time': draft.get('after_time')
    }
    
    giveaway_id = db.add_giveaway(user.id, giveaway_data)
    new_balance = balance - prize_amount
    db.update_user_balance(user.id, new_balance)
    db.delete_draft(draft_id)
    
    await query.edit_message_text(
        f"✅ Draft activated successfully!\n\n"
        f"₹{prize_amount:.2f} has been deducted from your balance.\n"
        f"New balance: ₹{new_balance:.2f}\n\n"
        f"Sending giveaway to channel now..."
    )
    
    await run_scheduled_giveaway(context, giveaway_id)

async def handle_draft_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    draft_id = query.data.replace("delete_draft_", "")
    db.delete_draft(draft_id)
    
    await query.edit_message_text("✅ Draft deleted successfully!", reply_markup=None)

async def handle_giveaway_view(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    giveaway_id = query.data.replace("view_giveaway_", "")
    giveaway = db.get_giveaway(giveaway_id)
    
    if not giveaway:
        await query.edit_message_text("❌ Giveaway not found!")
        return
    
    participants = giveaway.get('participants', [])
    winner_id = giveaway.get('winner_id')
    
    details = (
        f"📊 Giveaway Details\n\n"
        f"Type: {giveaway.get('giveaway_type', 'Unknown').title()}\n"
        f"Channel: {giveaway.get('channel', 'N/A')}\n"
        f"Dice Count: {giveaway.get('dice_count', 1)}\n"
        f"Prize: ₹{giveaway.get('prize_amount', 0):.2f}\n"
        f"Status: {giveaway.get('status', 'Unknown')}\n"
        f"Participants: {len(participants)}\n"
    )
    
    if winner_id:
        winner = next((p for p in participants if p.get('user_id') == winner_id), None)
        if winner:
            details += f"Winner: @{winner.get('username', 'Unknown')}\n"
            details += f"Prize Claimed: {'Yes' if giveaway.get('prize_claimed') else 'No'}\n"
    
    keyboard = [[InlineKeyboardButton("« Back", callback_data="close_menu")]]
    
    await query.edit_message_text(details, reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_giveaway_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    giveaway_id = query.data.replace("cancel_giveaway_", "")
    giveaway = db.get_giveaway(giveaway_id)
    
    if not giveaway:
        await query.edit_message_text("❌ Giveaway not found!")
        return
    
    if giveaway.get('status') != 'scheduled':
        await query.edit_message_text("❌ Can only cancel scheduled giveaways!")
        return
    
    job_name = f"roll_{giveaway_id}"
    current_jobs = context.application.job_queue.get_jobs_by_name(job_name)
    for job in current_jobs:
        job.schedule_removal()
    
    user_id = giveaway.get('user_id')
    prize_amount = giveaway.get('prize_amount', 0)
    user_data = db.get_user(user_id)
    new_balance = user_data.get('balance', 0) + prize_amount
    db.update_user_balance(user_id, new_balance)
    
    db.update_giveaway_status(giveaway_id, 'cancelled')
    
    await query.edit_message_text(
        f"✅ Giveaway cancelled!\n\n"
        f"₹{prize_amount:.2f} has been refunded to your balance.\n"
        f"New balance: ₹{new_balance:.2f}",
        reply_markup=None
    )

async def handle_close_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.delete_message()
