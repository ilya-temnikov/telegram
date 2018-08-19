# name:            HashTagCommentsBot
# token:           691311826:AAHkw8X7dWHGkfjchvmJAtic3_R2z6bTNaU
# chat_id:         191609600
# receive message: https://api.telegram.org/bot691311826:AAHkw8X7dWHGkfjchvmJAtic3_R2z6bTNaU/getUpdates
# send message:    https://api.telegram.org/bot691311826:AAHkw8X7dWHGkfjchvmJAtic3_R2z6bTNaU/sendMessage?chat_id=191609600&text=Hello

from telegram import *
from telegram.ext import *
import logging
import sqlite3

connection = sqlite3.connect("database")
cursor = connection.cursor()
#cursor.execute("delete from Liked_messages")
cursor.execute("DROP TABLE Liked_messages")
cursor.execute("CREATE TABLE IF NOT EXISTS Liked_messages (ID INT, text TEXT, user TEXT, sendId INT, likes INT,dislikes INT,messages INT,likedBy TEXT,dislikedBy TEXT)")

connection.commit()
connection.close()


#from telethon.tl.functions import *
tokenId = "691311826:AAHkw8X7dWHGkfjchvmJAtic3_R2z6bTNaU"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def button(bot, update):
    query = update.callback_query
    data=query.data
    if data=='like':
        text="+"
    if data=="dislike":
        text="-"
    conn = sqlite3.connect("database")
    cur = conn.cursor()
    cur.execute("select * from Liked_messages WHERE sendId = %s" % update.callback_query.message.message_id)
    res = cur.fetchone()
    likesManager(bot, update.callback_query.message,update.callback_query,text,res[0],res[1],res[2],0)
    conn.close()

def echo(bot, update):
    """Echo the user message."""
    update.message.reply_text("Answer: "+update.message.text)

def likesManager(bot,messageStruct,query,text,origId,origText,origUser,delete=1):
    chat = messageStruct.chat.id
    if delete:
        message = messageStruct.message_id
        bot.deleteMessage(chat_id=chat, message_id=message)
    conn = sqlite3.connect("database")
    cur = conn.cursor()
    cur.execute("select * from Liked_messages WHERE ID = %s" % origId)
    res = cur.fetchone()
    if res:
        likes = res[4]
        dislikes = res[5]
        messages = res[6]
        likedBy = res[7]
        dislikedBy = res[8]
    else:
        likes = 0
        dislikes = 0
        messages = 0
        likedBy = ""
        dislikedBy = ""
    stop = 0
    rep = query.from_user
    user=rep.username
    if user:
        user="_".join(user.split())
    fName = rep.first_name
    if fName:
        fName="_".join(fName.split())
    lName = rep.last_name
    if lName:
        lName="_".join(lName.split())
    if not user:
        if fName and lName:
            user = fName + "_" + lName
        elif fName:
            user = fName
        elif lName:
            user = lName
        else:
            user = str(rep.id)
    userName = user
    spl = likedBy.split(" ")
    if userName in spl:
        if text == "+":
            stop = 1
        else:
            likes = likes - 1
            likedBy = " ".join([l for l in spl if l != userName])
    spl = dislikedBy.split(" ")
    if userName in spl:
        if text == "-":
            stop = 1
        else:
            dislikes = dislikes - 1
            dislikedBy = " ".join([l for l in spl if l != userName])
    if not stop:
        likes = (likes + 1 if text == "+" else likes)
        dislikes = (dislikes + 1 if text == "-" else dislikes)
        messages = (messages + 1 if text not in ["-", "+"] else messages)
        strLikes = ("" if likes == 0 else str(likes))
        strDislikes = ("" if dislikes == 0 else str(dislikes))
        strMessages = ("" if messages == 0 else str(messages))
        if text == "+":
            likedBy = likedBy + userName + " "
        if text == "-":
            dislikedBy = dislikedBy + userName + " "
        keyboard = [
            [
                InlineKeyboardButton("👍" + strLikes, callback_data='like'),
                InlineKeyboardButton("👎" + strDislikes, callback_data='dislike'),
                # InlineKeyboardButton("↩" + strMessages, callback_data='reply')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard, resize_keyboard=True)
        #newText = origUser + " " + str(origId) + "\n" + origText
        #newText = "#M"+str(origId) +" from " + origUser + "\n" + origText
        newText = "<i>from</i> <b>" + origUser + "</b>\n" + origText
        if likedBy:
            newText = newText + "\n<b>Liked by:</b> " + likedBy
        if dislikedBy:
            newText = newText + "\n<b>Disliked by:</b> " + dislikedBy
        if res:
            id = res[3]
            cur.execute("UPDATE Liked_messages SET likes=? WHERE ID=?", [likes, origId])
            cur.execute("UPDATE Liked_messages SET dislikes=? WHERE ID=?", [dislikes, origId])
            cur.execute("UPDATE Liked_messages SET messages=? WHERE ID=?", [messages, origId])
            bot.deleteMessage(chat_id=chat, message_id=id)
        send = bot.send_message(
            chat_id=chat,
            text=newText,
            reply_markup=reply_markup,
            parse_mode="html"
        )
        id = send.message_id
        if res:
            cur.execute("UPDATE Liked_messages SET sendId=? WHERE ID=?", [id, origId])
            cur.execute("UPDATE Liked_messages SET likedBy=? WHERE ID=?", [likedBy, origId])
            cur.execute("UPDATE Liked_messages SET dislikedBy=? WHERE ID=?", [dislikedBy, origId])
        else:
            query = [str(origId), origText, origUser, id, likes, dislikes, messages, likedBy, dislikedBy]
            cur.execute(
                "insert into Liked_messages(ID, text, user, sendId,likes,dislikes,messages,likedBy,dislikedBy) values (?, ?, ?, ?,?,?,?,?,?)",
                query)
    conn.commit()
    conn.close()


def putTag(bot,update):
    if update.message.reply_to_message:
        text=update.message.text
        if text in ["+","-"]:
            origId = update.message.reply_to_message.message_id
            origText = update.message.reply_to_message.text
            #origUser = update.message.reply_to_message.from_user.username
            rep=update.message.reply_to_message.from_user
            user = rep.username
            if user:
                user = "_".join(user.split())
            fName = rep.first_name
            if fName:
                fName = "_".join(fName.split())
            lName = rep.last_name
            if lName:
                lName = "_".join(lName.split())
            if not user:
                if fName and lName:
                    user = fName + "_" + lName
                elif fName:
                    user = fName
                elif lName:
                    user = lName
                else:
                    user = str(rep.id)
            origUser=user
            likesManager(bot, update.message,update.message,text,origId,origText,origUser)

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(tokenId)

    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, putTag))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


def help(bot, update):
    update.message.reply_text("Use /start to test this bot.")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


if __name__ == '__main__':
    main()