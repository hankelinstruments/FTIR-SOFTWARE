# Analizador FTIR — Industrial Inspection Service

Software de escritorio para procesar espectros FTIR (CSV) y cruzarlos contra una
base de datos de picos característicos de polímeros industriales.

## Desarrollo

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Editar la base de datos de polímeros (laboratorio)

Los datos que usa el software **no están en el código**, viven en dos archivos
JSON dentro de la carpeta `data/` (junto al .exe una vez instalado):

- `data/polymer_db.json` — polímeros y sus bandas características (número de
  onda, intensidad, descripción), densidad y aplicaciones.
- `data/functional_groups.json` — rangos de número de onda asociados a grupos
  funcionales (usado para anotar picos automáticamente).

Se pueden editar con cualquier editor de texto (Notepad, VS Code) siguiendo la
estructura ya presente en el archivo — copiar un bloque de polímero existente,
pegarlo y cambiar los valores es la forma más segura de agregar uno nuevo.
Los cambios se aplican la próxima vez que se abre el programa.

Si el archivo se corrompe (JSON mal formado), el programa lo indica con un
mensaje de error claro al iniciar y sigue funcionando con los valores de
fábrica para esa sesión — sin perder ni sobrescribir el archivo editado, para
que se pueda corregir a mano.

Si se borra la carpeta `data/` por accidente, el programa la vuelve a crear
automáticamente a partir de los valores de fábrica embebidos en el .exe.

**Importante**: estos archivos junto al .exe distribuido son la copia "viva"
del laboratorio. Si se quiere conservar una edición a largo plazo (por ejemplo,
un polímero nuevo que vale la pena mantener en futuras versiones), hay que
copiar manualmente esos cambios al `data/` del repositorio — no hay sincronización
automática entre la copia distribuida y el repositorio, es intencional para
que la edición en campo no dependa de git ni de reconstruir el ejecutable.

## Compilar el ejecutable portable

```
pip install -r requirements.txt
pyinstaller build.spec
```

El resultado queda en `dist/FTIR_Analyzer.exe`. Después de compilar, copiar la
carpeta `data/` del repositorio junto al .exe (solo si `dist/data` no existe
todavía, para no pisar ediciones previas del laboratorio):

```
if (-not (Test-Path dist\data)) { Copy-Item -Path data -Destination dist\data -Recurse }
```

Se distribuye `FTIR_Analyzer.exe` + la carpeta `data/` juntos (por ejemplo,
comprimidos en un .zip).

### Build de depuración

`pyinstaller build_debug.spec` genera `dist/FTIR_Analyzer_debug.exe`, idéntico
pero con consola visible — útil para ver errores durante el desarrollo. No
distribuir esta variante al laboratorio.

Si el ejecutable `--windowed` cierra sin abrir ninguna ventana, revisar si
apareció `crash.log` junto al .exe: la aplicación registra ahí cualquier
excepción no capturada en el arranque.

## Regenerar el ícono

Si el logo (`assets/logo_iis.png`) cambia, regenerar `assets/icon.ico` con:

```
python tools/generate_icon.py
```
