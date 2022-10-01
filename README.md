# autoquakegen

An automatic [QuaKe profile picture generator](https://thefakequake.github.io/) that changes a Discord user or bot
profile picture once a day, and saves it to a folder.

## Usage

Requires Python 3.10 or higher.

Install dependencies with:
```
pip install -r requirements.txt
```

Create a config.json file with the below structure:
```json
{
  "token": "Bot or user token",
  "properties": {
    "os": "Windows",
    "browser": "Chrome",
    "browser_user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
  },
  "user": false,
  "intents": 0
}
```

Set `user` to `true` if you want to use a user account, please note that this is against [Discord's TOS](https://discord.com/terms) so use at your own risk.

Then run the main.py file:
```
py main.py
```
or
```
python3 main.py
```