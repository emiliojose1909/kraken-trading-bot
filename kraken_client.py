"""
Cliente REST de Kraken con autenticación segura.
Implementa comunicación con Kraken API para trading.
"""

import os
import json
import time
import hmac
import hashlib
import base64
import logging
import urllib.parse
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Tipos de órdenes soportadas"""
    MARKET = "market"
    LIMIT = "limit"
    STOP_LOSS = "stop-loss"
    TAKE_PROFIT = "take-profit"


class OrderSide(Enum):
    """Lados de la orden"""
    BUY = "buy"
    SELL = "sell"


@dataclass
class KrakenConfig:
    """Configuración de Kraken"""
    api_key: str
    api_secret: str
    api_url: str = "https://api.kraken.com"
    timeout: int = 30
    max_retries: int = 3
    retry_delay: float = 1.0


class KrakenClient:
    """
    Cliente REST para Kraken API.
    Maneja autenticación, reintentos y gestión de errores.
    """
    
    def __init__(self, config: KrakenConfig):
        """
        Inicializar cliente de Kraken.
        
        Args:
            config: Configuración de Kraken
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'KrakenTradingBot/1.0'
        })
        self._nonce_counter = int(time.time() * 1000)
        logger.info("Cliente Kraken inicializado")
    
    def _get_nonce(self) -> int:
        """
        Generar nonce siempre creciente.
        
        Returns:
            Nonce como entero de 64 bits
        """
        self._nonce_counter = max(self._nonce_counter + 1, int(time.time() * 1000))
        return self._nonce_counter
    
    def _get_kraken_signature(self, urlpath: str, data: Dict[str, Any], secret: str) -> str:
        """
        Generar firma HMAC-SHA512 para autenticación.
        
        Args:
            urlpath: Ruta del endpoint (ej: /0/private/AddOrder)
            data: Datos de la solicitud
            secret: Clave privada API
            
        Returns:
            Firma en base64
        """
        postdata = urllib.parse.urlencode(data)
        encoded = (str(data["nonce"]) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        
        signature = hmac.new(
            base64.b64decode(secret),
            message,
            hashlib.sha512
        )
        sigdigest = base64.b64encode(signature.digest())
        return sigdigest.decode()
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        private: bool = False,
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Realizar solicitud a Kraken API.
        
        Args:
            method: Método HTTP (GET, POST)
            endpoint: Endpoint de la API
            params: Parámetros de la solicitud
            private: Si es endpoint privado (requiere autenticación)
            retry_count: Contador de reintentos
            
        Returns:
            Respuesta JSON de Kraken
            
        Raises:
            Exception: Si la solicitud falla después de reintentos
        """
        url = f"{self.config.api_url}{endpoint}"
        headers = {}
        
        if private:
            if params is None:
                params = {}
            
            params["nonce"] = self._get_nonce()
            
            # Generar firma
            signature = self._get_kraken_signature(
                endpoint,
                params,
                self.config.api_secret
            )
            
            headers["API-Key"] = self.config.api_key
            headers["API-Sign"] = signature
        
        try:
            if method == "GET":
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.config.timeout
                )
            else:  # POST
                response = self.session.post(
                    url,
                    data=params,
                    headers=headers,
                    timeout=self.config.timeout
                )
            
            response.raise_for_status()
            result = response.json()
            
            # Verificar errores en respuesta
            if result.get("error"):
                error_msg = ", ".join(result["error"])
                logger.error(f"Error de Kraken: {error_msg}")
                
                # Reintentar si es error temporal
                if "EAPI:Rate limit exceeded" in error_msg and retry_count < self.config.max_retries:
                    wait_time = self.config.retry_delay * (2 ** retry_count)
                    logger.warning(f"Rate limit, reintentando en {wait_time}s...")
                    time.sleep(wait_time)
                    return self._request(method, endpoint, params, private, retry_count + 1)
                
                raise Exception(f"Error de Kraken API: {error_msg}")
            
            return result.get("result", {})
        
        except requests.exceptions.RequestException as e:
            if retry_count < self.config.max_retries:
                wait_time = self.config.retry_delay * (2 ** retry_count)
                logger.warning(f"Error de conexión: {e}, reintentando en {wait_time}s...")
                time.sleep(wait_time)
                return self._request(method, endpoint, params, private, retry_count + 1)
            
            logger.error(f"Error de solicitud después de {self.config.max_retries} reintentos: {e}")
            raise
    
    # ==================== Market Data Endpoints ====================
    
    def get_server_time(self) -> Dict[str, Any]:
        """Obtener tiempo del servidor"""
        return self._request("GET", "/0/public/Time")
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obtener estado del sistema"""
        return self._request("GET", "/0/public/SystemStatus")
    
    def get_asset_info(self, asset: Optional[str] = None) -> Dict[str, Any]:
        """Obtener información de activos"""
        params = {}
        if asset:
            params["asset"] = asset
        return self._request("GET", "/0/public/Assets", params)
    
    def get_tradable_pairs(self, pair: Optional[str] = None) -> Dict[str, Any]:
        """Obtener pares disponibles para trading"""
        params = {}
        if pair:
            params["pair"] = pair
        return self._request("GET", "/0/public/AssetPairs", params)
    
    def get_ticker(self, pair: str) -> Dict[str, Any]:
        """Obtener información de ticker"""
        params = {"pair": pair}
        return self._request("GET", "/0/public/Ticker", params)
    
    def get_ohlc(self, pair: str, interval: int = 1) -> Dict[str, Any]:
        """
        Obtener datos OHLC.
        
        Args:
            pair: Par de trading (ej: XBTUSD)
            interval: Intervalo en minutos (1, 5, 15, 30, 60, 240, 1440, 10080, 21600)
        """
        params = {"pair": pair, "interval": interval}
        return self._request("GET", "/0/public/OHLC", params)
    
    def get_order_book(self, pair: str, count: Optional[int] = None) -> Dict[str, Any]:
        """Obtener libro de órdenes"""
        params = {"pair": pair}
        if count:
            params["count"] = count
        return self._request("GET", "/0/public/Depth", params)
    
    def get_recent_trades(self, pair: str, since: Optional[int] = None) -> Dict[str, Any]:
        """Obtener operaciones recientes"""
        params = {"pair": pair}
        if since:
            params["since"] = since
        return self._request("GET", "/0/public/Trades", params)
    
    # ==================== Account Data Endpoints ====================
    
    def get_account_balance(self) -> Dict[str, Any]:
        """Obtener saldo de cuenta"""
        return self._request("POST", "/0/private/Balance", private=True)
    
    def get_extended_balance(self) -> Dict[str, Any]:
        """Obtener saldo extendido"""
        return self._request("POST", "/0/private/BalanceEx", private=True)
    
    def get_trade_balance(self, asset: str = "ZUSD") -> Dict[str, Any]:
        """Obtener saldo disponible para trading"""
        params = {"asset": asset}
        return self._request("POST", "/0/private/TradeBalance", params, private=True)
    
    def get_open_orders(self, trades: bool = False) -> Dict[str, Any]:
        """Obtener órdenes abiertas"""
        params = {"trades": trades}
        return self._request("POST", "/0/private/OpenOrders", params, private=True)
    
    def get_closed_orders(
        self,
        trades: bool = False,
        userref: Optional[int] = None,
        closetime: str = "both"
    ) -> Dict[str, Any]:
        """Obtener órdenes cerradas"""
        params = {
            "trades": trades,
            "closetime": closetime
        }
        if userref:
            params["userref"] = userref
        return self._request("POST", "/0/private/ClosedOrders", params, private=True)
    
    def query_orders_info(self, txid: List[str], trades: bool = False) -> Dict[str, Any]:
        """Obtener información de órdenes específicas"""
        params = {
            "txid": ",".join(txid),
            "trades": trades
        }
        return self._request("POST", "/0/private/QueryOrders", params, private=True)
    
    def get_trades_history(self, trades: bool = True) -> Dict[str, Any]:
        """Obtener historial de operaciones"""
        params = {"trades": trades}
        return self._request("POST", "/0/private/TradesHistory", params, private=True)
    
    def get_open_positions(self, txid: Optional[List[str]] = None) -> Dict[str, Any]:
        """Obtener posiciones abiertas"""
        params = {}
        if txid:
            params["txid"] = ",".join(txid)
        return self._request("POST", "/0/private/OpenPositions", params, private=True)
    
    # ==================== Trading Endpoints ====================
    
    def add_order(
        self,
        pair: str,
        side: str,
        ordertype: str,
        volume: float,
        price: Optional[float] = None,
        price2: Optional[float] = None,
        leverage: Optional[str] = None,
        oflags: Optional[str] = None,
        starttm: Optional[int] = None,
        expiretm: Optional[int] = None,
        userref: Optional[int] = None,
        validate: bool = False
    ) -> Dict[str, Any]:
        """
        Colocar nueva orden.
        
        Args:
            pair: Par de trading (ej: XBTUSD)
            side: Lado (buy, sell)
            ordertype: Tipo (market, limit, stop-loss, take-profit, etc)
            volume: Volumen
            price: Precio (requerido para limit orders)
            price2: Precio secundario
            leverage: Apalancamiento
            oflags: Banderas de orden
            starttm: Tiempo de inicio
            expiretm: Tiempo de expiración
            userref: Referencia de usuario
            validate: Solo validar sin ejecutar
        """
        params = {
            "pair": pair,
            "type": side,
            "ordertype": ordertype,
            "volume": volume
        }
        
        if price is not None:
            params["price"] = price
        if price2 is not None:
            params["price2"] = price2
        if leverage:
            params["leverage"] = leverage
        if oflags:
            params["oflags"] = oflags
        if starttm:
            params["starttm"] = starttm
        if expiretm:
            params["expiretm"] = expiretm
        if userref:
            params["userref"] = userref
        if validate:
            params["validate"] = True
        
        logger.info(f"Colocando orden: {side} {volume} {pair} @ {price}")
        return self._request("POST", "/0/private/AddOrder", params, private=True)
    
    def cancel_order(self, txid: str) -> Dict[str, Any]:
        """Cancelar orden"""
        params = {"txid": txid}
        logger.info(f"Cancelando orden: {txid}")
        return self._request("POST", "/0/private/CancelOrder", params, private=True)
    
    def cancel_all_orders(self) -> Dict[str, Any]:
        """Cancelar todas las órdenes abiertas"""
        logger.warning("Cancelando TODAS las órdenes abiertas")
        return self._request("POST", "/0/private/CancelAll", {}, private=True)
    
    def amend_order(
        self,
        txid: str,
        pair: str,
        volume: Optional[float] = None,
        price: Optional[float] = None,
        price2: Optional[float] = None,
        oflags: Optional[str] = None
    ) -> Dict[str, Any]:
        """Modificar parámetros de orden existente"""
        params = {
            "txid": txid,
            "pair": pair
        }
        
        if volume is not None:
            params["volume"] = volume
        if price is not None:
            params["price"] = price
        if price2 is not None:
            params["price2"] = price2
        if oflags:
            params["oflags"] = oflags
        
        logger.info(f"Modificando orden: {txid}")
        return self._request("POST", "/0/private/AmendOrder", params, private=True)
    
    def get_websocket_token(self) -> Dict[str, Any]:
        """Obtener token para WebSocket"""
        return self._request("POST", "/0/private/GetWebSocketsToken", {}, private=True)
    
    def close(self):
        """Cerrar sesión"""
        self.session.close()
        logger.info("Sesión de Kraken cerrada")


def create_kraken_client() -> KrakenClient:
    """
    Crear cliente de Kraken desde variables de entorno.
    
    Returns:
        Cliente de Kraken configurado
        
    Raises:
        ValueError: Si faltan credenciales
    """
    api_key = os.getenv("KRAKEN_API_KEY")
    api_secret = os.getenv("KRAKEN_API_SECRET")
    
    if not api_key or not api_secret:
        raise ValueError(
            "Credenciales de Kraken no encontradas. "
            "Configure KRAKEN_API_KEY y KRAKEN_API_SECRET"
        )
    
    config = KrakenConfig(
        api_key=api_key,
        api_secret=api_secret
    )
    
    return KrakenClient(config)


if __name__ == "__main__":
    # Ejemplo de uso
    try:
        client = create_kraken_client()
        
        # Prueba de conexión
        server_time = client.get_server_time()
        logger.info(f"Tiempo del servidor: {server_time}")
        
        # Obtener pares disponibles
        pairs = client.get_tradable_pairs("XBTUSD")
        logger.info(f"Pares disponibles: {list(pairs.keys())}")
        
        # Obtener saldo
        balance = client.get_account_balance()
        logger.info(f"Saldo: {balance}")
        
        client.close()
        
    except Exception as e:
        logger.error(f"Error: {e}")
