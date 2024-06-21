import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile

class Bot:
    def __init__(self, token, telegram_chat_url):
        self.telegram_bot_client = telebot.TeleBot(token)
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)

        retries = 4 
        for _ in range(retries):
            try:
                #self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)
                with open("/usr/src/app/YOURPUBLIC.pem", 'r') as cert:
                    self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', certificate=cert, timeout=60)
                logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')
                break  # Break out of the retry loop if successful
            except telebot.apihelper.ApiTelegramException as e:
                if e.error_code == 429:  # Too Many Requests error
                    retry_after = int(e.result_json.get('parameters', {}).get('retry_after', 1))
                    logger.warning(f"Too Many Requests. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                else:
                    raise e  # Re-raise the exception if it's not a 429 error
        else:
            logger.error("Failed to set webhook after retries")

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)
        time.sleep(3)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)
        time.sleep(3)

    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')
        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)
        time.sleep(3)
        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")
        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )
        time.sleep(3)

    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')
        time.sleep(3)

class ObjectDetectionBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')
        if "text" in msg and msg["text"] == "hi":
            self.send_text(msg['chat']['id'], f"Hi: {msg['chat']['first_name']} {msg['chat']['last_name']}, how can I help you?")
        if self.is_current_msg_photo(msg):
            photo_path = self.download_user_photo(msg)
            # TODO upload the photo to S3
            # TODO send a job to the SQS queue
            # TODO send message to the Telegram end-user (e.g. Your image is being processed. Please wait...)
