# app.py (im Root-Verzeichnis des Projekts)
from flask import Flask, request, render_template_string
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
import sys

# Pfad zum Scrapy-Projekt hinzufügen, damit Scrapy es finden kann
# Dies ist wichtig, da app.py im Root liegt und simple_scraper ein Unterordner ist.
# Vercel's Build-Prozess sollte die Verzeichnisstruktur beibehalten.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRAPY_PROJECT_PATH = os.path.join(BASE_DIR, 'simple_scraper')
# sys.path.append(SCRAPY_PROJECT_PATH) # Alternative, wenn os.chdir Probleme macht
# Besser: Scrapy sagen, wo es seine Settings findet, oder den CWD ändern

app = Flask(__name__)

# HTML-Vorlage (unverändert)
INDEX_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Scraper auf Vercel</title>
    <style>
        body { font-family: sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }
        .container { background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        label { display: block; margin-bottom: 8px; }
        input[type="url"], input[type="submit"] { 
            padding: 10px; 
            margin-bottom: 10px; 
            border-radius: 4px; 
            border: 1px solid #ddd;
        }
        input[type="url"] { width: calc(100% - 22px); }
        input[type="submit"] { background-color: #5cb85c; color: white; cursor: pointer; }
        input[type="submit"]:hover { background-color: #4cae4c; }
        .result { margin-top: 20px; }
        h2 { color: #555; }
        pre { 
            background-color: #eee; 
            padding: 15px; 
            border: 1px solid #ccc; 
            border-radius: 4px; 
            white-space: pre-wrap; 
            word-wrap: break-word; 
            max-height: 500px;
            overflow-y: auto;
        }
        .error { color: red; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Web Scraper auf Vercel</h1>
        <form method="POST" action="/scrape">
            <label for="url">Webseite-URL eingeben:</label>
            <input type="url" id="url" name="url" required placeholder="https://beispiel.com">
            <br>
            <input type="submit" value="Scrapen">
        </form>

        {% if error %}
            <div class="result error">
                <h2>Fehler:</h2>
                <p>{{ error }}</p>
            </div>
        {% endif %}

        {% if scraped_content %}
            <div class="result">
                <h2>Gescrapter Inhalt von: {{ scraped_url }}</h2>
                <pre>{{ scraped_content | e }}</pre> <!-- Wichtig: escapen für Sicherheit -->
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(INDEX_HTML)

@app.route('/scrape', methods=['POST'])
def scrape():
    url_to_scrape = request.form.get('url')
    if not url_to_scrape:
        return render_template_string(INDEX_HTML, error="Bitte geben Sie eine URL ein.")

    if not url_to_scrape.startswith(('http://', 'https://')):
        url_to_scrape = 'http://' + url_to_scrape
    
    scraped_results = []
    
    # Wichtig: Scrapy muss wissen, wo sein Projektkontext ist.
    # Wir ändern das Current Working Directory temporär in den Scrapy-Projektordner.
    # Dies hilft Scrapy, seine Einstellungen und Spider korrekt zu laden.
    # Vercel kann manchmal mit relativen Pfaden eigen sein.
    original_cwd = os.getcwd()
    # Der Pfad zum Scrapy-Projekt muss relativ zum app.py sein
    # In Vercel ist app.py im Root, simple_scraper ist ein Unterordner.
    scrapy_project_dir = os.path.join(os.path.dirname(__file__), 'simple_scraper')
    
    try:
        os.chdir(scrapy_project_dir) # In das Scrapy-Projektverzeichnis wechseln
        
        settings = get_project_settings()
        # Man kann hier Einstellungen überschreiben, falls nötig.
        # z.B. settings.set('LOG_LEVEL', 'DEBUG') für mehr Details beim Debuggen auf Vercel
        # Aber besser in der settings.py lassen.

        process = CrawlerProcess(settings)
        process.crawl('html_scraper', url_to_scrape=url_to_scrape, results_list=scraped_results)
        process.start() # Blockiert, bis der Crawl fertig ist

    except Exception as e:
        # Hier könnten auch Fehler von Scrapy selbst landen, wenn es z.B. die Settings nicht findet.
        # Fangen wir spezifischer: scrapy.exceptions.NotConfigured etc.
        return render_template_string(INDEX_HTML, error=f"Scraping fehlgeschlagen: {str(e)}. CWD: {os.getcwd()}, Scrapy Proj Dir: {scrapy_project_dir}")
    finally:
        os.chdir(original_cwd) # Zurück zum ursprünglichen CWD

    if scraped_results:
        content = scraped_results[0]['html_content']
        scraped_url = scraped_results[0]['url']
        return render_template_string(INDEX_HTML, scraped_content=content, scraped_url=scraped_url)
    else:
        return render_template_string(INDEX_HTML, error=f"Konnte keinen Inhalt von {url_to_scrape} abrufen. Die Seite gab möglicherweise keine Daten zurück oder der Spider wurde nicht korrekt ausgeführt.")

# Der folgende Block ist für lokales Testen und wird von Vercel nicht direkt verwendet.
# Vercel verwendet das `app`-Objekt als WSGI-Einstiegspunkt.
if __name__ == '__main__':
    # Für lokales Testen sicherstellen, dass wir im richtigen Kontext sind
    # oder dass Scrapy sein Projekt findet.
    # Der `os.chdir` in der scrape-Funktion ist hier primär relevant.
    app.run(host='0.0.0.0', port=5001, debug=True) # Anderer Port für lokales Testen
