# Docker

Docker es una plataforma de contenedores que permite empaquetar una aplicación y todas sus dependencias en una unidad portable y reproducible llamada **imagen**.

## Conceptos fundamentales

- **Imagen**: plantilla inmutable con el sistema de ficheros de la aplicación. Se construye con un `Dockerfile`.
- **Contenedor**: instancia en ejecución de una imagen. Aislado del host pero comparte el kernel.
- **Registry**: repositorio de imágenes. El público es Docker Hub; los privados suelen ser ECR, GCR o Harbor.
- **Dockerfile**: script de instrucciones para construir una imagen.
- **Docker Compose**: herramienta para definir y arrancar varios contenedores con un fichero `docker-compose.yml`.

## Dockerfile básico para una app Python

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Comandos esenciales

```bash
docker build -t mi-app:v1 .          # construir imagen
docker run -p 8000:8000 mi-app:v1    # arrancar contenedor
docker ps                            # listar contenedores activos
docker logs <id>                     # ver logs de un contenedor
docker stop <id>                     # parar contenedor
docker rm <id>                       # eliminar contenedor parado
docker images                        # listar imágenes locales
docker rmi <imagen>                  # eliminar imagen
docker exec -it <id> bash            # shell interactivo en contenedor
```

## Docker Compose

```yaml
version: "3.9"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MODE=prod
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
```

```bash
docker compose up -d      # arrancar en background
docker compose down       # parar y eliminar contenedores
docker compose logs -f    # seguir logs en tiempo real
```

## Buenas practicas

1. Usar imágenes base `slim` o `alpine` para reducir tamaño.
2. No ejecutar como root dentro del contenedor.
3. Separar la fase de instalación de dependencias de la copia del código fuente para aprovechar la caché de capas.
4. No incluir secretos en la imagen; usar variables de entorno o secrets.
5. Etiquetar imágenes con versiones semánticas, no solo `latest`.
