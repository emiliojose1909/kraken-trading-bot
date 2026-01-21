"""
Descargador de datos históricos de Kraken.
Obtiene datos OHLCV reales para backtesting.
"""

import os
import json
import time
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class KrakenDataDownloader:
    """
    Descargador de datos históricos de Kraken.
    Obtiene datos OHLCV sin necesidad de autenticación.
    """
    
    # URLs de Kraken
    BASE_URL = "https://api.kraken.com"
    OHLC_ENDPOINT = "/0/public/OHLC"
    
    # Timeframes disponibles (en minutos)
    TIMEFRAMES = {
        "1m": 1,
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "1h": 60,
        "4h": 240,
        "1d": 1440,
        "1w": 10080,
        "15d": 21600
    }
    
    # Límites de Kraken API
    MAX_CANDLES_PER_REQUEST = 720  # Máximo de velas por solicitud
    RATE_LIMIT_DELAY = 0.5  # Segundos entre solicitudes
    
    def __init__(self):
        """Inicializar descargador"""
        self.session = requests.Session()
        logger.info("Descargador de datos Kraken inicializado")
    
    def get_available_pairs(self) -> List[str]:
        """
        Obtener lista de pares disponibles en Kraken.
        
        Returns:
            Lista de pares (ej: ["XBTUSD", "ETHUSD"])
        """
        try:
            url = f"{self.BASE_URL}/0/public/AssetPairs"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("error"):
                logger.error(f"Error de Kraken: {data['error']}")
                return []
            
            pairs = []
            for pair_name, pair_info in data.get("result", {}).items():
                # Filtrar pares principales (USD)
                if "USD" in pair_name and not pair_name.endswith(".d"):
                    pairs.append(pair_name)
            
            return sorted(pairs)
        
        except Exception as e:
            logger.error(f"Error obteniendo pares: {e}")
            return []
    
    def download_ohlc(
        self,
        pair: str,
        timeframe: str = "5m",
        since: Optional[int] = None,
        limit: int = 720
    ) -> List[List]:
        """
        Descargar datos OHLCV de un par.
        
        Args:
            pair: Par de trading (ej: "XBTUSD")
            timeframe: Timeframe (ej: "5m", "1h", "1d")
            since: Timestamp desde el cual descargar (None = últimas velas)
            limit: Número máximo de velas a descargar
            
        Returns:
            Lista de datos OHLCV
        """
        if timeframe not in self.TIMEFRAMES:
            logger.error(f"Timeframe no válido: {timeframe}")
            return []
        
        interval = self.TIMEFRAMES[timeframe]
        ohlcv_data = []
        
        try:
            params = {
                "pair": pair,
                "interval": interval
            }
            
            if since:
                params["since"] = since
            
            logger.info(f"Descargando {limit} velas de {pair} ({timeframe})")
            
            while len(ohlcv_data) < limit:
                response = self.session.get(
                    f"{self.BASE_URL}{self.OHLC_ENDPOINT}",
                    params=params,
                    timeout=10
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data.get("error"):
                    logger.error(f"Error de Kraken: {data['error']}")
                    break
                
                result = data.get("result", {})
                
                if pair not in result:
                    logger.error(f"Par no encontrado: {pair}")
                    break
                
                candles = result[pair]
                if not candles:
                    logger.info("No hay más datos disponibles")
                    break
                
                # Agregar velas
                for candle in candles:
                    ohlcv_data.append(candle)
                    if len(ohlcv_data) >= limit:
                        break
                
                # Obtener timestamp de la última vela para la siguiente solicitud
                last_timestamp = candles[-1][0]
                
                # Verificar si hay más datos
                last_result = result.get("last")
                if not last_result or last_result == last_timestamp:
                    logger.info("Se alcanzó el final de los datos")
                    break
                
                # Actualizar since para la siguiente solicitud
                params["since"] = last_result
                
                # Respetar límite de rate
                time.sleep(self.RATE_LIMIT_DELAY)
            
            logger.info(f"Descargadas {len(ohlcv_data)} velas")
            return ohlcv_data[:limit]
        
        except Exception as e:
            logger.error(f"Error descargando datos: {e}")
            return []
    
    def download_multiple_pairs(
        self,
        pairs: List[str],
        timeframe: str = "5m",
        days: int = 30
    ) -> Dict[str, List[List]]:
        """
        Descargar datos de múltiples pares.
        
        Args:
            pairs: Lista de pares
            timeframe: Timeframe
            days: Número de días históricos a descargar
            
        Returns:
            Diccionario con datos por par
        """
        all_data = {}
        
        # Calcular número de velas basado en timeframe y días
        interval_minutes = self.TIMEFRAMES[timeframe]
        num_candles = (days * 24 * 60) // interval_minutes
        
        logger.info(f"Descargando {num_candles} velas por par para {len(pairs)} pares")
        
        for pair in pairs:
            logger.info(f"Procesando {pair}...")
            data = self.download_ohlc(pair, timeframe, limit=num_candles)
            
            if data:
                all_data[pair] = data
                logger.info(f"✓ {pair}: {len(data)} velas descargadas")
            else:
                logger.warning(f"✗ {pair}: No se obtuvieron datos")
            
            # Respetar rate limit entre pares
            time.sleep(self.RATE_LIMIT_DELAY)
        
        return all_data
    
    def save_data(self, data: Dict[str, List[List]], filename: str):
        """
        Guardar datos en archivo JSON.
        
        Args:
            data: Datos OHLCV
            filename: Nombre del archivo
        """
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Datos guardados en {filename}")
        except Exception as e:
            logger.error(f"Error guardando datos: {e}")
    
    def load_data(self, filename: str) -> Dict[str, List[List]]:
        """
        Cargar datos desde archivo JSON.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            Datos OHLCV
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            logger.info(f"Datos cargados desde {filename}")
            return data
        except Exception as e:
            logger.error(f"Error cargando datos: {e}")
            return {}
    
    def convert_to_backtester_format(
        self,
        ohlcv_data: List[List]
    ) -> List[List]:
        """
        Convertir datos de Kraken al formato del backtester.
        
        Formato Kraken: [time, open, high, low, close, vwap, volume, count]
        Formato Backtester: [time, open, high, low, close, 0, volume]
        
        Args:
            ohlcv_data: Datos en formato Kraken
            
        Returns:
            Datos en formato backtester
        """
        converted = []
        for candle in ohlcv_data:
            converted.append([
                candle[0],      # time
                float(candle[1]),  # open
                float(candle[2]),  # high
                float(candle[3]),  # low
                float(candle[4]),  # close
                0,              # unused
                float(candle[6])   # volume
            ])
        return converted


def main():
    """
    Función principal - Descargar datos de ejemplo.
    """
    downloader = KrakenDataDownloader()
    
    # Obtener pares disponibles
    logger.info("Obteniendo pares disponibles...")
    pairs = downloader.get_available_pairs()
    
    if pairs:
        logger.info(f"Pares disponibles: {len(pairs)}")
        logger.info(f"Ejemplos: {pairs[:5]}")
    else:
        logger.error("No se pudieron obtener pares")
        return
    
    # Descargar datos de pares principales
    main_pairs = ["XBTUSD", "ETHUSD", "XRPUSD"]
    
    logger.info(f"\nDescargando datos históricos de {main_pairs}...")
    
    # Descargar 30 días de datos en timeframe de 5 minutos
    data = downloader.download_multiple_pairs(
        pairs=main_pairs,
        timeframe="5m",
        days=30
    )
    
    if data:
        # Guardar datos
        downloader.save_data(data, "kraken_historical_data.json")
        
        # Mostrar resumen
        logger.info("\n=== RESUMEN DE DATOS DESCARGADOS ===")
        for pair, ohlcv_list in data.items():
            if ohlcv_list:
                first_time = datetime.fromtimestamp(ohlcv_list[0][0])
                last_time = datetime.fromtimestamp(ohlcv_list[-1][0])
                logger.info(f"{pair}: {len(ohlcv_list)} velas")
                logger.info(f"  Desde: {first_time}")
                logger.info(f"  Hasta: {last_time}")
    else:
        logger.error("No se descargaron datos")


if __name__ == "__main__":
    main()
