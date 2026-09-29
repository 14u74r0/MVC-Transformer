# Visor de imágenes con IA (MVC)

Aplicación web liviana: subís una imagen y un modelo transformer visión-lenguaje (SmolVLM) la describe o responde preguntas sobre ella. Corre 100 % local en la GPU con CUDA.

## Arquitectura MVC

| Capa | Archivo | Qué hace |
|---|---|---|
| Modelo | `app/models/vision_model.py` | Carga el transformer una sola vez y ofrece `describe()` y `ask()` |
| Vista | `app/views/` (`index.html`, `static/`) | HTML, CSS y JS planos, sin frameworks |
| Controlador | `app/controllers/routes.py` | Rutas FastAPI: valida la imagen, llama al modelo, responde JSON |
| Configuración | `app/config.py` | Modelo, límites y prompts en un solo lugar |
| Arranque | `main.py` | Crea la app y carga el modelo al iniciar |

## Requisitos

- Python 3.10 a 3.12 (recomendado 3.12)
- Driver de NVIDIA actualizado (versión 570 o superior para la RTX 5070 Ti)
- **No hace falta instalar el CUDA Toolkit**: PyTorch ya trae el runtime de CUDA adentro.
- Internet solo la primera vez, para descargar el modelo (unos cientos de MB)

## Instalación en Windows 11 (cmd)

```
cd vision-mvc
py -3.12 -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
pip install -r requirements.txt
```

## Instalación en Nobara (terminal)

```
cd vision-mvc
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
pip install -r requirements.txt
```

Si `python3 --version` da 3.13 o más y algo falla al instalar, instalá Python 3.12 (`sudo dnf install python3.12`) y creá el entorno con `python3.12 -m venv venv`.

## Verificar que la GPU se detecta

```
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

Tiene que imprimir `True` y el nombre de tu placa. Si imprime `False`, PyTorch se instaló sin CUDA (repetí el `pip install torch` con el índice `cu128`) o el driver está desactualizado.

## Ejecutar

```
python main.py
```

Abrí http://127.0.0.1:8000 en el navegador. La primera vez tarda porque descarga el modelo.

## Cambiar de modelo (sin tocar código)

Windows:
```
set VISION_MODEL_ID=HuggingFaceTB/SmolVLM-Instruct
python main.py
```

Nobara:
```
VISION_MODEL_ID=HuggingFaceTB/SmolVLM-Instruct python main.py
```

| Modelo | Tamaño | Pensado para |
|---|---|---|
| `SmolVLM-256M-Instruct` | 256M | Prueba mínima |
| `SmolVLM-500M-Instruct` (por defecto) | 500M | Laptop con 6 GB de VRAM |
| `SmolVLM-Instruct` | 2.2B | PC de escritorio con 16 GB de VRAM |

## Cosas a tener en cuenta

- El modelo responde mejor en **inglés**. Las preguntas en español suelen funcionar, pero la calidad es menor.
- Solo se procesa una imagen a la vez (hay un bloqueo para no saturar la GPU).
- Las imágenes se reducen a 1024 px de lado mayor antes de analizarse.
- Por ahora acepta **imágenes**. Para video, el siguiente paso natural es extraer algunos fotogramas y pasarlos al mismo modelo.

## Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `no kernel image is available` en la 5070 Ti | PyTorch sin soporte Blackwell | Reinstalar con `--index-url .../cu128` |
| `torch.cuda.is_available()` da `False` | Torch sin CUDA o driver viejo | Reinstalar torch y actualizar driver |
| Error de memoria (OOM) | Modelo o imagen muy grande para la VRAM | Usar un modelo más chico |
| `ModuleNotFoundError: num2words` | Falta dependencia del procesador | `pip install num2words` |

## Subir a GitHub

```
git init
git add .
git commit -m "Primera versión"
git branch -M main
git remote add origin https://github.com/<tu-usuario>/vision-mvc.git
git push -u origin main
```

En la otra PC: `git clone` de ese repositorio y repetir la instalación de arriba.
