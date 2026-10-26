import pytest
from pydantic import ValidationError

from eos.configuration.eos_config import FileDbConfig
from eos.database import file_db_interface
from eos.database.file_db_interface import FileDbInterface


class TestFileDbConfigCredentials:
    def test_static_keys(self):
        config = FileDbConfig(access_key_id="key", secret_access_key="secret")
        assert config.access_key_id == "key"
        assert config.secret_access_key == "secret"

    def test_no_keys_uses_default_credential_chain(self):
        config = FileDbConfig(access_key_id=None, secret_access_key=None)
        assert config.access_key_id is None
        assert config.secret_access_key is None

    @pytest.mark.parametrize(
        ("access_key_id", "secret_access_key"),
        [("key", None), (None, "secret")],
    )
    def test_only_one_key_is_rejected(self, access_key_id, secret_access_key):
        with pytest.raises(ValidationError, match="both EOS_S3_ACCESS_KEY_ID and EOS_S3_SECRET_ACCESS_KEY"):
            FileDbConfig(access_key_id=access_key_id, secret_access_key=secret_access_key)


class TestFileDbInterfaceCredentials:
    @pytest.mark.parametrize(
        ("access_key_id", "secret_access_key"),
        [("key", "secret"), (None, None)],
    )
    def test_keys_are_passed_to_boto3(self, monkeypatch, access_key_id, secret_access_key):
        calls = []
        monkeypatch.setattr(file_db_interface.boto3, "client", lambda *args, **kwargs: calls.append(kwargs))

        config = FileDbConfig(access_key_id=access_key_id, secret_access_key=secret_access_key)
        FileDbInterface(config, ensure_bucket=False)

        assert calls[0]["aws_access_key_id"] == access_key_id
        assert calls[0]["aws_secret_access_key"] == secret_access_key
