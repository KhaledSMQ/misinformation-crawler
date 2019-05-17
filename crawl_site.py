import argparse
import logging
import pkg_resources
import yaml
from scrapy.crawler import CrawlerProcess
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings
from misinformation.spiders import IndexPageSpider, ScattergunSpider, XMLSitemapSpider

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description=__name__)
    parser.add_argument('--site_name', '-s', required=True,
                        help='Name of site configuration.')
    parser.add_argument('--max_articles', '-n', type=int, default=0,
                        help='Maximum number of articles to process from each site.')
    parser.add_argument('--exporter', '-e', default='database', choices=['file', 'blob', 'database'],
                        help='Article export method.')
    args = parser.parse_args()

    # Set up logging
    configure_logging()
    logging.getLogger("azure.storage.common.storageclient").setLevel(logging.ERROR)
    logging.getLogger("sqlalchemy").setLevel(logging.ERROR)

    # Load crawl configuration for site from configuration
    site_configs = yaml.load(pkg_resources.resource_string(__name__, "site_configs.yml"))

    # Retrieve configuration for specified site
    site_config = site_configs[args.site_name]
    article_lists = yaml.load(pkg_resources.resource_string(__name__, "article_lists.yml"))
    if args.site_name in article_lists:
        site_config["article_list"] = article_lists[args.site_name]

    # Update crawler settings here as we can't seem to do this when using the
    # custom_settings attribute in the spider initialiser
    settings = get_project_settings()
    # Add custom settings
    settings.update({
        'ARTICLE_EXPORTER': args.exporter,
        'CONTENT_DIGESTS': True,
        'NODE_INDEXES': True,
        'ROBOTSTXT_OBEY': site_configs.get(args.site_name, {}).get("obey_robots_txt", True)
    })
    # Apply an item limit if specified
    if args.max_articles:
        settings.update({
            'CLOSESPIDER_ITEMCOUNT': args.max_articles
        })

    # Set up a crawler process
    process = CrawlerProcess(settings)

    # Get appropriate spider class for this site
    spider_classes = {
        'index_page': IndexPageSpider,
        'scattergun': ScattergunSpider,
        'sitemap': XMLSitemapSpider
    }
    try:
        crawl_strategy = site_configs[args.site_name]['crawl_strategy']['method']
    except KeyError:
        crawl_strategy = 'scattergun'

    # Run crawl for specified site
    process.crawl(spider_classes[crawl_strategy], config=site_configs[args.site_name])
    process.start()


if __name__ == "__main__":
    main()
