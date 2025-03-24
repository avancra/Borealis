import logging

LOGGER = logging.getLogger(__name__)


class Component:

    def __init__(self, session_orchestrator):
        self._orchestrator = session_orchestrator
        self._orchestrator.add_component(self)

    def send(self, message, **kwargs):
        """Sends a message to the mediator."""
        LOGGER.debug('Sending message: %s', message)
        self._orchestrator.notify(self, message, **kwargs)

    def receive(self, message, **kwargs):
        """Receives and processes messages from the mediator."""
        pass
