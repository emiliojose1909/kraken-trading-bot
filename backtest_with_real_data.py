"""
Backtester mejorado para usar datos reales de Kraken.
Realiza backtesting significativo con datos históricos.
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
import numpy as np

from backtester import Backtester
from download_historical_data import KrakenDataDownloader


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RealDataBacktester:
    """
    Backtester con datos reales de Kraken.
    Permite validar la estrategia con histórico real.
    """
    
    def __init__(self, initial_capital: float = 10000.0):
        """
        Inicializar backtester.
        
        Args:
            initial_capital: Capital inicial
        """
        self.initial_capital = initial_capital
        self.downloader = KrakenDataDownloader()
        self.results = {}
        
        logger.info(f"Backtester con datos reales inicializado")
    
    def download_data(
        self,
        pairs: List[str],
        timeframe: str = "5m",
        days: int = 30,
        save_file: str = "kraken_historical_data.json"
    ) -> Dict[str, List[List]]:
        """
        Descargar datos históricos.
        
        Args:
            pairs: Lista de pares
            timeframe: Timeframe
            days: Días históricos
            save_file: Archivo para guardar
            
        Returns:
            Datos descargados
        """
        logger.info(f"Descargando datos de {len(pairs)} pares...")
        
        data = self.downloader.download_multiple_pairs(
            pairs=pairs,
            timeframe=timeframe,
            days=days
        )
        
        if data:
            self.downloader.save_data(data, save_file)
            logger.info(f"Datos guardados en {save_file}")
        
        return data
    
    def load_data(self, filename: str) -> Dict[str, List[List]]:
        """
        Cargar datos desde archivo.
        
        Args:
            filename: Archivo de datos
            
        Returns:
            Datos cargados
        """
        return self.downloader.load_data(filename)
    
    def run_backtest_single_pair(
        self,
        pair: str,
        ohlcv_data: List[List],
        lookback_period: int = 200
    ) -> Dict:
        """
        Ejecutar backtest para un par.
        
        Args:
            pair: Par de trading
            ohlcv_data: Datos OHLCV
            lookback_period: Período de lookback
            
        Returns:
            Resultados del backtest
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"BACKTESTING: {pair}")
        logger.info(f"{'='*60}")
        
        # Crear backtester
        backtester = Backtester(initial_capital=self.initial_capital)
        
        # Ejecutar backtest
        report = backtester.run_backtest(
            ohlcv_data=ohlcv_data,
            pair=pair,
            lookback_period=lookback_period
        )
        
        # Mostrar resultados
        if report:
            backtester.print_report(report)
            
            # Guardar reporte
            report_file = f"backtest_report_{pair}.json"
            backtester.save_report(report, report_file)
        
        return report
    
    def run_backtest_multiple_pairs(
        self,
        data: Dict[str, List[List]],
        lookback_period: int = 200
    ) -> Dict[str, Dict]:
        """
        Ejecutar backtest para múltiples pares.
        
        Args:
            data: Diccionario con datos por par
            lookback_period: Período de lookback
            
        Returns:
            Resultados por par
        """
        results = {}
        
        for pair, ohlcv_data in data.items():
            if not ohlcv_data:
                logger.warning(f"Sin datos para {pair}")
                continue
            
            logger.info(f"\nProcesando {pair}...")
            report = self.run_backtest_single_pair(
                pair=pair,
                ohlcv_data=ohlcv_data,
                lookback_period=lookback_period
            )
            
            if report:
                results[pair] = report
        
        self.results = results
        return results
    
    def generate_summary_report(self) -> Dict:
        """
        Generar reporte resumen de todos los backtests.
        
        Returns:
            Reporte resumen
        """
        if not self.results:
            logger.warning("No hay resultados para resumir")
            return {}
        
        summary = {
            "total_pairs": len(self.results),
            "pairs_analyzed": list(self.results.keys()),
            "summary_by_pair": {},
            "aggregate_metrics": {}
        }
        
        # Recopilar métricas por par
        total_trades = 0
        total_wins = 0
        total_pnl = 0.0
        total_profit = 0.0
        total_loss = 0.0
        max_drawdowns = []
        sharpe_ratios = []
        
        for pair, report in self.results.items():
            backtest_summary = report.get("backtest_summary", {})
            trading_stats = report.get("trading_statistics", {})
            
            pair_summary = {
                "initial_capital": backtest_summary.get("initial_capital"),
                "final_capital": backtest_summary.get("final_capital"),
                "total_return": backtest_summary.get("total_return"),
                "total_pnl": backtest_summary.get("total_return_pnl"),
                "max_drawdown": backtest_summary.get("max_drawdown"),
                "sharpe_ratio": backtest_summary.get("sharpe_ratio"),
                "total_trades": trading_stats.get("total_trades"),
                "win_rate": trading_stats.get("win_rate"),
                "profit_factor": trading_stats.get("profit_factor")
            }
            
            summary["summary_by_pair"][pair] = pair_summary
            
            # Agregar a totales
            total_trades += trading_stats.get("total_trades", 0)
            total_wins += trading_stats.get("winning_trades", 0)
            total_pnl += backtest_summary.get("total_return_pnl", 0)
            total_profit += trading_stats.get("total_profit", 0)
            total_loss += trading_stats.get("total_loss", 0)
            
            md = backtest_summary.get("max_drawdown", 0)
            if md != 0:
                max_drawdowns.append(md)
            
            sr = backtest_summary.get("sharpe_ratio", 0)
            if sr != 0:
                sharpe_ratios.append(sr)
        
        # Calcular agregados
        aggregate = {
            "total_trades": total_trades,
            "total_winning_trades": total_wins,
            "aggregate_win_rate": total_wins / total_trades if total_trades > 0 else 0,
            "total_pnl": total_pnl,
            "total_profit": total_profit,
            "total_loss": total_loss,
            "aggregate_profit_factor": total_profit / total_loss if total_loss > 0 else 0,
            "average_max_drawdown": np.mean(max_drawdowns) if max_drawdowns else 0,
            "average_sharpe_ratio": np.mean(sharpe_ratios) if sharpe_ratios else 0
        }
        
        summary["aggregate_metrics"] = aggregate
        
        return summary
    
    def print_summary_report(self, summary: Dict):
        """
        Imprimir reporte resumen.
        
        Args:
            summary: Reporte resumen
        """
        if not summary:
            return
        
        logger.info("\n" + "="*60)
        logger.info("REPORTE RESUMEN - BACKTESTING MÚLTIPLES PARES")
        logger.info("="*60)
        
        logger.info(f"\nPares analizados: {summary.get('total_pairs')}")
        logger.info(f"Pares: {', '.join(summary.get('pairs_analyzed', []))}")
        
        logger.info("\n--- RESUMEN POR PAR ---")
        for pair, metrics in summary.get("summary_by_pair", {}).items():
            logger.info(f"\n{pair}:")
            logger.info(f"  Capital inicial:    ${metrics.get('initial_capital', 0):,.2f}")
            logger.info(f"  Capital final:      ${metrics.get('final_capital', 0):,.2f}")
            logger.info(f"  Retorno:            {metrics.get('total_return', 0):.2%}")
            logger.info(f"  PnL:                ${metrics.get('total_pnl', 0):,.2f}")
            logger.info(f"  Max Drawdown:       {metrics.get('max_drawdown', 0):.2%}")
            logger.info(f"  Sharpe Ratio:       {metrics.get('sharpe_ratio', 0):.2f}")
            logger.info(f"  Total Trades:       {metrics.get('total_trades', 0)}")
            logger.info(f"  Win Rate:           {metrics.get('win_rate', 0):.2%}")
            logger.info(f"  Profit Factor:      {metrics.get('profit_factor', 0):.2f}")
        
        aggregate = summary.get("aggregate_metrics", {})
        logger.info("\n--- MÉTRICAS AGREGADAS ---")
        logger.info(f"Total operaciones:      {aggregate.get('total_trades', 0)}")
        logger.info(f"Total ganadoras:        {aggregate.get('total_winning_trades', 0)}")
        logger.info(f"Win rate agregado:      {aggregate.get('aggregate_win_rate', 0):.2%}")
        logger.info(f"PnL total:              ${aggregate.get('total_pnl', 0):,.2f}")
        logger.info(f"Ganancias totales:      ${aggregate.get('total_profit', 0):,.2f}")
        logger.info(f"Pérdidas totales:       ${aggregate.get('total_loss', 0):,.2f}")
        logger.info(f"Profit factor agregado: {aggregate.get('aggregate_profit_factor', 0):.2f}")
        logger.info(f"Max drawdown promedio:  {aggregate.get('average_max_drawdown', 0):.2%}")
        logger.info(f"Sharpe ratio promedio:  {aggregate.get('average_sharpe_ratio', 0):.2f}")
        
        logger.info("\n" + "="*60)
    
    def save_summary_report(self, summary: Dict, filename: str = "backtest_summary.json"):
        """
        Guardar reporte resumen.
        
        Args:
            summary: Reporte resumen
            filename: Nombre del archivo
        """
        try:
            with open(filename, 'w') as f:
                json.dump(summary, f, indent=2)
            logger.info(f"Reporte resumen guardado en {filename}")
        except Exception as e:
            logger.error(f"Error guardando reporte: {e}")


def main():
    """
    Función principal - Ejemplo de uso.
    """
    # Crear backtester
    bt = RealDataBacktester(initial_capital=10000.0)
    
    # Opción 1: Descargar datos reales
    logger.info("OPCIÓN 1: Descargar datos reales de Kraken")
    logger.info("(Esto puede tomar algunos minutos)")
    
    pairs = ["XBTUSD", "ETHUSD"]
    data = bt.download_data(
        pairs=pairs,
        timeframe="5m",
        days=7,  # 7 días de datos
        save_file="kraken_historical_data.json"
    )
    
    if not data:
        logger.info("\nOPCIÓN 2: Cargar datos previamente descargados")
        data = bt.load_data("kraken_historical_data.json")
    
    if data:
        # Ejecutar backtests
        logger.info("\nEjecutando backtests...")
        results = bt.run_backtest_multiple_pairs(data)
        
        # Generar reporte resumen
        summary = bt.generate_summary_report()
        bt.print_summary_report(summary)
        bt.save_summary_report(summary)
    else:
        logger.error("No se pudieron obtener datos")


if __name__ == "__main__":
    main()
