import os
import discord
from discord.ext import commands
import requests

# Discord Bot設定
intents = discord.Intents.default()
intents.message_content = True   # メッセージ内容を拾えるようにする
bot = commands.Bot(command_prefix="/", intents=intents)

# 環境変数から取得
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CONOHA_USERNAME = os.getenv("CONOHA_USERNAME")
CONOHA_PASSWORD = os.getenv("CONOHA_PASSWORD")
TENANT_ID = os.getenv("TENANT_ID")
SERVER_ID = os.getenv("SERVER_ID")

# APIエンドポイント
IDENTITY_URL = "https://identity.c3j1.conoha.io/v3/auth/tokens"
COMPUTE_URL = f"https://compute.c3j1.conoha.io/v2/{TENANT_ID}/servers/{SERVER_ID}/action"

def get_token():
    payload = {
        "auth": {
            "identity": {
                "methods": ["password"],
                "password": {
                    "user": {
                        "name": CONOHA_USERNAME,
                        "domain": {"name": "default"},
                        "password": CONOHA_PASSWORD
                    }
                }
            },
            "scope": {"project": {"id": TENANT_ID}}
        }
    }
    r = requests.post(IDENTITY_URL, json=payload)
    print("Auth response:", r.status_code, r.text)  # デバッグ用ログ
    if r.status_code == 201:
        return r.headers["X-Subject-Token"]
    else:
        raise Exception(f"認証失敗: {r.text}")

def server_action(action):
    token = get_token()
    headers = {"X-Auth-Token": token, "Content-Type": "application/json"}
    payload = {action: None}

    # デバッグログ出力
    print("Request URL:", COMPUTE_URL)
    print("Headers:", headers)
    print("Payload:", payload)

    r = requests.post(COMPUTE_URL, headers=headers, json=payload)

    # レスポンスをログに出す
    print("Response:", r.status_code, r.text)

    return r.status_code, r.text

@bot.command()
async def start(ctx):
    code, msg = server_action("os-start")
    await ctx.send(f"サーバー起動リクエスト送信: {code}")

@bot.command()
async def stop(ctx):
    code, msg = server_action("os-stop")
    await ctx.send(f"サーバー停止リクエスト送信: {code}")

bot.run(DISCORD_TOKEN)
