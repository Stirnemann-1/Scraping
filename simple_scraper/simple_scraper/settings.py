BOT_NAME = "simple_scraper"

SPIDER_MODULES = ["simple_scraper.spiders"]
NEWSPIDER_MODULE = "simple_scraper.spiders"

# Obey robots.txt rules (für Testzwecke oft auf False, in Produktion überdenken)
ROBOTSTXT_OBEY = False

# Setze einen User-Agent, um nicht als Standard-Scrapy-Bot erkannt zu werden
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'

# Log-Level für Vercel reduzieren, um Logs übersichtlich zu halten
LOG_LEVEL = 'INFO' # Andere Optionen: 'DEBUG', 'WARNING', 'ERROR', 'CRITICAL'

# Deaktiviere die Telnet-Konsole, da sie auf Vercel nicht benötigt wird/funktioniert
TELNETCONSOLE_ENABLED = False

# Empfohlene Einstellungen für bessere Crawling-Praktiken (optional für dieses Beispiel)
# DOWNLOAD_DELAY = 1 # Fügt eine Verzögerung zwischen Anfragen hinzu
# CONCURRENT_REQUESTS_PER_DOMAIN = 8 # Begrenzt gleichzeitige Anfragen pro Domain

# Um sicherzustellen, dass der Twisted Reactor nicht mit dem von Flask kollidiert,
# wenn Scrapy innerhalb eines Flask-Requests läuft (obwohl CrawlerProcess dies meist handhabt)
# TWISTED_REACTOR = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor' # Nur wenn Probleme auftreten
# asyncio muss dann auch in requirements.txt sein. Für dieses einfache Beispiel meist nicht nötig.
