# ⚡ Inicio Rápido en 5 Minutos

## Si tienes prisa, aquí está lo esencial:

### 1️⃣ Descargar e Instalar (2 min)
```bash
unzip kraken_bot_complete_final.zip
cd kraken_bot
pip install -r requirements.txt
```

### 2️⃣ Obtener Credenciales de Kraken (1 min)
1. Ir a: https://www.kraken.com/c/account-settings/api
2. Generar nueva key
3. Copiar API Key y Private Key

### 3️⃣ Configurar (1 min)
```bash
# Crear archivo .env
cat > .env << EOF
KRAKEN_API_KEY=tu_api_key
KRAKEN_API_SECRET=tu_private_key
EOF
```

### 4️⃣ Ejecutar (1 min)
```bash
python trading_bot.py
```

**¡Listo!** El bot está funcionando en paper trading.

---

## Próximos Pasos

- Monitorear logs: `tail -f trading_bot.log`
- Detener: `Ctrl+C`
- Backtesting: `python backtest_with_real_data.py`

---

## Documentación Completa

- **STEP_BY_STEP.md** - Guía visual paso a paso
- **IMPLEMENTATION_GUIDE.md** - Guía completa de implementación
- **README.md** - Documentación técnica

---

**¡Eso es todo!** 🚀
