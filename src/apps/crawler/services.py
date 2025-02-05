import dataclasses
from concurrent.futures import as_completed
from concurrent.futures.thread import ThreadPoolExecutor
from dataclasses import field
from functools import lru_cache
from logging import getLogger
from typing import Dict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from requests import Response
from requests.adapters import HTTPAdapter, Retry

from .exceptions import ServiceException, UrlIsInvalid, UrlProcessingException

logger = getLogger(__name__)


@dataclasses.dataclass
class CrawledLink:
    domain: str
    title: str
    link: str


@dataclasses.dataclass
class CrawlerService:
    request_timeout: int = 2
    request_headers: Dict[str, str] = field(
        default_factory=lambda: {"User-Agent": "Mozilla/5.0"}
    )

    def __post_init__(self):
        self._url_validator = URLValidator()

        default_adapter = HTTPAdapter(pool_connections=100, max_retries=1)
        self._session = requests.Session()
        self._session.mount(prefix="https://", adapter=default_adapter)
        self._session.mount(prefix="http://", adapter=default_adapter)

    @property
    def url_validator(self):
        return self._url_validator

    @property
    def session(self):
        return self._session

    def _is_url_valid(self, url: str) -> bool:
        try:
            self.url_validator(url)
            return True
        except ValidationError:
            logger.info(f"Url Is Invalid: {url}")

        return False

    def _validate_url(self, url: str):
        if not url:
            raise UrlIsInvalid("Url Must Be Not Empty")
        try:
            self.url_validator(url)
        except ValidationError as ex:
            raise UrlIsInvalid(f"Url Is Invalid: {url}") from ex

    def _get_url_data(self, url: str) -> Response:
        self._validate_url(url)

        try:
            response = self.session.get(
                url, timeout=self.request_timeout, headers=self.request_headers
            )
            response.raise_for_status()
            return response
        except requests.Timeout as ex:
            raise UrlProcessingException(
                f"Timeout error while trying get response from {url}"
            ) from ex
        except requests.HTTPError as ex:
            raise UrlProcessingException(
                f"Unsuccessfully get response from {url}. Status: {ex.response.status_code}"
            ) from ex
        except requests.RequestException as ex:
            raise UrlProcessingException(
                f"Something went wrong while trying get response from: {ex}"
            ) from ex

    def _get_link_title(self, link: str) -> tuple[str, str]:
        response = self._get_url_data(link)
        soup = BeautifulSoup(response.text, "html.parser")
        title_tag = soup.find("title")
        title = title_tag.text.strip() if title_tag else "<empty title>"
        return link, title

    def _get_external_links(self, url: str) -> list[CrawledLink]:

        response = self._get_url_data(url)
        soup = BeautifulSoup(response.text, "html.parser")

        futures = []
        external_links = {}
        with ThreadPoolExecutor() as executor:
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if not self._is_url_valid(href) or href in external_links:
                    continue
                external_links[href] = (href, None)
                futures.append(executor.submit(self._get_link_title, href))

        for future in as_completed(futures):
            try:
                link, title = future.result()
                external_links[link] = (link, title)
            except ServiceException as ex:
                logger.warning("Error while getting url data", exc_info=ex)

        return [
            CrawledLink(urlparse(link).netloc, title, link)
            for link, title in external_links.values()
        ]

    def get_external_links(self, url: str) -> list[CrawledLink]:
        logger.info(f"get_external_links url:{url}")
        return self._get_external_links(url)


crawler_service = CrawlerService()
