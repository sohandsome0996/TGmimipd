import imghdr# TG 匿名投稿机器人（可自己投稿+审核）
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import time

# -------------------------- 必改3项 --------------------------
BOT_TOKEN = "8527067919:AAG8PzWMX7mEJDXpZODxnjdO4TGZlFgdcNk"  # @BotFather获取
ADMIN_ID = 7976084446             # 你的TG ID（@getidsbot获取）
TARGET_CHANNEL_ID = "-1003647769908"  # 投稿目标频道ID（@getidsbot获取）
# ----------------------------------------------------------------

# 启动命令
def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 欢迎使用匿名投稿机器人！\n直接发送文字/图片/视频即可投稿~")

# 处理投稿（核心）
def handle_submit(update: Update, context: CallbackContext):
    msg = update.message
    user_id = update.effective_user.id
    # 构建审核按钮
    keyboard = [
        [InlineKeyboardButton("✅ 通过", callback_data=f"pass_{msg.message_id}_{user_id}"),
         InlineKeyboardButton("❌ 拒绝", callback_data=f"reject_{msg.message_id}_{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # 转发给管理员
    context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📥 新投稿（用户ID：{user_id}）：",
        reply_markup=reply_markup
    )
    # 转发消息内容给管理员
    msg.forward(chat_id=ADMIN_ID)
    # 回复投稿人
    update.message.reply_text("✅ 投稿成功！等待管理员审核~")

# 处理审核按钮
def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    data = query.data.split("_")
    action, msg_id, user_id = data[0], data[1], data[2]
    if action == "pass":
        # 通过：转发到目标频道
        context.bot.forward_message(
            chat_id=TARGET_CHANNEL_ID,
            from_chat_id=ADMIN_ID,
            message_id=int(msg_id)
        )
        # 通知投稿人
        context.bot.send_message(
            chat_id=user_id,
            text="✅ 你的投稿已通过审核，已发布到频道！"
        )
        query.edit_message_text(text="✅ 已通过并发布到频道")
    elif action == "reject":
        # 拒绝：通知投稿人
        context.bot.send_message(
            chat_id=user_id,
            text="❌ 你的投稿未通过审核。"
        )
        query.edit_message_text(text="❌ 已拒绝")

# 保活机制（Railway用）
def main():
    while True:
        try:
            updater = Updater(BOT_TOKEN)
            dp = updater.dispatcher
            dp.add_handler(CommandHandler("start", start))
            dp.add_handler(MessageHandler(Filters.all & ~Filters.command, handle_submit))
            dp.add_handler(CallbackQueryHandler(handle_callback))
            updater.start_polling(poll_interval=3)
            print(f"🤖 投稿机器人启动成功！\n管理员ID：{ADMIN_ID}\n目标频道：{TARGET_CHANNEL_ID}")
            updater.idle()
        except Exception as e:
            print(f"⚠️ 机器人重启：{e}")
            time.sleep(5)

if __name__ == "__main__":
    main()

