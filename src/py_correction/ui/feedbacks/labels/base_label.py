from abc import ABC, abstractmethod


class BaseLabelText(ABC):

    @property
    @abstractmethod
    def html_text(self) -> str:
        ...

    @property
    def label_text(self) -> str:
        return f"<div>{self.html_text}</div>"
