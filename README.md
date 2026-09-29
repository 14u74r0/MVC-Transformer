# Visor y analísis de imágenes con IA (MVC)

Aplicación web liviana: subís una imagen y un modelo transformer visión-lenguaje (SmolVLM) la describe o responde preguntas sobre ella. Corre 100 % local en la GPU con CUDA.

## Arquitectura MVC

| Capa | Archivo | Qué hace |
|---|---|---|
| Modelo | `app/models/vision_model.py` | Carga el transformer una sola vez y ofrece `describe()` y `ask()` |
| Vista | `app/views/` (`index.html`, `static/`) | HTML, CSS y JS planos, sin frameworks |
| Controlador | `app/controllers/routes.py` | Rutas FastAPI: valida la imagen, llama al modelo, responde JSON |
| Configuración | `app/config.py` | Modelo, límites y prompts en un solo lugar |
| Arranque | `main.py` | Crea la app y carga el modelo al iniciar |

## Instalación (cmd)

```
cd vision-mvc
py -3.12 -m venv venv
venv\Scripts\activate
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
