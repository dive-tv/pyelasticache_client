# API Backwards compatibility

from pyelasticache_client.client.base import Client  # noqa
from pyelasticache_client.client.base import PooledClient  # noqa

from pyelasticache_client.exceptions import MemcacheError  # noqa
from pyelasticache_client.exceptions import MemcacheClientError  # noqa
from pyelasticache_client.exceptions import MemcacheUnknownCommandError  # noqa
from pyelasticache_client.exceptions import MemcacheIllegalInputError  # noqa
from pyelasticache_client.exceptions import MemcacheServerError  # noqa
from pyelasticache_client.exceptions import MemcacheUnknownError  # noqa
from pyelasticache_client.exceptions import MemcacheUnexpectedCloseError  # noqa
