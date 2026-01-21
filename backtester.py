"""
Backtester para validar la estrategia de trading.
Simula trading histórico para evaluar rendimiento.
"""

import json
import logging
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
import numpy as np

from technical_analysis import MarketDataProcessor
from signal_generator import SignalGenerator, SignalType
from risk_manager import RiskManager, RiskConfig, PositionStatus


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Backtester:
    """
    Backtester para validar estrategia de trading.
    Simula ejecución histórica del bot.
    """
    
    def __init__(
        self,
        initial_capital: float = 10000.0,
        risk_per_trade: float = 0.02,
        commission: float = 0.0005
    ):
        """
        Inicializar backtester.
        
        Args:
            initial_capital: Capital inicial
            risk_per_trade: Riesgo por operación
            commission: Comisión por operación
        """
        self.initial_capital = initial_capital
        self.risk_per_trade = risk_per_trade
        self.commission = commission
        
        # Componentes
        risk_config = RiskConfig(
            total_capital=initial_capital,
            risk_per_trade=risk_per_trade
        )
        self.risk_manager = RiskManager(risk_config)
        self.signal_generator = SignalGenerator()
        self.processor = MarketDataProcessor()
        
        # Estadísticas
        self.trades_executed = 0
        self.total_commission = 0.0
        self.equity_curve = [initial_capital]
        self.timestamps = []
        
        logger.info(f"Backtester inicializado con capital: {initial_capital}")
    
    def run_backtest(
        self,
        ohlcv_data: List[List],
        pair: str = "BTC/USD",
        lookback_period: int = 200
    ) -> Dict:
        """
        Ejecutar backtest.
        
        Args:
            ohlcv_data: Datos OHLCV históricos
            pair: Par de trading
            lookback_period: Período de lookback para indicadores
            
        Returns:
            Diccionario con resultados del backtest
        """
        logger.info(f"Iniciando backtest con {len(ohlcv_data)} velas")
        
        # Validar datos
        if len(ohlcv_data) < lookback_period:
            logger.error(f"Datos insuficientes: {len(ohlcv_data)} < {lookback_period}")
            return {}
        
        # Procesar cada vela
        for i in range(lookback_period, len(ohlcv_data)):
            # Obtener ventana de datos
            window_data = ohlcv_data[i-lookback_period:i]
            current_candle = ohlcv_data[i]
            current_price = float(current_candle[4])  # Close
            timestamp = current_candle[0]
            
            # Generar señal
            signal = self.signal_generator.generate_signal(
                window_data,
                current_price,
                atr_multiplier=2.0
            )
            
            # Ejecutar señal
            if signal:
                self._execute_signal(pair, signal, current_price, timestamp)
            
            # Monitorear posiciones
            self._monitor_positions(pair, current_price, timestamp)
            
            # Registrar equity
            current_equity = self.risk_manager.get_current_capital()
            self.equity_curve.append(current_equity)
            self.timestamps.append(timestamp)
        
        # Generar reporte
        return self._generate_backtest_report()
    
    def _execute_signal(
        self,
        pair: str,
        signal,
        current_price: float,
        timestamp: float
    ):
        """
        Ejecutar una señal de trading.
        
        Args:
            pair: Par de trading
            signal: Señal generada
            current_price: Precio actual
            timestamp: Timestamp
        """
        # Calcular tamaño de posición
        volume = self.risk_manager.calculate_position_size(
            signal.entry_price,
            signal.stop_loss,
            signal.confidence
        )
        
        if volume <= 0:
            return
        
        # Aplicar comisión
        commission_cost = signal.entry_price * volume * self.commission
        self.total_commission += commission_cost
        
        # Abrir posición
        position_id = f"{pair}_{int(timestamp)}"
        side = "buy" if signal.signal_type == SignalType.BUY else "sell"
        
        success = self.risk_manager.open_position(
            position_id=position_id,
            pair=pair,
            side=side,
            entry_price=signal.entry_price,
            volume=volume,
            stop_loss=signal.stop_loss,
            take_profit_1=signal.take_profit_1,
            take_profit_2=signal.take_profit_2,
            take_profit_3=signal.take_profit_3
        )
        
        if success:
            self.trades_executed += 1
            logger.debug(
                f"Señal ejecutada: {side.upper()} {volume:.4f} {pair} @ {current_price:.2f}"
            )
    
    def _monitor_positions(
        self,
        pair: str,
        current_price: float,
        timestamp: float
    ):
        """
        Monitorear posiciones abiertas.
        
        Args:
            pair: Par de trading
            current_price: Precio actual
            timestamp: Timestamp
        """
        for position_id, position in list(self.risk_manager.positions.items()):
            if position.pair != pair:
                continue
            
            # Actualizar precio
            self.risk_manager.update_position_price(position_id, current_price)
            
            # Verificar stop loss
            if self.risk_manager.check_stop_loss(position_id, current_price):
                self.risk_manager.close_position_stop_loss(position_id, current_price)
                logger.debug(f"Stop loss ejecutado: {position_id}")
            
            # Verificar take profit
            tp_level, reached = self.risk_manager.check_take_profit(position_id, current_price)
            if reached:
                self.risk_manager.close_position_partial(position_id, tp_level, current_price)
                logger.debug(f"Take profit {tp_level} ejecutado: {position_id}")
    
    def _generate_backtest_report(self) -> Dict:
        """
        Generar reporte de backtest.
        
        Returns:
            Diccionario con resultados
        """
        stats = self.risk_manager.get_statistics()
        
        # Calcular métricas adicionales
        equity_array = np.array(self.equity_curve)
        returns = np.diff(equity_array) / equity_array[:-1]
        
        # Sharpe Ratio (asumiendo 252 días de trading)
        annual_return = (equity_array[-1] / self.initial_capital) ** (252 / len(self.equity_curve)) - 1
        daily_volatility = np.std(returns)
        sharpe_ratio = (annual_return / 252) / (daily_volatility + 1e-10) if daily_volatility > 0 else 0
        
        # Máximo drawdown
        cummax = np.maximum.accumulate(equity_array)
        drawdown = (equity_array - cummax) / cummax
        max_drawdown = np.min(drawdown)
        
        # Recovery factor
        recovery_factor = stats["total_pnl"] / abs(max_drawdown * self.initial_capital) if max_drawdown != 0 else 0
        
        report = {
            "backtest_summary": {
                "initial_capital": self.initial_capital,
                "final_capital": equity_array[-1],
                "total_return": (equity_array[-1] - self.initial_capital) / self.initial_capital,
                "total_return_pnl": stats["total_pnl"],
                "annual_return": annual_return,
                "max_drawdown": max_drawdown,
                "sharpe_ratio": sharpe_ratio,
                "recovery_factor": recovery_factor,
                "total_commission": self.total_commission
            },
            "trading_statistics": stats,
            "equity_curve": self.equity_curve[-100:],  # Últimas 100 velas
            "timestamps": self.timestamps[-100:] if self.timestamps else []
        }
        
        return report
    
    def print_report(self, report: Dict):
        """
        Imprimir reporte de backtest.
        
        Args:
            report: Reporte de backtest
        """
        if not report:
            logger.error("Reporte vacío")
            return
        
        summary = report.get("backtest_summary", {})
        stats = report.get("trading_statistics", {})
        
        logger.info("=" * 60)
        logger.info("REPORTE DE BACKTEST")
        logger.info("=" * 60)
        
        logger.info("\nRESUMEN FINANCIERO:")
        logger.info(f"  Capital inicial:        ${summary.get('initial_capital', 0):,.2f}")
        logger.info(f"  Capital final:          ${summary.get('final_capital', 0):,.2f}")
        logger.info(f"  Retorno total:          {summary.get('total_return', 0):.2%}")
        logger.info(f"  PnL realizado:          ${summary.get('total_return_pnl', 0):,.2f}")
        logger.info(f"  Comisiones pagadas:     ${summary.get('total_commission', 0):,.2f}")
        
        logger.info("\nMÉTRICAS DE RIESGO:")
        logger.info(f"  Máximo drawdown:        {summary.get('max_drawdown', 0):.2%}")
        logger.info(f"  Sharpe Ratio:           {summary.get('sharpe_ratio', 0):.2f}")
        logger.info(f"  Recovery Factor:        {summary.get('recovery_factor', 0):.2f}")
        
        logger.info("\nESTADÍSTICAS DE TRADING:")
        logger.info(f"  Total operaciones:      {stats.get('total_trades', 0)}")
        logger.info(f"  Operaciones ganadoras:  {stats.get('winning_trades', 0)}")
        logger.info(f"  Operaciones perdedoras:  {stats.get('losing_trades', 0)}")
        logger.info(f"  Win rate:               {stats.get('win_rate', 0):.2%}")
        logger.info(f"  Profit factor:          {stats.get('profit_factor', 0):.2f}")
        logger.info(f"  Ganancias totales:      ${stats.get('total_profit', 0):,.2f}")
        logger.info(f"  Pérdidas totales:       ${stats.get('total_loss', 0):,.2f}")
        
        logger.info("\n" + "=" * 60)
    
    def save_report(self, report: Dict, filename: str = "backtest_report.json"):
        """
        Guardar reporte en archivo.
        
        Args:
            report: Reporte de backtest
            filename: Nombre del archivo
        """
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Reporte guardado en {filename}")


def generate_sample_data(
    initial_price: float = 100.0,
    num_candles: int = 1000,
    volatility: float = 0.02,
    trend: float = 0.0001
) -> List[List]:
    """
    Generar datos OHLCV de ejemplo para backtesting.
    
    Args:
        initial_price: Precio inicial
        num_candles: Número de velas
        volatility: Volatilidad diaria
        trend: Tendencia diaria
        
    Returns:
        Lista de datos OHLCV
    """
    ohlcv_data = []
    current_price = initial_price
    
    for i in range(num_candles):
        # Generar movimiento de precio
        daily_return = np.random.normal(trend, volatility)
        
        open_price = current_price
        high = open_price * (1 + abs(np.random.normal(0, volatility/2)))
        low = open_price * (1 - abs(np.random.normal(0, volatility/2)))
        close = open_price * (1 + daily_return)
        volume = np.random.uniform(900, 1100)
        
        # Asegurar que high >= close >= low
        high = max(high, close)
        low = min(low, close)
        
        ohlcv_data.append([
            i,  # timestamp
            open_price,
            high,
            low,
            close,
            0,  # unused
            volume
        ])
        
        current_price = close
    
    return ohlcv_data


if __name__ == "__main__":
    # Generar datos de ejemplo
    logger.info("Generando datos de ejemplo...")
    sample_data = generate_sample_data(
        initial_price=100.0,
        num_candles=500,
        volatility=0.02,
        trend=0.0005
    )
    
    # Ejecutar backtest
    logger.info("Ejecutando backtest...")
    backtester = Backtester(initial_capital=10000.0)
    report = backtester.run_backtest(sample_data)
    
    # Mostrar resultados
    backtester.print_report(report)
    backtester.save_report(report)
