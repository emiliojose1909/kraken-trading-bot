"""
Suite de pruebas unitarias para el bot de trading.
Valida todas las capas del sistema.
"""

import unittest
import logging
from datetime import datetime
import numpy as np

from technical_analysis import TechnicalAnalysis, MarketDataProcessor, TechnicalIndicators
from signal_generator import SignalGenerator, SignalType
from risk_manager import RiskManager, RiskConfig, PositionStatus


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestTechnicalAnalysis(unittest.TestCase):
    """Pruebas para análisis técnico"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        # Generar datos de ejemplo
        self.prices = np.array([100.0 + i*0.5 for i in range(200)])
        self.ta = TechnicalAnalysis()
    
    def test_ema_calculation(self):
        """Probar cálculo de EMA"""
        ema = self.ta.calculate_ema(self.prices, 12)
        self.assertEqual(len(ema), len(self.prices))
        self.assertFalse(np.isnan(ema[-1]))
        logger.info(f"EMA 12: {ema[-1]:.2f}")
    
    def test_rsi_calculation(self):
        """Probar cálculo de RSI"""
        rsi = self.ta.calculate_rsi(self.prices, 14)
        self.assertEqual(len(rsi), len(self.prices))
        # RSI debe estar entre 0 y 100
        valid_rsi = rsi[~np.isnan(rsi)]
        self.assertTrue(np.all(valid_rsi >= 0) and np.all(valid_rsi <= 100))
        logger.info(f"RSI 14: {rsi[-1]:.2f}")
    
    def test_macd_calculation(self):
        """Probar cálculo de MACD"""
        macd, signal, histogram = self.ta.calculate_macd(self.prices)
        self.assertEqual(len(macd), len(self.prices))
        self.assertEqual(len(signal), len(self.prices))
        self.assertEqual(len(histogram), len(self.prices))
        logger.info(f"MACD: {macd[-1]:.4f}, Signal: {signal[-1]:.4f}, Histogram: {histogram[-1]:.4f}")
    
    def test_bollinger_bands_calculation(self):
        """Probar cálculo de Bandas de Bollinger"""
        upper, middle, lower = self.ta.calculate_bollinger_bands(self.prices, 20, 2.0)
        self.assertEqual(len(upper), len(self.prices))
        # Upper debe ser > middle > lower
        valid_idx = ~(np.isnan(upper) | np.isnan(middle) | np.isnan(lower))
        self.assertTrue(np.all(upper[valid_idx] > middle[valid_idx]))
        self.assertTrue(np.all(middle[valid_idx] > lower[valid_idx]))
        logger.info(f"BB Upper: {upper[-1]:.2f}, Middle: {middle[-1]:.2f}, Lower: {lower[-1]:.2f}")
    
    def test_atr_calculation(self):
        """Probar cálculo de ATR"""
        high = self.prices + 1.0
        low = self.prices - 1.0
        atr = self.ta.calculate_atr(high, low, self.prices, 14)
        self.assertEqual(len(atr), len(self.prices))
        self.assertFalse(np.isnan(atr[-1]))
        logger.info(f"ATR 14: {atr[-1]:.2f}")
    
    def test_adx_calculation(self):
        """Probar cálculo de ADX"""
        high = self.prices + 1.0
        low = self.prices - 1.0
        adx = self.ta.calculate_adx(high, low, self.prices, 14)
        self.assertEqual(len(adx), len(self.prices))
        valid_adx = adx[~np.isnan(adx)]
        # ADX debe estar entre 0 y 100
        self.assertTrue(np.all(valid_adx >= 0) and np.all(valid_adx <= 100))
        logger.info(f"ADX 14: {adx[-1]:.2f}")


class TestMarketDataProcessor(unittest.TestCase):
    """Pruebas para procesador de datos de mercado"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.processor = MarketDataProcessor(min_candles=200)
        # Generar datos OHLCV de ejemplo
        self.ohlcv_data = []
        for i in range(200):
            time = 1000 + i
            open_price = 100.0 + i*0.1
            high = open_price + 1.0
            low = open_price - 1.0
            close = open_price + 0.5
            volume = 1000 + i*10
            self.ohlcv_data.append([time, open_price, high, low, close, volume])
    
    def test_process_ohlcv(self):
        """Probar procesamiento de datos OHLCV"""
        indicators = self.processor.process_ohlcv(self.ohlcv_data)
        self.assertIsNotNone(indicators)
        self.assertGreater(indicators.ema_12, 0)
        self.assertGreater(indicators.ema_50, 0)
        self.assertGreater(indicators.rsi_14, 0)
        logger.info(f"Indicadores procesados: EMA12={indicators.ema_12:.2f}, RSI={indicators.rsi_14:.2f}")
    
    def test_get_trend(self):
        """Probar detección de tendencia"""
        indicators = self.processor.process_ohlcv(self.ohlcv_data)
        trend = self.processor.get_trend(indicators)
        self.assertIn(trend, ["UPTREND", "DOWNTREND", "SIDEWAYS"])
        logger.info(f"Tendencia detectada: {trend}")
    
    def test_get_trend_strength(self):
        """Probar detección de fuerza de tendencia"""
        indicators = self.processor.process_ohlcv(self.ohlcv_data)
        strength = self.processor.get_trend_strength(indicators)
        self.assertIn(strength, ["STRONG", "MODERATE", "WEAK"])
        logger.info(f"Fuerza de tendencia: {strength}")


class TestSignalGenerator(unittest.TestCase):
    """Pruebas para generador de señales"""
    
    def setUp(self):
        """Configurar datos de prueba"""
        self.generator = SignalGenerator()
        # Generar datos OHLCV de ejemplo con tendencia alcista
        self.ohlcv_data = []
        for i in range(200):
            time = 1000 + i
            open_price = 100.0 + i*0.5  # Tendencia alcista
            high = open_price + 1.0
            low = open_price - 0.5
            close = open_price + 0.3
            volume = 1000 + i*10
            self.ohlcv_data.append([time, open_price, high, low, close, volume])
    
    def test_generate_signal(self):
        """Probar generación de señal"""
        current_price = 200.0
        signal = self.generator.generate_signal(self.ohlcv_data, current_price)
        
        if signal:
            self.assertIn(signal.signal_type, [SignalType.BUY, SignalType.SELL, SignalType.NEUTRAL])
            self.assertGreaterEqual(signal.confidence, 0.0)
            self.assertLessEqual(signal.confidence, 1.0)
            self.assertGreater(signal.position_size_percent, 0.0)
            logger.info(f"Señal generada: {signal.signal_type.value}, Confianza: {signal.confidence:.2%}")
        else:
            logger.info("No se generó señal (normal en datos de prueba)")


class TestRiskManager(unittest.TestCase):
    """Pruebas para gestor de riesgos"""
    
    def setUp(self):
        """Configurar gestor de riesgos"""
        config = RiskConfig(
            total_capital=10000.0,
            risk_per_trade=0.02,
            max_positions=5,
            max_position_size=0.10,
            max_drawdown=0.15
        )
        self.manager = RiskManager(config)
    
    def test_can_open_position(self):
        """Probar verificación de apertura de posición"""
        can_open, reason = self.manager.can_open_position()
        self.assertTrue(can_open)
        logger.info(f"Puede abrir posición: {can_open}")
    
    def test_calculate_position_size(self):
        """Probar cálculo de tamaño de posición"""
        entry_price = 100.0
        stop_loss = 95.0
        confidence = 0.8
        
        volume = self.manager.calculate_position_size(entry_price, stop_loss, confidence)
        self.assertGreater(volume, 0)
        logger.info(f"Tamaño de posición calculado: {volume:.4f}")
    
    def test_open_position(self):
        """Probar apertura de posición"""
        success = self.manager.open_position(
            position_id="test_001",
            pair="BTC/USD",
            side="buy",
            entry_price=45000.0,
            volume=0.1,
            stop_loss=44000.0,
            take_profit_1=46500.0,
            take_profit_2=48000.0,
            take_profit_3=50000.0
        )
        self.assertTrue(success)
        self.assertIn("test_001", self.manager.positions)
        logger.info("Posición abierta exitosamente")
    
    def test_update_position_price(self):
        """Probar actualización de precio de posición"""
        self.manager.open_position(
            position_id="test_002",
            pair="BTC/USD",
            side="buy",
            entry_price=45000.0,
            volume=0.1,
            stop_loss=44000.0,
            take_profit_1=46500.0,
            take_profit_2=48000.0,
            take_profit_3=50000.0
        )
        
        self.manager.update_position_price("test_002", 46000.0)
        position = self.manager.positions["test_002"]
        self.assertEqual(position.current_price, 46000.0)
        self.assertGreater(position.unrealized_pnl, 0)
        logger.info(f"Precio actualizado. PnL no realizado: {position.unrealized_pnl:.2f}")
    
    def test_check_stop_loss(self):
        """Probar verificación de stop loss"""
        self.manager.open_position(
            position_id="test_003",
            pair="BTC/USD",
            side="buy",
            entry_price=45000.0,
            volume=0.1,
            stop_loss=44000.0,
            take_profit_1=46500.0,
            take_profit_2=48000.0,
            take_profit_3=50000.0
        )
        
        # Precio por debajo del stop loss
        hit_sl = self.manager.check_stop_loss("test_003", 43900.0)
        self.assertTrue(hit_sl)
        logger.info("Stop loss detectado correctamente")
    
    def test_check_take_profit(self):
        """Probar verificación de take profit"""
        self.manager.open_position(
            position_id="test_004",
            pair="BTC/USD",
            side="buy",
            entry_price=45000.0,
            volume=0.1,
            stop_loss=44000.0,
            take_profit_1=46500.0,
            take_profit_2=48000.0,
            take_profit_3=50000.0
        )
        
        # Precio en TP1
        tp_level, reached = self.manager.check_take_profit("test_004", 46500.0)
        self.assertTrue(reached)
        self.assertEqual(tp_level, 1)
        logger.info("Take profit 1 detectado correctamente")
    
    def test_close_position_partial(self):
        """Probar cierre parcial de posición"""
        self.manager.open_position(
            position_id="test_005",
            pair="BTC/USD",
            side="buy",
            entry_price=45000.0,
            volume=0.1,
            stop_loss=44000.0,
            take_profit_1=46500.0,
            take_profit_2=48000.0,
            take_profit_3=50000.0
        )
        
        volume_closed = self.manager.close_position_partial("test_005", 1, 46500.0)
        self.assertGreater(volume_closed, 0)
        position = self.manager.positions["test_005"]
        self.assertGreater(position.realized_pnl, 0)
        logger.info(f"Cierre parcial: {volume_closed:.4f}, PnL: {position.realized_pnl:.2f}")
    
    def test_get_statistics(self):
        """Probar obtención de estadísticas"""
        # Abrir y cerrar algunas posiciones
        for i in range(3):
            self.manager.open_position(
                position_id=f"test_stat_{i}",
                pair="BTC/USD",
                side="buy",
                entry_price=45000.0,
                volume=0.1,
                stop_loss=44000.0,
                take_profit_1=46500.0,
                take_profit_2=48000.0,
                take_profit_3=50000.0
            )
            self.manager.close_position_partial(f"test_stat_{i}", 1, 46500.0)
        
        stats = self.manager.get_statistics()
        self.assertGreater(stats["total_trades"], 0)
        self.assertGreater(stats["win_rate"], 0)
        logger.info(f"Estadísticas: {stats}")


class TestIntegration(unittest.TestCase):
    """Pruebas de integración del sistema completo"""
    
    def test_full_trading_cycle(self):
        """Probar ciclo completo de trading"""
        # Crear datos OHLCV
        ohlcv_data = []
        for i in range(200):
            time = 1000 + i
            open_price = 100.0 + i*0.5
            high = open_price + 1.0
            low = open_price - 0.5
            close = open_price + 0.3
            volume = 1000 + i*10
            ohlcv_data.append([time, open_price, high, low, close, volume])
        
        # Generar señal
        generator = SignalGenerator()
        current_price = 200.0
        signal = generator.generate_signal(ohlcv_data, current_price)
        
        # Gestionar riesgo
        config = RiskConfig(total_capital=10000.0)
        manager = RiskManager(config)
        
        if signal:
            volume = manager.calculate_position_size(
                signal.entry_price,
                signal.stop_loss,
                signal.confidence
            )
            
            if volume > 0:
                manager.open_position(
                    position_id="integration_test",
                    pair="BTC/USD",
                    side="buy" if signal.signal_type == SignalType.BUY else "sell",
                    entry_price=signal.entry_price,
                    volume=volume,
                    stop_loss=signal.stop_loss,
                    take_profit_1=signal.take_profit_1,
                    take_profit_2=signal.take_profit_2,
                    take_profit_3=signal.take_profit_3
                )
                
                # Verificar posición abierta
                self.assertIn("integration_test", manager.positions)
                logger.info("Ciclo de trading completado exitosamente")


def run_tests():
    """Ejecutar todas las pruebas"""
    # Crear suite de pruebas
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar pruebas
    suite.addTests(loader.loadTestsFromTestCase(TestTechnicalAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestMarketDataProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestSignalGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestRiskManager))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Ejecutar pruebas
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Retornar resultado
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
