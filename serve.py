
from src.bot import *
from src.config.config import config
from src.config.config_misc import config_misc

bot = Roboraj(config, config_misc)
bot.run()