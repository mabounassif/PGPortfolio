import pytest
import re

from pgportfolio.tools.configprocess import parse_time

from pgportfolio.marketdata.poloniex import Poloniex
from pgportfolio.marketdata.coinbase import Coinbase

exchanges = [Poloniex, Coinbase]


def get_pair(exchange):
    return 'BTC_ETH' if exchange.__class__ == Poloniex else 'ETH_BTC'


@pytest.fixture(params=exchanges, scope='module')
def exchange(request):
    Exchange = request.param
    return Exchange()


@pytest.fixture(params=exchanges)
def exchange(request):
    Exchange = request.param
    return Exchange()


@pytest.mark.vcr
def test_market_volume(exchange):
    p = re.compile('[A-Za-z]{2,8}_[A-Za-z]{2,8}')
    vol = exchange.marketVolume()
    vol = dict(filter(lambda v: 'total' not in v[0], vol.items()))

    assert all([re.fullmatch(p, v) for v in vol])
    assert all([list(v.keys()) == k.split('_') for k, v in vol.items()])


@pytest.mark.vcr
def test_market_ticker(exchange):
    p = re.compile('[A-Za-z]{2,8}_[A-Za-z]{2,8}')
    ticker = exchange.marketTicker()

    assert all([re.fullmatch(p, t) for t in ticker])
    assert all(['last' in v.keys() for k, v in ticker.items()])


@pytest.mark.vcr
def test_market_status(exchange):
    p = re.compile(r"""\w{2,8}""")
    status = exchange.marketStatus()

    assert all([re.fullmatch(p, k) for k in status.keys()])


@pytest.mark.vcr
def test_market_chart(exchange):
    DAY = 24 * 3600
    START = parse_time('2015/07/01')
    END = parse_time('2017/07/01')

    attr_set = set([
        'volume',
        'quoteVolume',
        'weightedAverage',
        'close',
        'low',
        'high',
        'date',
        'open'
    ])

    chart = exchange.marketChart(
        pair=get_pair(exchange),
        start=START,
        period=DAY,
        end=END
    )

    assert all(
        [
            attr_set <= set(v.keys()) for v in chart
        ]
    )
