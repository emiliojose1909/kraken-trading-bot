# Guía Completa de Implementación - Bot de Trading Kraken

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Paso 1: Preparar el Entorno](#paso-1-preparar-el-entorno)
3. [Paso 2: Obtener Credenciales de Kraken](#paso-2-obtener-credenciales-de-kraken)
4. [Paso 3: Instalar el Bot](#paso-3-instalar-el-bot)
5. [Paso 4: Configurar el Bot](#paso-4-configurar-el-bot)
6. [Paso 5: Validar la Instalación](#paso-5-validar-la-instalación)
7. [Paso 6: Ejecutar en Paper Trading](#paso-6-ejecutar-en-paper-trading)
8. [Paso 7: Backtesting](#paso-7-backtesting)
9. [Paso 8: Trading Real (Opcional)](#paso-8-trading-real-opcional)
10. [Troubleshooting](#troubleshooting)

---

## Requisitos Previos

### Hardware Mínimo
- **CPU**: 2 núcleos
- **RAM**: 2 GB
- **Almacenamiento**: 500 MB libres
- **Conexión**: Internet estable (10+ Mbps)

### Software Requerido
- **Python 3.8 o superior**
- **pip** (gestor de paquetes)
- **Terminal/Consola**

### Cuenta Kraken
- Cuenta activa en https://www.kraken.com
- Verificación de identidad completada
- Saldo disponible (mínimo $100 para testing)

---

## Paso 1: Preparar el Entorno

### 1.1 Verificar Python

```bash
# Verificar versión de Python
python3 --version

# Debe mostrar: Python 3.8.0 o superior
```

**Si no tienes Python:**

**En Windows:**
1. Descargar desde https://www.python.org/downloads/
2. Ejecutar instalador
3. ✓ Marcar "Add Python to PATH"
4. Instalar

**En Mac:**
```bash
brew install python3
```

**En Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
```

### 1.2 Verificar pip

```bash
# Verificar pip
pip3 --version

# Debe mostrar: pip X.X.X from ...
```

### 1.3 Crear Carpeta del Proyecto

```bash
# Crear carpeta
mkdir mi_bot_trading
cd mi_bot_trading

# Verificar que estás en la carpeta correcta
pwd  # En Mac/Linux
cd   # En Windows (mostrará la ruta actual)
```

---

## Paso 2: Obtener Credenciales de Kraken

### 2.1 Acceder a Kraken API

1. Ir a https://www.kraken.com/c/account-settings/api
2. Iniciar sesión con tu cuenta Kraken
3. Si no tienes cuenta, crear una en https://www.kraken.com

### 2.2 Generar Nueva API Key

1. Hacer clic en **"Generate New Key"**
2. Completar el formulario:
   - **Key Description**: "Trading Bot" (o nombre que prefieras)
   - **Nonce Window**: 0
   - **Post-only**: No (sin marcar)

### 2.3 Configurar Permisos

Marcar SOLO estos permisos:
- ✓ **Query Funds** - Ver saldo
- ✓ **Query Open Orders** - Ver órdenes abiertas
- ✓ **Query Closed Orders** - Ver histórico
- ✓ **Query Trades** - Ver trades
- ✓ **Create & Modify Orders** - Crear órdenes
- ✓ **Cancel/Close Orders** - Cancelar órdenes

**NO marcar:**
- ❌ Modify Settings
- ❌ Access Ledger Query
- ❌ Query Account Ledger
- ❌ Withdraw Funds

### 2.4 Guardar las Credenciales

Después de generar, verás:
- **API Key** (Public Key)
- **Private Key** (Secret)

**IMPORTANTE**: 
- Copiar ambas claves
- Guardar en lugar seguro
- NO compartir con nadie
- NO subir a internet

**Ejemplo de cómo se ven:**
```
API Key: vK83Hd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0...
Private Key: xK83Hd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0...
```

---

## Paso 3: Instalar el Bot

### 3.1 Descargar el ZIP

1. Descargar `kraken_bot_complete_v2.zip`
2. Extraer en la carpeta `mi_bot_trading`

```bash
# En la carpeta mi_bot_trading
unzip kraken_bot_complete_v2.zip

# Verificar que se extrajo correctamente
ls -la kraken_bot/
```

### 3.2 Crear Entorno Virtual (Recomendado)

```bash
# Crear entorno virtual
python3 -m venv venv

# Activar entorno virtual
# En Mac/Linux:
source venv/bin/activate

# En Windows (Command Prompt):
venv\Scripts\activate

# En Windows (PowerShell):
venv\Scripts\Activate.ps1

# Verificar que está activado (debe mostrar (venv) al inicio)
```

### 3.3 Instalar Dependencias

```bash
# Asegúrate de estar en la carpeta kraken_bot
cd kraken_bot

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
pip list | grep -E "requests|numpy|pandas"
```

**Dependencias que se instalarán:**
- `requests` - Cliente HTTP
- `numpy` - Cálculos numéricos
- `pandas` - Procesamiento de datos
- `python-dotenv` - Variables de entorno

---

## Paso 4: Configurar el Bot

### 4.1 Configurar Variables de Entorno

**Opción A: Archivo .env (Recomendado)**

```bash
# Crear archivo .env en la carpeta kraken_bot
cat > .env << EOF
KRAKEN_API_KEY=tu_api_key_aqui
KRAKEN_API_SECRET=tu_private_key_aqui
EOF
```

**Reemplazar:**
- `tu_api_key_aqui` con tu API Key de Kraken
- `tu_private_key_aqui` con tu Private Key de Kraken

**Ejemplo:**
```
KRAKEN_API_KEY=vK83Hd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0
KRAKEN_API_SECRET=xK83Hd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0
```

**Opción B: Variables de Entorno del Sistema**

```bash
# En Mac/Linux
export KRAKEN_API_KEY="tu_api_key"
export KRAKEN_API_SECRET="tu_private_key"

# En Windows (Command Prompt)
set KRAKEN_API_KEY=tu_api_key
set KRAKEN_API_SECRET=tu_private_key

# En Windows (PowerShell)
$env:KRAKEN_API_KEY="tu_api_key"
$env:KRAKEN_API_SECRET="tu_private_key"
```

### 4.2 Configurar bot_config.json

Editar `bot_config.json` con tus preferencias:

```json
{
  "trading_pairs": ["XBTUSD", "ETHUSD"],
  "timeframe_minutes": 5,
  "total_capital": 1000.0,
  "risk_per_trade": 0.01,
  "max_positions": 2,
  "max_position_size": 0.05,
  "max_drawdown": 0.10,
  "max_consecutive_losses": 3,
  "rsi_oversold": 30.0,
  "rsi_overbought": 70.0,
  "adx_threshold": 25.0,
  "volume_threshold": 1.1,
  "min_confidence": 0.75,
  "min_signal_interval_minutes": 5,
  "atr_multiplier": 2.0,
  "paper_trading": true,
  "logging_level": "INFO"
}
```

**Parámetros Importantes:**

| Parámetro | Recomendación | Descripción |
|-----------|--------------|-------------|
| `total_capital` | 1000-10000 | Capital a invertir |
| `risk_per_trade` | 0.01-0.02 | 1-2% del capital |
| `max_positions` | 2-5 | Máximo de posiciones abiertas |
| `paper_trading` | true (primero) | Modo simulación |

### 4.3 Verificar Configuración

```bash
# Verificar que las variables de entorno están configuradas
python3 -c "
import os
key = os.getenv('KRAKEN_API_KEY')
secret = os.getenv('KRAKEN_API_SECRET')
print('API Key configurada:', 'Sí' if key else 'No')
print('API Secret configurada:', 'Sí' if secret else 'No')
"
```

---

## Paso 5: Validar la Instalación

### 5.1 Ejecutar Pruebas Unitarias

```bash
# Ejecutar todas las pruebas
python3 test_bot.py

# Salida esperada:
# Ran 19 tests in X.XXXs
# OK
```

### 5.2 Verificar Módulos

```bash
# Verificar que todos los módulos se importan correctamente
python3 -c "
import kraken_client
import technical_analysis
import signal_generator
import risk_manager
import trading_bot
print('✓ Todos los módulos se importaron correctamente')
"
```

### 5.3 Verificar Conexión a Kraken

```bash
# Probar conexión a Kraken
python3 -c "
from kraken_client import KrakenClient
client = KrakenClient()
print('Conectando a Kraken...')
balance = client.get_balance()
if balance:
    print('✓ Conexión exitosa')
    print('Saldo:', balance)
else:
    print('✗ Error en la conexión')
"
```

---

## Paso 6: Ejecutar en Paper Trading

### 6.1 Verificar Configuración de Paper Trading

```bash
# Asegurar que paper_trading está en true
grep "paper_trading" bot_config.json
# Debe mostrar: "paper_trading": true
```

### 6.2 Ejecutar el Bot

```bash
# Ejecutar el bot
python3 trading_bot.py

# Salida esperada:
# 2026-01-21 12:00:00 - trading_bot - INFO - Bot de trading inicializado
# 2026-01-21 12:00:01 - kraken_client - INFO - Conexión establecida
# 2026-01-21 12:00:02 - trading_bot - INFO - Saldo inicial: {...}
# 2026-01-21 12:00:03 - trading_bot - INFO - Ciclo de trading iniciado
```

### 6.3 Monitorear el Bot

```bash
# Ver logs en tiempo real (en otra terminal)
tail -f trading_bot.log

# Ver últimas 50 líneas
tail -50 trading_bot.log

# Buscar errores
grep ERROR trading_bot.log
```

### 6.4 Detener el Bot

```bash
# Presionar Ctrl+C en la terminal donde está ejecutándose
# El bot cerrará posiciones y generará reporte
```

### 6.5 Ver Reporte

```bash
# Ver reporte final
cat trading_report.json | python3 -m json.tool

# O ver con less (para navegar)
less trading_report.json
```

---

## Paso 7: Backtesting

### 7.1 Descargar Datos Históricos

```bash
# Descargar 30 días de datos
python3 download_historical_data.py

# Salida esperada:
# Descargador de datos Kraken inicializado
# Obteniendo pares disponibles...
# Descargando datos históricos de ['XBTUSD', 'ETHUSD', 'XRPUSD']...
# ✓ XBTUSD: 8640 velas descargadas
# ✓ ETHUSD: 8640 velas descargadas
# ✓ XRPUSD: 8640 velas descargadas
# Datos guardados en kraken_historical_data.json
```

### 7.2 Ejecutar Backtesting

```bash
# Ejecutar backtesting con datos reales
python3 backtest_with_real_data.py

# Salida esperada:
# Backtester con datos reales inicializado
# Cargando datos...
# Ejecutando backtests...
# ============================================================
# BACKTESTING: XBTUSD
# ============================================================
# Capital inicial:        $10,000.00
# Capital final:          $10,250.00
# Retorno total:          2.50%
# ...
```

### 7.3 Analizar Resultados

```bash
# Ver resumen
cat backtest_summary.json | python3 -m json.tool

# Buscar métricas clave
grep -E "max_drawdown|sharpe_ratio|win_rate|profit_factor" backtest_summary.json
```

### 7.4 Interpretar Resultados

**Buscar estos valores:**

```
Max Drawdown: -12.5%   ← Debe ser < 15%
Sharpe Ratio: 1.45     ← Debe ser > 1.0
Win Rate: 52.3%        ← Debe ser > 45%
Profit Factor: 2.15    ← Debe ser > 1.5
```

**Si todos están bien → Listo para paper trading**

---

## Paso 8: Trading Real (Opcional)

### ⚠️ ADVERTENCIA

**SOLO después de:**
- ✓ Validación exitosa en paper trading (1-2 semanas)
- ✓ Backtesting positivo con múltiples pares
- ✓ Monitoreo activo de logs
- ✓ Comprensión completa de la estrategia

### 8.1 Cambiar a Trading Real

```bash
# Editar bot_config.json
# Cambiar: "paper_trading": false

# O usar sed para cambiar automáticamente
sed -i 's/"paper_trading": true/"paper_trading": false/' bot_config.json
```

### 8.2 Ejecutar en Trading Real

```bash
# Ejecutar el bot
python3 trading_bot.py

# Monitorear constantemente
tail -f trading_bot.log
```

### 8.3 Parar el Bot

```bash
# Presionar Ctrl+C
# El bot cerrará todas las posiciones
```

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'requests'"

**Solución:**
```bash
# Instalar dependencias nuevamente
pip install -r requirements.txt

# O instalar específicamente
pip install requests numpy pandas python-dotenv
```

### Error: "KRAKEN_API_KEY not found"

**Solución:**
```bash
# Verificar que .env existe
ls -la .env

# Si no existe, crear:
cat > .env << EOF
KRAKEN_API_KEY=tu_clave
KRAKEN_API_SECRET=tu_secreto
EOF

# O configurar variables de entorno
export KRAKEN_API_KEY="tu_clave"
export KRAKEN_API_SECRET="tu_secreto"
```

### Error: "Connection refused"

**Solución:**
```bash
# Verificar conexión a internet
ping google.com

# Verificar que Kraken API está disponible
curl https://api.kraken.com/0/public/Time

# Si falla, esperar y reintentar
```

### Error: "Insufficient funds"

**Solución:**
```bash
# Reducir capital en bot_config.json
"total_capital": 100.0  # Reducir a 100 USD

# O reducir riesgo por trade
"risk_per_trade": 0.005  # Reducir a 0.5%
```

### El bot no genera señales

**Posibles causas:**
1. Confianza muy alta (`min_confidence`: 0.75)
2. Datos insuficientes (necesita 200+ velas)
3. Condiciones de mercado no favorables

**Solución:**
```json
{
  "min_confidence": 0.70,  // Reducir de 0.75
  "adx_threshold": 20.0,   // Reducir de 25
  "volume_threshold": 1.0  // Reducir de 1.1
}
```

### Bot muy lento

**Solución:**
```bash
# Aumentar timeframe
"timeframe_minutes": 15  # De 5 a 15 minutos

# O reducir número de pares
"trading_pairs": ["XBTUSD"]  # Solo 1 par
```

### Pérdidas en backtesting

**Solución:**
```json
{
  "risk_per_trade": 0.01,      // Reducir riesgo
  "max_position_size": 0.05,   // Reducir posición
  "min_confidence": 0.80       // Aumentar confianza
}
```

---

## Checklist de Implementación

- [ ] Python 3.8+ instalado
- [ ] pip verificado
- [ ] Carpeta del proyecto creada
- [ ] ZIP descargado y extraído
- [ ] Credenciales de Kraken obtenidas
- [ ] Variables de entorno configuradas
- [ ] bot_config.json editado
- [ ] Pruebas unitarias pasadas
- [ ] Conexión a Kraken verificada
- [ ] Paper trading ejecutado (1-2 semanas)
- [ ] Backtesting realizado
- [ ] Resultados analizados
- [ ] Logs monitoreados
- [ ] Trading real iniciado (opcional)

---

## Próximos Pasos

1. **Hoy**: Instalar y configurar
2. **Mañana**: Ejecutar en paper trading
3. **Semana 1-2**: Monitorear y validar
4. **Semana 2-3**: Backtesting con datos reales
5. **Semana 3+**: Trading real (opcional)

---

## Recursos Útiles

- **Documentación Kraken**: https://docs.kraken.com/rest/
- **Python**: https://www.python.org/
- **Análisis Técnico**: https://en.wikipedia.org/wiki/Technical_analysis

---

**¡Listo para implementar!** 🚀

Sigue estos pasos en orden y tendrás el bot funcionando en menos de 1 hora.
