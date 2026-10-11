# PlayTime Tracker 🎮

**PlayTime Tracker** es un plugin para [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader) que registra el tiempo de juego en SteamOS y muestra estadísticas desde el menú de acceso rápido de Steam.

Está desarrollado con **React, TypeScript y Python**, y almacena los datos localmente en **SQLite**.

## Funcionalidades

- Seguimiento automático de juegos de Steam detectados mediante procesos de Linux.
- Estadísticas de tiempo jugado por día, semana, mes, año y total.
- Historial de sesiones y gráficos de actividad.
- Pausa manual del seguimiento y control de suspensión.
- Recordatorios de descanso y límites diarios configurables.
- Exportación de datos a JSON y CSV.
- Información de consumo de batería cuando el sistema ofrece esa métrica.
- Interfaz en **español e inglés**, con selección automática de idioma.

## Instalación

Necesitas tener **Decky Loader** instalado en tu dispositivo con SteamOS.

1. Descarga el ZIP instalable desde las *Releases* del repositorio (cuando esté publicado).
2. Abre **Decky Loader → Configuración → Developer** y activa el modo desarrollador si es necesario.
3. Selecciona **Install Plugin from ZIP** e instala el archivo descargado.
4. Abre **PlayTime Tracker** desde el menú Decky.

## Compilar desde el código fuente

Requisitos: **Node.js, npm y Python 3**.

```bash
npm ci
npm run typecheck
npm run build
python -m unittest discover -s tests -v
python scripts/build_zip.py
```

El instalador se generará con el nombre `PlayTime-Tracker-v<VERSION>-INSTALL.zip`, tomando la versión de `package.json`.

## Estructura del proyecto

```text
backend/      Seguimiento, detección de juegos y SQLite
src/          Interfaz React/TypeScript y traducciones
scripts/      Compilación y empaquetado
tests/       Pruebas automatizadas
main.py       Punto de entrada de Decky Loader
plugin.json   Configuración del plugin
```

## Consideraciones

- Los registros se almacenan **localmente**; el plugin no necesita una cuenta ni servicios en la nube.
- La detección de juegos se basa en procesos de Steam/Linux. **No garantiza que el juego esté en primer plano o que exista interacción activa**; las estadísticas son estimaciones.
- Las métricas de energía dependen de los sensores disponibles en cada dispositivo.

## Licencia

Distribuido bajo la **licencia BSD 3-Clause**. Consulta el archivo [LICENSE](LICENSE).
