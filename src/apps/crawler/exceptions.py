class ServiceException(Exception): ...


class UrlIsInvalid(ServiceException): ...


class UrlProcessingException(ServiceException): ...
