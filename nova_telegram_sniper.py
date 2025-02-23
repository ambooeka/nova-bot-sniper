from telethon import TelegramClient, events
import re
import csv
from datetime import datetime
from telethon.tl.functions.messages import SendMessageRequest

# Step 1: Add your Telegram API details
api_id = '21219321'      # Replace with your API ID
api_hash = '94229e97f887637338435d48391cd6ce'  # Replace with your API Hash
client = TelegramClient('nova_bot_session', api_id, api_hash)

# Step 2: Telegram channels to monitor
channels_to_monitor = ['cryptoclubpump', 'channel_username_2']

# Step 3: Trusted friends' Telegram usernames (without @)
trusted_users = ['allgudshi', 'friend_username2']

# Step 4: Your Telegram user ID for notifications
owner_user_id = 1792496847  # Replace with your Telegram user ID

# Step 5: Regex to detect Solana token addresses (Base58, 32-44 chars)
TOKEN_REGEX = r'(?<!\\w)[1-9A-HJ-NP-Za-km-z]{32,44}(?!\\w)'

# Step 6: Create CSV log file if it doesn't exist
with open('trade_log.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'Token Address', 'Status', 'Buy Price (SOL)', 'Sell Price (SOL)', 'Profit (SOL)', 'Fees (SOL)', 'PnL (%)'])

# Step 7: Log each trade with PnL details
def log_trade(token, status, buy_price=None, sell_price=None, profit=None, fees=None, pnl_percent=None):
    with open('trade_log.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now(), token, status, buy_price, sell_price, profit, fees, pnl_percent
        ])
    print(f"📝 Trade logged for {token} | Status: {status}")

# Step 8: Send notification to your Telegram account
async def notify_owner(message):
    await client(SendMessageRequest(peer=owner_user_id, message=message))
    print(f"📨 Notification sent: {message}")

# Step 9: Simulate purchase confirmation
async def purchase_confirmation(token):
    buy_price = 1.0  # Simulated buy price in SOL
    fees = 0.01      # Simulated fees in SOL
    log_trade(token, 'Purchase Completed', buy_price=buy_price, fees=fees)
    await notify_owner(f"✅ Purchase Successful:\nToken: {token}\nBuy Price: {buy_price} SOL\nFees: {fees} SOL")

# Step 10: Simulate sale confirmation and PnL calculation
async def sale_confirmation(token, buy_price):
    sell_price = buy_price * 4.0  # Simulate 4x sell
    fees = 0.01
    profit = sell_price - buy_price - fees
    pnl_percent = (profit / buy_price) * 100
    log_trade(token, 'Sale Completed', buy_price=buy_price, sell_price=sell_price, profit=profit, fees=fees, pnl_percent=pnl_percent)
    await notify_owner(
        f"💸 Sale Completed:\nToken: {token}\nSell Price: {sell_price} SOL\nProfit: {profit:.4f} SOL ({pnl_percent:.2f}% gain)\nFees: {fees} SOL"
    )

# Step 11: Send token address to Nova bot and simulate full trade cycle
async def send_to_nova(token):
    await client.send_message('YourNovaBotUsername', token)
    print(f"📩 Sent {token} to Nova bot for auto-buy.")
    log_trade(token, 'Sent to Nova Bot')
    await notify_owner(f"✅ Token sent to Nova Bot: {token}")
    await purchase_confirmation(token)
    await sale_confirmation(token, buy_price=1.0)

# Step 12: Monitor Telegram channels and trusted users for token addresses
@client.on(events.NewMessage())
async def handler(event):
    sender = await event.get_sender()
    username = sender.username
    message = event.raw_text
    token_addresses = re.findall(TOKEN_REGEX, message)

    if username in trusted_users and token_addresses:
        for token in token_addresses:
            print(f"🤝 Trusted user @{username} sent token: {token}")
            await send_to_nova(token)
    elif token_addresses and event.chat.username in channels_to_monitor:
        for token in token_addresses:
            print(f"✅ Token from monitored channel @{event.chat.username}: {token}")
            await send_to_nova(token)
    else:
        print(f"🔎 Ignored message from @{username} or no valid token found.")

# Step 13: Start the client
client.start()
print("🚀 Bot is running. Monitoring Telegram channels and trusted users...")
client.run_until_disconnected()
