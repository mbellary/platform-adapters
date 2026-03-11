"""Package smoke tests."""


def test_package_importable() -> None:
    import platform_adapters

    assert platform_adapters.__doc__
