from flask import has_request_context, request


def flask_request_remote_addr_prefix():
    return request.remote_addr if has_request_context() else ""
