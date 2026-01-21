# ⚡ Subir a GitHub en UN SOLO COMANDO

## Opción 1: Script Automático (Recomendado)

```bash
cd /home/ubuntu/kraken_bot && ./auto_upload_github.sh && git push -u origin main
```

Cuando pida credenciales:
- **Username:** `emiliojose1909`
- **Password:** Tu Personal Access Token

---

## Opción 2: Comando Manual

```bash
cd /home/ubuntu/kraken_bot && git remote add origin https://github.com/emiliojose1909/kraken-trading-bot.git && git push -u origin main
```

---

## Opción 3: Usar Git Bundle (Sin Credenciales)

Si no quieres usar credenciales ahora:

1. **Descargar:** `kraken-bot.bundle` (adjunto)

2. **En tu computadora local:**
```bash
# Crear repositorio desde el bundle
git clone kraken-bot.bundle kraken-trading-bot
cd kraken-trading-bot

# Conectar con GitHub
git remote set-url origin https://github.com/emiliojose1909/kraken-trading-bot.git

# Subir
git push -u origin main
```

---

## 🔑 Generar Personal Access Token

1. Ir a: https://github.com/settings/tokens
2. Click: "Generate new token (classic)"
3. Seleccionar: ✓ repo
4. Copiar token
5. Usar como password

---

## ✅ Verificar que Subió

Después de hacer push, ir a:
**https://github.com/emiliojose1909/kraken-trading-bot**

Deberías ver:
- ✓ 24 archivos
- ✓ README profesional
- ✓ Documentación completa
- ✓ Commit inicial

---

**¡Eso es todo!** 🚀
