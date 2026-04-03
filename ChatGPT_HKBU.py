import requests
import configparser

class ChatGPT:
    def __init__(self, config):
        api_key = config['CHATGPT']['API_KEY']
        base_url = config['CHATGPT']['BASE_URL']
        model = config['CHATGPT']['MODEL']
        api_ver = config['CHATGPT']['API_VER']

        self.url = f'{base_url}/deployments/{model}/chat/completions?api-version={api_ver}'

        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "api-key": api_key,
        }

        self.system_message = (
            'You are HKBU Campus Assistant Bot, an official AI helper for Hong Kong Baptist University '
            'students and staff. You are friendly, helpful, and conversational. '
            'You can answer questions about: courses, class schedules, campus facilities, library, '
            'canteens, events, clubs, transportation, weather in HK, and general university life. '
            'Reply in simple English or Chinese depending on the user\'s language. '
            'Always be encouraging and direct. If you don\'t know something, say so honestly and suggest '
            'where the user can find the information (e.g. HKBU website or app).'
        )
        # =============================================================================

    def submit(self, user_message: str):
        messages = [
            {"role": "system", "content": self.system_message},
            {"role": "user", "content": user_message},
        ]

        payload = {
            "messages": messages,
            "temperature": 1,
            "max_tokens": 300,
            "top_p": 1,
            "stream": False
        }

        response = requests.post(self.url, json=payload, headers=self.headers)

        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code} - {response.text}"


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    chatGPT = ChatGPT(config)
    while True:
        print('Input your query: ', end='')
        print(chatGPT.submit(input()))
