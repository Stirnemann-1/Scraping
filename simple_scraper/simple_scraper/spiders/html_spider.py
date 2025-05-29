import scrapy

class HtmlSpider(scrapy.Spider):
    name = "html_scraper"
    # start_urls wird dynamisch von der Flask-App übergeben

    def __init__(self, url_to_scrape=None, results_list=None, *args, **kwargs):
        super(HtmlSpider, self).__init__(*args, **kwargs)
        if url_to_scrape:
            self.start_urls = [url_to_scrape]
        else:
            # Ohne URL sollte der Spider nicht starten oder einen Fehler werfen
            # Aber in diesem Setup fangen wir das vorher ab oder Scrapy meldet einen Fehler.
            self.start_urls = []
        
        # Die Liste wird von der Flask-App übergeben, um das Ergebnis zu sammeln
        self.results_list = results_list

    def parse(self, response):
        # Überprüfe, ob die Anfrage erfolgreich war (Status 2xx)
        if 200 <= response.status < 300:
            scraped_data = {
                'url': response.url,
                'html_content': response.text # response.body.decode(response.encoding) wäre genauer
            }
            
            if self.results_list is not None:
                self.results_list.append(scraped_data)
            else:
                # Sollte nicht passieren, wenn von app.py korrekt aufgerufen
                self.logger.warning("results_list wurde nicht an den Spider übergeben.")
            
            # Für dieses Setup, wo wir direkt in eine Liste schreiben, ist yield nicht zwingend,
            # aber es ist gute Scrapy-Praxis, wenn man Items durch Pipelines schicken würde.
            # yield scraped_data 
        else:
            self.logger.error(f"Fehler beim Abrufen von {response.url}: Status {response.status}")
            if self.results_list is not None:
                # Optional: Fehler auch in der Ergebnisliste vermerken
                self.results_list.append({
                    'url': response.url,
                    'error': f"Status {response.status}",
                    'html_content': f"Konnte die Seite nicht laden. Status: {response.status}"
                })
