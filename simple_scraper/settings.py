# simple_scraper/simple_scraper/settings.py
BOT_NAME = "simple_scraper"

SPIDER_MODULES = ["simple_scraper.spiders"]
NEWSPIDER_MODULE = "simple_scraper.spiders"

ROBOTSTXT_OBEY = False # Für Testzwecke

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'

# WICHTIG für Vercel, um unnötiges Logging und ggf. Fehler zu vermeiden:
LOG_LEVEL = 'INFO' # oder 'WARNING' / 'ERROR'
# TELNETCONSOLE_ENABLED = False # Telnet-Konsole wird auf Vercel nicht benötigt/funktionieren
