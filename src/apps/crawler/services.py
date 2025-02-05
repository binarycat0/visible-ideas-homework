import dataclasses
from dataclasses import field
from logging import getLogger
from typing import Dict
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from requests import Response

from .exceptions import UrlIsInvalid, UrlProcessingException, ServiceException

logger = getLogger(__name__)


@dataclasses.dataclass
class CrawledLink:
    domain: str
    title: str
    link: str


@dataclasses.dataclass
class CrawlerService:
    url_validator: URLValidator = field(default_factory=URLValidator)
    request_timeout: int = 10
    request_headers: Dict[str, str] = field(default_factory=lambda: {"User-Agent": "Mozilla/5.0"})

    def _is_url_valid(self, url: str) -> bool:
        try:
            self.url_validator(url)
            return True
        except ValidationError:
            logger.info("Url Is Invalid")

        return False

    def _validate_url(self, url: str):
        if not url:
            raise UrlIsInvalid("Url Must Be Not Empty")
        try:
            self.url_validator(url)
        except ValidationError as ex:
            raise UrlIsInvalid("Url Is Invalid") from ex

    def _get_url_data(self, url: str) -> Response:
        self._validate_url(url)

        try:
            response = requests.get(url, timeout=self.request_timeout, headers=self.request_headers)
            response.raise_for_status()
            return response
        except requests.Timeout as ex:
            raise UrlProcessingException(f"Timeout error while trying get response from {url}") from ex
        except requests.HTTPError as ex:
            raise UrlProcessingException(
                f"Unsuccessfully get response from {url}. Status: {ex.response.status_code}"
            ) from ex

    def _get_link_title(self, link: str):
        response = self._get_url_data(link)
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.find("title")
        return title_tag.text.strip() if title_tag else "<empty title>"

    def get_external_links(self, url: str) -> list[CrawledLink]:

        response = self._get_url_data(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        external_links = set()
        result = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            if not self._is_url_valid(href) or href in external_links:
                continue

            title = ""
            try:
                title = self._get_link_title(href)
            except ServiceException as ex:
                logger.warning("Error while getting url title", exc_info=ex)

            external_links.add(href)
            result.append(
                CrawledLink(urlparse(href).netloc, title, href)
            )

        return result


crawler_service = CrawlerService()
