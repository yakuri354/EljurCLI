import logging
from functools import wraps
import telegram.ext as tb
import telegram as tg


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
bot = tb.Updater(token="932266569:AAFYG_Mk6RWlni3EqKX23138TYaUkqE1bik", use_context=True)
greeting = """
Available commands:
/add: add a task
/remove: remove a task
/list: list all saved tasks
/clear: clear all your tasks
"""

users = []
remove_uid = ""
to_remove = False
reminders = []

class User:
    def __init__(self, username):
        self.task_list = []
        self.uid = username

    def append(self, task):
        self.task_list.append(task)

    def clear(self):
        self.task_list = []

    def remove(self, task):
        self.task_list.remove(task)

    def __str__(self):
        return "User: " + str(users.index(self)) + "\nUsername: " + self.uid + "\n" + str(
            len(self.task_list)) + " tasks"


def send_typing_action(func):
    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=tg.ChatAction.TYPING)
        return func(update, context, *args, **kwargs)
    return command_func


def find_user(uid):
    for x in users:
        if x.uid == uid:
            return x


def build_menu(buttons, n_cols, header_buttons=None, footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


print("Successfully connected!")


@send_typing_action
def start(update, context):
    uid = update.effective_user.username
    if User(uid) not in users:
        users.append(User(uid))
        print("Added new User!")
    context.bot.send_message(update.effective_chat.id, greeting)


@send_typing_action
def list_tasks(update, context):
    global users
    uid = update.effective_user.username
    current_user = find_user(uid)
    print("Listing tasks for user " + str(current_user.uid))
    task_list = current_user.task_list
    task_string = ""
    for i in range(len(task_list)):
        task_string += "Task {0}: {1}\n".format(i + 1, task_list[i])
    if task_string == "":
        task_string = "You have no tasks!"
    print(task_list)
    context.bot.send_message(update.effective_chat.id, task_string)


@send_typing_action
def add_task(update, context):
    global users
    if context.args == [] or None or "":
        context.bot.send_message(update.effective_chat.id, "What task do you want to add?")
    uid = update.effective_user.username
    current_user = find_user(uid)
    task_text = " ".join(context.args)
    current_user.append(task_text)
    print("Adding task: " + task_text + " for user: " + str(current_user.uid) + ". This user now has " +
          str(len(current_user.task_list)) + " task(s).")
    context.bot.send_message(update.effective_chat.id, "Task added: {0}".format(task_text))
    context.bot.send_message(update.effective_chat.id, "Do you want me to remind you?")


@send_typing_action
def remove_task(update, context):
    uid = update.effective_user.username
    current_user = find_user(uid)
    top_header = tg.InlineKeyboardButton("Select a task to delete")
    bottom_footer = tg.InlineKeyboardButton("Cancel", callback_data="cancel")
    markup = tg.ReplyKeyboardMarkup(current_user.task_list, True, True)
    context.bot.send_message(update.effective_chat.id, "Choose a task to delete:", reply_markup=markup)


def remover_handler(update, context):
    print("                                 !!!!!reg")
    uid = update.effective_user.username
    current_user = find_user(uid)
    cb_data = " ".join(context.args)
    if cb_data not in current_user.task_list:
        context.bot.send_message(update.effective_chat.id, "Specified task not found!")
        return
    current_user.remove(cb_data)
    context.bot.send_message(update.effective_chat.id, "Task " + cb_data + " successfully removed!")


@send_typing_action
def clear_tasks(update, context):
    uid = update.effective_user.username
    find_user(uid).clear()
    context.bot.send_message(update.effective_chat.id, "Task list cleared!")


bot.dispatcher.add_handler(tb.CommandHandler('start', start))
bot.dispatcher.add_handler(tb.CommandHandler('add', add_task))
bot.dispatcher.add_handler(tb.CommandHandler('remove', remove_task))
bot.dispatcher.add_handler(tb.CommandHandler('list', list_tasks))
bot.dispatcher.add_handler(tb.CommandHandler('clear', clear_tasks))

bot.start_polling()
