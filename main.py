import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler, CallbackQueryHandler
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN, ADMIN_USER_ID
from handlers.start import start, handle_balance, handle_add, handle_help, handle_contact, handle_prize_claim
from handlers.giveaway import start_create_giveaway, receive_channel, receive_giveaway_type, receive_discussion_group, receive_dice_count, receive_prize_amount, receive_after_time, cancel, CHANNEL, GIVEAWAY_TYPE, DISCUSSION_GROUP, DICE_COUNT, PRIZE_AMOUNT, AFTER_TIME
from handlers.withdraw import start_withdraw, receive_withdraw_amount, receive_withdraw_upi, WITHDRAW_AMOUNT, WITHDRAW_UPI
from handlers.management import handle_my_giveaways, handle_drafts, handle_draft_activate, handle_draft_delete, handle_giveaway_view, handle_giveaway_cancel, handle_close_menu
from handlers.admin import admin_panel, ban_user, unban_user, add_balance_admin, remove_balance_admin, say_to_user, start_broadcast, receive_broadcast_message, handle_withdraw_done, handle_withdraw_reject, handle_rejection_reason, BROADCAST_MESSAGE
from handlers.giveaway_runner import handle_giveaway_participation
from keyboards import get_main_keyboard

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    if update.message.chat.type != 'private':
        return

    text = update.message.text

    if text == "Balance":
        await handle_balance(update, context)
    elif text == "Add":
        await handle_add(update, context)
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
            "Please use the buttons below to navigate.",
            reply_markup=get_main_keyboard()
        )

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

    withdraw_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Out$"), start_withdraw)],
        states={
            WITHDRAW_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_withdraw_amount)],
            WITHDRAW_UPI: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_withdraw_upi)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Commands first
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("panel", admin_panel))
    application.add_handler(CommandHandler("ban", ban_user))
    application.add_handler(CommandHandler("unban", unban_user))
    application.add_handler(CommandHandler("add", add_balance_admin))
    application.add_handler(CommandHandler("remove", remove_balance_admin))
    application.add_handler(CommandHandler("say", say_to_user))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(handle_withdraw_done, pattern="^withdraw_done_"))
    application.add_handler(CallbackQueryHandler(handle_withdraw_reject, pattern="^withdraw_reject_"))
    application.add_handler(CallbackQueryHandler(handle_draft_activate, pattern="^activate_draft_"))
    application.add_handler(CallbackQueryHandler(handle_draft_delete, pattern="^delete_draft_"))
    application.add_handler(CallbackQueryHandler(handle_giveaway_view, pattern="^view_giveaway_"))
    application.add_handler(CallbackQueryHandler(handle_giveaway_cancel, pattern="^cancel_giveaway_"))
    application.add_handler(CallbackQueryHandler(handle_close_menu, pattern="^close_menu$"))
    
    # Conversation handlers
    application.add_handler(broadcast_handler)
    application.add_handler(withdraw_handler)
    application.add_handler(conv_handler)
    
    # Group message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & (filters.ChatType.GROUP | filters.ChatType.SUPERGROUP), handle_giveaway_participation))
    
    # Private message handlers - handle buttons BEFORE conversation fallback
    application.add_handler(MessageHandler(filters.Regex("^(Balance|Add|Help|Contact|My Giveaways|Drafts)$") & filters.ChatType.PRIVATE, handle_text))
    
    # Admin rejection reason handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE & filters.User(ADMIN_USER_ID), handle_rejection_reason))
    
    # Catch-all for other private messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE, handle_text))

    logger.info("Bot started successfully!")

    async def post_init(application):
        scheduler.start()
        logger.info("Scheduler started successfully!")

    application.post_init = post_init
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()