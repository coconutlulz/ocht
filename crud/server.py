
import socketserver
import argparse

from crud.controllers import controller_mapping
from crud.views import view_mapping


class RequestHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def handle(self):
        data = self.request.recv(1024).decode()
        operation, operation_type, pattern = data.split(':::')
        pattern = pattern.split(' ')
        result = str(self._handle(operation, operation_type, pattern))
        self.request.send(result.encode())

    def _handle(self, operation: str, operation_type: str, pattern: list):
        if operation == "get":
            view = view_mapping[operation_type]
            get_func = getattr(view, f"get_{operation_type}")
            pattern = int(pattern[0])
            result = get_func(pattern)
            return result
        elif operation == "create":
            controller = controller_mapping[operation_type]
            create_func = getattr(controller, f"create_{operation_type}")
            pattern = pattern[0]
            dict_repr = literal_eval(pattern)
            result = create_func(**dict_repr)
            return result
        elif operation == "update":
            controller = controller_mapping[operation_type]
            update_func = getattr(controller, f"update_{operation_type}")
            model_id = int(pattern[0])
            pattern = pattern[1]
            dict_repr = literal_eval(pattern)
            result = update_func(model_id, **dict_repr)
            return result
        elif operation == "deactivate":
            controller = controller_mapping[operation_type]
            deactivate_func = getattr(controller, f"deactivate_{operation_type}")
            model_id = int(pattern[0])
            result = deactivate_func(model_id)
            return result
        elif operation == "filter":
            view = view_mapping[operation_type]
            filter_func = getattr(view, f"get_{operation_type}_filtered")
            filter_pattern = ' '.join(pattern)
            result = filter_func(filter_pattern)
            return result


class RequestServer(socketserver.TCPServer):
    def __init__(self, server_address, handler_class=RequestHandler):
        super().__init__(server_address, handler_class)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "port",
        type=int,
    )
    args = parser.parse_args()
    server = RequestServer(('localhost', args.port))
    server.serve_forever()
