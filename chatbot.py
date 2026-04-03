'''
This program requires the following modules:
- python-telegram-bot==22.5
- urllib3==2.6.2
- psycopg2-binary   
'''
from ChatGPT_HKBU import ChatGPT
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
import configparser
import logging
import psycopg2
from datetime import datetime

gpt = None
db_conn = None

def main():
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

    logging.info('INIT: Loading configuration...')
    config = configparser.ConfigParser()
    config.read('config.ini')
    global gpt, db_conn
    gpt = ChatGPT(config)
    logging.info('INIT: Connecting to AWS RDS database for logging...')
    try:
        db_conn = psycopg2.connect(
            host=config['DATABASE']['HOST'],
            dbname=config['DATABASE']['DBNAME'],
            user=config['DATABASE']['USER'],
            password=config['DATABASE']['PASSWORD'],
            port=config['DATABASE']['PORT']
        )
        cur = db_conn.cursor()
        
        # create table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS interaction_logs (
                id SERIAL PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_id BIGINT,
                username TEXT,
                user_message TEXT,
                bot_response TEXT
            )
        """)
        db_conn.commit()
        cur.close()
        
        logging.info('✅ Database connected and table is ready!')
    except Exception as e:
        logging.error(f'❌ Database connection failed: {e}')
        db_conn = None
    # =====================================================================

    logging.info('INIT: Connecting the Telegram bot...')
    app = ApplicationBuilder().token(config['TELEGRAM']['ACCESS_TOKEN']).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, callback))

    logging.info('INIT: Initialization done! Bot is running...')
    app.run_polling()


async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"📨 User {update.message.from_user.id} ({update.message.from_user.username}): {update.message.text}")

    loading_message = await update.message.reply_text('Thinking...')

    # 调用 LLM
    response = gpt.submit(update.message.text)

    # 发送回复
    await loading_message.edit_text(response)

    # ==================== 【核心 Must-Have】写入数据库日志 ====================
    if db_conn:
        try:
            cur = db_conn.cursor()
            cur.execute("""
                INSERT INTO interaction_logs 
                (timestamp, user_id, username, user_message, bot_response)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                datetime.now(),
                update.message.from_user.id,
                update.message.from_user.username or "unknown",
                update.message.text,
                response
            ))
            db_conn.commit()
            cur.close()
            logging.info('✅ Interaction logged to RDS')
        except Exception as e:
            logging.error(f'❌ Failed to log to DB: {e}')
    # =====================================================================


if __name__ == '__main__':
    main()
