# Tareas — Spec 003: Contenerización y Despliegue en la Nube

- [x] **T1. Configuración de Dockerfile y .dockerignore.** RF-1, RF-2, RF-3
  - Hecho cuando: Existan `Dockerfile` con instalación de `ffmpeg` y arranque dinámico con `$PORT`, y `.dockerignore` excluyendo `.env` y archivos temporales.
- [x] **T2. Aseguramiento de repositorio Git y .gitignore.** RF-5, RNF-1
  - Hecho cuando: `.gitignore` garantice la exclusión de `.env` y archivos no versionables, el repositorio local esté inicializado con un commit limpio listo para GitHub.
- [x] **T3. Subida a GitHub y vinculación con Render Web Service.** RF-4, RF-5
  - Hecho cuando: El código esté alojado en un repositorio de GitHub y conectado a Render configurando las variables de entorno de producción.
- [x] **T4. Verificación de producción y actualización del Webhook de Meta.** RF-4, RF-6
  - Hecho cuando: El endpoint `/health` en Render responda 200 OK y el webhook en Meta Developers esté verificado apuntando a `https://tu-app.onrender.com/webhook`.
