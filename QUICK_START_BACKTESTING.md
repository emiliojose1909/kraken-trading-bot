# Guía Rápida: Backtesting con Datos Reales

## 3 Pasos Simples

### Paso 1: Descargar Datos (5-10 minutos)
```bash
cd /home/ubuntu/kraken_bot
python3 download_historical_data.py
```

Esto descarga 30 días de datos de BTC, ETH y XRP en timeframe de 5 minutos.

**Archivo generado**: `kraken_historical_data.json`

### Paso 2: Ejecutar Backtesting (2-5 minutos)
```bash
python3 backtest_with_real_data.py
```

Esto ejecuta backtesting en todos los pares descargados.

**Archivos generados**:
- `backtest_report_XBTUSD.json`
- `backtest_report_ETHUSD.json`
- `backtest_summary.json`

### Paso 3: Analizar Resultados (5 minutos)
```bash
# Ver resumen
cat backtest_summary.json | python3 -m json.tool

# Ver métricas clave
grep -E "max_drawdown|sharpe_ratio|win_rate|profit_factor" backtest_summary.json
```

## Personalizar Descargas

### Descargar Datos Específicos

```python
from download_historical_data import KrakenDataDownloader

downloader = KrakenDataDownloader()

# Descargar 60 días de datos en 1 hora
data = downloader.download_multiple_pairs(
    pairs=["XBTUSD"],
    timeframe="1h",
    days=60
)

downloader.save_data(data, "btc_60days_1h.json")
```

### Opciones de Timeframe

| Timeframe | Uso | Días Máx |
|-----------|-----|----------|
| 1m | Scalping rápido | 5 |
| 5m | Day trading | 30 |
| 15m | Day trading | 60 |
| 1h | Swing trading | 180 |
| 1d | Posición | 365 |

## Interpretar Resultados Rápidamente

### Métricas Clave

```
Max Drawdown: -12.5%  → Pérdida máxima desde pico
Sharpe Ratio: 1.45    → Retorno ajustado por riesgo
Win Rate: 52.3%       → % de operaciones ganadoras
Profit Factor: 2.15   → Ganancias / Pérdidas
```

### Decisión Rápida

| Métrica | Bueno | Excelente |
|---------|-------|-----------|
| Max Drawdown | < 15% | < 10% |
| Sharpe Ratio | > 1.0 | > 1.5 |
| Win Rate | > 45% | > 55% |
| Profit Factor | > 1.5 | > 2.0 |

**Si todos son "Bueno" o mejor → Listo para paper trading**

## Troubleshooting Rápido

### Error: "No internet connection"
```bash
# Verificar conexión
ping google.com

# Usar datos previamente descargados
python3 backtest_with_real_data.py  # Carga kraken_historical_data.json
```

### Error: "Pair not found"
```bash
# Ver pares disponibles
python3 -c "from download_historical_data import KrakenDataDownloader; d = KrakenDataDownloader(); print(d.get_available_pairs()[:10])"
```

### Backtesting muy lento
```python
# Usar menos datos o timeframe mayor
data = downloader.download_multiple_pairs(
    pairs=["XBTUSD"],  # Solo 1 par
    timeframe="1h",     # Timeframe mayor
    days=7              # Menos días
)
```

## Próximos Pasos

1. ✓ Ejecutar backtesting con datos reales
2. ✓ Analizar métricas
3. ✓ Si resultados son buenos → Paper trading
4. ✓ Monitorear 1-2 semanas
5. ✓ Trading real (opcional)

---

**Tiempo total**: ~20 minutos
**Resultado**: Validación completa de la estrategia
