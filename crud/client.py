# -*- coding: utf-8 -*-
import argparse
import socket

from ast import literal_eval

from crud.controllers import controller_mapping
from crud.views import view_mapping


class Client:
    def __init__(self, hostname: str, port: int):
        self.hostname = hostname
        self.port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((hostname, port))

    def send(self, args: argparse.Namespace):
        pattern = " ".join(args.pattern)
        payload = f"{args.operation}:::{args.type}:::{pattern}"
        payload = payload.encode()
        self._socket.send(payload)
        response = self._socket.recv(1024)
        print(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "operation",
        choices=["get", "create", "update", "filter", "deactivate"]
    )
    parser.add_argument(
        "type",
        choices=["sport", "event", "selection"]
    )
    parser.add_argument(
        "pattern",
        nargs="*"
    )
    parser.add_argument("--hostname", default="localhost")
    parser.add_argument("--port", type=int, default=10000)
    args = parser.parse_args()

    client = Client(args.hostname, args.port)
    client.send(args)

