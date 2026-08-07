import pytest


def test_transport_service_module_imports():
    from app.services import transport_service

    assert hasattr(transport_service, "bus_service")
    assert hasattr(transport_service, "route_service")
    assert hasattr(transport_service, "driver_service")
    assert hasattr(transport_service, "student_transport_service")
    assert hasattr(transport_service, "transport_summary")


def test_transport_summary_function_exists():
    from app.services.transport_service import transport_summary

    assert callable(transport_summary)


def test_driver_service_has_required_methods():
    from app.services.transport_service import driver_service

    assert hasattr(driver_service, "create")
    assert hasattr(driver_service, "get")
    assert hasattr(driver_service, "list")
    assert hasattr(driver_service, "update")
    assert hasattr(driver_service, "delete")
