
from telegram import ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from config import CHANNEL_USERNAME

def get_main_keyboard():
    keyboard = [
        ["Create Giveaway", "Balance"],
        ["My Giveaways", "Drafts"],
        ["Out", "Add"],
        ["Help", "Contact"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_back_keyboard():
    keyboard = [["Back"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_giveaway_type_keyboard():
    keyboard = [
        ["Dice Giveaway"],
        ["Back"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_dice_count_keyboard():
    keyboard = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9", "10"],
        ["Back"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_draft_set_keyboard():
    keyboard = [
        ["Draft", "Set"],
        ["Back"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_join_channel_keyboard():
    keyboard = [
        [InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}")]
    ]
    return InlineKeyboardMarkup(keyboard)
