"""
This module contains functions for extracting data from webpages
"""
from .extract_article import extract_article, xpath_extract_spec, simplify_extracted_byline, simplify_extracted_title
from .extract_datetime import extract_datetime_string
from .extract_element import extract_element

__all__ = [
    "extract_article",
    "extract_datetime_string",
    "extract_element",
    "xpath_extract_spec",
    "simplify_extracted_byline",
    "simplify_extracted_title",
]
