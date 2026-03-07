# Anime Filter Bot

A powerful Telegram bot designed to provide verified anime channel links and manage anime requests.

## Features

- **Anime Search**: Search for anime and get verified channel links.
- **A-Z Indexing**: Browse anime by alphabetical order.
- **Request System**: Users can request anime, and admins can browse/manage requests.
- **Force Subscription (FSub)**: Restrict access to subscribers of specific channels.
- **Maintenance Mode**: Admins can temporarily lock the bot for maintenance.
- **Database Backup**: Export all filters to a JSON file.
- **Docker Support**: Easy deployment using Docker and Docker Compose.

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

## Bot Commands

### User Commands
- `/start` - Start the bot and see welcome options.
- `/help` - View help information on how to use the bot.
- `/about` - View details about the bot and developers.
- `/request <anime_name>` - Submit a request for a missing anime.
- `/id` - View your Telegram User ID (and Group ID if used in a group).

### Admin/Owner Commands
- `/stats` - View bot statistics (Users, Filters, etc.).
- `/filters` - List all available filter keywords.
- `/add_admin <user_id>` - Add a new admin (Owner only).
- `/del_admin <user_id>` - Remove an admin (Owner only).
- `/admins` - List all authorized bot admins.
- `/broadcast` - (Reply to msg) Broadcast message to all bot users.
- `/gbroadcast` - (Reply to msg) Broadcast message to all groups where the bot is added.
- `/add_fsub <channel_id>` - Add a channel to Force Subscription.
- `/fsub` - Manage and list Force Subscription channels.
- `/del_fsub <channel_id/all>` - Remove a specific or all FSub channels.
- `/add_slot <keyword>` - Create a custom slot filter with custom buttons.
- `/del_filter <keyword/all>` - Delete a specific filter or clear the entire database.
- `/requests` - View and manage pending user requests via an interactive menu.
- `/maintenance` - Toggle Maintenance Mode (Non-admins will be blocked from searching).
- `/backup` - Generate and download a JSON backup of all filters.
- `/ping` - Check the bot's latency.

## Credits

Created by **@UNRATED_CODER**. Support available at [@UNRATED_CODER](https://t.me/UNRATED_CODER).
