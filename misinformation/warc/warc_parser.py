import datetime
import logging
from termcolor import colored
from misinformation.extractors import extract_article
from misinformation.database import Connector, RecoverableDatabaseError, NonRecoverableDatabaseError, Article, Webpage
from .serialisation import response_from_warc


class WarcParser(Connector):
    def __init__(self, content_digests=False, node_indexes=False):
        super().__init__()
        self.content_digests = content_digests
        self.node_indexes = node_indexes


    def process_webpages(self, site_name, config):
        start_time = datetime.datetime.utcnow()
        entries = self.read_entries(Webpage, site_name=site_name)
        n_pages, n_articles = len(entries), 0
        logging.info("Loaded %s pages for %s", colored(n_pages, "blue"), colored(site_name, "green"))

        for idx, entry in enumerate(entries, start=1):
            logging.info("Searching for an article at: %s", colored(entry.article_url, "green"))

            # Load WARC data from blob storage
            blob_key = entry.blob_key
            blob = self.block_blob_service.get_blob_to_bytes(self.blob_container_name, blob_key)

            # Create a response from the WARC content and attempt to extract an article
            response = response_from_warc(blob.content)
            article = extract_article(response, config, entry, self.content_digests, self.node_indexes)

            # Add article to database
            if article["content"]:
                self.add_to_database(article)
                n_articles += 1
            logging.info("Finished processing %s/%s: %s", idx, n_pages, entry.article_url)

        # Print statistics
        duration = datetime.datetime.utcnow() - start_time
        processing_rate = "{:.2f} Hz".format(float(n_pages / duration.seconds) if duration.seconds > 0 else 0)
        logging.info("Processed %s pages in %s => %s",
                     colored(n_pages, "blue"),
                     colored(duration, "blue"),
                     colored(processing_rate, "green"),
                     )
        hit_percentage = "{:.2f}%".format(float(100 * n_articles / n_pages) if n_pages > 0 else 0)
        logging.info("Found articles in %s/%s pages => %s",
                     colored(n_articles, "blue"),
                     colored(n_pages, "blue"),
                     colored(hit_percentage, "green"),
                     )


    def add_to_database(self, article):
        '''Add an article to the database'''
        logging.info("  starting database export for: %s", article["article_url"])

        # Construct Article table entry
        article_data = Article(**article)

        # Add webpage entry to database
        try:
            self.add_entry(article_data)
        except RecoverableDatabaseError as err:
            logging.info(str(err))
        except NonRecoverableDatabaseError as err:
            logging.critical(str(err))
            raise

        logging.info("  finished database export for: %s", article["article_url"])
