# Trabajo Práctico: Sistema de Monitoreo de Calidad Industrial

## Situación Hipotética

**Empresa de tecnología** fabrica componentes en lotes y evalúa muestras mediante procedimientos de inspección. En la actualidad registra mediciones, calibraciones y defectos en documentos separados: puede utilizar equipos con calibración vencida, cerrar lotes incompletos y producir reportes que no explican qué defectos causaron el rechazo.


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
| Lote | Un conjunto de componentes iguales entre sí | Permite a la empresa decidir si está listo o no para su uso. Sus datos permiten crear Muestras | 
| Muestra | Un subconjunto identificado del lote | Defectos, estado y resultado de conformidad | 
| Procedimiento | Interfaz abstracta que define el contrato de inspeccion | Establecer el limite de gravedad acumulada permitida y exigir el método para evaluar observaciones.
| Procedimiento Dimensional| Especialización basada en mediciones físicas. | Comparar valores medidos contra tolerancias (mín/máx) y transformarlos en defectos de tipo "DIMENSIONAL". |
| Procedimiento  Visual | Especialización basada en observación cualitativa. | Registrar descripciones de anomalías estéticas o funcionales y transformarlas en defectos de tipo "VISUAL". |
| Profesional | El operario o técnico de calidad a cargo | Garantizar su propria identidad y validar si posee las certificationes requeridas vigentes en la fecha de la inspeccion | 
| Equipo | El instrumento utilizado para medir o evaluar | Validar que sea la categoria adecuada y certificar que su calibracion no exceda el maximo legal (182 dias). | 
| Defecto | Una anomalía específica hallada durante la evaluación. | Contener de manera inmutable el tipo, la descripción y el nivel de gravedad (escala 1 a 5). | 
| Inspección | El evento transaccional que une todos los elementos. | Coordinar y validar los requisitos (certificación, calibración, estados) de forma previa, bloqueando el contexto durante la ejecución. | 
| Reporte | El documento de respaldo oficial ante un rechazo. | Congelar une "foto" inalterable con las causas (defectos), fecha y responsable de cualquier muestra que resulte NO_CONFORME | 

### Estructura del Repo

Se detalla la función de cada archivo y clase dentro del proyecto como si ya estuviese completamente implementado:


#### 1. Utilidades y Configuración Base

- **`excepciones.py`**: Define excepciones de dominio personalizadas (ej. `DatosInvalidosError`, `TransicionIlegalError`, `CalibracionVencidaError`, `CertificacionFaltanteError`).

#### 2. Entidades de Calidad (Dominio)
- **`defecto.py` (`Defecto`)**: Representa una desviación observada. Encapsula el tipo, descripción y gravedad (1 a 5, donde 5 es crítico). Es inmutable tras su creación.
- **`muestra.py` (`Muestra`)**: Representa un subconjunto del lote. Controla sus propios estados (`PENDIENTE`, `EN_INSPECCION`, `CONFORME`, `NO_CONFORME`). Es la encargada de agrupar defectos e impedir modificaciones una vez cerrada.
- **`lote.py` (`Lote`)**: Representa una partida de componentes. Valida que las muestras le pertenezcan y no excedan su capacidad. Calcula si el lote es `APROBADO` o `RECHAZADO` evaluando el % de muestras no conformes (> 5%).
- **`reporte.py` (`Reporte`)**: Generado automáticamente y de forma inmutable cuando una muestra se cierra como `NO_CONFORME`. Almacena una copia estática de las causas (defectos), responsable y fecha.

#### 3. Actores y Recursos
- **`profesional.py` (`Profesional`)**: Representa al inspector. Conoce su identidad y gestiona sus certificaciones, pudiendo validar si posee una certificación vigente para la fecha requerida.
- **`equipo.py` (`Equipo`)**: Representa un instrumento de medición. Valida si es de la categoría correcta y si su calibración está vigente (no más de 182 días de antigüedad respecto a la fecha de inspección).

#### 4. Motor de Inspecciones
- **`inspeccion.py` (`Inspeccion`)**: Coordina el proceso. Relaciona la `Muestra`, el `Profesional`, el `Equipo` y el `Procedimiento`. Se encarga de validar los requisitos cruzados *antes* de iniciar (profesional certificado, equipo calibrado) y bloquea el contexto para que no cambien durante la ejecución.

#### 5. Procedimientos y Polimorfismo
- **`procedimiento.py` (`Procedimiento`)**: Clase abstracta (interfaz) que define el comportamiento esperado de cualquier inspección. Contiene el límite de gravedad acumulada y define el método polimórfico `evaluar(observaciones)`.
- **`proc_dimensional.py` (`ProcedimientoDimensional`)**: Hereda de `Procedimiento`. Evalúa observaciones basadas en medidas numéricas (valor medido vs tolerancias min/max) y genera defectos de tipo "DIMENSIONAL".
- **`proc_visual.py` (`ProcedimientoVisual`)**: Hereda de `Procedimiento`. Evalúa observaciones visuales de los operarios y genera defectos de tipo "VISUAL".

#### 6. Ejecución y Pruebas
- **`main.py`**: Punto de entrada del programa. Ejecuta una simulación completa (End-to-End) creando lotes, asignando muestras, ejecutando inspecciones visuales y dimensionales, y mostrando por consola el veredicto final.

#### 7. Directorio de Tests (`/tests`)
Pruebas automatizadas construidas con `pytest` que garantizan el cumplimiento de las 12 reglas de negocio:
- **`test_validacion.py`**: Pruebas unitarias de las funciones de validación de datos base.
- **`test_defecto.py`**: Pruebas de la creación, inmutabilidad y límites de gravedad (1-5).
- **`test_muestra.py`** y **`test_estado_muestra.py`**: Pruebas de los estados (PENDIENTE, EN_INSPECCION, etc.), manejo de defectos y cálculo de conformidad.
- **`test_lote.py`** y **`test_estado_lote.py`**: Pruebas de la agregación de muestras, porcentajes de no conformidad y la decisión final de aprobación o rechazo.
- **`test_profesional.py`** y **`test_certificacion.py`**: Verificación de identidades y límites de vigencia de las certificaciones en la fecha de inspección.
- **`test_equipo.py`**: Verificación de categorías compatibles y del cálculo de calibración en el límite de los 182 días.
- **`test_procedimeinto.py`**: Comprobación del polimorfismo entre los distintos métodos visuales y dimensionales. *(Nota: archivo escrito como 'procedimeinto' en el respositorio)*.
- **`test_inspeccion.py`**: Pruebas de validación cruzada antes de iniciar la evaluación, asegurando que el contexto se congele durante la ejecución.
- **`test_reporte.py`**: Validación de la generación de la copia estática e inmutable de los defectos cuando una muestra resulta rechazada.

---

## Cómo ejecutar (Simulación)

Dado que es un sistema Core sin UI, la ejecucion se realiza corriendo el flujo principal o los tests:

1. Instalar dependencias para pruebas (solo se requiere `pytest`):
   ```bash
   pip install pytest
   ```
2. Ejecutar la suite de pruebas automatizadas:
   ```bash
   pytest
   ```
3. Ejecutar la simulación completa del flujo:
   ```bash
   python main.py
   ```

---
## Diagrama Mermaid 

```mermaid
classDiagram
    direction TB

    %% ══════════════════════════════════════════════
    %% Administrador (represente main.py)
    %% ══════════════════════════════════════════════

    class Administrador {
        +registrar_lote(id str, cantidad int) Lote
        +registrar_muestra(id str, cantidad int) Muestra
        +registrar_profesional(id str, nombre str) Profesional
        +registrar_equipo(id str, categoria str, fecha_calibracion date) Equipo
        +registrar_procedimiento(proc Procedimiento)
        +lanzar_inspeccion(muestra Muestra, profesional Profesional, equipo Equipo, procedimiento Procedimiento, fecha date) Inspeccion
    }

    %% ══════════════════════════════════════════════
    %% ÉTAPE 1 — Enums
    %% ══════════════════════════════════════════════

    class EstadoMuestra {
        <<enum>>
        PENDIENTE
        EN_INSPECCION
        CONFORME
        NO_CONFORME
    }

    class EstadoLote {
        <<enum>>
        EN_PRODUCCION
        APROBADO
        RECHAZADO
    }

    %% ══════════════════════════════════════════════
    %% ÉTAPE 1 — Defecto
    %% ══════════════════════════════════════════════

    class Defecto {
        -_tipo : str
        -_descripcion : str
        -_gravedad : int
        +tipo : str
        +descripcion : str
        +gravedad : int
        +es_critico() bool
        +copia() Defecto
    }

    %% ══════════════════════════════════════════════
    %% ÉTAPE 1 — Muestra
    %% ══════════════════════════════════════════════

    class Muestra {
        -_id : str
        -_cantidad : int
        -_estado : EstadoMuestra
        -_defectos : list~Defecto~
        -_lote_id : str
        -_inspeccion : Inspeccion
        -_reporte : Reporte
        +id : str
        +cantidad : int
        +estado : EstadoMuestra
        +defectos : tuple~Defecto~
        +lote_id : str
        +reporte : Reporte
        +asignar_lote(lote_id str)
        +iniciar_inspeccion()
        +agregar_defecto(defecto Defecto)
        +cerrar(limite_gravedad int) Reporte
        +suma_gravedades() int
        +tiene_critico() bool
    }

    %% ══════════════════════════════════════════════
    %% ÉTAPE 1 — Lote
    %% ══════════════════════════════════════════════

    class Lote {
        -_id : str
        -_cantidad_fabricada : int
        -_estado : EstadoLote
        -_muestras : dict~str Muestra~
        +id : str
        +cantidad_fabricada : int
        +estado : EstadoLote
        +muestras : tuple~Muestra~
        +nombre_componente : str
        +agregar_muestra(muestra Muestra)
        +decidir() EstadoLote
        +porcentaje_no_conforme() float
        +todas_cerradas() bool
        +total_defectos_criticos() int
        +conteo_por_tipo() dict~str int~
    }

    %% ══════════════════════════════════════════════
    %% ÉTAPE 2 — Certificacion
    %% ══════════════════════════════════════════════

    class Certificacion {
        -_nombre : str
        -_fecha_inicio : date
        -_fecha_fin : date
        +nombre : str
        +es_vigente(fecha date) bool
    }

    %% ══════════════════════════════════════════════
    %% ÉTAPE 2 — Profesional
    %% ══════════════════════════════════════════════

    class Profesional {
        -_id : str
        -_nombre : str
        -_certificaciones : list~Certificacion~
        +id : str
        +nombre : str
        +agregar_certificacion(cert Certificacion)
        +tiene_certificacion_vigente(nombre str, fecha date) bool
    }

    %% ══════════════════════════════════════════════
    %% ÉTAPE 2 — Equipo
    %% ══════════════════════════════════════════════

    class Equipo {
        -_id : str
        -_categoria : str
        -_fecha_calibracion : date
        +id : str
        +categoria : str
        +fecha_calibracion : date
        +esta_calibrado(fecha date) bool
        +es_compatible(categoria_requerida str) bool
    }

    %% ══════════════════════════════════════════════
    %% ÉTAPE 2 — Inspeccion
    %% ══════════════════════════════════════════════

    class Inspeccion {
        -_id : str
        -_muestra : Muestra
        -_profesional : Profesional
        -_equipo : Equipo
        -_procedimiento : Procedimiento
        -_fecha : date
        -_defectos : list~Defecto~
        -_cerrada : bool
        +id : str
        +muestra_id : str
        +profesional_id : str
        +equipo_id : str
        +procedimiento_id : str
        +fecha : date
        +defectos : tuple~Defecto~
        +ejecutar(observaciones list)
        +cerrar() Reporte
    }

    %% ══════════════════════════════════════════════
    %% ÉTAPE 3 — Reporte
    %% ══════════════════════════════════════════════

    class Reporte {
        -_muestra_id : str
        -_lote_id : str
        -_profesional_id : str
        -_fecha : date
        -_defectos : tuple~Defecto~
        +muestra_id : str
        +lote_id : str
        +profesional_id : str
        +fecha : date
        +defectos : tuple~Defecto~
    }

    %% ══════════════════════════════════════════════
    %% ÉTAPE 4 — Polymorphisme
    %% ══════════════════════════════════════════════

    class Procedimiento {
        <<abstract>>
        -_id : str
        -_limite_gravedad_acumulada : int
        -_categoria_equipo_requerida : str
        -_certificacion_requerida : str
        +id : str
        +limite_gravedad_acumulada : int
        +categoria_equipo_requerida : str
        +certificacion_requerida : str
        +evaluar(observaciones list) list~Defecto~*
    }
    note for Procedimiento "_certificacion_requerida puede ser None (regla 5)"

    class ProcedimientoDimensional {
        +evaluar(observaciones list) list~Defecto~
    }

    class ProcedimientoVisual {
        +evaluar(observaciones list) list~Defecto~
    }

    %% ══════════════════════════════════════════════
    %% RELATIONS
    %% ══════════════════════════════════════════════

    %% Etapa 1 — Estructura base
    Lote "1" o-- "0..*" Muestra : contiene
    Muestra "1" *-- "0..*" Defecto : acumula
    Muestra "1" --> "0..1" Reporte : genera si NO_CONFORME

    %% Etapa 1 — Dependencias enums
    Muestra ..> EstadoMuestra : usa
    Lote ..> EstadoLote : usa

    %% Etapa 2 — Inspeccion
    Inspeccion "1" --> "1" Muestra : evalua
    Inspeccion "1" --> "1" Profesional : ejecutada por
    Inspeccion "1" --> "1" Equipo : utiliza
    Inspeccion "1" --> "1" Procedimiento : guiada por

    %% Etapa 2 — Profesional
    Profesional "1" *-- "0..*" Certificacion : posee

    %% Etapa 3 — Reporte
    Reporte "1" *-- "1..*" Defecto : copia fija

    %% Etapa 4 — Herencia
    Procedimiento <|-- ProcedimientoDimensional
    Procedimiento <|-- ProcedimientoVisual

    %% Administrador — crea y coordina todo
    Administrador ..> Lote : registra
    Administrador ..> Muestra : registra
    Administrador ..> Profesional : registra
    Administrador ..> Equipo : registra
    Administrador ..> Procedimiento : registra
    Administrador ..> Inspeccion : lanza
```
