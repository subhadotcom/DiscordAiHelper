# Discord AI Helper

A powerful Discord bot that integrates AI capabilities to enhance server interactions and provide intelligent responses. This bot combines Discord.py with OpenAI and Google's Generative AI to offer a rich set of features for Discord communities.

## Features

- 🤖 **AI-Powered Conversations**: Engage in intelligent conversations with AI integration
- 🔧 **Command System**: Easy-to-use command interface with comprehensive error handling
- 🌐 **Web Interface**: Flask-based web dashboard for bot management
- 📊 **Server Management**: Automatic welcome messages and server tracking
- 🔄 **Multi-Process Architecture**: Separate processes for bot and web interface
- 📝 **Logging System**: Comprehensive logging for debugging and monitoring

## Technical Stack

- **Backend**: Python 3.11+
- **Discord Integration**: discord.py
- **Web Framework**: Flask
- **AI Integration**: 
  - OpenAI API
  - Google Generative AI
- **Database**: SQLAlchemy with PostgreSQL
- **Web Server**: Gunicorn
- **Logging**: Custom logging system

## Project Structure

```
DiscordAiHelper/
├── cogs/              # Discord command modules
├── static/            # Static web assets
├── templates/         # Web interface templates
├── utils/             # Utility modules
├── app.py            # Flask web application
├── bot.py            # Discord bot implementation
├── main.py           # Application entry point
├── models.py         # Database models
└── pyproject.toml    # Project dependencies
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DiscordAiHelper.git
cd DiscordAiHelper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
- `DISCORD_TOKEN`: Your Discord bot token
- `OPENAI_API_KEY`: Your OpenAI API key
- `GOOGLE_API_KEY`: Your Google AI API key
- `DATABASE_URL`: Your PostgreSQL database URL

## Configuration

The bot uses a configuration system that can be customized through environment variables or a config file. Key settings include:

- Command prefix
- Bot activity status
- Logging levels
- API keys and tokens

## Usage

1. Start the bot:
```bash
python main.py
```

2. The bot will automatically:
   - Connect to Discord
   - Load all command modules
   - Start the web interface
   - Set up logging

3. Basic Commands:
   - `!help`: Show available commands
   - `!ping`: Check bot latency
   - `!ai <message>`: Get AI response

## Development

- The project uses a modular design with separate cogs for different command categories
- Web interface runs on port 5000 by default
- Logs are stored in the `logs` directory
- Error handling is implemented for both bot and web components

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the Apache License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Acknowledgments

- Discord.py team for the excellent Discord API wrapper
- OpenAI for their powerful language models
- Google for their generative AI capabilities 