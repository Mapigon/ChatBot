import configparser
config = configparser.ConfigParser()
config.read('/Users/mapigon/ChatBot/config.ini')
print(config['TELEGRAM']['ACCESS_TOKEN'])
