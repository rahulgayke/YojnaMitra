from fastapi import Request

from yojanamitra.infrastructure.services import Services


def get_services(request: Request) -> Services:
    services = getattr(request.app.state, "services", None)
    if services is None:
        raise RuntimeError("Application services are not initialized")
    return services
