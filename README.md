# expenseBot

**expenseBot** is a Telegram bot designed to streamline the process of logging business expenses.  
It enables users to quickly record expenses and submit them to IQ Navigator, reducing administrative overhead and ensuring timely expense reporting.

## Features

- User-friendly Telegram interface for logging expenses.
- Integration with IQ Navigator for seamless expense submission.
- Structured codebase with modules for classes, functions, logging, and testing.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/toosolid2003/expenseBot.git
   cd expenseBot
   ```
2. **Install dependencies**
   Ensure you have Python 3.x installed. Then, install the required packages:
   ```
   pip install -r requirements.txt
   ```
4. Configure the bot
   Set up your Telegram bot token and any necessary configurations in botParams.py.

## Usage
To start the bot, run:
```
python botTelegram.py
```
Interact with your Telegram bot to log expenses, which will then be processed and submitted to IQ Navigator.

## Project structure
•	botClasses/ – Contains class definitions used by the bot.  
•	botFunctions/ – Utility functions supporting bot operations.  
•	logger/ – Logging configurations and handlers.  
•	support_files/ – Additional resources and templates.  
•	test/ – Unit tests for various components.  
•	botParams.py – Configuration parameters for the bot.  
•	botTelegram.py – Main script to run the Telegram bot.  
•	sendgrid_sample.py – Example integration with SendGrid for email notifications.  

 ## Contributing
 Contributions are welcome! Please fork the repository and submit a pull request with your enhancements.

 ## License
 This project is licensed under the MIT License.
