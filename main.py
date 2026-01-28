from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
)
import asyncio

# -------------------------- 直接用，不用改（已填你的信息） --------------------------
BOT_TOKEN = "8527067919:AAG8PzWMX7mEJDXpZ0Dxnj04TGZ1FgdcNk"
ADMIN_ID = 7976084446
TARGET_CHANNEL_ID = "-1003647769908"
# -----------------------------------------------------------------------------------

# 启动命令
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 欢迎使用匿名投稿机器人！\n直接发送文字/图片/视频即可投稿~")

# 处理投稿（核心）
async def handle_submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    user_id = update.effective_user.id
    # 构建审核按钮
    keyboard = [
        [InlineKeyboardButton("✅ 通过", callback_data=f"pass_{msg.message_id}_{user_id}"),
         InlineKeyboardButton("❌ 拒绝", callback_data=f"reject_{msg.message_id}_{user_id}")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # 转发给管理员
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"📥 新投稿（用户ID：{user_id}）：",
        reply_markup=reply_markup
    )
    # 转发消息内容给管理员
    await msg.forward(chat_id=ADMIN_ID)
    # 回复投稿人
    await update.message.reply_text("✅ 投稿成功！等待管理员审核~")

# 处理审核按钮
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    action, msg_id, user_id = data[0], data[1], data[2]
    if action == "pass":
        # 通过：转发到目标频道
        await context.bot.forward_message(
            chat_id=TARGET_CHANNEL_ID,
            from_chat_id=ADMIN_ID,
            message_id=int(msg_id)
        )
        # 通知投稿人
        await context.bot.send_message(
            chat_id=user_id,
            text="✅ 你的投稿已通过审核，已发布到频道！"
        )
        await query.edit_message_text(text="✅ 已通过并发布到频道")
    elif action == "reject":
        # 拒绝：通知投稿人
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ 你的投稿未通过审核。"
        )
        await query.edit_message_text(text="❌ 已拒绝")

# 主函数（新版异步启动）
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_submit))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.run_polling()

if __name__ == "__main__":
    main()
