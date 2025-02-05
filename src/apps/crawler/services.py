import dataclasses
from dataclasses import field
from logging import getLogger

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from .exceptions import UrlIsInvalid

logger = getLogger(__name__)


@dataclasses.dataclass
class CrawledLink:
    title: str
    domain: str
    link: str


@dataclasses.dataclass
class CrawlerService:
    url_validator: URLValidator = field(default_factory=URLValidator)

    def _validate_url(self, url: str) -> bool:
        if not url:
            raise UrlIsInvalid("Url Must Be Not Empty")

        try:
            self.url_validator(url)
        except ValidationError as ex:
            logger.error("Url Is Invalid", exc_info=ex)
            raise UrlIsInvalid("Url Is Invalid") from ex

    def get_external_links(self, url: str) -> list[CrawledLink]:

        self._validate_url(url)

        return [
            CrawledLink("test", "test", "link")
        ]


crawler_service = CrawlerService()
