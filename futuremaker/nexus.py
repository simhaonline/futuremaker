import datetime

from futuremaker import utils
from futuremaker.bitmex.bitmex_ws import BitmexWS
from futuremaker.candle_handler import CandleHandler
from futuremaker.log import logger


class Nexus(object):
    """
    거래소의 상태를 모두 가지고 있는 매우 중요한 객체.
    포지션, 주문, 잔고등이 웹소켓을 통해 지속적으로 업데이트 된다.
    물론 캔들데이터도 저장된다.
    주문기능도 가지고 있다.
    nexus.api.put_order() 와 같이 사용.
    """

    def __init__(self, api, symbol, candle_limit, candle_period=None, dry_run=True):
        """
        :param symbol: 심볼페어. XBTUSD, BTC/USD
        :param dry_run: 참일 경우 실제 주문 api를 호출하지 않는다.
        :param candle_limit: 저장할 최대 캔들갯수.
        :param candle_period: 봉주기. Bitmex는 4가지만 지원한다. 1m, 5m, 1h, 1d
        """
        self.candle_handler = None
        self.api = api
        self.cb_update_candle = None
        self.dry_run = dry_run

        logger.info(f'Nexus symbol[{symbol}] period[{candle_period}] dry_run[{dry_run}]')

        if candle_limit and candle_period:
            period_in_second = 0
            if candle_period == '1m':
                period_in_second = 60
            elif candle_period == '5m':
                period_in_second = 300
            elif candle_period == '1h':
                period_in_second = 3600
            elif candle_period == '1d':
                period_in_second = 3600 * 24
            ts = datetime.datetime.now().timestamp() - period_in_second * candle_limit
            since = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            # 현재시각에서 since를 뺀 날짜를 string으로 만든다.
            self.candle_handler = CandleHandler(self.api, symbol, period=candle_period, since=since)

    def callback(self, update_orderbook=None, update_candle=None, update_order=None, update_position=None):
        """
        데이터 변경시 호출되는 콜백함수들을 설정한다.
        :param update_orderbook: 호가창 업데이트시마다 호출. 매우 빈번히 호출.
        :param update_candle: 캔들업데이트시 호출되는 콜백함수. 캔들의 period 마다 호출된다.
        :param update_order: 주문이 성공되거나 할때 호출되는 콜백함수
        :param update_position: 포지션 변경시 호출되는 콜백함수
        :return:
        """
        self.cb_update_candle = update_candle
        # self.ws.update_orderbook = update_orderbook
        # self.ws.update_candle = self._update_candle
        # self.ws.update_order = update_order
        # self.ws.update_position = update_position

    def _update_candle(self, item):
        candle_df = self.candle_handler.update(item)
        # 캔들업뎃호출
        if self.cb_update_candle:
            self.cb_update_candle(candle_df, item)

    async def load(self):
        try:

            # await
            # self.api.load_markets()

            if self.candle_handler:
                # await
                self.candle_handler.load()
            else:
                logger.info('candle_handler 를 사용하지 않습니다.')

            # await self.ws.connect()
        except:
            utils.print_traceback()

    async def start(self):
        # await self.ws.listen()
        pass

    async def wait_ready(self):
        # await self.ws.wait_ready()
        pass

    # def __getitem__(self, item):
    #     if item in self.ws.data:
    #         return self.ws.data[item]