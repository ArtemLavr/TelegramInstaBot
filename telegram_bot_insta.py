import logging
import requests
from lxml import html 
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters,  CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from random import seed
from random import randint
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from time import sleep
from explicit import waiter, XPATH
import itertools
from selenium.webdriver.common.action_chains import ActionChains
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

"https://habr.com/ru/"


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.

def main_menu_keyboard():
    keyboard = [ 
        [InlineKeyboardButton("Начать проверку", callback_data= "check_work")],
        [InlineKeyboardButton("Настройки", callback_data="setting_menu")]
        ]
    return InlineKeyboardMarkup(keyboard)


def start(update, context):
    update.message.reply_text("Главное Меню:",
                         reply_markup=main_menu_keyboard())
    
    

def main_menu(update, context):
    update.callback_query.message.edit_text("Главное Меню:",
                          reply_markup=main_menu_keyboard())



def setting_menu(update,context): 
        keyboard = [ 
            [InlineKeyboardButton("Посмотреть настройки", callback_data= "show_setting")],
            [InlineKeyboardButton("Изменить настройки", callback_data="change_setting_menu")],
            [InlineKeyboardButton("Назад", callback_data="main")]
            
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.message.edit_text('Меню настроек:', reply_markup=reply_markup)
    
def show_setting(update, context):
        username, password, bloger = setting_load()
        keyboard = [ 
            [InlineKeyboardButton("Назад", callback_data= "setting_menu")],
            [InlineKeyboardButton("Главное Меню", callback_data="main")],
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.message.edit_text(f"""
        Instagram логин: {username}
        Instagram пароль: {password}
        Аккаунт для проверки: {bloger}""", reply_markup=reply_markup)
        
def change_setting_menu(update,context): 
        keyboard = [ 
            [InlineKeyboardButton("Изменить свой аккаунт", callback_data= "change_setting_login")],
            [InlineKeyboardButton("Именить аккаунт для проверки", callback_data="change_setting_bloger")],
            [InlineKeyboardButton("Назад", callback_data="setting_menu")]
            
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.message.edit_text('Выберете настройки которые хотите изменить:', reply_markup=reply_markup)
    


def change_setting_login(update, context):
    update.callback_query.message.edit_text('Введите логин и пароль для Instagram через пробел')

def change_setting_bloger(update, context):
    update.callback_query.message.edit_text('Введите имя аккаунта для проверки')


def new_settings(update, context):
    logpass = update.message.text
    newSetting = logpass.split()
    if len(newSetting)==1:
        bloger = newSetting[0]
        with open("setting.json", "r") as jsonFile:
            data = json.load(jsonFile)

        data["bloger"] = bloger
        with open("setting.json", "w") as jsonFile:
            json.dump(data, jsonFile)

        keyboard = [ 
                [InlineKeyboardButton("Главное Меню", callback_data="main")],
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(f"""
            Данные введены:
            Аккаунт для проверки: {bloger}
                """, reply_markup=reply_markup)
    elif len(newSetting)==2:    
        insta_username = newSetting[0]
        password = newSetting[1]

        with open("setting.json", "r") as jsonFile:
            data = json.load(jsonFile)

        data["insta_username"] = insta_username
        data['password'] = password
        with open("setting.json", "w") as jsonFile:
            json.dump(data, jsonFile)
        
        keyboard = [ 
                [InlineKeyboardButton("Главное Меню", callback_data="main")],
                ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(f"""
            Данные введены:
            Instagram логин: {insta_username}
            Instagram пароль: {password}
                """, reply_markup=reply_markup)


def scrape_followers(driver, account):

    driver.get("https://www.instagram.com/{0}/".format(account))
    sleep(getRandomTime())
    
    driver.find_element_by_partial_link_text("following").click()
    waiter.find_element(driver, "//div[@role='dialog']", by=XPATH)
    allfoll = int(driver.find_element_by_xpath("//li[3]/a/span").text)

    actions = ActionChains(driver)
            
    follower_css = "ul div li:nth-child({}) a.notranslate"
    for group in itertools.count(start=1, step=12):
        for follower_index in range(group, group + 12):
            if follower_index > allfoll:
                raise StopIteration
            yield waiter.find_element(driver, follower_css.format(follower_index)).text

       
        last_follower = waiter.find_element(driver, follower_css.format(group+11))
        sleep(getRandomTime())
        driver.execute_script("arguments[0].scrollIntoView();", last_follower)
        

def setting_load():
    with open('setting.json') as f:
        data = json.load(f)

    return data["insta_username"], data["password"],data['bloger']




def check_work(update, context):
    
    username, password, bloger = setting_load()
    if username and password and bloger:

        driver = webdriver.Firefox()
        #   chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--disable-dev-shm-usage")
        # chrome_options.add_argument("--no-sandbox")
        # chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        # driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
        
        driver.get("https://www.instagram.com/accounts/login/")
        sleep(getRandomTime())
        # Login
        driver.find_element_by_name("username").send_keys(username)
        driver.find_element_by_name("password").send_keys(password)
        submit = driver.find_element_by_tag_name('form')
        submit.submit()
        
        
        
        sleep(getRandomTime())
        sheet_url = "https://docs.google.com/spreadsheets/d/1-j5qvUBKxwmQ86kGt60__hf2bWf7CQFscx03y4r7YoY/edit#gid=0"
        url_1 = sheet_url.replace("/edit#gid=", "/export?format=csv&gid=")
        followers_pd = pd.read_csv(url_1)
        bad_list = []
        for account in followers_pd.iloc[:,2]:
            flag = True
            for count, follower in enumerate(scrape_followers(driver, account=account), 1):
                if bloger == follower:
                    flag = False   
                    print(accountr+" +++")
            
            if flag:
                bad_list.append(account)

        keyboard = [ 
                [InlineKeyboardButton("Главное Меню", callback_data="main")],
                ]
        
        text ="""\n""".join()
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(f"""
            Не подписались:\n{text}
                """, reply_markup=reply_markup)

    else:
        keyboard = [ 
                [InlineKeyboardButton("Меню настроек", callback_data="setting_menu")],
                ]
        
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.callback_query.message.edit_text(f"Проверьте настройки. Не все данные заполнены.", reply_markup=reply_markup)


def getRandomTime():
        randTime = randint(3, 5)
        return randTime




def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1906300122:AAEqy-QNiXwA3plKD92-RCO-hvjcGO1Hpng", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("help", help_command))
    # dp.add_handler(CommandHandler("habr", habr))
    dp.add_handler(CallbackQueryHandler(main_menu, pattern='main'))
    dp.add_handler(CallbackQueryHandler(setting_menu, pattern='setting_menu'))
    dp.add_handler(CallbackQueryHandler(change_setting_menu, pattern='change_setting_menu'))
    dp.add_handler(CallbackQueryHandler(change_setting_bloger, pattern='change_setting_bloger'))
    dp.add_handler(CallbackQueryHandler(change_setting_login, pattern='change_setting_login'))
    dp.add_handler(CallbackQueryHandler(show_setting, pattern='show_setting'))
    dp.add_handler(CallbackQueryHandler(check_work, pattern='check_work'))
    
    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, new_settings))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()