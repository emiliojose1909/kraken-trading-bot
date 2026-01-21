# Guía de Instalación y Configuración - Bot de Trading Kraken

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación](#instalación)
3. [Configuración de Credenciales](#configuración-de-credenciales)
4. [Configuración del Bot](#configuración-del-bot)
5. [Ejecución](#ejecución)
6. [Monitoreo](#monitoreo)
7. [Troubleshooting](#troubleshooting)

---

## Requisitos Previos

### Hardware
- **CPU**: Mínimo 2 núcleos
- **RAM**: Mínimo 2 GB
- **Almacenamiento**: 500 MB libres
- **Conexión**: Internet estable (recomendado 10+ Mbps)

### Software
- **Python**: 3.8 o superior
- **Pip**: Gestor de paquetes de Python
- **Git**: Para clonar el repositorio (opcional)

### Cuenta Kraken
- Cuenta activa en https://www.kraken.com
- Verificación de identidad completada
- API habilitada en la cuenta

---

## Instalación

### Paso 1: Descargar el Proyecto

**Opción A: Usando Git**
```bash
git clone <repository-url>
cd kraken_bot
```

**Opción B: Descargar ZIP**
```bash
# Descargar y extraer el archivo ZIP
unzip kraken_bot.zip
cd kraken_bot
```

### Paso 2: Crear Entorno Virtual (Recomendado)

```bash
# En Linux/Mac
python3 -m venv venv
source venv/bin/activate

# En Windows
python -m venv venv
venv\Scripts\activate
```

### Paso 3: Instalar Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias incluidas:**
- `requests`: Cliente HTTP para API
- `numpy`: Cálculos numéricos
- `pandas`: Procesamiento de datos
- `python-dotenv`: Gestión de variables de entorno

---

## Configuración de Credenciales

### Paso 1: Obtener API Keys de Kraken

1. Ir a https://www.kraken.com/c/account-settings/api
2. Hacer clic en "Generate New Key"
3. Configurar permisos:
   - ✓ Query Funds
   - ✓ Query Open Orders
   - ✓ Query Closed Orders
   - ✓ Query Trades
   - ✓ Create & Modify Orders
   - ✓ Cancel/Close Orders
4. **NO** habilitar "Modify Settings" o "Access Ledger Query"
5. Copiar la **Public Key** y **Private Key**

### Paso 2: Configurar Variables de Entorno

**Opción A: Archivo .env (Recomendado)**

Crear archivo `.env` en el directorio raíz:

```bash
cat > .env << EOF
KRAKEN_API_KEY=tu_clave_publica_aqui
KRAKEN_API_SECRET=tu_clave_privada_aqui
EOF
```

**Opción B: Variables de Entorno del Sistema**

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

### Paso 3: Verificar Configuración

```bash
python3 -c "
import os
key = os.getenv('KRAKEN_API_KEY')
secret = os.getenv('KRAKEN_API_SECRET')
print(f'API Key: {key[:10]}...' if key else 'API Key: NO CONFIGURADA')
print(f'API Secret: {secret[:10]}...' if secret else 'API Secret: NO CONFIGURADA')
"
```

---

## Configuración del Bot

### Archivo bot_config.json

El archivo `bot_config.json` controla todos los parámetros del bot:

```json
{
  "trading_pairs": ["XBTUSD", "ETHUSD", "XRPUSD"],
  "timeframe_minutes": 5,
  "total_capital": 10000.0,
  "risk_per_trade": 0.02,
  "max_positions": 5,
  "max_position_size": 0.10,
  "max_drawdown": 0.15,
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

### Parámetros Importantes

#### Capital y Riesgo

| Parámetro | Descripción | Recomendación |
|-----------|-------------|---------------|
| `total_capital` | Capital inicial a invertir | Empezar con 1000-10000 USD |
| `risk_per_trade` | Porcentaje de capital en riesgo por operación | 1-3% (conservador: 1-2%) |
| `max_position_size` | Máximo % del capital por posición | 5-15% |
| `max_drawdown` | Máximo drawdown permitido | 10-20% |

#### Estrategia

| Parámetro | Descripción | Recomendación |
|-----------|-------------|---------------|
| `rsi_oversold` | Umbral RSI para sobreventa | 20-35 |
| `rsi_overbought` | Umbral RSI para sobrecompra | 65-80 |
| `adx_threshold` | Umbral ADX para confirmar tendencia | 20-30 |
| `min_confidence` | Confianza mínima para señal | 0.70-0.80 |
| `atr_multiplier` | Multiplicador para stops dinámicos | 1.5-3.0 |

#### Operación

| Parámetro | Descripción | Recomendación |
|-----------|-------------|---------------|
| `trading_pairs` | Pares a tradear | Empezar con 1-2 pares |
| `min_signal_interval_minutes` | Intervalo mínimo entre señales | 5-15 minutos |
| `paper_trading` | Modo simulación | `true` para testing |

### Configuración Recomendada para Principiantes

```json
{
  "trading_pairs": ["XBTUSD"],
  "total_capital": 1000.0,
  "risk_per_trade": 0.01,
  "max_positions": 2,
  "max_position_size": 0.05,
  "max_drawdown": 0.10,
  "min_confidence": 0.80,
  "paper_trading": true
}
```

### Configuración Recomendada para Avanzados

```json
{
  "trading_pairs": ["XBTUSD", "ETHUSD", "XRPUSD"],
  "total_capital": 10000.0,
  "risk_per_trade": 0.02,
  "max_positions": 5,
  "max_position_size": 0.10,
  "max_drawdown": 0.15,
  "min_confidence": 0.75,
  "paper_trading": false
}
```

---

## Ejecución

### Modo Paper Trading (Recomendado Primero)

```bash
# Asegurar que paper_trading está en true en bot_config.json
python3 trading_bot.py
```

**Salida esperada:**
```
2026-01-21 12:00:00 - trading_bot - INFO - Bot de trading inicializado
2026-01-21 12:00:01 - kraken_client - INFO - Conexión establecida
2026-01-21 12:00:02 - trading_bot - INFO - Saldo inicial: {...}
2026-01-21 12:00:03 - trading_bot - INFO - Ciclo de trading iniciado
```

### Modo Trading Real

**ADVERTENCIA**: Solo después de validación exhaustiva en paper trading.

1. Cambiar en `bot_config.json`:
```json
{
  "paper_trading": false
}
```

2. Ejecutar:
```bash
python3 trading_bot.py
```

### Detener el Bot

```bash
# Presionar Ctrl+C en la terminal
# El bot cerrará posiciones y generará reporte
```

---

## Monitoreo

### Logs en Tiempo Real

El bot genera logs en dos lugares:

**1. Consola (en vivo)**
```bash
# Ver logs mientras se ejecuta el bot
tail -f trading_bot.log
```

**2. Archivo de log**
```bash
# Ver archivo completo
cat trading_bot.log

# Ver últimas 50 líneas
tail -50 trading_bot.log

# Buscar errores
grep ERROR trading_bot.log
```

### Reporte Final

Cuando se detiene el bot, genera `trading_report.json`:

```bash
# Ver reporte
cat trading_report.json

# Ver con formato legible
python3 -m json.tool trading_report.json
```

### Métricas Clave a Monitorear

- **Win Rate**: % de operaciones ganadoras (objetivo: >50%)
- **Profit Factor**: Ganancias/Pérdidas (objetivo: >1.5)
- **Drawdown**: Máxima pérdida desde pico (mantener <15%)
- **Sharpe Ratio**: Retorno ajustado por riesgo (objetivo: >1.0)

---

## Troubleshooting

### Error: "Credenciales de Kraken no encontradas"

**Solución:**
```bash
# Verificar que las variables de entorno están configuradas
echo $KRAKEN_API_KEY
echo $KRAKEN_API_SECRET

# Si están vacías, configurarlas nuevamente
export KRAKEN_API_KEY="tu_clave"
export KRAKEN_API_SECRET="tu_secreto"
```

### Error: "Rate limit exceeded"

**Causa**: Demasiadas solicitudes a la API de Kraken

**Soluciones:**
1. Aumentar `min_signal_interval_minutes` en `bot_config.json`
2. Reducir número de `trading_pairs`
3. Esperar 15 minutos antes de reintentar

### Error: "Insufficient funds"

**Causa**: No hay suficiente saldo en la cuenta

**Soluciones:**
1. Verificar saldo en Kraken
2. Reducir `total_capital` en `bot_config.json`
3. Reducir `risk_per_trade`

### El bot no genera señales

**Posibles causas:**
1. Confianza de señal muy alta (`min_confidence`)
2. Datos insuficientes (necesita 200+ velas)
3. Condiciones de mercado no favorables

**Soluciones:**
1. Reducir `min_confidence` a 0.70
2. Esperar más tiempo para acumular datos
3. Revisar logs para ver por qué se rechazan señales

### Conexión lenta o timeouts

**Soluciones:**
1. Verificar conexión a internet
2. Aumentar timeouts en `kraken_client.py`
3. Usar servidor más cercano a Kraken
4. Ejecutar en servidor en la nube

---

## Mejores Prácticas

### 1. Validación Inicial
- Ejecutar en paper trading mínimo 1-2 semanas
- Validar estadísticas antes de trading real
- Revisar logs regularmente

### 2. Gestión de Capital
- Nunca invertir más del 5-10% del capital disponible
- Mantener reservas para emergencias
- Diversificar entre múltiples pares

### 3. Monitoreo Activo
- Revisar logs diariamente
- Monitorear drawdown
- Estar preparado para pausar si es necesario

### 4. Ajustes Graduales
- Cambiar un parámetro a la vez
- Validar cambios en paper trading primero
- Documentar todos los cambios

### 5. Seguridad
- Nunca compartir API keys
- Usar IP whitelist en Kraken
- Habilitar 2FA en cuenta Kraken
- Hacer backup de configuración

---

## Soporte y Recursos

### Documentación
- **Kraken API**: https://docs.kraken.com/rest/
- **Indicadores Técnicos**: https://en.wikipedia.org/wiki/Technical_analysis
- **Trading Algorítmico**: https://www.investopedia.com/terms/a/algorithmictrading.asp

### Comunidades
- **Kraken Community**: https://www.reddit.com/r/Kraken/
- **Crypto Trading**: https://www.reddit.com/r/algotrading/
- **Python Finance**: https://github.com/topics/algorithmic-trading

---

## Próximos Pasos

1. ✓ Instalar dependencias
2. ✓ Configurar credenciales
3. ✓ Ejecutar en paper trading
4. ✓ Validar estrategia
5. ✓ Ajustar parámetros si es necesario
6. ✓ Ejecutar en trading real (opcional)

---

**Última actualización**: 2026-01-21

**Versión**: 1.0.0

**Disclaimer**: Este bot es para propósitos educativos. El trading conlleva riesgos significativos. Use bajo su propio riesgo.
