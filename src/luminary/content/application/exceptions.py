from common.application.exceptions import ApplicationError


class ParsingError(ApplicationError):
    def __init__(self) -> None:
        super().__init__("parsing failed")
