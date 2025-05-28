from abc import ABC, abstractmethod


class IA_Agent(ABC):
    """
    An abstract base class for AI agents.
    """
    @abstractmethod
    def __init__(self, api_key: str, model: str) -> None:
        """
        Initializes the AI agent with a name.
        """
        raise NotImplementedError("Subclasses must implement this method.")


    @abstractmethod
    def respond(self, message: str) -> dict:
        """
        Generates a response to the given message.
        This method should be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")
    