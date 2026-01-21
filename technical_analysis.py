"""
Capa de análisis técnico.
Calcula indicadores técnicos para generación de señales.
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


logger = logging.getLogger(__name__)


@dataclass
class TechnicalIndicators:
    """Contenedor para indicadores técnicos calculados"""
    ema_12: float
    ema_50: float
    ema_200: float
    rsi_14: float
    macd: float
    macd_signal: float
    macd_histogram: float
    bb_upper: float
    bb_middle: float
    bb_lower: float
    atr_14: float
    adx_14: float
    volume_ma: float
    current_volume: float


class TechnicalAnalysis:
    """
    Calculador de indicadores técnicos.
    Implementa indicadores estándar de trading.
    """
    
    @staticmethod
    def calculate_ema(data: np.ndarray, period: int) -> np.ndarray:
        """
        Calcular Media Móvil Exponencial (EMA).
        
        Args:
            data: Array de precios
            period: Período de la EMA
            
        Returns:
            Array con valores de EMA
        """
        if len(data) < period:
            return np.full_like(data, np.nan)
        
        ema = np.zeros_like(data)
        multiplier = 2.0 / (period + 1)
        
        # SMA inicial
        ema[:period] = np.mean(data[:period])
        
        # EMA
        for i in range(period, len(data)):
            ema[i] = (data[i] * multiplier) + (ema[i-1] * (1 - multiplier))
        
        return ema
    
    @staticmethod
    def calculate_sma(data: np.ndarray, period: int) -> np.ndarray:
        """
        Calcular Media Móvil Simple (SMA).
        
        Args:
            data: Array de precios
            period: Período de la SMA
            
        Returns:
            Array con valores de SMA
        """
        if len(data) < period:
            return np.full_like(data, np.nan)
        
        return pd.Series(data).rolling(window=period).mean().values
    
    @staticmethod
    def calculate_rsi(data: np.ndarray, period: int = 14) -> np.ndarray:
        """
        Calcular Índice de Fuerza Relativa (RSI).
        
        Args:
            data: Array de precios
            period: Período del RSI
            
        Returns:
            Array con valores de RSI (0-100)
        """
        if len(data) < period + 1:
            return np.full_like(data, np.nan)
        
        deltas = np.diff(data)
        seed = deltas[:period+1]
        
        up = seed[seed >= 0].sum() / period
        down = -seed[seed < 0].sum() / period
        
        rs = up / down if down != 0 else 0
        rsi = np.zeros_like(data)
        rsi[:period] = 100.0 - 100.0 / (1.0 + rs)
        
        for i in range(period, len(data)):
            delta = deltas[i-1]
            
            if delta > 0:
                upval = delta
                downval = 0.0
            else:
                upval = 0.0
                downval = -delta
            
            up = (up * (period - 1) + upval) / period
            down = (down * (period - 1) + downval) / period
            
            rs = up / down if down != 0 else 0
            rsi[i] = 100.0 - 100.0 / (1.0 + rs)
        
        return rsi
    
    @staticmethod
    def calculate_macd(
        data: np.ndarray,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calcular MACD (Moving Average Convergence Divergence).
        
        Args:
            data: Array de precios
            fast: Período EMA rápida
            slow: Período EMA lenta
            signal: Período línea de señal
            
        Returns:
            Tupla (MACD, Signal Line, Histogram)
        """
        ema_fast = TechnicalAnalysis.calculate_ema(data, fast)
        ema_slow = TechnicalAnalysis.calculate_ema(data, slow)
        
        macd = ema_fast - ema_slow
        signal_line = TechnicalAnalysis.calculate_ema(macd, signal)
        histogram = macd - signal_line
        
        return macd, signal_line, histogram
    
    @staticmethod
    def calculate_bollinger_bands(
        data: np.ndarray,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calcular Bandas de Bollinger.
        
        Args:
            data: Array de precios
            period: Período de la media móvil
            std_dev: Número de desviaciones estándar
            
        Returns:
            Tupla (Upper Band, Middle Band, Lower Band)
        """
        middle = TechnicalAnalysis.calculate_sma(data, period)
        
        std = pd.Series(data).rolling(window=period).std().values
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return upper, middle, lower
    
    @staticmethod
    def calculate_atr(
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        period: int = 14
    ) -> np.ndarray:
        """
        Calcular Average True Range (ATR).
        
        Args:
            high: Array de máximos
            low: Array de mínimos
            close: Array de cierres
            period: Período del ATR
            
        Returns:
            Array con valores de ATR
        """
        if len(high) < period:
            return np.full_like(high, np.nan)
        
        # Calcular True Range
        tr1 = high - low
        tr2 = np.abs(high - np.roll(close, 1))
        tr3 = np.abs(low - np.roll(close, 1))
        
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        tr[0] = tr1[0]
        
        # ATR es SMA del TR
        atr = TechnicalAnalysis.calculate_sma(tr, period)
        
        return atr
    
    @staticmethod
    def calculate_adx(
        high: np.ndarray,
        low: np.ndarray,
        close: np.ndarray,
        period: int = 14
    ) -> np.ndarray:
        """
        Calcular Average Directional Index (ADX).
        
        Args:
            high: Array de máximos
            low: Array de mínimos
            close: Array de cierres
            period: Período del ADX
            
        Returns:
            Array con valores de ADX (0-100)
        """
        if len(high) < period * 2:
            return np.full_like(high, np.nan)
        
        # Calcular movimientos direccionales
        up_move = high[1:] - high[:-1]
        down_move = low[:-1] - low[1:]
        
        pos_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        neg_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        # Calcular ATR
        tr1 = high[1:] - low[1:]
        tr2 = np.abs(high[1:] - close[:-1])
        tr3 = np.abs(low[1:] - close[:-1])
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        
        # Calcular DI+, DI-
        di_plus = 100 * TechnicalAnalysis.calculate_sma(pos_dm, period) / TechnicalAnalysis.calculate_sma(tr, period)
        di_minus = 100 * TechnicalAnalysis.calculate_sma(neg_dm, period) / TechnicalAnalysis.calculate_sma(tr, period)
        
        # Calcular DX
        dx = 100 * np.abs(di_plus - di_minus) / (di_plus + di_minus + 1e-10)
        
        # ADX es SMA del DX
        adx = TechnicalAnalysis.calculate_sma(dx, period)
        
        return adx
    
    @staticmethod
    def analyze_candle(
        open_price: float,
        high: float,
        low: float,
        close: float,
        volume: float
    ) -> Dict[str, any]:
        """
        Analizar una vela individual.
        
        Args:
            open_price: Precio de apertura
            high: Máximo
            low: Mínimo
            close: Cierre
            volume: Volumen
            
        Returns:
            Diccionario con análisis de la vela
        """
        body = abs(close - open_price)
        upper_wick = high - max(open_price, close)
        lower_wick = min(open_price, close) - low
        
        is_bullish = close > open_price
        is_bearish = close < open_price
        is_doji = body < (high - low) * 0.1
        
        return {
            "is_bullish": is_bullish,
            "is_bearish": is_bearish,
            "is_doji": is_doji,
            "body": body,
            "upper_wick": upper_wick,
            "lower_wick": lower_wick,
            "range": high - low,
            "close_position": (close - low) / (high - low) if high != low else 0.5
        }


class MarketDataProcessor:
    """
    Procesador de datos de mercado.
    Convierte datos OHLCV en indicadores técnicos.
    """
    
    def __init__(self, min_candles: int = 200):
        """
        Inicializar procesador.
        
        Args:
            min_candles: Mínimo de velas requeridas para análisis
        """
        self.min_candles = min_candles
        self.ta = TechnicalAnalysis()
    
    def process_ohlcv(self, ohlcv_data: List[List[float]]) -> Optional[TechnicalIndicators]:
        """
        Procesar datos OHLCV y calcular indicadores.
        
        Args:
            ohlcv_data: Lista de [time, open, high, low, close, volume]
            
        Returns:
            TechnicalIndicators con todos los indicadores calculados
        """
        if len(ohlcv_data) < self.min_candles:
            logger.warning(f"Datos insuficientes: {len(ohlcv_data)} < {self.min_candles}")
            return None
        
        # Convertir a arrays numpy
        data = np.array(ohlcv_data)
        close = data[:, 4].astype(float)
        high = data[:, 3].astype(float)
        low = data[:, 2].astype(float)
        volume = data[:, 5].astype(float)
        
        # Calcular indicadores
        ema_12 = self.ta.calculate_ema(close, 12)[-1]
        ema_50 = self.ta.calculate_ema(close, 50)[-1]
        ema_200 = self.ta.calculate_ema(close, 200)[-1]
        
        rsi_14 = self.ta.calculate_rsi(close, 14)[-1]
        
        macd, macd_signal, macd_histogram = self.ta.calculate_macd(close)
        
        bb_upper, bb_middle, bb_lower = self.ta.calculate_bollinger_bands(close)
        
        atr_14 = self.ta.calculate_atr(high, low, close, 14)[-1]
        
        adx_14 = self.ta.calculate_adx(high, low, close, 14)[-1]
        
        volume_ma = self.ta.calculate_sma(volume, 50)[-1]
        current_volume = volume[-1]
        
        return TechnicalIndicators(
            ema_12=ema_12,
            ema_50=ema_50,
            ema_200=ema_200,
            rsi_14=rsi_14,
            macd=macd[-1],
            macd_signal=macd_signal[-1],
            macd_histogram=macd_histogram[-1],
            bb_upper=bb_upper[-1],
            bb_middle=bb_middle[-1],
            bb_lower=bb_lower[-1],
            atr_14=atr_14,
            adx_14=adx_14,
            volume_ma=volume_ma,
            current_volume=current_volume
        )
    
    def get_trend(self, indicators: TechnicalIndicators) -> str:
        """
        Determinar tendencia actual.
        
        Args:
            indicators: Indicadores técnicos
            
        Returns:
            "UPTREND", "DOWNTREND", o "SIDEWAYS"
        """
        if indicators.ema_12 > indicators.ema_50 > indicators.ema_200:
            return "UPTREND"
        elif indicators.ema_12 < indicators.ema_50 < indicators.ema_200:
            return "DOWNTREND"
        else:
            return "SIDEWAYS"
    
    def get_trend_strength(self, indicators: TechnicalIndicators) -> str:
        """
        Determinar fuerza de tendencia.
        
        Args:
            indicators: Indicadores técnicos
            
        Returns:
            "STRONG", "MODERATE", o "WEAK"
        """
        if indicators.adx_14 > 25:
            return "STRONG"
        elif indicators.adx_14 > 20:
            return "MODERATE"
        else:
            return "WEAK"


if __name__ == "__main__":
    # Ejemplo de uso
    logging.basicConfig(level=logging.INFO)
    
    # Datos de ejemplo (OHLCV)
    example_data = [
        [1000 + i, 100 + i*0.1, 101 + i*0.1, 99 + i*0.1, 100.5 + i*0.1, 1000 + i*10]
        for i in range(200)
    ]
    
    processor = MarketDataProcessor()
    indicators = processor.process_ohlcv(example_data)
    
    if indicators:
        logger.info(f"EMA 12: {indicators.ema_12:.2f}")
        logger.info(f"EMA 50: {indicators.ema_50:.2f}")
        logger.info(f"RSI 14: {indicators.rsi_14:.2f}")
        logger.info(f"MACD: {indicators.macd:.4f}")
        logger.info(f"ATR 14: {indicators.atr_14:.2f}")
        logger.info(f"ADX 14: {indicators.adx_14:.2f}")
        
        trend = processor.get_trend(indicators)
        strength = processor.get_trend_strength(indicators)
        logger.info(f"Tendencia: {trend} ({strength})")
