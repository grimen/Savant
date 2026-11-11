"""Sink client types supplied by Savant RS."""

from savant_rs.py.client.runner.sink import AsyncSinkRunner as SavantRsAsyncSinkRunner
from savant_rs.py.client.runner.sink import SinkResult


class _ReceivedMessage:
    def __init__(self, message):
        self._message = message

    def __getattr__(self, name):
        return getattr(self._message, name)

    def validate_seq_id(self):
        pass


class AsyncSinkRunner(SavantRsAsyncSinkRunner):
    def _handle_message(self, zmq_message):
        if not hasattr(zmq_message.message, 'validate_seq_id'):
            message = _ReceivedMessage(zmq_message.message)
            zmq_message = zmq_message._replace(message=message)
        return super()._handle_message(zmq_message)


__all__ = ['AsyncSinkRunner', 'SinkResult']
