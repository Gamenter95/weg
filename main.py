import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
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

db = Database()
scheduler = AsyncIOScheduler()

CHANNEL, GIVEAWAY_TYPE, DISCUSSION_GROUP, DICE_COUNT, PRIZE_AMOUNT, SEND_TIME, AFTER_TIME = range(7)

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
        "Make sure I'm added as an admin in that channel!\n\n"
        "You can also save this for later by typing 'Save for later'",
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
    
    if text.lower() == "save for later":
        await update.message.reply_text(
            "You can provide the channel later. For now, let's continue...\n\n"
            "Select giveaway type:",
            reply_markup=get_giveaway_type_keyboard()
        )
        context.user_data['channel'] = None
        return GIVEAWAY_TYPE
    
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
            "When should the giveaway message be sent?\n"
            "Please enter the time in format: HH:MM (24-hour format)\n"
            "Example: 12:00 or 23:30",
            reply_markup=get_back_keyboard()
        )
        return SEND_TIME
    except ValueError:
        await update.message.reply_text(
            "Please enter a valid number for the prize amount:",
            reply_markup=get_back_keyboard()
        )
        return PRIZE_AMOUNT

async def receive_send_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Back":
        await update.message.reply_text(
            "Please send the prize amount:",
            reply_markup=get_back_keyboard()
        )
        return PRIZE_AMOUNT
    
    try:
        time_parts = text.split(':')
        if len(time_parts) != 2:
            raise ValueError
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
        
        context.user_data['send_time'] = text
        await update.message.reply_text(
            f"Send time set to: {text}\n\n"
            "How long after sending should the giveaway start?\n"
            "Please enter time in minutes:\n"
            "Example: 5 (for 5 minutes)",
            reply_markup=get_back_keyboard()
        )
        return AFTER_TIME
    except ValueError:
        await update.message.reply_text(
            "Invalid time format. Please use HH:MM (24-hour format)\n"
            "Example: 12:00 or 23:30",
            reply_markup=get_back_keyboard()
        )
        return SEND_TIME

async def receive_after_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "Back":
        await update.message.reply_text(
            "Please enter the send time in HH:MM format:",
            reply_markup=get_back_keyboard()
        )
        return SEND_TIME
    
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
            f"Send Time: {context.user_data.get('send_time')}\n"
            f"Start After: {after_minutes} minutes\n\n"
            f"Your Balance: ₹{balance:.2f}\n"
        )
        
        if balance >= prize_amount:
            summary += "\n✅ You have sufficient balance!\n\nWhat would you like to do?"
            await update.message.reply_text(
                summary,
                reply_markup=get_draft_set_keyboard()
            )
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
        
        return ConversationHandler.END
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
                'send_time': context.user_data.get('send_time'),
                'after_time': context.user_data.get('after_time')
            }
            
            giveaway_id = db.add_giveaway(user.id, giveaway_data)
            new_balance = balance - prize_amount
            db.update_user_balance(user.id, new_balance)
            
            await update.message.reply_text(
                f"✅ Giveaway created successfully!\n\n"
                f"₹{prize_amount:.2f} has been deducted from your balance.\n"
                f"New balance: ₹{new_balance:.2f}\n\n"
                f"Your giveaway will be sent at {context.user_data.get('send_time')}",
                reply_markup=get_main_keyboard()
            )
            context.user_data.clear()
        else:
            await update.message.reply_text(
                "❌ Insufficient balance! Please save as draft and add funds first.",
                reply_markup=get_main_keyboard()
            )
            context.user_data.clear()
    
    elif text == "Back":
        await update.message.reply_text(
            "Giveaway creation cancelled.",
            reply_markup=get_main_keyboard()
        )
        context.user_data.clear()

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
    elif text in ["Draft", "Set", "Back"]:
        await handle_draft_set_choice(update, context)
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
            SEND_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_send_time)],
            AFTER_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_after_time)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
