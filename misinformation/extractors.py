import itertools
from misinformation.items import Article
import re
from readability import readability
import warnings


# Helper function for selecting elements by class name. This is a little complex in xpath as
# (i) div[@class="<classname>"] only matches a single exact class name (no whitespace padding or multiple classes)
# (ii) div[contains(@class, "<classname>")] will also select class names containing <classname> as a substring
def xpath_class(element, class_name):
    return "{element}[contains(concat(' ', normalize-space(@class), ' '), ' {class_name} ')]".format(
        class_name=class_name, element=element)


def xpath_extract_spec(xpath_expression, match_rule="single"):
    extract_spec = {
        "select-method": "xpath",
        "select-expression": xpath_expression,
        'match-rule': match_rule
    }
    return extract_spec


def extract_element(response, extract_spec):
    # Extract selector specification
    method = extract_spec['select-method']
    expression = extract_spec['select-expression']
    # Default match rule to 'one', which wil throw an error if multiple matches are found
    if 'match-rule' not in extract_spec:
        match_rule = 'one'
    else:
        match_rule = extract_spec['match-rule']

    # Apply selector to response to extract chosen metadata field
    if method == 'xpath':
        # Extract all instances matching xpath expression
        elements = response.xpath(expression).extract()
        # Strip leading and trailing whitespace
        elements = [item.strip() for item in elements]
        if not elements:
            warnings.warn("Failed to extract element from {url} using xpath selector '{xpath}'".format(
                xpath=expression, url=response.url))
        elif match_rule == 'single':
            num_matches = len(elements)
            if num_matches == 1:
                elements = elements[0]
            else:
                raise ValueError("Extracted {count} elements from {url} matching {xpath}. \
                    Only one element permitted by match-rule '{rule}'.".format(
                    count=num_matches, url=response.url, xpath=expression, rule=match_rule))
        elif match_rule == 'first':
            elements = elements[0]
        elif match_rule == 'all':
            # Nothing to do but need this to pass validity check
            elements = elements
        else:
            raise ValueError("'{match_rule}' is not a valid match-rule".format(match_rule=match_rule))
    else:
        raise ValueError("'{method}' is not a valid select-expression".format(method=method))
    return elements


def extract_article(response, config, crawl_info=None):
    # Create new article and set URL from the response (not the request). The idea here is that this should be the same
    # for the same article, regardless of how it was requested (e.g. aliases, redirects etc).
    article = Article()
    article['article_url'] = response.url

    # Ensure core fields are exported as nulls even if they are not extracted from article
    article["title"] = None  # String field (can be NULL)
    article["byline"] = None  # String field (can be NULL)
    article["publication_date"] = None  # Datetime field (can be NULL)
    article['metadata'] = None  # JSON dictionary (can be NULL)
    article["structured_content"] = None  # String field (can be NULL)
    article["plain_content"] = None  # JSON array of strings (can be NULL)


    # Get default article by running readability extract on full page
    page_html = extract_element(response, xpath_extract_spec("/html", "single"))
    default_readability_article = readability.extract_readable_article(page_html)
    article["title"] = default_readability_article["title"]
    article["byline"] = default_readability_article["byline"]
    article["structured_content"] = default_readability_article["structured_content"]
    article["plain_content"] = default_readability_article["plain_content"]

    # Overwrite default values where extract specifications have been provided
    if 'article' in config:
        if 'title' in config['article']:
            # Extract title from specified element
            custom_title = extract_element(response, config['article']['title'])
            if custom_title:
                article['title'] = custom_title
        if 'byline' in config['article']:
            article['byline'] = extract_element(response, config['article']['byline'])
        if 'content' in config['article']:
            # Extract readable article content from specified element
            article_html = extract_element(response, config['article']['content'])
            custom_readability_article = readability.extract_readable_article(article_html)
            article["structured_content"] = custom_readability_article["structured_content"]
            article["plain_content"] = custom_readability_article["plain_content"]


    # Extract additional article metadata
    if 'metadata' in config:
        # Attempt to extract all metadata fields
        for fieldname in config['metadata']:
            article['metadata'][fieldname] = extract_element(response, config['metadata'][fieldname])

    # Add crawl information if provided
    if crawl_info:
        article["crawl_id"] = crawl_info["crawl_id"]
        article["crawl_datetime"] = crawl_info["crawl_datetime"]
        article['site_name'] = crawl_info['site_name']

    return article