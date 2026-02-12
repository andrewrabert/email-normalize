import asyncio
import operator
import time
import uuid
from unittest import mock

import aiodns
import pytest

import email_normalize


@pytest.fixture(autouse=True)
def _clear_cache():
    email_normalize.cache = {}
    yield
    email_normalize.cache = {}


@pytest.fixture
async def normalizer():
    return email_normalize.Normalizer()


async def test_mx_records(normalizer):
    resolver = aiodns.DNSResolver()
    result = await resolver.query('gmail.com', 'MX')
    expectation = sorted(
        [(r.priority, r.host) for r in result], key=operator.itemgetter(0, 1)
    )
    assert await normalizer.mx_records('gmail.com') == expectation


async def test_cache(normalizer):
    await normalizer.mx_records('gmail.com')
    await normalizer.mx_records('gmail.com')
    assert email_normalize.cache['gmail.com'].hits == 2
    del email_normalize.cache['gmail.com']
    assert 'gmail.com' not in email_normalize.cache
    with pytest.raises(KeyError):
        email_normalize.cache['foo']


async def test_cache_max_size(normalizer):
    for offset in range(normalizer.cache_limit):
        key = f'key-{offset}'
        email_normalize.cache[key] = email_normalize.CachedItem([], 60)
        email_normalize.cache[key].hits = 3
        email_normalize.cache[key].last_access = time.monotonic()

    await normalizer.mx_records('gmail.com')
    assert 'key-0' not in email_normalize.cache

    await normalizer.mx_records('github.com')
    assert 'gmail.com' not in email_normalize.cache
    assert 'github.com' in email_normalize.cache


async def test_cache_expiration(normalizer):
    await normalizer.mx_records('gmail.com')
    cached_at = email_normalize.cache['gmail.com'].cached_at
    email_normalize.cache['gmail.com'].ttl = 1
    await asyncio.sleep(1)
    assert email_normalize.cache['gmail.com'].expired
    await normalizer.mx_records('gmail.com')
    assert email_normalize.cache['gmail.com'].cached_at > cached_at


async def test_empty_mx_list(normalizer):
    with mock.patch.object(normalizer, 'mx_records') as mx_records:
        mx_records.return_value = []
        result = await normalizer.normalize('foo@bar.com')
        assert result.normalized_address == 'foo@bar.com'
        assert result.mailbox_provider is None
        assert result.mx_records == []


async def test_failure_cached(normalizer):
    key = str(uuid.uuid4())
    records = await normalizer.mx_records(key)
    assert records == []
    assert key in email_normalize.cache


async def test_failure_not_cached(normalizer):
    normalizer.cache_failures = False
    key = str(uuid.uuid4())
    records = await normalizer.mx_records(key)
    assert records == []


async def test_weird_mx_list(normalizer):
    with mock.patch.object(normalizer, 'mx_records') as recs:
        recs.return_value = [
            (1, str(uuid.uuid4())),
            (10, 'aspmx.l.google.com'),
        ]
        result = await normalizer.normalize('f.o.o+bar@gmail.com')
        assert result.normalized_address == 'foo@gmail.com'
        assert result.mailbox_provider == 'Google'
