"""Client builders with Savant compatibility runners."""

from savant_rs.py.client.builder.sink import SinkBuilder as SavantRsSinkBuilder

from .runner.sink import AsyncSinkRunner, SinkRunner


class SinkBuilder(SavantRsSinkBuilder):
    def build(self) -> SinkRunner:
        assert self._socket is not None, 'socket is required'
        return SinkRunner(
            socket=self._socket,
            log_provider=self._log_provider,
            idle_timeout=self._idle_timeout,
            module_health_check_url=self._module_health_check_url,
            module_health_check_timeout=self._module_health_check_timeout,
            module_health_check_interval=self._module_health_check_interval,
            source_id=self._source_id,
            source_id_prefix=self._source_id_prefix,
        )

    def build_async(self) -> AsyncSinkRunner:
        assert self._socket is not None, 'socket is required'
        return AsyncSinkRunner(
            socket=self._socket,
            log_provider=self._log_provider,
            idle_timeout=self._idle_timeout,
            module_health_check_url=self._module_health_check_url,
            module_health_check_timeout=self._module_health_check_timeout,
            module_health_check_interval=self._module_health_check_interval,
            source_id=self._source_id,
            source_id_prefix=self._source_id_prefix,
        )

    def _with_field(self, field: str, value) -> 'SinkBuilder':
        return type(self)(
            **{
                'socket': self._socket,
                'log_provider': self._log_provider,
                'idle_timeout': self._idle_timeout,
                'module_health_check_url': self._module_health_check_url,
                'module_health_check_timeout': self._module_health_check_timeout,
                'module_health_check_interval': self._module_health_check_interval,
                'source_id': self._source_id,
                'source_id_prefix': self._source_id_prefix,
                field: value,
            }
        )
