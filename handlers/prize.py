
from telegram import Update
from telegram.ext import ContextTypes
from database import Database
from keyboards import get_main_keyboard

db = Database()

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
