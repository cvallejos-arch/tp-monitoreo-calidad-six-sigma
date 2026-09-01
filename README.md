# Trabajo Práctico: Sistema de Monitoreo de Calidad Industrial

## Situación Hipotética

**Empresa** fabrica componentes en lotes y evalúa muestras mediante procedimientos de inspección. En la actualidad registra mediciones, calibraciones y defectos en documentos separados: puede utilizar equipos con calibración vencida, cerrar lotes incompletos y producir reportes que no explican qué defectos causaron el rechazo.


## Solución
El equipo presenta un prototipo que coordine inspecciones y determine la calidad de muestras y lotes. El sistema aplica umbrales definidos; y se ocupa de reportar errores o defectos encontrados.

### Objetivo del sistema

El prototipo deberá:

- registrar lotes, muestras, profesionales, equipos y procedimientos;
- verificar certificaciones y vigencia de calibración antes de inspeccionar;
- ejecutar procedimientos diferentes;
- registrar defectos y cerrar muestras mediante modificaciones de estado controladas;
- emitir reportes de desviación trazables (asociado a una muestra y un conjunto de defectos);
- aprobar un lote solo cuando todas sus muestras estén inspeccionadas.


### Arquitectura del Sistema

| Entidad | Representa | Objetivos | 
| --- | --- | --- |
| Lote | Un conjunto de componentes iguales entre sí | permite identificar   | 
| Muestra | Un subconjunto identificado del lote | Defectos, estado y resultado de conformidad | 
| Procedimiento | Interfaz abstracta que define el contrato de inspeccion | Establecer el limite de gravedad acumulada permitida y exigir el método para evaluar observaciones.
| Procedimiento Dimensional| Una forma definida de inspección | Requisitos y criterio para convertir observaciones en defectos |
| Procedimiento  Visual | Una forma definida de inspección | Requisitos y criterio para convertir observaciones en defectos |
| Profesional | Quien ejecuta una inspección | Identidad y certificaciones vigentes | 
| Equipo | Un instrumento de medición | Identidad, categoría y última calibración | 
| Defecto | Una desviación observada | Tipo, descripción y gravedad | 
| Inspección | La ejecución de un procedimiento | Muestra, profesional, equipo, fecha y resultado | 
| Reporte | El respaldo de una muestra no conforme | Causas, responsable y fecha | 


