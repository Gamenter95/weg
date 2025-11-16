
from telegram import KeyboardButton, ReplyKeyboardMarkup

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
