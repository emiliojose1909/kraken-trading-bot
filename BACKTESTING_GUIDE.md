# Guía de Backtesting con Datos Reales de Kraken

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Requisitos](#requisitos)
3. [Paso 1: Descargar Datos Históricos](#paso-1-descargar-datos-históricos)
4. [Paso 2: Ejecutar Backtesting](#paso-2-ejecutar-backtesting)
5. [Paso 3: Analizar Resultados](#paso-3-analizar-resultados)
6. [Interpretación de Métricas](#interpretación-de-métricas)
7. [Mejora Continua](#mejora-continua)

---

## Introducción

El backtesting con datos reales es esencial para validar la estrategia antes de trading real. Este proceso:

- **Valida la estrategia** con histórico real
- **Identifica problemas** potenciales
- **Optimiza parámetros** para mejores resultados
- **Estima rendimiento** esperado

### ¿Por qué es importante?

| Aspecto | Beneficio |
|--------|----------|
| **Validación** | Confirmar que la estrategia funciona en condiciones reales |
| **Optimización** | Ajustar parámetros para máximo rendimiento |
| **Confianza** | Ganar confianza antes de invertir dinero real |
| **Riesgo** | Identificar drawdowns y pérdidas potenciales |

---

## Requisitos

### Software
- Python 3.8+
- Dependencias instaladas: `pip install -r requirements.txt`

### Datos
- Conexión a internet (para descargar datos de Kraken)
- Espacio en disco (~50 MB por 30 días de datos)

### Tiempo
- Descarga: 5-10 minutos (primero)
- Backtesting: 1-5 minutos por par
- Análisis: 10-30 minutos

---

## Paso 1: Descargar Datos Históricos

### Método A: Descargar Automáticamente (Recomendado)

```bash
cd /home/ubuntu/kraken_bot
python3 download_historical_data.py
```

**Salida esperada:**
```
2026-01-21 12:00:00 - __main__ - INFO - Descargador de datos Kraken inicializado
2026-01-21 12:00:01 - __main__ - INFO - Obteniendo pares disponibles...
2026-01-21 12:00:02 - __main__ - INFO - Pares disponibles: 45
2026-01-21 12:00:03 - __main__ - INFO - Descargando datos históricos de ['XBTUSD', 'ETHUSD', 'XRPUSD']...
2026-01-21 12:00:15 - __main__ - INFO - ✓ XBTUSD: 8640 velas descargadas
2026-01-21 12:00:25 - __main__ - INFO - ✓ ETHUSD: 8640 velas descargadas
2026-01-21 12:00:35 - __main__ - INFO - ✓ XRPUSD: 8640 velas descargadas
2026-01-21 12:00:35 - __main__ - INFO - Datos guardados en kraken_historical_data.json
```

### Método B: Descargar Datos Específicos

Crear script personalizado:

```python
from download_historical_data import KrakenDataDownloader

downloader = KrakenDataDownloader()

# Descargar datos específicos
data = downloader.download_multiple_pairs(
    pairs=["XBTUSD", "ETHUSD"],
    timeframe="1h",  # 1 hora
    days=60  # 60 días
)

downloader.save_data(data, "my_data.json")
```

### Parámetros Disponibles

| Parámetro | Opciones | Descripción |
|-----------|----------|-------------|
| `timeframe` | 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 15d | Intervalo de velas |
| `days` | 1-365 | Días históricos a descargar |
| `pairs` | Cualquier par USD | Pares a descargar |

### Recomendaciones

**Para Testing Rápido:**
```python
# 7 días de datos en 5 minutos
pairs=["XBTUSD", "ETHUSD"]
timeframe="5m"
days=7
```

**Para Validación Robusta:**
```python
# 90 días de datos en 1 hora
pairs=["XBTUSD", "ETHUSD", "XRPUSD"]
timeframe="1h"
days=90
```

**Para Análisis Profundo:**
```python
# 1 año de datos en 1 día
pairs=["XBTUSD"]
timeframe="1d"
days=365
```

---

## Paso 2: Ejecutar Backtesting

### Opción A: Backtesting Simple (Un Par)

```bash
python3 backtester.py
```

### Opción B: Backtesting Múltiples Pares (Recomendado)

```bash
python3 backtest_with_real_data.py
```

**Salida esperada:**
```
2026-01-21 12:00:00 - __main__ - INFO - Backtester con datos reales inicializado
2026-01-21 12:00:01 - __main__ - INFO - Cargando datos...
2026-01-21 12:00:02 - __main__ - INFO - Ejecutando backtests...

============================================================
BACKTESTING: XBTUSD
============================================================
2026-01-21 12:00:03 - __main__ - INFO - Iniciando backtest con 8640 velas
2026-01-21 12:00:05 - __main__ - INFO - ============================================================
2026-01-21 12:00:05 - __main__ - INFO - REPORTE DE BACKTEST
2026-01-21 12:00:05 - __main__ - INFO - ============================================================
2026-01-21 12:00:05 - __main__ - INFO - 
RESUMEN FINANCIERO:
2026-01-21 12:00:05 - __main__ - INFO -   Capital inicial:        $10,000.00
2026-01-21 12:00:05 - __main__ - INFO -   Capital final:          $10,250.00
2026-01-21 12:00:05 - __main__ - INFO -   Retorno total:          2.50%
...
```

### Personalizar Backtesting

```python
from backtest_with_real_data import RealDataBacktester

# Crear backtester
bt = RealDataBacktester(initial_capital=50000.0)  # Capital mayor

# Cargar datos
data = bt.load_data("kraken_historical_data.json")

# Ejecutar backtests
results = bt.run_backtest_multiple_pairs(
    data=data,
    lookback_period=200  # Período de lookback para indicadores
)

# Generar resumen
summary = bt.generate_summary_report()
bt.print_summary_report(summary)
```

---

## Paso 3: Analizar Resultados

### Archivos Generados

```
backtest_report_XBTUSD.json    # Reporte detallado por par
backtest_report_ETHUSD.json    # Reporte detallado por par
backtest_summary.json          # Resumen agregado
```

### Ver Resultados

```bash
# Ver reporte resumen
cat backtest_summary.json | python3 -m json.tool

# Ver reporte específico
cat backtest_report_XBTUSD.json | python3 -m json.tool

# Buscar métrica específica
grep "sharpe_ratio" backtest_summary.json
```

### Ejemplo de Análisis

```python
import json

# Cargar reporte
with open("backtest_summary.json") as f:
    summary = json.load(f)

# Analizar resultados
aggregate = summary["aggregate_metrics"]

print(f"Total operaciones: {aggregate['total_trades']}")
print(f"Win rate: {aggregate['aggregate_win_rate']:.2%}")
print(f"Profit factor: {aggregate['aggregate_profit_factor']:.2f}")
print(f"Max drawdown: {aggregate['average_max_drawdown']:.2%}")
print(f"Sharpe ratio: {aggregate['average_sharpe_ratio']:.2f}")
```

---

## Interpretación de Métricas

### Métricas Principales

#### 1. Max Drawdown (Máximo Drawdown)

**Definición**: Máxima pérdida desde el pico de capital

**Rango Aceptable**: 10-20%
- **< 10%**: Muy conservador, posiblemente pocos trades
- **10-20%**: Óptimo, buen balance riesgo-retorno
- **> 20%**: Riesgoso, requiere ajustes

**Ejemplo**:
```
Max Drawdown: -12.5%
Interpretación: En el peor momento, perdiste 12.5% del capital
```

#### 2. Sharpe Ratio

**Definición**: Retorno ajustado por riesgo

**Rango Aceptable**: 1.0-3.0
- **< 0.5**: Pobre, retorno no compensa riesgo
- **0.5-1.0**: Aceptable, pero mejorable
- **1.0-2.0**: Bueno, retorno adecuado para riesgo
- **> 2.0**: Excelente, retorno muy superior al riesgo

**Ejemplo**:
```
Sharpe Ratio: 1.45
Interpretación: Por cada unidad de riesgo, ganas 1.45 unidades de retorno
```

#### 3. Win Rate (Tasa de Ganancia)

**Definición**: % de operaciones ganadoras

**Rango Aceptable**: 45-65%
- **< 40%**: Insuficiente, requiere mejora
- **40-50%**: Aceptable con buen profit factor
- **50-60%**: Bueno, estrategia sólida
- **> 60%**: Excelente, muy pocas pérdidas

**Ejemplo**:
```
Win Rate: 52.3%
Interpretación: 52 de cada 100 operaciones son ganadoras
```

#### 4. Profit Factor

**Definición**: Ganancias totales / Pérdidas totales

**Rango Aceptable**: 1.5-3.0
- **< 1.0**: Negativo, pierdes dinero
- **1.0-1.5**: Marginal, poco rentable
- **1.5-2.0**: Bueno, ganas 1.5-2x lo que pierdes
- **> 2.0**: Excelente, muy rentable

**Ejemplo**:
```
Profit Factor: 2.15
Interpretación: Por cada $1 perdido, ganas $2.15
```

#### 5. Total Return (Retorno Total)

**Definición**: (Capital Final - Capital Inicial) / Capital Inicial

**Rango Aceptable**: 5-50% (anual)
- **< 0%**: Pérdida neta
- **0-5%**: Bajo retorno
- **5-20%**: Retorno moderado
- **20-50%**: Retorno alto
- **> 50%**: Retorno muy alto (verificar validez)

**Ejemplo**:
```
Total Return: 12.5%
Interpretación: Ganaste 12.5% sobre tu capital inicial
```

### Matriz de Decisión

| Métrica | Resultado | Acción |
|---------|-----------|--------|
| Max Drawdown | > 25% | ❌ Rechazar, muy riesgoso |
| Max Drawdown | 15-25% | ⚠️ Revisar, considerar ajustes |
| Max Drawdown | 10-15% | ✓ Aceptable |
| Max Drawdown | < 10% | ✓✓ Excelente |
| Sharpe Ratio | < 0.5 | ❌ Rechazar |
| Sharpe Ratio | 0.5-1.0 | ⚠️ Revisar |
| Sharpe Ratio | > 1.0 | ✓ Aceptable |
| Sharpe Ratio | > 2.0 | ✓✓ Excelente |
| Win Rate | < 40% | ⚠️ Necesita profit factor alto |
| Win Rate | 40-60% | ✓ Aceptable |
| Win Rate | > 60% | ✓✓ Excelente |
| Profit Factor | < 1.5 | ⚠️ Revisar |
| Profit Factor | 1.5-2.0 | ✓ Bueno |
| Profit Factor | > 2.0 | ✓✓ Excelente |

---

## Mejora Continua

### Ciclo de Optimización

```
1. BACKTESTING INICIAL
   ↓
2. ANÁLISIS DE RESULTADOS
   ↓
3. IDENTIFICAR PROBLEMAS
   ↓
4. AJUSTAR PARÁMETROS
   ↓
5. BACKTESTING NUEVO
   ↓
6. COMPARAR RESULTADOS
   ↓
7. VALIDAR EN PAPER TRADING
   ↓
8. TRADING REAL (si es positivo)
```

### Parámetros a Ajustar

#### Si Max Drawdown es muy alto (> 20%)

```python
# Aumentar conservadurismo
{
    "min_confidence": 0.80,      # De 0.75 a 0.80
    "max_position_size": 0.05,   # De 0.10 a 0.05
    "risk_per_trade": 0.01       # De 0.02 a 0.01
}
```

#### Si Win Rate es muy baja (< 40%)

```python
# Mejorar calidad de señales
{
    "adx_threshold": 30,         # De 25 a 30
    "volume_threshold": 1.2,     # De 1.1 a 1.2
    "rsi_oversold": 25,          # De 30 a 25
    "rsi_overbought": 75         # De 70 a 75
}
```

#### Si Sharpe Ratio es bajo (< 1.0)

```python
# Mejorar retorno ajustado por riesgo
{
    "atr_multiplier": 1.5,       # De 2.0 a 1.5 (stops más ajustados)
    "min_confidence": 0.75,      # Mantener selectivo
    "max_positions": 3            # De 5 a 3 (menos posiciones simultáneas)
}
```

### Checklist de Optimización

- [ ] Backtesting con 30+ días de datos
- [ ] Backtesting en múltiples pares
- [ ] Max drawdown < 15%
- [ ] Sharpe ratio > 1.0
- [ ] Win rate > 45%
- [ ] Profit factor > 1.5
- [ ] Total return > 5% (anual)
- [ ] Validación en paper trading 1-2 semanas
- [ ] Monitoreo activo de logs
- [ ] Documentación de cambios

---

## Ejemplos de Resultados

### Ejemplo 1: Resultado Excelente ✓✓

```json
{
  "max_drawdown": -8.5,
  "sharpe_ratio": 2.15,
  "win_rate": 0.58,
  "profit_factor": 2.45,
  "total_return": 0.18,
  "total_trades": 145
}
```

**Interpretación**: Estrategia muy sólida, lista para trading real

### Ejemplo 2: Resultado Aceptable ✓

```json
{
  "max_drawdown": -12.3,
  "sharpe_ratio": 1.05,
  "win_rate": 0.52,
  "profit_factor": 1.75,
  "total_return": 0.12,
  "total_trades": 89
}
```

**Interpretación**: Estrategia funciona, pero requiere monitoreo

### Ejemplo 3: Resultado Pobre ❌

```json
{
  "max_drawdown": -28.5,
  "sharpe_ratio": 0.35,
  "win_rate": 0.38,
  "profit_factor": 0.95,
  "total_return": -0.05,
  "total_trades": 234
}
```

**Interpretación**: Estrategia no funciona, requiere cambios significativos

---

## Preguntas Frecuentes

### ¿Cuántos datos históricos necesito?

- **Mínimo**: 30 días (para validación rápida)
- **Recomendado**: 90 días (validación robusta)
- **Óptimo**: 1 año (análisis completo)

### ¿Qué timeframe debo usar?

- **Scalping**: 1m, 5m
- **Day trading**: 5m, 15m, 30m
- **Swing trading**: 1h, 4h
- **Posición**: 1d, 1w

### ¿Cómo sé si el backtest es realista?

1. Usar datos reales de Kraken
2. Incluir comisiones (0.05%)
3. Simular slippage (0.1%)
4. Múltiples pares y períodos
5. Validar en paper trading

### ¿Puedo confiar en los resultados del backtest?

Parcialmente. Los backtests son indicativos pero no garantizan:
- Condiciones futuras diferentes
- Comportamiento del mercado cambia
- Slippage real puede ser mayor
- Comisiones pueden variar

**Siempre validar en paper trading primero**

---

## Recursos Adicionales

- [Kraken API Documentation](https://docs.kraken.com/rest/)
- [Technical Analysis](https://en.wikipedia.org/wiki/Technical_analysis)
- [Backtesting Best Practices](https://www.investopedia.com/terms/b/backtesting.asp)

---

**Última actualización**: 2026-01-21

**Versión**: 1.0.0
