from abc import ABC, abstractmethod
from html.parser import HTMLParser
from typing import override


class _HTMLStripper(HTMLParser):

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    @override
    def handle_data(self, d):  # noqa
        self.text.append(d)

    def get_data(self) -> str:
        return "".join(self.text)


class BaseMessageText(ABC):

    @property
    @abstractmethod
    def title(self) -> str:
        ...

    @property
    @abstractmethod
    def html_text(self) -> str:
        ...

    @staticmethod
    def _strip_tags(html_str: str) -> str:
        stripper = _HTMLStripper()
        stripper.feed(html_str)
        return stripper.get_data()

    @property
    def popup_text(self) -> str:
        return f"<div>{self.html_text}</div>"

    @property
    def log_text(self) -> str:
        return self._strip_tags(self.html_text)
