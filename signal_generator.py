"""
Generador de señales de trading.
Implementa lógica de generación de señales basada en indicadores técnicos.
"""

import logging
from typing import Dict, Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from technical_analysis import TechnicalIndicators, MarketDataProcessor


logger = logging.getLogger(__name__)


class SignalType(Enum):
    """Tipos de señales"""
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"


class TrendType(Enum):
    """Tipos de tendencia"""
    UPTREND = "UPTREND"
    DOWNTREND = "DOWNTREND"
    SIDEWAYS = "SIDEWAYS"


@dataclass
class TradingSignal:
    """Señal de trading generada"""
    signal_type: SignalType
    confidence: float  # 0.0 a 1.0
    entry_price: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float
    position_size_percent: float
    reasoning: str
    indicators_snapshot: Dict


class SignalGenerator:
    """
    Generador de señales de trading.
    Implementa estrategia híbrida Momentum-Reversion.
    """
    
    def __init__(
        self,
        rsi_oversold: float = 30.0,
        rsi_overbought: float = 70.0,
        adx_threshold: float = 25.0,
        volume_threshold: float = 1.1,
        min_confidence: float = 0.75
    ):
        """
        Inicializar generador de señales.
        
        Args:
            rsi_oversold: Umbral RSI para sobreventa
            rsi_overbought: Umbral RSI para sobrecompra
            adx_threshold: Umbral ADX para confirmar tendencia
            volume_threshold: Multiplicador de volumen para confirmar
            min_confidence: Confianza mínima para generar señal
        """
        self.rsi_oversold = rsi_oversold
        self.rsi_overbought = rsi_overbought
        self.adx_threshold = adx_threshold
        self.volume_threshold = volume_threshold
        self.min_confidence = min_confidence
        self.processor = MarketDataProcessor()
    
    def _get_adaptive_rsi_thresholds(self, trend: str) -> Tuple[float, float]:
        """
        Obtener umbrales RSI adaptativos según tendencia.
        
        Args:
            trend: Tipo de tendencia
            
        Returns:
            Tupla (oversold, overbought)
        """
        if trend == "UPTREND":
            return 40.0, 80.0
        elif trend == "DOWNTREND":
            return 20.0, 60.0
        else:
            return self.rsi_oversold, self.rsi_overbought
    
    def _check_trend_confirmation(
        self,
        indicators: TechnicalIndicators,
        trend: str
    ) -> bool:
        """
        Verificar confirmación de tendencia.
        
        Args:
            indicators: Indicadores técnicos
            trend: Tipo de tendencia esperada
            
        Returns:
            True si la tendencia está confirmada
        """
        if trend == "UPTREND":
            # Verificar alineación de EMAs o precio sobre EMA 200 (más flexible)
            ema_aligned = (indicators.ema_12 > indicators.ema_50) or (indicators.close > indicators.ema_200)
            # Verificar fuerza de tendencia (umbral reducido)
            trend_strong = indicators.adx_14 > (self.adx_threshold - 5.0)
            return ema_aligned and trend_strong
        
        elif trend == "DOWNTREND":
            # Verificar alineación de EMAs o precio bajo EMA 200
            ema_aligned = (indicators.ema_12 < indicators.ema_50) or (indicators.close < indicators.ema_200)
            # Verificar fuerza de tendencia
            trend_strong = indicators.adx_14 > (self.adx_threshold - 5.0)
            return ema_aligned and trend_strong
        
        return False
    
    def _check_momentum_signal(
        self,
        indicators: TechnicalIndicators,
        signal_type: SignalType
    ) -> bool:
        """
        Verificar señal de momentum.
        
        Args:
            indicators: Indicadores técnicos
            signal_type: Tipo de señal esperada
            
        Returns:
            True si hay señal de momentum
        """
        if signal_type == SignalType.BUY:
            # RSI en zona de compra (usando configuración)
            rsi_signal = indicators.rsi_14 < (self.rsi_oversold + 10.0) # Margen de +10 para ser más agresivo
            # MACD con histograma positivo o subiendo
            macd_signal = indicators.macd_histogram > 0 or (indicators.macd_histogram > indicators.macd_histogram_prev)
            return rsi_signal and macd_signal
        
        elif signal_type == SignalType.SELL:
            # RSI en zona de venta (usando configuración)
            rsi_signal = indicators.rsi_14 > (self.rsi_overbought - 10.0) # Margen de -10
            # MACD con histograma negativo o bajando
            macd_signal = indicators.macd_histogram < 0 or (indicators.macd_histogram < indicators.macd_histogram_prev)
            return rsi_signal and macd_signal
        
        return False
    
    def _check_bollinger_bands_signal(
        self,
        indicators: TechnicalIndicators,
        current_price: float,
        signal_type: SignalType
    ) -> bool:
        """
        Verificar señal de Bandas de Bollinger.
        
        Args:
            indicators: Indicadores técnicos
            current_price: Precio actual
            signal_type: Tipo de señal esperada
            
        Returns:
            True si hay señal de BB
        """
        if signal_type == SignalType.BUY:
            # Precio cerca de banda inferior
            bb_range = indicators.bb_upper - indicators.bb_lower
            distance_to_lower = current_price - indicators.bb_lower
            return distance_to_lower < bb_range * 0.2
        
        elif signal_type == SignalType.SELL:
            # Precio cerca de banda superior
            bb_range = indicators.bb_upper - indicators.bb_lower
            distance_to_upper = indicators.bb_upper - current_price
            return distance_to_upper < bb_range * 0.2
        
        return False
    
    def _check_volume_confirmation(
        self,
        indicators: TechnicalIndicators
    ) -> bool:
        """
        Verificar confirmación de volumen.
        
        Args:
            indicators: Indicadores técnicos
            
        Returns:
            True si el volumen confirma la señal
        """
        return indicators.current_volume > indicators.volume_ma * self.volume_threshold
    
    def _calculate_position_size(
        self,
        confidence: float,
        max_position_size: float = 0.10
    ) -> float:
        """
        Calcular tamaño de posición basado en confianza.
        
        Args:
            confidence: Confianza de la señal (0.0-1.0)
            max_position_size: Tamaño máximo de posición
            
        Returns:
            Tamaño de posición como porcentaje del capital
        """
        return max_position_size * confidence
    
    def generate_signal(
        self,
        ohlcv_data: list,
        current_price: float,
        atr_multiplier: float = 2.0
    ) -> Optional[TradingSignal]:
        """
        Generar señal de trading.
        
        Args:
            ohlcv_data: Datos OHLCV
            current_price: Precio actual
            atr_multiplier: Multiplicador para stops dinámicos
            
        Returns:
            TradingSignal si se genera señal, None si no hay señal
        """
        # Procesar datos y calcular indicadores
        indicators = self.processor.process_ohlcv(ohlcv_data)
        if indicators is None:
            logger.warning("No se pudieron calcular indicadores")
            return None
        
        # Determinar tendencia
        trend = self.processor.get_trend(indicators)
        
        # Intentar generar señal de compra
        if trend == "UPTREND":
            buy_signal = self._generate_buy_signal(
                indicators, current_price, atr_multiplier
            )
            if buy_signal and buy_signal.confidence >= self.min_confidence:
                return buy_signal
        
        # Intentar generar señal de venta
        elif trend == "DOWNTREND":
            sell_signal = self._generate_sell_signal(
                indicators, current_price, atr_multiplier
            )
            if sell_signal and sell_signal.confidence >= self.min_confidence:
                return sell_signal
        
        return None
    
    def _generate_buy_signal(
        self,
        indicators: TechnicalIndicators,
        current_price: float,
        atr_multiplier: float
    ) -> Optional[TradingSignal]:
        """
        Generar señal de compra.
        
        Args:
            indicators: Indicadores técnicos
            current_price: Precio actual
            atr_multiplier: Multiplicador para stops
            
        Returns:
            TradingSignal o None
        """
        confidence_score = 0.0
        reasoning_parts = []
        
        # Verificar confirmación de tendencia (peso: 30%)
        if self._check_trend_confirmation(indicators, "UPTREND"):
            confidence_score += 0.30
            reasoning_parts.append("Tendencia alcista confirmada")
        else:
            return None
        
        # Verificar señal de momentum (peso: 30%)
        if self._check_momentum_signal(indicators, SignalType.BUY):
            confidence_score += 0.30
            reasoning_parts.append("Señal de momentum alcista")
        else:
            return None
        
        # Verificar Bandas de Bollinger (peso: 20%)
        if self._check_bollinger_bands_signal(indicators, current_price, SignalType.BUY):
            confidence_score += 0.20
            reasoning_parts.append("Precio en banda inferior de Bollinger")
        
        # Verificar volumen (peso: 20%)
        if self._check_volume_confirmation(indicators):
            confidence_score += 0.20
            reasoning_parts.append("Volumen confirmado")
        
        if confidence_score < self.min_confidence:
            return None
        
        # Calcular stops y targets
        stop_loss = current_price - (indicators.atr_14 * atr_multiplier)
        
        # Take profits escalonados
        tp1 = current_price + (indicators.atr_14 * 1.5)
        tp2 = current_price + (indicators.atr_14 * 2.5)
        tp3 = current_price + (indicators.atr_14 * 4.0)
        
        position_size = self._calculate_position_size(confidence_score)
        
        return TradingSignal(
            signal_type=SignalType.BUY,
            confidence=confidence_score,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit_1=tp1,
            take_profit_2=tp2,
            take_profit_3=tp3,
            position_size_percent=position_size,
            reasoning="; ".join(reasoning_parts),
            indicators_snapshot={
                "ema_12": indicators.ema_12,
                "ema_50": indicators.ema_50,
                "ema_200": indicators.ema_200,
                "rsi_14": indicators.rsi_14,
                "macd": indicators.macd,
                "atr_14": indicators.atr_14,
                "adx_14": indicators.adx_14
            }
        )
    
    def _generate_sell_signal(
        self,
        indicators: TechnicalIndicators,
        current_price: float,
        atr_multiplier: float
    ) -> Optional[TradingSignal]:
        """
        Generar señal de venta.
        
        Args:
            indicators: Indicadores técnicos
            current_price: Precio actual
            atr_multiplier: Multiplicador para stops
            
        Returns:
            TradingSignal o None
        """
        confidence_score = 0.0
        reasoning_parts = []
        
        # Verificar confirmación de tendencia (peso: 30%)
        if self._check_trend_confirmation(indicators, "DOWNTREND"):
            confidence_score += 0.30
            reasoning_parts.append("Tendencia bajista confirmada")
        else:
            return None
        
        # Verificar señal de momentum (peso: 30%)
        if self._check_momentum_signal(indicators, SignalType.SELL):
            confidence_score += 0.30
            reasoning_parts.append("Señal de momentum bajista")
        else:
            return None
        
        # Verificar Bandas de Bollinger (peso: 20%)
        if self._check_bollinger_bands_signal(indicators, current_price, SignalType.SELL):
            confidence_score += 0.20
            reasoning_parts.append("Precio en banda superior de Bollinger")
        
        # Verificar volumen (peso: 20%)
        if self._check_volume_confirmation(indicators):
            confidence_score += 0.20
            reasoning_parts.append("Volumen confirmado")
        
        if confidence_score < self.min_confidence:
            return None
        
        # Calcular stops y targets
        stop_loss = current_price + (indicators.atr_14 * atr_multiplier)
        
        # Take profits escalonados
        tp1 = current_price - (indicators.atr_14 * 1.5)
        tp2 = current_price - (indicators.atr_14 * 2.5)
        tp3 = current_price - (indicators.atr_14 * 4.0)
        
        position_size = self._calculate_position_size(confidence_score)
        
        return TradingSignal(
            signal_type=SignalType.SELL,
            confidence=confidence_score,
            entry_price=current_price,
            stop_loss=stop_loss,
            take_profit_1=tp1,
            take_profit_2=tp2,
            take_profit_3=tp3,
            position_size_percent=position_size,
            reasoning="; ".join(reasoning_parts),
            indicators_snapshot={
                "ema_12": indicators.ema_12,
                "ema_50": indicators.ema_50,
                "ema_200": indicators.ema_200,
                "rsi_14": indicators.rsi_14,
                "macd": indicators.macd,
                "atr_14": indicators.atr_14,
                "adx_14": indicators.adx_14
            }
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Ejemplo de uso
    generator = SignalGenerator()
    
    # Datos de ejemplo
    example_data = [
        [1000 + i, 100 + i*0.05, 101 + i*0.05, 99 + i*0.05, 100.5 + i*0.05, 1000 + i*10]
        for i in range(200)
    ]
    
    signal = generator.generate_signal(example_data, 110.0)
    
    if signal:
        logger.info(f"Señal: {signal.signal_type.value}")
        logger.info(f"Confianza: {signal.confidence:.2%}")
        logger.info(f"Entrada: {signal.entry_price:.2f}")
        logger.info(f"Stop Loss: {signal.stop_loss:.2f}")
        logger.info(f"TP1: {signal.take_profit_1:.2f}")
        logger.info(f"TP2: {signal.take_profit_2:.2f}")
        logger.info(f"TP3: {signal.take_profit_3:.2f}")
        logger.info(f"Razón: {signal.reasoning}")
    else:
        logger.info("No se generó señal")
