# name:            HashTagCommentsBot
# token:           691311826:AAHkw8X7dWHGkfjchvmJAtic3_R2z6bTNaU
# chat_id:         191609600
# receive message: https://api.telegram.org/bot691311826:AAHkw8X7dWHGkfjchvmJAtic3_R2z6bTNaU/getUpdates
# send message:    https://api.telegram.org/bot691311826:AAHkw8X7dWHGkfjchvmJAtic3_R2z6bTNaU/sendMessage?chat_id=191609600&text=Hello
#cd C:\Users\Ilya\virtualenv\my_env\telegram
#git commit -m "text" HashTagCommentsBot.py
#git push heroky master



from telegram import *
from telegram.ext import *
import logging
import sqlite3
import math

connection = sqlite3.connect("database")
cursor = connection.cursor()
#cursor.execute("delete from Liked_messages")
#cursor.execute("DROP TABLE Liked_messages")
cursor.execute("CREATE TABLE IF NOT EXISTS Liked_messages (ID INT, text TEXT, user TEXT, sendId INT, likes INT,dislikes INT,messages INT,likedBy TEXT,dislikedBy TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS Locations (ID INT, sendID INT,prevX FLOAT,prevY FLOAT,x FLOAT,y FLOAT)")

connection.commit()
connection.close()

tokenId = "691311826:AAHkw8X7dWHGkfjchvmJAtic3_R2z6bTNaU"
tokenId = "761966309:AAHWzqBvNvqL6JO8cZL1keSDPDsm5pItbSw"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def button(bot, update):
    query = update.callback_query
    data=query.data
    text=""
    if data=='like':
        text="+"
    if data=="dislike":
        text="-"
    #if data=="reply":
    #    #update.callback_query.message.replyText("Reply the message")
    #    send = bot.send_message(
    #        chat_id=update.callback_query.message.chat.id,
    #        text="*",
    #        reply_markup=ForceReply(True)
    #    )
    #    #bot.deleteMessage(chat_id=update.callback_query.message.chat.id,message_id=send.message_id)
    #    #print(dir(query.message))
    #    #query.message.reply_text(text="aaaaa")
    #    #text="*"+send.text
    #    text="+"
    if text:
        conn = sqlite3.connect("database")
        cur = conn.cursor()
        cur.execute("select * from Liked_messages WHERE sendId = %s" % update.callback_query.message.message_id)
        res = cur.fetchone()
        if res:
            likesManager(bot, update.callback_query.message,update.callback_query,text,res[0],res[1],res[2],0,update.callback_query)
        conn.close()

def likesManager(bot,messageStruct,query,text,origId,origText,origUser,delete=1,qry=0):
    #origUser="test"
    chat = messageStruct.chat.id
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
    userName = getUserName(query)
    spl = likedBy.split(" ")
    dontEffect=0
    if userName in spl:
        #stop = 1
        if text == "+":
            #dontEffect=1
            if qry:
                bot.answerCallbackQuery(qry.id, "😓 You can't like the message twice")
            stop = 1
        #else:
        if text=="-":
            likes = likes - 1
            likedBy = " ".join([l for l in spl if l != userName])
            dontEffect = 1
            bot.answerCallbackQuery(qry.id, "↩ You've undone " + origUser + "'s message dislike")
    spl = dislikedBy.split(" ")
    if userName in spl:
        #stop = 1
        if text == "-":
            #dontEffect = 1
            if qry:
                bot.answerCallbackQuery(qry.id, "😓 You can't dislike the message twice")
            stop = 1
        #else:
        if text == "+":
            dislikes = dislikes - 1
            dislikedBy = " ".join([l for l in spl if l != userName])
            dontEffect = 1
            bot.answerCallbackQuery(qry.id, "↩ You've undone "+origUser+"'s message dislike")
    cur.execute("select * from Liked_messages WHERE ID = %s" % origId)
    res = cur.fetchone()
    if origUser==userName:
        if text in ['+','-','*']:
            stop=1
        if qry:
            if text == '+':
                bot.answerCallbackQuery(qry.id, "😓 You can't like your own message")
            if text == '-':
                bot.answerCallbackQuery(qry.id, "😓 You can't dislike your own message")
    if not stop:
        if not dontEffect:
            if text[0] == '+' and userName!=origUser:
                likes =likes + 1
                likedBy = likedBy + userName + " "
                if qry:
                    bot.answerCallbackQuery(qry.id, "👍 You've liked the message from "+origUser)
            if text[0] == '-' and userName != origUser:
                dislikes = dislikes + 1
                dislikedBy = dislikedBy + userName + " "
                if qry:
                    bot.answerCallbackQuery(qry.id, "👎 You've disliked the message from "+origUser)
        sendComment = 0
        if len(text)>1:
            messages = messages + 1
            sendComment=1
            text = text[1:]
        strLikes = ("" if likes == 0 else str(likes))
        strDislikes = ("" if dislikes == 0 else str(dislikes))
        strMessages = ("" if messages == 0 else str(messages))
        keyboard = [
            [
                InlineKeyboardButton("👍" + strLikes, callback_data='like'),
                InlineKeyboardButton("👎" + strDislikes, callback_data='dislike'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard, resize_keyboard=True)
        newText = "💬 " + origUser
        if messages>0:
            newText = newText + " ↩#M"+str(origId)+" ("+strMessages+")"
        newText = newText + "\n" + origText
        if likedBy:
            newText = newText + "\n👍 " + likedBy
        if dislikedBy:
            newText = newText + "\n👎 " + dislikedBy
        send = bot.send_message(
            chat_id=chat,
            text=newText,
            reply_markup=reply_markup,
            parse_mode="html"
        )
        if sendComment:
            comText = "↩#M" + str(origId) + " " + userName + "\n" + text
            bot.send_message(
                chat_id=chat,
                text=comText,
                parse_mode="html"
            )
        id = send.message_id
        if res:
            cur.execute("UPDATE Liked_messages SET sendId=? WHERE ID=?", [id, origId])
            cur.execute("UPDATE Liked_messages SET likedBy=? WHERE ID=?", [likedBy, origId])
            cur.execute("UPDATE Liked_messages SET dislikedBy=? WHERE ID=?", [dislikedBy, origId])
            cur.execute("UPDATE Liked_messages SET likes=? WHERE ID=?", [likes, origId])
            cur.execute("UPDATE Liked_messages SET dislikes=? WHERE ID=?", [dislikes, origId])
            cur.execute("UPDATE Liked_messages SET messages=? WHERE ID=?", [messages, origId])
            bot.deleteMessage(chat_id=chat, message_id=res[3])
        else:
            cur.execute(
                "insert into Liked_messages(ID, text, user, sendId,likes,dislikes,messages,likedBy,dislikedBy) values (?, ?, ?, ?,?,?,?,?,?)",
                [str(origId), origText, origUser, id, likes, dislikes, messages, likedBy, dislikedBy]
            )
    conn.commit()
    conn.close()
    if delete:
        bot.deleteMessage(chat_id=chat, message_id=messageStruct.message_id)

def putTag(bot,update):
    if update.message.reply_to_message:
        text=update.message.text
        origId = update.message.reply_to_message.message_id

        conn = sqlite3.connect("database")
        cur = conn.cursor()
        cur.execute("select * from Liked_messages WHERE sendId = %s" % origId)
        res = cur.fetchone()
        conn.close()
        if text[0] in ["+", "-", "*"] or res:
            if res:
                origId=res[0]
                origText = res[1]
                origUser = res[2]
                text="*"+text
            else:
                origText = update.message.reply_to_message.text
                origUser=getUserName(update.message.reply_to_message,update.message)
            likesManager(bot, update.message,update.message,text,origId,origText,origUser)

def getUserName(rep,mes=0):
    user = rep.from_user.username
    if user:
        if user=="HashTagCommentsBot":
            if(mes):
                user=getUserName(mes)
        else:
            user = "@" + "_".join(user.split())
    else:
        fName = rep.from_user.first_name
        if fName:
            fName = "_".join(fName.split())
        lName = rep.from_user.last_name
        if lName:
            lName = "_".join(lName.split())
        if fName and lName:
            user = fName + "_" + lName
        elif fName:
            user = fName
        elif lName:
            user = lName
        else:
            user = str(rep.from_user.id)
    return user
def showPic(bot,update):
    if update.edited_message:
        message = update.edited_message
        first=False
    else:
        message = update.message
        first=True

    #UNCOMMENT
    current_pos = [message.location.latitude, message.location.longitude]
    #current_pos=message.text.split(",")
    origId=message.message_id
    conn = sqlite3.connect("database")
    cur = conn.cursor()
    chat = message.chat.id
    x=str(current_pos[0])
    y=str(current_pos[1])
    base = "http://maps.google.com/maps?q=&layer=c&cbll="+x+","+y+"&cbp=11,"
    if first:
        MyUrl = base + "0,0,0,0"
        send = bot.send_message(
            chat_id=chat,
            text="<a href=\""+MyUrl+"\">Show Location Photo</a>",
            disable_web_page_preview=True,
            parse_mode="HTML",
        )
        cur.execute(
            "insert into Locations(ID,sendID,prevX,prevY,x,y) values (?,?,?,?,?,?)",
            [origId,send.message_id, x,y,x,y]
        )
    else:
        cur.execute("select * from Locations WHERE ID = %s" % origId)
        res = cur.fetchone()
        ang=math.degrees(math.atan2(float(current_pos[1])-res[3],float(current_pos[0])-res[2]))
        MyUrl = base + str(ang)+",0,0,0"
        if res:
            bot.editMessageText(
                chat_id=chat,
                message_id=res[1],
                text="<a href=\""+MyUrl+"\">Show Location Photo</a>",
                disable_web_page_preview=True,
                parse_mode="HTML",
            )
            cur.execute("UPDATE Locations SET prevX=? WHERE ID=?", [res[4], origId])
            cur.execute("UPDATE Locations SET prevY=? WHERE ID=?", [res[5], origId])
            cur.execute("UPDATE Locations SET x=? WHERE ID=?", [x, origId])
            cur.execute("UPDATE Locations SET y=? WHERE ID=?", [y, origId])
    conn.commit()
    conn.close()

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(tokenId)

    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, putTag))
    updater.dispatcher.add_handler(MessageHandler(Filters.location, showPic, edited_updates=True))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

if __name__ == '__main__':
    main()
