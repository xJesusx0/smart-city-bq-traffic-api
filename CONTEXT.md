# Proyecto: Sistema Inteligente de Gestión de Semáforos (smart-city-bq)

## 1. Propósito del Proyecto

El proyecto busca **mejorar la movilidad urbana** mediante la automatización inteligente de semáforos.  
El sistema analizará en tiempo real el flujo vehicular y peatonal a partir de cámaras, aplicando modelos de inteligencia artificial que permitan **ajustar los tiempos de semáforos dinámicamente**, con el fin de optimizar la movilidad y aumentar la seguridad vial.

Se enmarca en la visión de **Smart Cities**, aprovechando datos en tiempo real y analítica avanzada.

---

## 2. Flujo General

1. Cámaras → envían video.
2. `video-analysis-service` → procesa video con IA para obtener conteos y patrones de tráfico.
3. `traffic-decision-service` → calcula la mejor estrategia de semaforización.
4. `traffic-lights-service` → ejecuta los comandos sobre los semáforos físicos.
5. Durante todo el proceso, los servicios generan **eventos** (detecciones, decisiones, estados).
6. `traffic-api` → recibe esos eventos, los persiste en la base de datos y los expone al `web-client` para **administración y monitoreo**.

---

## 3. Componentes y Responsabilidades

| Componente                   | Responsabilidades principales                                                                           |
| ---------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Web Client (Svelte)**      | Interfaz para usuarios (login, gestión de roles, monitoreo de semáforos, métricas, acciones).           |
| **Traffic-API**              | Backend administrativo (BFF). Maneja auth/roles, persiste eventos, expone datos al frontend.            |
| **DB-Contract & Main DB**    | Base central de usuarios, roles, logs, métricas e historial de semáforos.                               |
| **Video-Analysis-Service**   | Procesa streams de video, ejecuta detección y conteo con IA, envía resultados al decision-service.      |
| **Traffic-Decision-Service** | Calcula planes de semáforo (tiempos, fases), emite decisiones a lights-service y eventos a traffic-api. |
| **Traffic-Lights-Service**   | Traduce planes en comandos físicos para los semáforos, asegura ejecución segura.                        |
| **AI Models**                | Modelos IA conectados al análisis de video y a la toma de decisiones.                                   |

---

## 4. Contratos

- **Video/Frame Source Contract** → estándar para ingestión de video desde cámaras.
- **Video-Analysis Contract** → resultados del análisis de video (detecciones, conteos, métricas).
- **Decision-Making Contract** → decisiones de semaforización (planes, tiempos, prioridades).
- **Traffic-Light Contract** → comandos para los controladores físicos de semáforos.
- **DB-Contract** → acceso y consistencia en la base de datos central.

---

## 5. Recomendaciones de Diseño

- Usar **eventos/mensajería** para comunicación entre servicios analíticos y administrativos.
- Base relacional (usuarios/roles/logs) + opcional base de series temporales (métricas de tráfico).
- Versionado de modelos IA y despliegue desacoplado (microservicios de inferencia).
- Definir fallback local de semáforos (ciclos básicos) en caso de fallo de comunicación.
- Diseñar métricas, logs y health checks desde el inicio para observabilidad.
