"""
Bot principal de trading para Kraken.
Orquesta todas las capas del sistema.
"""

import os
import sys
import json
import time
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from pathlib import Path

from kraken_client import KrakenClient, KrakenConfig
from technical_analysis import MarketDataProcessor, TechnicalIndicators
from signal_generator import SignalGenerator, SignalType
from risk_manager import RiskManager, RiskConfig


# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TradingBot:
    """
    Bot principal de trading.
    Orquesta todas las capas: cliente API, análisis técnico, generación de señales, gestión de riesgos.
    """
    
    def __init__(self, config_file: str = "bot_config.json"):
        """
        Inicializar bot de trading.
        
        Args:
            config_file: Ruta del archivo de configuración
        """
        self.config = self._load_config(config_file)
        
        # Inicializar componentes
        self.kraken_client = self._init_kraken_client()
        self.signal_generator = SignalGenerator(
            rsi_oversold=self.config.get("rsi_oversold", 30.0),
            rsi_overbought=self.config.get("rsi_overbought", 70.0),
            adx_threshold=self.config.get("adx_threshold", 25.0),
            volume_threshold=self.config.get("volume_threshold", 1.1),
            min_confidence=self.config.get("min_confidence", 0.75)
        )
        
        risk_config = RiskConfig(
            total_capital=self.config.get("total_capital", 10000.0),
            risk_per_trade=self.config.get("risk_per_trade", 0.02),
            max_positions=self.config.get("max_positions", 5),
            max_position_size=self.config.get("max_position_size", 0.10),
            max_drawdown=self.config.get("max_drawdown", 0.15)
        )
        self.risk_manager = RiskManager(risk_config)
        
        # Estado del bot
        self.is_running = False
        self.last_signal_time = {}
        self.min_signal_interval = self.config.get("min_signal_interval_minutes", 5) * 60
        
        logger.info("Bot de trading inicializado")
    
    def _load_config(self, config_file: str) -> Dict:
        """
        Cargar configuración desde archivo JSON.
        
        Args:
            config_file: Ruta del archivo de configuración
            
        Returns:
            Diccionario con configuración
        """
        if not os.path.exists(config_file):
            logger.warning(f"Archivo de configuración no encontrado: {config_file}")
            return self._get_default_config()
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        logger.info(f"Configuración cargada desde {config_file}")
        return config
    
    def _get_default_config(self) -> Dict:
        """
        Obtener configuración por defecto.
        
        Returns:
            Diccionario con configuración por defecto
        """
        return {
            "trading_pairs": ["XBTUSD", "ETHUSD"],
            "timeframe_minutes": 5,
            "total_capital": 10000.0,
            "risk_per_trade": 0.02,
            "max_positions": 5,
            "max_position_size": 0.10,
            "max_drawdown": 0.15,
            "rsi_oversold": 30.0,
            "rsi_overbought": 70.0,
            "adx_threshold": 25.0,
            "volume_threshold": 1.1,
            "min_confidence": 0.75,
            "min_signal_interval_minutes": 5,
            "atr_multiplier": 2.0,
            "paper_trading": True
        }
    
    def _init_kraken_client(self) -> KrakenClient:
        """
        Inicializar cliente de Kraken.
        
        Returns:
            Cliente de Kraken
        """
        api_key = os.getenv("KRAKEN_API_KEY")
        api_secret = os.getenv("KRAKEN_API_SECRET")
        
        if not api_key or not api_secret:
            logger.error("Credenciales de Kraken no encontradas")
            raise ValueError(
                "Configure KRAKEN_API_KEY y KRAKEN_API_SECRET como variables de entorno"
            )
        
        config = KrakenConfig(
            api_key=api_key,
            api_secret=api_secret
        )
        
        return KrakenClient(config)
    
    def start(self):
        """
        Iniciar el bot de trading.
        """
        self.is_running = True
        logger.info("Bot iniciado")
        
        try:
            # Verificar conexión
            server_time = self.kraken_client.get_server_time()
            logger.info(f"Conexión establecida. Tiempo del servidor: {server_time}")
            
            # Obtener saldo inicial
            balance = self.kraken_client.get_account_balance()
            logger.info(f"Saldo inicial: {balance}")
            
            # Loop principal
            while self.is_running:
                try:
                    self._trading_cycle()
                    time.sleep(60)  # Esperar 1 minuto antes del siguiente ciclo
                except Exception as e:
                    logger.error(f"Error en ciclo de trading: {e}", exc_info=True)
                    time.sleep(60)
        
        except KeyboardInterrupt:
            logger.info("Bot interrumpido por usuario")
        except Exception as e:
            logger.error(f"Error fatal: {e}", exc_info=True)
        finally:
            self.stop()
    
    def stop(self):
        """
        Detener el bot de trading.
        """
        self.is_running = False
        logger.info("Deteniendo bot...")
        
        # Cancelar todas las órdenes
        try:
            self.kraken_client.cancel_all_orders()
            logger.info("Todas las órdenes canceladas")
        except Exception as e:
            logger.error(f"Error al cancelar órdenes: {e}")
        
        # Generar reporte final
        self._generate_report()
        
        # Cerrar cliente
        self.kraken_client.close()
        logger.info("Bot detenido")
    
    def _trading_cycle(self):
        """
        Ejecutar un ciclo de trading.
        """
        logger.debug("Iniciando ciclo de trading")
        
        # Procesar cada par de trading
        for pair in self.config.get("trading_pairs", []):
            try:
                self._process_pair(pair)
            except Exception as e:
                logger.error(f"Error procesando {pair}: {e}", exc_info=True)
        
        # Monitorear posiciones abiertas
        self._monitor_positions()
    
    def _process_pair(self, pair: str):
        """
        Procesar un par de trading.
        
        Args:
            pair: Par de trading (ej: XBTUSD)
        """
        # Obtener datos OHLCV
        try:
            ohlcv_data = self._fetch_ohlcv(pair)
            if not ohlcv_data:
                logger.warning(f"No se obtuvieron datos para {pair}")
                return
            
            # Obtener precio actual
            ticker = self.kraken_client.get_ticker(pair)
            current_price = float(ticker[pair]["c"][0])
            
            # Generar señal
            signal = self.signal_generator.generate_signal(
                ohlcv_data,
                current_price,
                atr_multiplier=self.config.get("atr_multiplier", 2.0)
            )
            
            if signal:
                self._handle_signal(pair, signal, current_price)
        
        except Exception as e:
            logger.error(f"Error procesando {pair}: {e}")
    
    def _fetch_ohlcv(self, pair: str) -> Optional[List]:
        """
        Obtener datos OHLCV para un par.
        
        Args:
            pair: Par de trading
            
        Returns:
            Lista de datos OHLCV o None
        """
        try:
            # Obtener datos OHLC de 5 minutos
            ohlc_data = self.kraken_client.get_ohlc(pair, interval=5)
            
            if pair not in ohlc_data:
                return None
            
            # Convertir a formato esperado [time, open, high, low, close, volume]
            ohlcv_list = []
            for candle in ohlc_data[pair]:
                ohlcv_list.append([
                    candle[0],  # time
                    float(candle[1]),  # open
                    float(candle[2]),  # high
                    float(candle[3]),  # low
                    float(candle[4]),  # close
                    float(candle[6])   # volume
                ])
            
            return ohlcv_list
        
        except Exception as e:
            logger.error(f"Error obteniendo OHLCV para {pair}: {e}")
            return None
    
    def _handle_signal(self, pair: str, signal, current_price: float):
        """
        Manejar una señal de trading.
        
        Args:
            pair: Par de trading
            signal: Señal generada
            current_price: Precio actual
        """
        # Verificar intervalo mínimo entre señales
        last_time = self.last_signal_time.get(pair, 0)
        if time.time() - last_time < self.min_signal_interval:
            logger.debug(f"Intervalo mínimo no alcanzado para {pair}")
            return
        
        if signal.signal_type == SignalType.BUY:
            self._execute_buy_signal(pair, signal, current_price)
        elif signal.signal_type == SignalType.SELL:
            self._execute_sell_signal(pair, signal, current_price)
        
        self.last_signal_time[pair] = time.time()
    
    def _execute_buy_signal(self, pair: str, signal, current_price: float):
        """
        Ejecutar señal de compra.
        
        Args:
            pair: Par de trading
            signal: Señal de compra
            current_price: Precio actual
        """
        logger.info(
            f"Señal de COMPRA para {pair}: Confianza {signal.confidence:.2%}, "
            f"Precio: {current_price:.2f}"
        )
        
        # Calcular tamaño de posición
        volume = self.risk_manager.calculate_position_size(
            signal.entry_price,
            signal.stop_loss,
            signal.confidence
        )
        
        if volume <= 0:
            logger.warning(f"Volumen inválido para {pair}: {volume}")
            return
        
        # Abrir posición
        position_id = f"{pair}_{int(time.time())}"
        
        if self.config.get("paper_trading", True):
            # Paper trading - simular
            self.risk_manager.open_position(
                position_id=position_id,
                pair=pair,
                side="buy",
                entry_price=signal.entry_price,
                volume=volume,
                stop_loss=signal.stop_loss,
                take_profit_1=signal.take_profit_1,
                take_profit_2=signal.take_profit_2,
                take_profit_3=signal.take_profit_3
            )
            logger.info(f"Posición de COMPRA simulada: {position_id}")
        else:
            # Trading real
            try:
                result = self.kraken_client.add_order(
                    pair=pair,
                    side="buy",
                    ordertype="limit",
                    volume=volume,
                    price=signal.entry_price
                )
                logger.info(f"Orden de COMPRA ejecutada: {result}")
            except Exception as e:
                logger.error(f"Error ejecutando orden de compra: {e}")
    
    def _execute_sell_signal(self, pair: str, signal, current_price: float):
        """
        Ejecutar señal de venta.
        
        Args:
            pair: Par de trading
            signal: Señal de venta
            current_price: Precio actual
        """
        logger.info(
            f"Señal de VENTA para {pair}: Confianza {signal.confidence:.2%}, "
            f"Precio: {current_price:.2f}"
        )
        
        # Calcular tamaño de posición
        volume = self.risk_manager.calculate_position_size(
            signal.entry_price,
            signal.stop_loss,
            signal.confidence
        )
        
        if volume <= 0:
            logger.warning(f"Volumen inválido para {pair}: {volume}")
            return
        
        # Abrir posición
        position_id = f"{pair}_{int(time.time())}"
        
        if self.config.get("paper_trading", True):
            # Paper trading - simular
            self.risk_manager.open_position(
                position_id=position_id,
                pair=pair,
                side="sell",
                entry_price=signal.entry_price,
                volume=volume,
                stop_loss=signal.stop_loss,
                take_profit_1=signal.take_profit_1,
                take_profit_2=signal.take_profit_2,
                take_profit_3=signal.take_profit_3
            )
            logger.info(f"Posición de VENTA simulada: {position_id}")
        else:
            # Trading real
            try:
                result = self.kraken_client.add_order(
                    pair=pair,
                    side="sell",
                    ordertype="limit",
                    volume=volume,
                    price=signal.entry_price
                )
                logger.info(f"Orden de VENTA ejecutada: {result}")
            except Exception as e:
                logger.error(f"Error ejecutando orden de venta: {e}")
    
    def _monitor_positions(self):
        """
        Monitorear posiciones abiertas.
        """
        if not self.risk_manager.positions:
            return
        
        for position_id, position in list(self.risk_manager.positions.items()):
            try:
                # Obtener precio actual
                ticker = self.kraken_client.get_ticker(position.pair)
                current_price = float(ticker[position.pair]["c"][0])
                
                # Actualizar precio
                self.risk_manager.update_position_price(position_id, current_price)
                
                # Verificar stop loss
                if self.risk_manager.check_stop_loss(position_id, current_price):
                    self.risk_manager.close_position_stop_loss(position_id, current_price)
                    logger.warning(f"Stop loss ejecutado: {position_id}")
                
                # Verificar take profit
                tp_level, reached = self.risk_manager.check_take_profit(position_id, current_price)
                if reached:
                    self.risk_manager.close_position_partial(position_id, tp_level, current_price)
                    logger.info(f"Take profit {tp_level} ejecutado: {position_id}")
            
            except Exception as e:
                logger.error(f"Error monitoreando posición {position_id}: {e}")
    
    def _generate_report(self):
        """
        Generar reporte de trading.
        """
        stats = self.risk_manager.get_statistics()
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "statistics": stats,
            "positions": [
                {
                    "id": p.position_id,
                    "pair": p.pair,
                    "side": p.side,
                    "entry_price": p.entry_price,
                    "volume": p.volume,
                    "entry_time": p.entry_time.isoformat(),
                    "status": p.status.value,
                    "realized_pnl": p.realized_pnl
                }
                for p in self.risk_manager.closed_positions[-10:]  # Últimas 10 posiciones
            ]
        }
        
        report_file = "trading_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Reporte guardado en {report_file}")
        logger.info(f"Estadísticas finales: {stats}")


def main():
    """
    Función principal.
    """
    try:
        bot = TradingBot()
        bot.start()
    except KeyboardInterrupt:
        logger.info("Bot interrumpido")
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
