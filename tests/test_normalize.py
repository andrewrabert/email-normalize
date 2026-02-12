import uuid
from unittest import mock

import email_normalize


def _perform_test(address, normalized, mx_records, provider):
    with mock.patch('email_normalize.Normalizer.mx_records') as mxr:
        mxr.return_value = mx_records
        result = email_normalize.normalize(address)
    assert isinstance(result, email_normalize.Result)
    assert result.address == address
    assert result.normalized_address == normalized
    assert result.mx_records == mx_records
    assert result.mailbox_provider == provider


def test_invalid_domain_part():
    address = f'{uuid.uuid4()}@{uuid.uuid4()}'
    result = email_normalize.normalize(address)
    assert isinstance(result, email_normalize.Result)
    assert result.address == address
    assert result.normalized_address == address
    assert result.mx_records == []
    assert result.mailbox_provider is None


def test_apple():
    local_part = str(uuid.uuid4())
    domain_part = str(uuid.uuid4())
    address = f'{local_part}+test@{domain_part}'
    mx_records = [(10, 'mx01.mail.icloud.com')]
    _perform_test(address, f'{local_part}@{domain_part}', mx_records, 'Apple')


def test_fastmail_plus_addressing():
    local_part = str(uuid.uuid4())
    domain_part = str(uuid.uuid4())
    address = f'{local_part}+test@{domain_part}'
    mx_records = [(10, 'in1-smtp.messagingengine.com')]
    _perform_test(
        address, f'{local_part}@{domain_part}', mx_records, 'Fastmail'
    )


def test_fastmail_local_part_as_hostname():
    local_part = str(uuid.uuid4())
    domain_part = f'{uuid.uuid4()}.com'
    address = f'testing@{local_part}.{domain_part}'
    mx_records = [(10, 'in1-smtp.messagingengine.com')]
    _perform_test(
        address, f'{local_part}@{domain_part}', mx_records, 'Fastmail'
    )


def test_google():
    local_part = str(uuid.uuid4()).replace('-', '.')
    domain_part = str(uuid.uuid4())
    address = f'{local_part}+test@{domain_part}'
    mx_records = [(1, 'aspmx.l.google.com')]
    _perform_test(
        address,
        f'{local_part.replace(".", "")}@{domain_part}',
        mx_records,
        'Google',
    )


def test_microsoft():
    local_part = str(uuid.uuid4())
    domain_part = str(uuid.uuid4())
    address = f'{local_part}+test@{domain_part}'
    mx_records = [(10, 'domain-com.mail.protection.outlook.com')]
    _perform_test(
        address, f'{local_part}@{domain_part}', mx_records, 'Microsoft'
    )


def test_protonmail():
    local_part = str(uuid.uuid4())
    domain_part = str(uuid.uuid4())
    address = f'{local_part}+test@{domain_part}'
    mx_records = [(5, 'mail.protonmail.ch')]
    _perform_test(
        address, f'{local_part}@{domain_part}', mx_records, 'ProtonMail'
    )


def test_rackspace():
    local_part = str(uuid.uuid4())
    domain_part = str(uuid.uuid4())
    address = f'{local_part}+test@{domain_part}'
    mx_records = [(10, 'mx1.emailsrvr.com')]
    _perform_test(
        address, f'{local_part}@{domain_part}', mx_records, 'Rackspace'
    )


def test_yahoo():
    local_part = str(uuid.uuid4())
    domain_part = str(uuid.uuid4())
    address = f'{local_part}@{domain_part}'
    mx_records = [(1, 'mta5.am0.yahoodns.net')]
    _perform_test(
        address,
        f'{local_part.split("-", 1)[0]}@{domain_part}',
        mx_records,
        'Yahoo',
    )


def test_yandex():
    local_part = str(uuid.uuid4())
    domain_part = str(uuid.uuid4())
    address = f'{local_part}+test@{domain_part}'
    mx_records = [(10, 'mx.yandex.net')]
    _perform_test(address, f'{local_part}@{domain_part}', mx_records, 'Yandex')


def test_zoho():
    local_part = str(uuid.uuid4())
    domain_part = str(uuid.uuid4())
    address = f'{local_part}+test@{domain_part}'
    mx_records = [(10, 'mx.zoho.com')]
    _perform_test(address, f'{local_part}@{domain_part}', mx_records, 'Zoho')
