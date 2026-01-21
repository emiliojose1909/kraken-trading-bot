# Instalación Rápida - Bot de Trading Kraken

## Paso 1: Extraer el ZIP

```bash
unzip kraken_bot_complete.zip
cd kraken_bot
```

## Paso 2: Instalar Dependencias

```bash
pip install -r requirements.txt
```

## Paso 3: Configurar Credenciales de Kraken

### Obtener API Keys

1. Ir a https://www.kraken.com/c/account-settings/api
2. Hacer clic en "Generate New Key"
3. Configurar permisos:
   - ✓ Query Funds
   - ✓ Query Open Orders
   - ✓ Query Closed Orders
   - ✓ Query Trades
   - ✓ Create & Modify Orders
   - ✓ Cancel/Close Orders
4. Copiar Public Key y Private Key

### Configurar Variables de Entorno

```bash
# Linux/Mac
export KRAKEN_API_KEY="tu_clave_publica"
export KRAKEN_API_SECRET="tu_clave_privada"

# Windows (Command Prompt)
set KRAKEN_API_KEY=tu_clave_publica
set KRAKEN_API_SECRET=tu_clave_privada

# Windows (PowerShell)
$env:KRAKEN_API_KEY="tu_clave_publica"
$env:KRAKEN_API_SECRET="tu_clave_privada"
```

## Paso 4: Ejecutar el Bot

### Paper Trading (Recomendado primero)

```bash
python3 trading_bot.py
```

### Backtesting con Datos Reales

```bash
# Descargar datos
python3 download_historical_data.py

# Ejecutar backtesting
python3 backtest_with_real_data.py
```

## Documentación

- **README.md** - Documentación completa del bot
- **SETUP_GUIDE.md** - Guía detallada de instalación
- **BACKTESTING_GUIDE.md** - Guía de backtesting
- **QUICK_START_BACKTESTING.md** - Guía rápida (3 pasos)
- **PROJECT_SUMMARY.md** - Resumen técnico

## Archivos Principales

- `trading_bot.py` - Bot principal
- `kraken_client.py` - Cliente de Kraken API
- `technical_analysis.py` - Indicadores técnicos
- `signal_generator.py` - Generador de señales
- `risk_manager.py` - Gestor de riesgos
- `download_historical_data.py` - Descargador de datos
- `backtest_with_real_data.py` - Backtester
- `test_bot.py` - Pruebas unitarias

## Próximos Pasos

1. ✓ Instalar dependencias
2. ✓ Configurar credenciales
3. ✓ Ejecutar en paper trading
4. ✓ Hacer backtesting con datos reales
5. ✓ Trading real (opcional)

## Soporte

Para reportar bugs o sugerencias, crear issue en el repositorio.

---

**Versión**: 1.0.0
**Fecha**: 2026-01-21
