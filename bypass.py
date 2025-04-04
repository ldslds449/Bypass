import sys
import logging
from typing import Optional

from proxy.common.flag import flags
from proxy.http.proxy import HttpProxyBasePlugin
from proxy.http.parser import HttpParser
from proxy.http.responses import seeOthersResponse
from proxy.common.constants import SLASH, COLON

logger = logging.getLogger(__name__)

flags.add_argument(
    "--bypass-ip",
    default="127.0.0.1",
    type=str,
    help="ip of bypass server",
)
flags.add_argument(
    "--bypass-port", default=8282, type=int, help="port of bypass server"
)


class CustomPlugin(HttpProxyBasePlugin):

    def __init__(
        self, uid, flag, client, event_queue, upstream_conn_pool=None
    ):
        super().__init__(uid, flag, client, event_queue, upstream_conn_pool)
        self.bypass_ip: str = flag.bypass_ip
        self.bypass_port: int = flag.bypass_port
        logger.info("Connect IP: %s", self.bypass_ip)
        logger.info("Connect Port: %d", self.bypass_port)

    def __is_bypass_host(self, host: bytes, port: int):
        return host == self.bypass_ip.encode() and port == self.bypass_port

    def before_upstream_connection(
        self,
        request: HttpParser,
    ) -> Optional[HttpParser]:
        if not self.__is_bypass_host(request.host, request.port):
            return None
        return request

    def handle_client_request(
        self,
        request: HttpParser,
    ) -> Optional[HttpParser]:
        logger.info("Request host: %s", request.host)
        logger.info("Request path: %s", request.path)
        if not self.__is_bypass_host(request.host, request.port):
            scheme = b"https" if request.port == 443 else b"http"
            host = request.host
            path = SLASH if not request.path else request.path

            new_request = (
                b"https://"
                + self.bypass_ip.encode()
                + COLON
                + str(self.bypass_port).encode()
                + SLASH
                + b"html"
            )
            new_request += (
                b"?url=" + scheme + COLON + SLASH + SLASH + host + path
            )
            logger.info("New request: %s", new_request)

            self.client.queue(
                seeOthersResponse(new_request),
            )
            return None
        return request


if __name__ == "__main__":
    from proxy.proxy import Proxy, sleep_loop

    with Proxy(
        sys.argv[1:],
        plugins=[CustomPlugin],
    ) as p:
        sleep_loop(p)
