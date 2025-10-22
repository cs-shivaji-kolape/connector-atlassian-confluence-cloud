"""
Copyright start
MIT License
Copyright (c) 2025 Fortinet Inc
Copyright end
"""

from connectors.core.connector import Connector, get_logger, ConnectorError
from .operations import operations, _check_health

logger = get_logger('atlassian-confluence-cloud')


class ConfluenceCloud(Connector):
    def execute(self, config, operation, params, **kwargs):
        try:
            operation = operations.get(operation)
            return operation(config, params)
        except Exception as err:
            logger.error('{}'.format(err))
            raise ConnectorError('{}'.format(err))

    def check_health(self, config):
        logger.info('starting health check')
        return _check_health(config)

