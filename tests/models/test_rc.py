from cnairgapper.models.rc import RC


def test_rc_default_initialization():
    rc = RC()
    assert rc.ok is False
    assert rc.err is False
    assert rc.sync_cnt is False
    assert rc.msg == ""
    assert rc.ref == ""
    assert rc.type == ""
    assert rc.entity is None


def test_rc_initialization_with_custom_values():
    rc = RC(
        ok=True,
        err=True,
        sync_cnt=True,
        msg="Test message",
        ref="Test reference",
        type="CustomType",
        entity={"key": "value"},
    )
    assert rc.ok is True
    assert rc.err is True
    assert rc.sync_cnt is True
    assert rc.msg == "Test message"
    assert rc.ref == "Test reference"
    assert rc.type == "CustomType"
    assert rc.entity == {"key": "value"}


def test_rc_partial_initialization():
    rc = RC(ok=True, msg="Partial initialization")
    assert rc.ok is True
    assert rc.msg == "Partial initialization"
    assert rc.err is False
    assert rc.sync_cnt is False
    assert rc.ref == ""
    assert rc.type == ""
    assert rc.entity is None
