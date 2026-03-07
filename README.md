# Anime Filter Bot

A powerful Telegram bot designed to provide verified anime channel links and manage anime requests.

## Features

- **Anime Search**: Search for anime and get verified channel links.
- **A-Z Indexing**: Browse anime by alphabetical order.
- **Request System**: Users can request anime, and admins can reply directly.
- **Force Subscription (FSub)**: Restrict access to subscribers of specific channels.
- **Admin Tools**: Add/Delete admins, manage filters, broadcast messages, and more.
- **Custom Slots**: Create custom messages with buttons and save them as filters.
- **Anilist Integration**: Fetch anime details and posters automatically.

## Deployment

### Environment Variables

The bot requires the following environment variables:

- `API_TOKEN`: Your Telegram Bot Token from [@BotFather](https://t.me/BotFather).
- `OWNER_ID`: Your Telegram User ID.
- `MONGO_URI`: Your MongoDB connection string.
- `DB_CHANNEL_ID`: ID of the channel used to store database messages.
- `LOG_CHANNEL_ID`: ID of the channel for system logs.

### Manual Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd <repo-name>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file and add your configuration.

4. Run the bot:
   ```bash
   python main.py
   ```

## Admin Commands

- `/start` - Start the bot.
- `/help` - Show help message.
- `/about` - Show bot information.
- `/stats` - View bot statistics.
- `/filters` - List all available filters.
- `/add_admin <user_id>` - Add a new admin (Owner only).
- `/del_admin <user_id>` - Remove an admin (Owner only).
- `/broadcast` - Reply to a message to broadcast to all users.
- `/gbroadcast` - Reply to a message to broadcast to all groups.
- `/add_fsub <channel_id>` - Add a channel to Force Subscription.
- `/fsub` - Manage FSub channels.
- `/add_slot <keyword>` - Create a custom slot filter.
- `/del_filter <keyword>` - Delete a specific filter or use `/del_filter all`.

## Credits

Created by **@UNRATED_CODER**. Support available at [@UNRATED_CODER](https://t.me/UNRATED_CODER).
