"""
Gestor de riesgos y posiciones.
Implementa gestión de capital, stops dinámicos y control de riesgo.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


logger = logging.getLogger(__name__)


class PositionStatus(Enum):
    """Estados de una posición"""
    OPEN = "OPEN"
    PARTIALLY_CLOSED = "PARTIALLY_CLOSED"
    CLOSED = "CLOSED"
    STOPPED_OUT = "STOPPED_OUT"


@dataclass
class Position:
    """Representa una posición abierta"""
    position_id: str
    pair: str
    side: str  # "buy" o "sell"
    entry_price: float
    volume: float
    stop_loss: float
    take_profit_1: float
    take_profit_2: float
    take_profit_3: float
    entry_time: datetime
    status: PositionStatus = PositionStatus.OPEN
    
    # Tracking de cierre parcial
    volume_closed_tp1: float = 0.0
    volume_closed_tp2: float = 0.0
    volume_closed_tp3: float = 0.0
    
    # Métricas
    current_price: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    
    def get_open_volume(self) -> float:
        """Obtener volumen abierto"""
        return self.volume - self.volume_closed_tp1 - self.volume_closed_tp2 - self.volume_closed_tp3
    
    def update_current_price(self, price: float):
        """Actualizar precio actual y calcular PnL no realizado"""
        self.current_price = price
        
        if self.side == "buy":
            self.unrealized_pnl = (price - self.entry_price) * self.get_open_volume()
        else:
            self.unrealized_pnl = (self.entry_price - price) * self.get_open_volume()


@dataclass
class RiskConfig:
    """Configuración de riesgo"""
    # Capital
    total_capital: float
    risk_per_trade: float = 0.02  # 2% por operación
    
    # Límites de posición
    max_positions: int = 5
    max_position_size: float = 0.10  # 10% del capital
    
    # Límites de riesgo
    max_drawdown: float = 0.15  # 15%
    max_consecutive_losses: int = 3
    
    # Stops dinámicos
    trailing_stop_enabled: bool = True
    trailing_stop_distance: float = 0.05  # 5%
    
    # Pausa de trading
    pause_after_max_losses: bool = True
    pause_duration_minutes: int = 60


class RiskManager:
    """
    Gestor de riesgos y posiciones.
    Implementa control de capital, stops dinámicos y límites de riesgo.
    """
    
    def __init__(self, config: RiskConfig):
        """
        Inicializar gestor de riesgos.
        
        Args:
            config: Configuración de riesgo
        """
        self.config = config
        self.positions: Dict[str, Position] = {}
        self.closed_positions: List[Position] = []
        self.consecutive_losses = 0
        self.total_realized_pnl = 0.0
        self.peak_capital = config.total_capital
        
        # Cargar estado previo si existe
        self.load_state()
        
        logger.info(f"Gestor de riesgos inicializado con capital: {config.total_capital}")

    def save_state(self):
        """Guardar estado actual a archivo"""
        try:
            state = {
                "positions": {
                    pid: {
                        **asdict(pos),
                        "entry_time": pos.entry_time.isoformat(),
                        "status": pos.status.value
                    }
                    for pid, pos in self.positions.items()
                },
                "consecutive_losses": self.consecutive_losses,
                "total_realized_pnl": self.total_realized_pnl
            }
            
            with open("bot_state.json", 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error guardando estado: {e}")

    def load_state(self):
        """Cargar estado desde archivo"""
        if not os.path.exists("bot_state.json"):
            return
            
        try:
            with open("bot_state.json", 'r') as f:
                state = json.load(f)
                
            # Cargar posiciones
            for pid, pos_data in state.get("positions", {}).items():
                # Reconstruir datetime
                if "entry_time" in pos_data and isinstance(pos_data["entry_time"], str):
                    pos_data["entry_time"] = datetime.fromisoformat(pos_data["entry_time"])
                
                # Reconstruir Enum
                if "status" in pos_data and isinstance(pos_data["status"], str):
                    pos_data["status"] = PositionStatus(pos_data["status"])
                
                self.positions[pid] = Position(**pos_data)
                
            self.consecutive_losses = state.get("consecutive_losses", 0)
            self.total_realized_pnl = state.get("total_realized_pnl", 0.0)
            
            logger.info(f"Estado recuperado: {len(self.positions)} posiciones abiertas")
            
        except Exception as e:
            logger.error(f"Error cargando estado: {e}")
    
    def can_open_position(self) -> Tuple[bool, str]:
        """
        Verificar si se puede abrir una nueva posición.
        
        Returns:
            Tupla (puede_abrir, razón)
        """
        # Verificar número máximo de posiciones
        if len(self.positions) >= self.config.max_positions:
            return False, f"Máximo de posiciones alcanzado ({self.config.max_positions})"
        
        # Verificar drawdown máximo
        current_capital = self.get_current_capital()
        drawdown = (self.peak_capital - current_capital) / self.peak_capital
        if drawdown > self.config.max_drawdown:
            return False, f"Drawdown máximo alcanzado ({drawdown:.2%})"
        
        # Verificar pérdidas consecutivas
        if self.consecutive_losses >= self.config.max_consecutive_losses:
            if self.config.pause_after_max_losses:
                return False, f"Máximo de pérdidas consecutivas ({self.config.max_consecutive_losses})"
        
        return True, "OK"
    
    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        confidence: float = 1.0
    ) -> float:
        """
        Calcular tamaño de posición basado en riesgo.
        
        Args:
            entry_price: Precio de entrada
            stop_loss: Precio de stop loss
            confidence: Confianza de la señal (0.0-1.0)
            
        Returns:
            Volumen a operar
        """
        # Calcular riesgo por operación
        risk_amount = self.config.total_capital * self.config.risk_per_trade * confidence
        
        # Calcular riesgo por unidad
        risk_per_unit = abs(entry_price - stop_loss)
        
        if risk_per_unit == 0:
            return 0.0
        
        # Calcular volumen
        volume = risk_amount / risk_per_unit
        
        # Aplicar límite de tamaño máximo de posición
        max_volume = (self.config.total_capital * self.config.max_position_size) / entry_price
        volume = min(volume, max_volume)
        
        # Verificar saldo disponible
        available_capital = self.get_available_capital()
        max_volume_by_capital = available_capital / entry_price
        volume = min(volume, max_volume_by_capital)
        
        return volume
    
    def open_position(
        self,
        position_id: str,
        pair: str,
        side: str,
        entry_price: float,
        volume: float,
        stop_loss: float,
        take_profit_1: float,
        take_profit_2: float,
        take_profit_3: float
    ) -> bool:
        """
        Abrir una nueva posición.
        
        Args:
            position_id: ID único de la posición
            pair: Par de trading
            side: Lado (buy/sell)
            entry_price: Precio de entrada
            volume: Volumen
            stop_loss: Precio de stop loss
            take_profit_1: Primer take profit
            take_profit_2: Segundo take profit
            take_profit_3: Tercer take profit
            
        Returns:
            True si se abrió la posición
        """
        can_open, reason = self.can_open_position()
        if not can_open:
            logger.warning(f"No se puede abrir posición: {reason}")
            return False
        
        position = Position(
            position_id=position_id,
            pair=pair,
            side=side,
            entry_price=entry_price,
            volume=volume,
            stop_loss=stop_loss,
            take_profit_1=take_profit_1,
            take_profit_2=take_profit_2,
            take_profit_3=take_profit_3,
            entry_time=datetime.now()
        )
        
        self.positions[position_id] = position
        
        self.save_state()  # Guardar estado
        
        logger.info(
            f"Posición abierta: {position_id} {side.upper()} {volume} {pair} @ {entry_price} "
            f"SL: {stop_loss} TP1: {take_profit_1}"
        )
        return True
    
    def update_position_price(self, position_id: str, current_price: float):
        """
        Actualizar precio actual de una posición.
        
        Args:
            position_id: ID de la posición
            current_price: Precio actual
        """
        if position_id not in self.positions:
            return
        
        position = self.positions[position_id]
        position.update_current_price(current_price)
    
    def check_stop_loss(self, position_id: str, current_price: float) -> bool:
        """
        Verificar si se alcanzó el stop loss.
        
        Args:
            position_id: ID de la posición
            current_price: Precio actual
            
        Returns:
            True si se alcanzó el stop loss
        """
        if position_id not in self.positions:
            return False
        
        position = self.positions[position_id]
        
        if position.side == "buy":
            if current_price <= position.stop_loss:
                return True
        else:
            if current_price >= position.stop_loss:
                return True
        
        return False
    
    def check_take_profit(
        self,
        position_id: str,
        current_price: float
    ) -> Tuple[int, bool]:
        """
        Verificar si se alcanzó algún take profit.
        
        Args:
            position_id: ID de la posición
            current_price: Precio actual
            
        Returns:
            Tupla (nivel_tp, alcanzado)
        """
        if position_id not in self.positions:
            return 0, False
        
        position = self.positions[position_id]
        
        if position.side == "buy":
            if current_price >= position.take_profit_3 and position.volume_closed_tp3 == 0:
                return 3, True
            elif current_price >= position.take_profit_2 and position.volume_closed_tp2 == 0:
                return 2, True
            elif current_price >= position.take_profit_1 and position.volume_closed_tp1 == 0:
                return 1, True
        else:
            if current_price <= position.take_profit_3 and position.volume_closed_tp3 == 0:
                return 3, True
            elif current_price <= position.take_profit_2 and position.volume_closed_tp2 == 0:
                return 2, True
            elif current_price <= position.take_profit_1 and position.volume_closed_tp1 == 0:
                return 1, True
        
        return 0, False
    
    def close_position_partial(
        self,
        position_id: str,
        tp_level: int,
        close_price: float
    ) -> float:
        """
        Cerrar parcialmente una posición en take profit.
        
        Args:
            position_id: ID de la posición
            tp_level: Nivel de TP (1, 2, 3)
            close_price: Precio de cierre
            
        Returns:
            Volumen cerrado
        """
        if position_id not in self.positions:
            return 0.0
        
        position = self.positions[position_id]
        
        # Determinar volumen a cerrar según nivel
        if tp_level == 1:
            volume_to_close = position.volume * 0.30
            position.volume_closed_tp1 = volume_to_close
        elif tp_level == 2:
            volume_to_close = position.volume * 0.40
            position.volume_closed_tp2 = volume_to_close
        elif tp_level == 3:
            volume_to_close = position.volume * 0.30
            position.volume_closed_tp3 = volume_to_close
        else:
            return 0.0
        
        # Calcular PnL realizado
        if position.side == "buy":
            pnl = (close_price - position.entry_price) * volume_to_close
        else:
            pnl = (position.entry_price - close_price) * volume_to_close
        
        position.realized_pnl += pnl
        self.total_realized_pnl += pnl
        
        logger.info(
            f"Cierre parcial TP{tp_level}: {position_id} {volume_to_close} @ {close_price} "
            f"PnL: {pnl:.2f}"
        )
        
        # Actualizar estado si está completamente cerrada
        if position.get_open_volume() == 0:
            position.status = PositionStatus.CLOSED
            self._move_to_closed(position_id)
        else:
            position.status = PositionStatus.PARTIALLY_CLOSED
        
        self.save_state()  # Guardar estado
        return volume_to_close
    
    def close_position_stop_loss(
        self,
        position_id: str,
        close_price: float
    ) -> float:
        """
        Cerrar posición por stop loss.
        
        Args:
            position_id: ID de la posición
            close_price: Precio de cierre
            
        Returns:
            Volumen cerrado
        """
        if position_id not in self.positions:
            return 0.0
        
        position = self.positions[position_id]
        volume_to_close = position.get_open_volume()
        
        # Calcular PnL
        if position.side == "buy":
            pnl = (close_price - position.entry_price) * volume_to_close
        else:
            pnl = (position.entry_price - close_price) * volume_to_close
        
        position.realized_pnl += pnl
        self.total_realized_pnl += pnl
        
        # Actualizar estado
        position.status = PositionStatus.STOPPED_OUT
        self._move_to_closed(position_id)
        
        # Actualizar contador de pérdidas consecutivas
        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        logger.warning(
            f"Stop loss ejecutado: {position_id} {volume_to_close} @ {close_price} "
            f"PnL: {pnl:.2f}"
        )
        
        self.save_state()  # Guardar estado
        return volume_to_close
    
    def _move_to_closed(self, position_id: str):
        """
        Mover posición a historial de cerradas.
        
        Args:
            position_id: ID de la posición
        """
        if position_id in self.positions:
            position = self.positions.pop(position_id)
            self.closed_positions.append(position)
    
    def get_current_capital(self) -> float:
        """
        Obtener capital actual (inicial + PnL realizado + PnL no realizado).
        
        Returns:
            Capital actual
        """
        unrealized_pnl = sum(p.unrealized_pnl for p in self.positions.values())
        return self.config.total_capital + self.total_realized_pnl + unrealized_pnl
    
    def get_available_capital(self) -> float:
        """
        Obtener capital disponible para nuevas posiciones.
        
        Returns:
            Capital disponible
        """
        capital_in_use = sum(
            p.entry_price * p.get_open_volume() for p in self.positions.values()
        )
        return self.get_current_capital() - capital_in_use
    
    def get_drawdown(self) -> float:
        """
        Obtener drawdown actual.
        
        Returns:
            Drawdown como porcentaje
        """
        current = self.get_current_capital()
        return (self.peak_capital - current) / self.peak_capital
    
    def get_statistics(self) -> Dict:
        """
        Obtener estadísticas de trading.
        
        Returns:
            Diccionario con estadísticas
        """
        total_trades = len(self.closed_positions)
        winning_trades = sum(1 for p in self.closed_positions if p.realized_pnl > 0)
        losing_trades = total_trades - winning_trades
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        total_profit = sum(p.realized_pnl for p in self.closed_positions if p.realized_pnl > 0)
        total_loss = abs(sum(p.realized_pnl for p in self.closed_positions if p.realized_pnl < 0))
        
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "total_profit": total_profit,
            "total_loss": total_loss,
            "profit_factor": profit_factor,
            "total_pnl": self.total_realized_pnl,
            "current_capital": self.get_current_capital(),
            "available_capital": self.get_available_capital(),
            "drawdown": self.get_drawdown(),
            "open_positions": len(self.positions),
            "consecutive_losses": self.consecutive_losses
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Ejemplo de uso
    config = RiskConfig(total_capital=10000.0)
    manager = RiskManager(config)
    
    # Abrir posición
    manager.open_position(
        position_id="pos_001",
        pair="BTC/USD",
        side="buy",
        entry_price=45000.0,
        volume=0.1,
        stop_loss=44000.0,
        take_profit_1=46500.0,
        take_profit_2=48000.0,
        take_profit_3=50000.0
    )
    
    # Actualizar precio
    manager.update_position_price("pos_001", 46000.0)
    
    # Verificar TP
    tp_level, reached = manager.check_take_profit("pos_001", 46500.0)
    if reached:
        manager.close_position_partial("pos_001", tp_level, 46500.0)
    
    # Estadísticas
    stats = manager.get_statistics()
    logger.info(f"Estadísticas: {stats}")
