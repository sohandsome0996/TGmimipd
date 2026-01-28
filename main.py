from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
import time

# 你的机器人配置（已填好，直接用）
BOT_TOKEN = "8527067919:AAG8PzWMX7mEJDXpZ0Dxnj04TGZ1FgdcNk"
ADMIN_ID = 7976084446
TARGET_CHANNEL_ID = "-1003647769908"

# 启动命令
def start(update: Update, context: CallbackContext):
    update.message.reply_text("👋 欢迎使用匿名投稿机器人！\n直接发送文字/图片/视频即可投稿~")

# 处理用户投稿（文字/图片/视频都支持）
def handle_submit(update: Update, context: CallbackContext):
    msg = update.message
    user_id = update.effective_user.id
    # 构建审核按钮
    keyboard = [[
        InlineKeyboardButton("✅ 通过", callback_data=f"pass_{msg.message_id}_{user_id}"),
        InlineKeyboardButton("❌ 拒绝", callback_data=f"reject_{msg.message_id}_{user_id}")
    ]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # 发送审核通知给管理员
    context.bot.send_message(chat_id=ADMIN_ID, text=f"📥 新投稿（用户ID：{user_id}）：", reply_markup=reply_markup)
    # 转发投稿内容给管理员
    msg.forward(chat_id=ADMIN_ID)
    # 回复投稿人
    update.message.reply_text("✅ 投稿成功！等待管理员审核~")

# 处理管理员审核操作
def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()  # 必须加，否则 Telegram 会报错
    # 解析按钮参数
    action, msg_id, user_id = query.data.split("_")
    if action == "pass":
        # 审核通过：转发到目标频道
        context.bot.forward_message(
            chat_id=TARGET_CHANNEL_ID,
            from_chat_id=ADMIN_ID,
            message_id=int(msg_id)
        )
        # 通知投稿人通过
        context.bot.send_message(chat_id=user_id, text="✅ 你的投稿已通过审核，已发布到频道！")
        # 更新审核消息文字
        query.edit_message_text(text="✅ 已通过并发布到频道")
    else:
        # 审核拒绝：仅通知投稿人
        context.bot.send_message(chat_id=user_id, text="❌ 你的投稿未通过审核。")
        query.edit_message_text(text="❌ 已拒绝")

# 主函数：启动机器人 + 报错自动重启（保活）
def main():
    while True:
        try:
            # 初始化机器人
            updater = Updater(BOT_TOKEN)
            dp = updater.dispatcher
            # 注册所有功能
            dp.add_handler(CommandHandler("start", start))
            dp.add_handler(MessageHandler(Filters.all & ~Filters.command, handle_submit))
            dp.add_handler(CallbackQueryHandler(handle_callback))
            # 启动机器人
            updater.start_polling(poll_interval=3, timeout=10)
            print("="*50)
            print("🤖 匿名投稿机器人启动成功！可以正常使用了～")
            print(f"📌 管理员ID：{ADMIN_ID}")
            print(f"📌 目标频道ID：{TARGET_CHANNEL_ID}")
            print("="*50)
            updater.idle()
        except Exception as e:
            # 有报错就 5 秒后自动重启，不影响使用
            print(f"⚠️  机器人临时中断，5秒后自动重启 | 报错信息：{str(e)[:50]}")
            time.sleep(5)

if __name__ == "__main__":

    main()
    # 之前的代码（命令、处理器等）
@dp.message_handler(commands=['start'])
async def start_cmd(message):
    await message.answer('欢迎使用机器人！')

# 机器人启动轮询，持续监听消息（核心行，必须有）
if __name__ == '__main__':
    dp.start_polling()
