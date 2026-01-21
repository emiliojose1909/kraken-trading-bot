# Guía Paso a Paso Visual - Implementación del Bot

## 🎯 Objetivo Final
Tener el bot de trading funcionando en tu computadora en 5 pasos simples.

---

## PASO 1: Verificar Python ✓

### En Windows:
1. Abrir **Command Prompt** (Cmd)
2. Escribir:
```cmd
python --version
```
3. Debe mostrar: `Python 3.8.0` o superior

**Si no aparece nada:**
- Descargar Python desde https://www.python.org/downloads/
- Ejecutar el instalador
- ✓ Marcar "Add Python to PATH"
- Reiniciar Command Prompt

### En Mac:
```bash
python3 --version
```

### En Linux:
```bash
python3 --version
```

---

## PASO 2: Obtener Credenciales de Kraken 🔑

### Paso 2.1: Ir a Kraken API
1. Abrir navegador
2. Ir a: https://www.kraken.com/c/account-settings/api
3. Iniciar sesión

### Paso 2.2: Generar Nueva Key
1. Hacer clic en **"Generate New Key"**
2. Llenar:
   - Key Description: `Trading Bot`
   - Nonce Window: `0`
3. Hacer clic en **"Generate"**

### Paso 2.3: Configurar Permisos
Marcar SOLO estos:
- ✓ Query Funds
- ✓ Query Open Orders
- ✓ Query Closed Orders
- ✓ Query Trades
- ✓ Create & Modify Orders
- ✓ Cancel/Close Orders

### Paso 2.4: Guardar Credenciales
Verás dos claves:
```
API Key: vK83Hd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0
Private Key: xK83Hd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0
```

**Guardar en un archivo de texto seguro** (no compartir)

---

## PASO 3: Descargar e Instalar 📦

### Paso 3.1: Descargar ZIP
1. Descargar `kraken_bot_complete_v2.zip`
2. Guardar en una carpeta (ej: `C:\Users\Tu_Usuario\Desktop\bot_trading`)

### Paso 3.2: Extraer ZIP

**En Windows:**
1. Hacer clic derecho en el ZIP
2. Seleccionar "Extraer todo..."
3. Elegir carpeta de destino
4. Hacer clic en "Extraer"

**En Mac/Linux:**
```bash
unzip kraken_bot_complete_v2.zip
```

### Paso 3.3: Abrir Terminal en la Carpeta

**En Windows:**
1. Abrir la carpeta extraída
2. Hacer clic en la barra de direcciones
3. Escribir: `cmd`
4. Presionar Enter

**En Mac:**
1. Abrir Terminal
2. Escribir:
```bash
cd /ruta/a/la/carpeta
```

**En Linux:**
1. Abrir Terminal
2. Escribir:
```bash
cd /ruta/a/la/carpeta
```

### Paso 3.4: Instalar Dependencias

En la terminal, escribir:
```bash
pip install -r requirements.txt
```

Esperar a que termine (puede tomar 2-3 minutos)

---

## PASO 4: Configurar Credenciales ⚙️

### Paso 4.1: Crear Archivo .env

En la terminal, escribir:

**En Windows (Command Prompt):**
```cmd
echo KRAKEN_API_KEY=tu_api_key > .env
echo KRAKEN_API_SECRET=tu_private_key >> .env
```

**En Mac/Linux:**
```bash
cat > .env << EOF
KRAKEN_API_KEY=tu_api_key
KRAKEN_API_SECRET=tu_private_key
EOF
```

### Paso 4.2: Reemplazar Valores

1. Abrir archivo `.env` con editor de texto
2. Reemplazar:
   - `tu_api_key` → Tu API Key de Kraken
   - `tu_private_key` → Tu Private Key de Kraken
3. Guardar archivo

**Ejemplo final:**
```
KRAKEN_API_KEY=vK83Hd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0
KRAKEN_API_SECRET=xK83Hd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0Ld9Kd8Ks0
```

### Paso 4.3: Configurar bot_config.json

1. Abrir `bot_config.json` con editor de texto
2. Cambiar estos valores:

```json
{
  "total_capital": 1000.0,        // Cambiar según tu presupuesto
  "risk_per_trade": 0.01,         // 1% del capital
  "paper_trading": true,          // IMPORTANTE: true para testing
  "trading_pairs": ["XBTUSD"]     // Empezar con 1 par
}
```

3. Guardar archivo

---

## PASO 5: Ejecutar el Bot 🚀

### Paso 5.1: Validar Instalación

En la terminal, escribir:
```bash
python test_bot.py
```

Debe mostrar:
```
Ran 19 tests in X.XXXs
OK
```

### Paso 5.2: Ejecutar en Paper Trading

En la terminal, escribir:
```bash
python trading_bot.py
```

Debe mostrar:
```
2026-01-21 12:00:00 - trading_bot - INFO - Bot de trading inicializado
2026-01-21 12:00:01 - kraken_client - INFO - Conexión establecida
2026-01-21 12:00:02 - trading_bot - INFO - Saldo inicial: {...}
2026-01-21 12:00:03 - trading_bot - INFO - Ciclo de trading iniciado
```

### Paso 5.3: Monitorear el Bot

**En otra terminal:**
```bash
tail -f trading_bot.log
```

Verás logs en tiempo real del bot.

### Paso 5.4: Detener el Bot

En la terminal donde está ejecutándose:
- Presionar **Ctrl+C**

El bot cerrará posiciones y generará un reporte.

---

## PASO 6: Backtesting (Opcional) 📊

### Paso 6.1: Descargar Datos

```bash
python download_historical_data.py
```

Esperar a que descargue (5-10 minutos)

### Paso 6.2: Ejecutar Backtesting

```bash
python backtest_with_real_data.py
```

Verás resultados como:
```
Capital inicial:        $10,000.00
Capital final:          $10,250.00
Retorno total:          2.50%
Max Drawdown:           -12.5%
Sharpe Ratio:           1.45
Win Rate:               52.3%
```

### Paso 6.3: Analizar Resultados

```bash
cat backtest_summary.json
```

---

## 🎯 Resumen de Comandos

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Validar instalación
python test_bot.py

# 3. Ejecutar en paper trading
python trading_bot.py

# 4. Monitorear logs (en otra terminal)
tail -f trading_bot.log

# 5. Descargar datos históricos
python download_historical_data.py

# 6. Ejecutar backtesting
python backtest_with_real_data.py

# 7. Ver resultados
cat backtest_summary.json
```

---

## ⏱️ Tiempo Estimado

| Tarea | Tiempo |
|-------|--------|
| Verificar Python | 5 min |
| Obtener credenciales | 10 min |
| Descargar e instalar | 10 min |
| Configurar | 5 min |
| Validar | 5 min |
| Paper trading | 1-2 semanas |
| Backtesting | 10 min |
| **Total** | **~1 hora** |

---

## ✅ Checklist Final

- [ ] Python 3.8+ instalado
- [ ] ZIP descargado y extraído
- [ ] Dependencias instaladas
- [ ] Credenciales de Kraken obtenidas
- [ ] Archivo .env creado
- [ ] bot_config.json configurado
- [ ] Pruebas pasadas
- [ ] Bot ejecutándose en paper trading
- [ ] Logs monitoreados
- [ ] Backtesting realizado

---

## 🆘 Problemas Comunes

### "Python no encontrado"
```bash
# Verificar ruta de Python
where python          # Windows
which python3         # Mac/Linux
```

### "ModuleNotFoundError"
```bash
# Reinstalar dependencias
pip install -r requirements.txt
```

### "API Key not found"
```bash
# Verificar archivo .env
cat .env              # Mac/Linux
type .env             # Windows
```

### "Connection refused"
```bash
# Verificar internet
ping google.com
```

---

## 📚 Documentación

- **INSTALL.md** - Instalación detallada
- **README.md** - Documentación completa
- **SETUP_GUIDE.md** - Configuración avanzada
- **BACKTESTING_GUIDE.md** - Guía de backtesting

---

## 🎉 ¡Listo!

Sigue estos pasos y tendrás el bot funcionando.

**Tiempo total: ~1 hora**

¿Preguntas? Revisar documentación o logs.
