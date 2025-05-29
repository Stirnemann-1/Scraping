from flask import Flask, request, render_template_string
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
import traceback # Für detaillierte Fehlermeldungen

# Flask-Anwendung initialisieren
app = Flask(__name__)

# HTML-Vorlage direkt im Code für Einfachheit
INDEX_HTML = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Scraper (Vercel)</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f0f2f5; color: #1c1e21; line-height: 1.6; }
        .container { max-width: 800px; margin: 0 auto; background-color: #fff; padding: 25px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1), 0 8px 16px rgba(0,0,0,0.1); }
        h1 { color: #1877f2; text-align: center; margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; color: #606770; }
        input[type="url"] { 
            width: calc(100% - 24px); 
            padding: 10px; 
            margin-bottom: 15px; 
            border-radius: 6px; 
            border: 1px solid #dddfe2;
            font-size: 16px;
        }
        input[type="submit"] { 
            background-color: #1877f2; 
            color: white; 
            padding: 10px 20px; 
            border: none;
            border-radius: 6px; 
            cursor: pointer; 
            font-size: 16px;
            font-weight: bold;
            transition: background-color 0.3s ease;
        }
        input[type="submit"]:hover { background-color: #166fe5; }
        .result { margin-top: 25px; border-top: 1px solid #dddfe2; padding-top: 20px; }
        h2 { color: #1c1e21; font-size: 1.2em; }
        pre { 
            background-color: #f5f6f7; 
            padding: 15px; 
            border: 1px solid #ccd0d5; 
            border-radius: 6px; 
            white-space: pre-wrap; 
            word-wrap: break-word; 
            max-height: 600px;
            overflow-y: auto;
            font-family: "Consolas", "Monaco", monospace;
            font-size: 14px;
        }
        .error { 
            color: #fa383e; 
            background-color: #ffebe6; 
            border: 1px solid #fa383e;
            padding: 10px;
            border-radius: 6px;
            font-weight: bold;
        }
        .error pre { background-color: #ffebe6; border-color: #fa383e; color: #c12c30; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Web Scraper</h1>
        <form method="POST" action="/scrape">
            <label for="url">Webseite-URL eingeben:</label>
            <input type="url" id="url" name="url" required placeholder="z.B. https://example.com">
            <br>
            <input type="submit" value="Seite Scrapen">
        </form>

        {% if error_message %}
            <div class="result error">
                <h2>Fehler beim Scraping:</h2>
                <pre>{{ error_message }}</pre>
            </div>
        {% endif %}

        {% if scraped_content %}
            <div class="result">
                <h2>Gescrapter HTML-Code von: {{ scraped_url }}</h2>
                <pre>{{ scraped_content | e }}</pre> <!-- Wichtig: |e für HTML-Escaping -->
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
        return render_template_string(INDEX_HTML, error_message="Bitte geben Sie eine URL ein.")

    # Einfache URL-Validierung und Schema-Ergänzung
    if not url_to_scrape.startswith(('http://', 'https://')):
        url_to_scrape = 'http://' + url_to_scrape
    
    scraped_results_list = [] # Diese Liste wird dem Spider übergeben
    
    # Pfad zum Scrapy-Projekt (relativ zu app.py)
    # In Vercel liegt app.py im Root (/var/task), simple_scraper ist ein Unterordner.
    scrapy_project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simple_scraper')
    original_cwd = os.getcwd()

    try:
        # In das Verzeichnis des Scrapy-Projekts wechseln,
        # damit Scrapy seine Konfiguration (scrapy.cfg) findet.
        os.chdir(scrapy_project_dir)
        
        # Scrapy-Projekteinstellungen laden
        # get_project_settings() sucht nach scrapy.cfg im aktuellen Arbeitsverzeichnis
        settings = get_project_settings() 
        
        # Hier könnten bei Bedarf Einstellungen überschrieben werden:
        # settings.set('LOG_LEVEL', 'DEBUG') # Zum Debuggen

        process = CrawlerProcess(settings)
        
        # Starte den Spider. Der Spider-Name 'html_scraper' muss mit dem `name`-Attribut
        # in der Spider-Klasse (html_spider.py) übereinstimmen.
        process.crawl('html_scraper', 
                      url_to_scrape=url_to_scrape, 
                      results_list=scraped_results_list) # Übergabe der Liste
        
        process.start() # Blockiert, bis alle Crawling-Jobs beendet sind.
                        # Für Vercel sollte dies schnell gehen, um Timeouts zu vermeiden.

        # Nach dem Crawl zurück zum ursprünglichen Arbeitsverzeichnis
        os.chdir(original_cwd)

        if scraped_results_list:
            # Wir erwarten nur ein Ergebnis von diesem einfachen Spider
            result = scraped_results_list[0]
            if 'error' in result:
                 return render_template_string(INDEX_HTML, error_message=f"Fehler von {result.get('url', url_to_scrape)}: {result.get('html_content', 'Unbekannter Fehler')}")
            
            content = result.get('html_content', '')
            scraped_url = result.get('url', url_to_scrape)
            return render_template_string(INDEX_HTML, scraped_content=content, scraped_url=scraped_url)
        else:
            # Dies kann passieren, wenn der Spider die Seite nicht erreichen konnte (z.B. DNS-Fehler, Timeout)
            # oder ein anderer Fehler im Spider auftrat, der kein Ergebnis in die Liste geschrieben hat.
            os.chdir(original_cwd) # Sicherstellen, dass wir im richtigen CWD sind für den Fehler-Render
            return render_template_string(INDEX_HTML, error_message=f"Konnte keinen Inhalt von {url_to_scrape} abrufen oder der Spider hat keine Daten zurückgegeben.")

    except Exception as e:
        # Detaillierte Fehlerbehandlung für Debugging
        os.chdir(original_cwd) # Sicherstellen, dass wir im richtigen CWD sind für den Fehler-Render
        tb_str = traceback.format_exc()
        error_msg = (f"Allgemeiner Fehler im Scraping-Prozess:\n"
                     f"Typ: {type(e).__name__}\n"
                     f"Meldung: {str(e)}\n"
                     f"CWD beim Fehler: {os.getcwd()} (sollte jetzt {original_cwd} sein)\n"
                     f"Scrapy Projekt-Verzeichnis war: {scrapy_project_dir}\n"
                     f"Traceback:\n{tb_str}")
        print(f"APP ERROR: {error_msg}") # Für Vercel Logs
        return render_template_string(INDEX_HTML, error_message=error_msg)

# Dieser Teil ist für lokales Testen. Vercel verwendet das `app` Objekt direkt.
if __name__ == '__main__':
    # Port kann angepasst werden, wenn 5000 belegt ist
    app.run(host='0.0.0.0', port=5001, debug=True)
