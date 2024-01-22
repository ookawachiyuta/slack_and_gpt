from flask import Flask,request,Response,jsonify,json
from dotenv import load_dotenv
import requests
import threading
import os
import openai

load_dotenv()

app = Flask(__name__)

def send_gpt(text):
    try:
        url = os.environ["SLACK_URL"]
        data ={"text":"〜〜少々お待ちください〜〜"}
        requests.post(url,json=data)

        openai.api_key = os.environ['OPENAI_APIKEY']
        completion = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            max_tokens = 1000,
            messages=[{"role": "user", "content": text},]
        )
        gpt_response = completion.choices[0].message.content
        print(gpt_response)

        blocks = [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "【回答】",
                            "emoji": True
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": gpt_response
                        }
                    }
                ]

        response = requests.post(url,json={"blocks": blocks})

        return response
    except Exception as e:
        url = os.environ["SLACK_URL"]
        data ={"text":"エラーで回答そ取得できませんでした"}
        requests.post(url,json=data)
        print(f"エラーが発生しました: {e}")
        return None 
    finally:
        print("ok")


@app.route('/button',methods=['POST'])
def slack_button():
    form_data = request.form
    slack_payload = json.loads(form_data["payload"])
    text = slack_payload["state"]["values"]["hYqy4"]["plain_text_input-action"]["value"]

    thread = threading.Thread(target=send_gpt, args=(text,))
    thread.start()
    return Response(), 200

@app.route('/slack',methods=['POST'])
def slack_challenge():
    slack_event = request.json

    if "challenge" in slack_event:
        print(slack_event)
        return Response(slack_event["challenge"],mimetype='text/plain')
    else:
        print(slack_event)
        url = os.environ["SLACK_URL"]
        blocks =[
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "ChatGPTに質問したいこと",
                            "emoji": True
                        }
                    },
                    {
                        "type": "input",
                        "element": {
                            "type": "plain_text_input",
                            "multiline": True,
                            "action_id": "plain_text_input-action"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "質問を記入",
                            "emoji": True
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "送信",
                                    "emoji": True
                                },
                                "value": "click_me_123",
                                "action_id": "actionId-0"
                            }
                        ]
                    }
                ]

        response = requests.post(url,json={"blocks": blocks})
        return jsonify({'status': response.status_code})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

