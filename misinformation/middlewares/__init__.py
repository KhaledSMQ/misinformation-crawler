"""
This module contains any project-specific Scrapy middleware

See documentation at:
https://doc.scrapy.org/en/latest/topics/spider-middleware.html
"""
from .cloudflaremiddleware import CloudFlareMiddleware
from .delayedretrymiddleware import DelayedRetryMiddleware
from .jsloadbuttonmiddleware import JSLoadButtonMiddleware

__all__ = [
    "CloudFlareMiddleware",
    "DelayedRetryMiddleware",
    "JSLoadButtonMiddleware",
]
