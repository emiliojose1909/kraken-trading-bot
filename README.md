# 🤖 Bot de Trading Algorítmico para Kraken

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production-success.svg)]()

Bot de trading algorítmico profesional para Kraken con estrategia **Momentum-Reversion híbrida**, análisis técnico avanzado y gestión de riesgos sofisticada.

---

## 🎯 Características Principales

- ✅ **Estrategia Momentum-Reversion Híbrida** - Validación multi-indicador
- ✅ **6 Indicadores Técnicos** - EMA, RSI, MACD, Bandas de Bollinger, ATR, ADX
- ✅ **Gestión de Riesgos Sofisticada** - Position sizing dinámico, stops y take profits escalonados
- ✅ **Paper Trading** - Validar sin dinero real
- ✅ **Backtesting con Datos Reales** - Descarga automática de Kraken
- ✅ **19 Pruebas Unitarias** - Código validado
- ✅ **Documentación Exhaustiva** - 9 guías completas

---

## 🚀 Inicio Rápido (5 minutos)

```bash
# 1. Clonar repositorio
git clone https://github.com/emiliojose1909/kraken-trading-bot.git
cd kraken-trading-bot

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar credenciales
cat > .env << EOF
KRAKEN_API_KEY=tu_api_key
KRAKEN_API_SECRET=tu_private_key
EOF

# 4. Ejecutar en paper trading
python trading_bot.py
```

**Ver guía completa:** [QUICK_START_5MIN.md](QUICK_START_5MIN.md)

---

## 📊 Estrategia de Trading

### Indicadores Técnicos

| Indicador | Uso | Período |
|-----------|-----|---------|
| **EMA** | Tendencia | 12, 50, 200 |
| **RSI** | Sobreventa/Sobrecompra | 14 |
| **MACD** | Momentum | 12, 26, 9 |
| **Bandas de Bollinger** | Volatilidad | 20, 2σ |
| **ATR** | Stops dinámicos | 14 |
| **ADX** | Fuerza de tendencia | 14 |

### Señales de Trading

**Compra:**
- Tendencia alcista (EMA 12 > EMA 50 > EMA 200)
- RSI < 30 (sobreventa)
- MACD positivo
- Volumen confirmado

**Venta:**
- Tendencia bajista (EMA 12 < EMA 50 < EMA 200)
- RSI > 70 (sobrecompra)
- MACD negativo
- Volumen confirmado

### Gestión de Riesgos

- **Stop Loss**: Entrada - (ATR × 2)
- **Take Profit 1**: Entrada + (ATR × 1.5) → 30% del volumen
- **Take Profit 2**: Entrada + (ATR × 2.5) → 40% del volumen
- **Take Profit 3**: Entrada + (ATR × 4.0) → 30% del volumen

---

## 📁 Estructura del Proyecto

```
kraken-trading-bot/
├── trading_bot.py              # Bot principal
├── kraken_client.py            # Cliente REST de Kraken
├── technical_analysis.py       # Indicadores técnicos
├── signal_generator.py         # Generador de señales
├── risk_manager.py             # Gestor de riesgos
├── download_historical_data.py # Descargador de datos
├── backtest_with_real_data.py  # Backtester avanzado
├── test_bot.py                 # Pruebas unitarias
├── backtester.py               # Backtester básico
├── bot_config.json             # Configuración
├── requirements.txt            # Dependencias
└── docs/                       # Documentación
    ├── QUICK_START_5MIN.md
    ├── STEP_BY_STEP.md
    ├── IMPLEMENTATION_GUIDE.md
    ├── BACKTESTING_GUIDE.md
    └── ...
```

---

## 📖 Documentación

### Guías de Implementación

| Guía | Descripción | Tiempo |
|------|-------------|--------|
| [QUICK_START_5MIN.md](QUICK_START_5MIN.md) | Inicio rápido | 5 min |
| [STEP_BY_STEP.md](STEP_BY_STEP.md) | Paso a paso visual | 30 min |
| [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) | Guía completa | 1 hora |

### Guías Técnicas

| Guía | Descripción |
|------|-------------|
| [README.md](README.md) | Documentación técnica completa |
| [SETUP_GUIDE.md](SETUP_GUIDE.md) | Configuración detallada |
| [BACKTESTING_GUIDE.md](BACKTESTING_GUIDE.md) | Guía de backtesting |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Resumen del proyecto |

---

## 🔧 Requisitos

### Software
- Python 3.8 o superior
- pip (gestor de paquetes)

### Cuenta Kraken
- Cuenta activa en [Kraken](https://www.kraken.com)
- API Key con permisos:
  - Query Funds
  - Query Orders
  - Create & Modify Orders
  - Cancel Orders

### Dependencias Python
```
requests>=2.31.0
numpy>=1.24.0
pandas>=2.0.0
python-dotenv>=1.0.0
```

---

## 🧪 Testing

### Ejecutar Pruebas Unitarias

```bash
python test_bot.py
```

**Resultado esperado:**
```
Ran 19 tests in 0.020s
OK
```

### Backtesting con Datos Reales

```bash
# Descargar datos históricos
python download_historical_data.py

# Ejecutar backtesting
python backtest_with_real_data.py
```

---

## 📈 Métricas de Rendimiento

El bot calcula automáticamente:

| Métrica | Descripción | Objetivo |
|---------|-------------|----------|
| **Win Rate** | % de operaciones ganadoras | > 45% |
| **Profit Factor** | Ganancias / Pérdidas | > 1.5 |
| **Sharpe Ratio** | Retorno ajustado por riesgo | > 1.0 |
| **Max Drawdown** | Máxima pérdida desde pico | < 15% |
| **Recovery Factor** | Ganancia / Drawdown | > 2.0 |

---

## ⚙️ Configuración

### Parámetros Principales (bot_config.json)

```json
{
  "trading_pairs": ["XBTUSD", "ETHUSD"],
  "total_capital": 10000.0,
  "risk_per_trade": 0.02,
  "max_positions": 5,
  "max_position_size": 0.10,
  "max_drawdown": 0.15,
  "min_confidence": 0.75,
  "paper_trading": true
}
```

**Recomendaciones:**
- Empezar con `paper_trading: true`
- Capital conservador: $1,000 - $10,000
- Riesgo por trade: 1-2%
- Máximo 2-5 posiciones simultáneas

---

## 🔐 Seguridad

### Mejores Prácticas

- ✅ Usar archivo `.env` para credenciales
- ✅ Nunca compartir API keys
- ✅ Habilitar 2FA en Kraken
- ✅ Usar IP whitelist en Kraken
- ✅ Limitar permisos de API key
- ✅ Monitorear logs regularmente

### Permisos de API Key

**Habilitar:**
- Query Funds
- Query Open Orders
- Query Closed Orders
- Query Trades
- Create & Modify Orders
- Cancel/Close Orders

**NO habilitar:**
- Modify Settings
- Withdraw Funds

---

## 📊 Ejemplo de Uso

### Paper Trading

```python
# El bot ejecuta automáticamente en modo simulación
python trading_bot.py
```

### Backtesting

```python
from backtest_with_real_data import RealDataBacktester

# Crear backtester
bt = RealDataBacktester(initial_capital=10000.0)

# Descargar datos
data = bt.download_data(
    pairs=["XBTUSD", "ETHUSD"],
    timeframe="1h",
    days=90
)

# Ejecutar backtesting
results = bt.run_backtest_multiple_pairs(data)

# Generar resumen
summary = bt.generate_summary_report()
bt.print_summary_report(summary)
```

---

## 🐛 Troubleshooting

### Problemas Comunes

**"ModuleNotFoundError"**
```bash
pip install -r requirements.txt
```

**"API Key not found"**
```bash
# Verificar archivo .env
cat .env
```

**"Connection refused"**
```bash
# Verificar conexión a internet
ping api.kraken.com
```

**Ver más:** [IMPLEMENTATION_GUIDE.md - Troubleshooting](IMPLEMENTATION_GUIDE.md#troubleshooting)

---

## 📈 Estadísticas del Proyecto

| Métrica | Valor |
|---------|-------|
| Líneas de Código | ~3,000+ |
| Archivos Python | 8 |
| Pruebas Unitarias | 19 |
| Indicadores Técnicos | 6 |
| Parámetros Configurables | 20+ |
| Documentación | 9 archivos |

---

## 🗺️ Roadmap

- [ ] WebSocket para datos en tiempo real
- [ ] Machine learning para optimización
- [ ] Dashboard web de monitoreo
- [ ] Alertas por email/Telegram
- [ ] Múltiples estrategias simultáneas
- [ ] Análisis de sentimiento
- [ ] Optimización automática de parámetros

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crear una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## ⚠️ Disclaimer

Este bot es para propósitos educativos. El trading conlleva riesgos significativos de pérdida financiera. Use bajo su propio riesgo. Nunca invierta más de lo que pueda permitirse perder.

**No somos asesores financieros.** Este software se proporciona "tal cual" sin garantías de ningún tipo.

---

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/emiliojose1909/kraken-trading-bot/issues)
- **Documentación**: Ver carpeta `docs/`
- **Kraken API**: [docs.kraken.com](https://docs.kraken.com/rest/)

---

## 🙏 Agradecimientos

- [Kraken](https://www.kraken.com) por su excelente API
- Comunidad de trading algorítmico
- Contribuidores del proyecto

---

## 📊 Badges

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![Tests](https://img.shields.io/badge/Tests-19%20passed-success)
![Code Size](https://img.shields.io/badge/Code-3000%2B%20lines-informational)
![Docs](https://img.shields.io/badge/Docs-9%20guides-blue)

---

**Versión:** 1.0.0  
**Fecha:** 2026-01-21  
**Estado:** Producción

---

⭐ **Si este proyecto te ayudó, dale una estrella en GitHub!**
