# Resumen Completo del Proyecto -- TP Monitoreo Calidad Six Sigma

## 1. Contexto del Proyecto

### Situacion
La empresa **QuantumTech Precision** fabrica componentes en lotes y evalua muestras mediante procedimientos de inspeccion. Actualmente registra mediciones, calibraciones y defectos en documentos separados. Consecuencia: puede utilizar equipos con calibracion vencida, cerrar lotes incompletos y producir reportes que no explican que defectos causaron el rechazo.

### Objetivo
Construir un **prototipo** que:
- Registre lotes, muestras, profesionales, equipos y procedimientos
- Verifique certificaciones y vigencia de calibracion **antes** de inspeccionar
- Ejecute procedimientos con comportamientos de evaluacion **diferentes** (polimorfismo)
- Registre defectos y cierre muestras mediante **transiciones de estado controladas**
- Emita reportes de desviacion trazables
- Decida un lote **unicamente** cuando todas sus muestras esten inspeccionadas

### Reglas de negocio clave
- Gravedad: entero de 1 a 5 (5 = critico)
- Calibracion valida: `fecha_inspeccion - fecha_calibracion <= 182 dias` (limites inclusivos)
- Conformidad: `NO_CONFORME` si defecto critico O suma gravedades > limite
- Decision del lote: `RECHAZADO` si % no conforme > 5%, de lo contrario `APROBADO` (5% exacto = APROBADO)

---

## 2. Logica de Funcionamiento Global: ¿Quien crea que, en que orden y por que?

Para comprender adecuadamente la arquitectura del proyecto, es fundamental visualizar el **ciclo de vida operativo** del sistema industrial: que componente interviene, quien es responsable de la instanciacion y por que este orden cronologico es indispensable para satisfacer las reglas del dominio.

```
       ┌────────────────────────────────────────────────────────┐
       │                  EMPRESA (Fachada)                     │
       │ Punto de entrada unico para inicializar y registrar    │
       └────┬──────────────┬───────────────┬──────────────┬─────┘
            │ 1            │ 2             │ 3            │ 4
            ▼              ▼               ▼              ▼
       ┌─────────┐   ┌────────────┐   ┌─────────┐  ┌──────────────┐
       │  LOTE   │   │PROFESIONAL │   │ EQUIPO  │  │PROCEDIMIENTO │
       └────┬────┘   └─────┬──────┘   └────┬────┘  └──────┬───────┘
            │ crea         │ posee         │ apto         │ reglas
            ▼ (compos.)    ▼               │              │
       ┌─────────┐   ┌────────────┐        │              │
       │ MUESTRA │   │CERTIFICAC. │        │              │
       └────┬────┘   └─────┬──────┘        │              │
            │              │               │              │
            └──────────────┼───────────────┼──────────────┘
                           │ 5. Lanzamiento
                           ▼
                  ┌──────────────────┐
                  │    INSPECCION    │ ───► Valida requisitos "Fail-Fast"
                  └────────┬─────────┘      (calibracion, certif, compatibilidad)
                           │ 6. Ejecucion
                           ▼
                  ┌──────────────────┐
                  │ OBSERVACIONES    │ ───► Evaluadas polimorficamente
                  └────────┬─────────┘      genera DEFECTOS
                           │ 7. Cierre
                           ▼
                  ┌──────────────────┐
                  │ MUESTRA (Cierre) │ ───► CONFORME o NO_CONFORME
                  └────────┬─────────┘      (crea REPORTE si NO_CONFORME)
                           │ 8. Veredicto final
                           ▼
                  ┌──────────────────┐
                  │  LOTE (Decision) │ ───► APROBADO (<=5%) o RECHAZADO (>5%)
                  └──────────────────┘
```

### 2.1 Los Actores y sus Responsabilidades en el flujo

1. **La Fachada (`Empresa`)**: Es el orquestador global. En lugar de que el codigo cliente instancie manualmente cada objeto conociendo detalles internos, `Empresa` provee una API unificada (`crear_registrar_*`, `lanzar_inspeccion`). Centraliza todos los registros en diccionarios categorizados.
2. **La Produccion (`Lote` y `Muestra`)**: El nucleo manufacturero. El lote representa la partida completa de componentes fabricados. Las muestras son subconjuntos extraidos para ensaye.
3. **Los Recursos de Control (`Profesional` + `Certificacion`, `Equipo`)**: El personal tecnico y el instrumental de medicion que deben contar con vigencia formal en la fecha del control.
4. **El Marco Normativo (`Procedimiento`)**: Reglas tecnicas de evaluacion (visual o dimensional) con sus limites de gravedad acumulada y tolerancias.
5. **El Evento Transaccional (`Inspeccion`)**: La sesion de evaluacion que une a una muestra, un profesional calificado, un equipo calibrado y un procedimiento especifico en una fecha determinada.
6. **El Respaldo Documental (`Reporte` y `Defecto`)**: Evidencia inalterable y congelada de las causas de cualquier rechazo.

---

### 2.2 Desarrollo cronologico detallado: ¿Quien crea que y por que?

#### 1. Creacion del Lote (`Lote`) y de sus Muestras (`Muestra`) -- *Composicion estricta*
- **¿Quien crea?** La empresa instancia el `Lote` (`empresa.crear_registrar_lote`). Luego, para crear las muestras, la empresa **delega la creacion directamente al lote** (`empresa.crear_registrar_muestra(cantidad, lote)` que invoca a `lote.crear_muestra(cantidad)`).
- **¿Por que en este orden?**
  - **Sentido del dominio**: Una muestra fisica no puede existir suspendida en la nada; es por definicion un subconjunto de un lote especifico.
  - **Regla 2 de la consigna**: *"Cada muestra pertenece a exactamente un lote"*.
  - **Validacion de capacidad**: El lote debe existir previamente para constatar que la sumatoria de muestras no exceda la cantidad fabricada (`capacidad_usada + cantidad <= cantidad_fabricada`).
  - **Ciclo de vida ligado (Composicion)**: El identificador `_lote_id` queda establecido desde la construccion de la muestra y es inmutable.

#### 2. Registro de Inspectores (`Profesional`) y sus Certificaciones (`Certificacion`)
- **¿Quien crea?** La empresa registra al `Profesional`. Luego se le incorporan las certificaciones vigentes (`prof.agregar_certificacion(cert)`).
- **¿Por que en este orden?**
  - Una certificacion carece de validez sin estar adjudicada a un profesional individual.
  - La acreditacion debe estar registrada **antes** de intentar inspeccionar para que el sistema valide si el profesional esta habilitado a la fecha de la prueba.

#### 3. Registro de Instrumentos de Medicion (`Equipo`) y Calibracion
- **¿Quien crea?** La empresa registra cada equipo con su categoria tecnica (ej: `"Visual"`, `"Dimensional"`) y su fecha de calibracion.
- **¿Por que en este orden?**
  - Ninguna medicion de calidad es valida si el instrumento no esta registrado y debidamente calibrado (maximo 182 dias de antiguedad). El equipo debe estar disponible de antemano.

#### 4. Definicion de Procedimientos de Inspeccion (`Procedimiento`)
- **¿Quien crea?** La empresa configura las instancias de procedimientos concretos (`ProcedimientoVisual`, `ProcedimientoDimensional`) usando `**kwargs`.
- **¿Por que en este orden?**
  - El procedimiento establece las condiciones normativas: que tipo de equipo requiere, que certificacion exige y cual es el umbral de gravedad permitida. Sin esto, la inspeccion no posee criterios sobre los cuales evaluar.

#### 5. Lanzamiento de la Inspeccion (`Inspeccion`) -- *Validacion cruzada "Fail-Fast"*
- **¿Quien crea?** La empresa ejecuta `empresa.lanzar_inspeccion(muestra, profesional, equipo, procedimiento, fecha)`.
- **¿Por que aqui y como?**
  - Es el punto de validacion de integridad. El constructor de `Inspeccion` aplica el patron **Fail-Fast**:
    1. Verifica que la muestra se encuentre en estado `PENDIENTE`.
    2. Verifica que el profesional cuente con la certificacion requerida activa a la fecha indicada (`es_vigente(fecha)`).
    3. Verifica que el equipo pertenezca a la categoria que exige el procedimiento (`es_compatible()`).
    4. Verifica que el equipo tenga calibracion vigente ($\le 182$ dias) a la fecha (`esta_calibrado(fecha)`).
  - **Si alguna condicion no se cumple**: se lanza de inmediato la excepcion correspondiente, el objeto `Inspeccion` nunca llega a crearse y la muestra permanece intacta en `PENDIENTE` (Regla 5).
  - **Si todo es correcto**: la muestra avanza al estado `EN_INSPECCION` y se asocia a la inspeccion (`asignar_inspeccion`). El contexto queda congelado.

#### 6. Evaluacion de Observaciones y Deteccion de Defectos (`Defecto`) -- *Polimorfismo*
- **¿Quien hace que?** Se ingresan observaciones a `inspeccion.ejecutar(observaciones)`.
- **¿Por que el polimorfismo?**
  - La inspeccion delega ciegamente a `self._procedimiento.evaluar(observaciones)`.
  - Si es dimensional, compara medidas contra tolerancias y calcula la gravedad segun la desviacion.
  - Si es visual, identifica anomalias cualitativas y las asigna con su severidad.
  - Cada defecto hallado se acumula en la muestra (`muestra.agregar_defecto(defecto)`).

#### 7. Cierre de la Muestra y Trazabilidad (`Reporte`)
- **¿Quien hace que?** Se ejecuta `inspeccion.cerrar()`, lo que dispara `muestra.cerrar(limite_gravedad)`.
- **¿Por que y cual es el efecto?**
  - La muestra determina su estado final:
    - Si contiene algun defecto critico (gravedad = 5) O si la suma de gravedades supera el limite del procedimiento $\rightarrow$ `NO_CONFORME`.
    - De lo contrario $\rightarrow$ `CONFORME`.
  - **Generacion automatica de `Reporte`**: Si la muestra resulta `NO_CONFORME`, se genera un reporte inmutable con copias estaticas de los defectos, fecha, lote y responsable.
  - La muestra queda cerrada e inmutable (se bloquean modificaciones o nuevas inspecciones).

#### 8. Decision Final sobre el Lote (`Lote.decidir()`) -- *Criterio Six Sigma*
- **¿Quien decide?** El propio `Lote`.
- **¿Por que al final?**
  - No puede decidirse un lote incompleto. Verifica que **todas** sus muestras esten cerradas (`todas_cerradas() == True`).
  - Calcula el porcentaje de no conformidad (`porcentaje_no_conforme()`).
  - Si es $> 5\%$ $\rightarrow$ `RECHAZADO`. Si es $\le 5\%$ (5% exacto inclusive) $\rightarrow$ `APROBADO`.
  - El lote asume un estado definitivo e irreversible.

---

## 3. Arquitectura Detallada y Analisis de Archivos

Una vez comprendida la logica global, examinamos cada archivo, sus elecciones de diseño y especificidades tecnicas en Python.

### 3.1 Archivos base

#### `excepciones.py` -- Excepciones custom
**Utilidad**: Definir excepciones de dominio especificas en lugar de usar `ValueError` generico.

**Especificidades Python**:
- **Herencia de clases**: todas heredan de `CalidadError`, que hereda de `Exception`
- **Jerarquia de excepciones**: permite capturar `CalidadError` para atrapar TODAS las fallas del dominio, o capturar un tipo exacto

**¿Por que custom en lugar de ValueError?**
La consigna lo exige (regla 86). Facilita discriminar errores de logica de negocio de fallas genericas del interprete.

**Clases**:
| Excepcion | Uso |
|---|---|
| `CalidadError` | Clase base comun |
| `DatosInvalidosError` | Datos fuera de formato o rango (cantidades, gravedades, textos vacios) |
| `EquipoNoAptoError` | Equipo descalibrado o categoria incompatible |
| `CertificacionNoVigenteError` | Certificacion ausente o caducada a la fecha de control |
| `TransicionIlegalError` | Cambios de estado no permitidos (cerrar muestra ya cerrada, capacidad superada) |
| `InspeccionInvalidaError` | Intentos de operar sobre inspeccion cerrada |

---

#### `validacion.py` -- Funciones de validacion centralizadas
**Utilidad**: Centralizar la logica de validacion (principio DRY). Cada clase recurre a estas funciones evitando duplicacion.

**Especificidades Python**:
- **Funciones puras**: reciben un valor, validan y retornan o lanzan excepcion
- **`isinstance(valor, int) or isinstance(valor, bool)`**: en Python, `bool` hereda de `int` (`True == 1`). Debe descartarse explcitamente el booleano
- **f-strings**: interpolacion eficiente y limpia

**¿Por que retornar el valor?**
Permite la asignacion directa: `self._cantidad = validar_cantidad(cantidad)`.

**Funciones**:
| Funcion | Valida | Retorna |
|---|---|---|
| `validar_entero(valor)` | Es int (no bool) | El valor |
| `validar_cantidad(cantidad)` | Int > 0 | El valor |
| `validar_gravedad(gravedad)` | Int entre 1 y 5 | El valor |
| `validar_texto(texto)` | String no vacio, solo caracteres alfabeticos | El valor |
| `validar_descripcion(descripcion)` | String no vacio (acepta digitos) | El valor |
| `validar_fecha_tipo(fecha)` | Instancia de `date` | El valor |
| `validar_rango_fechas(inicio, fin)` | inicio <= fin | None |
| `validar_rango_entero(valor, min, max)` | Int en [min, max] | El valor |

---

### 3.2 Enums

#### `estado_muestra.py` y `estado_lote.py`
**Utilidad**: Modelar los estados finitos de muestras y lotes mediante constantes inmutables.

**Especificidades Python**:
- **`Enum`**: previene el empleo de cadenas libres. Valida por identidad (`==`)
- **`.value`**: expone el texto representativo

---

### 3.3 Clases de dominio

#### `defecto.py` -- Defecto
**Utilidad**: Registra una anomalia observada. Inmutable tras crearse.

**Especificidades Python**:
- **`@property`**: expone atributos en modo solo lectura (`tipo`, `descripcion`, `gravedad`)
- **Metodo `copia()`**: clona la instancia para que el `Reporte` congele una copia no vinculada a la lista original
- **Metodo `es_critico()`**: evalua si gravedad == 5 (Regla 8)

---

#### `certificacion.py` -- Certificacion
**Utilidad**: Acredita la vigencia temporal de una especialidad tecnica.
**Metodo `es_vigente(fecha)`**: corrobora `fecha_inicio <= fecha <= fecha_fin` (limites inclusivos, Regla 5).

---

#### `equipo.py` -- Equipo
**Utilidad**: Instrumento de medicion clasificado por categoria y fecha de calibracion.
- **`esta_calibrado(fecha)`**: `0 <= dias <= 182` (maximo legal de 182 dias, Regla 4).
- **`es_compatible(categoria)`**: compara igualdad con la categoria exigida por la prueba.

---

#### `profesional.py` -- Profesional
**Utilidad**: Tecnico evaluador con sus certificaciones.
- **`dict` para `_certificaciones`**: busqueda instantanea O(1) por nombre de certificacion.
- **`dict.get(nombre)`**: retorno seguro (`None`) ante claves inexistentes.
- **`dict(self._certificaciones)`**: expone copia superficial protegiendo la coleccion interna.

---

#### `muestra.py` -- Muestra
**Utilidad**: Subconjunto del lote bajo ensayo.
- **Composicion con `Lote`**: constructor exige `lote_id`. Una muestra no puede existir sin su lote (Regla 2).
- **`tuple(self._defectos)`**: garantiza que la coleccion de defectos sea inmutable desde el exterior.
- **`sum(map(lambda d: d.gravedad, self._defectos))`**: sumatoria funcional de gravedades exigida por consigna.
- **`any(map(lambda d: d.es_critico(), self._defectos))`**: deteccion con cortocircuito de defectos criticos.
- **`asignar_inspeccion()`**: asignacion formal protegiendo encapsulamiento.

---

#### `lote.py` -- Lote
**Utilidad**: Partida de produccion que contiene muestras y emite la decision final.
- **`crear_muestra(cantidad)`**: crea e incorpora sus muestras internamente (Composicion), validando capacidad restante (`sum(map(...))`).
- **`dict` para `_muestras`**: indexacion O(1) por UUID de muestra.
- **`all(map(...))`**: control de que el 100% de muestras esten en estado terminal antes de decidir.
- **`conteo_por_tipo()`**: utiliza `dict.get(tipo, 0) + 1` para contabilizacion idiomática.

---

#### `reporte.py` -- Reporte
**Utilidad**: Documento oficial inalterable emitido ante rechazo (`NO_CONFORME`).
- **`tuple(map(lambda d: d.copia(), defectos))`**: realiza copias profundas de defectos encapsuladas en tupla inmutable.

---

#### `inspeccion.py` -- Inspeccion
**Utilidad**: Sesion de ensayo que articula muestra, profesional, equipo y procedimiento.
- **Constructor Fail-Fast**: valida tipo de fecha, estado PENDIENTE de muestra, certificacion requerida, compatibilidad de equipo y calibracion antes de consolidar el objeto.

---

### 3.4 Procedimientos y Polimorfismo

#### `procedimiento.py` -- Clase Base Abstracta
Define el contrato con `evaluar(observaciones)` que lanza `NotImplementedError` si una subclase no lo implementa.

#### `proc_dimensional.py` -- ProcedimientoDimensional
Mide variaciones cuantitativas respecto a limites (min/max). Calcula gravedades proporcionales al desvio y crea defectos de tipo `"DIMENSIONAL"`.

#### `proc_visual.py` -- ProcedimientoVisual
Registra anomalias cualitativas detectadas por observacion y crea defectos de tipo `"VISUAL"`.

---

### 3.5 Observaciones
- `ObservacionDimensional`: propiedades calculadas `@property` para `desviacion` y `tolerancia`.
- `ObservacionVisual`: parametro optativo `gravedad=None` si no hubo anomalia detectada.

---

### 3.6 Fachada (`empresa.py`)
- Punto unico de gestion (`Fachada`).
- `crear_registrar_muestra(cantidad, lote)`: delega al lote la creacion (`lote.crear_muestra(cantidad)`) y la registra en su inventario.
- `**kwargs` en `crear_registrar_procedimiento`: provee total flexibilidad para admitir parametros heterogeneos segun el procedimiento.

---

### 3.7 Ejecucion (`main.py`)
Simulacion E2E que recorre en 10 pasos la creacion, las validaciones que fallan preventivamente, las inspecciones conformes y no conformes, los reportes emitidos y la aprobacion del lote segun Six Sigma.

---

## 4. Relaciones entre las clases (Analisis UML)

### 4.1 Tipos de relaciones UML

#### Composicion (rombo negro `*--`): "forma parte de" -- ciclo de vida ligado
| Relacion | Explicacion | En el codigo |
|---|---|---|
| `Lote *-- Muestra` | Una muestra pertenece obligatoriamente a exactamente un lote desde su creacion (Regla 2). El lote crea y controla sus muestras | `lote.crear_muestra(cantidad)` instancia `Muestra(cantidad, self._id)` internamente |
| `Muestra *-- Defecto` | Los defectos solo existen en el contexto de una muestra | `self._defectos = []` -- la lista se crea en Muestra y pertenece a Muestra |
| `Profesional *-- Certificacion` | Las certificaciones no tienen sentido sin el profesional | `self._certificaciones = {}` -- el dict se crea en Profesional |
| `Reporte *-- Defecto` | El reporte contiene copias fijas de los defectos | `self._defectos = tuple(map(...))` -- copias creadas en la construccion |

#### Agregacion (rombo blanco `o--`): "contiene" -- ciclo de vida independiente
En este diseño la relacion `Lote` / `Muestra` es de **composicion estricta** (`*--`): no se concibe una `Muestra` huerfana sin su lote (el `lote_id` es obligatorio e inmutable desde el constructor).

#### Asociacion (flecha `-->`): "usa / referencia"
| Relacion | Explicacion | En el codigo |
|---|---|---|
| `Inspeccion --> Muestra` | La inspeccion referencia una muestra pero no la posee | `self._muestra = muestra` |
| `Inspeccion --> Profesional` | Idem | `self._profesional = profesional` |
| `Inspeccion --> Equipo` | Idem | `self._equipo = equipo` |
| `Inspeccion --> Procedimiento` | Idem | `self._procedimiento = procedimiento` |
| `Muestra --> Reporte` | La muestra referencia su reporte oficial | `self._reporte = Reporte(...)` |

#### Dependencia (flecha punteada `..>`): "usa temporalmente"
- `Empresa ..> Lote/Muestra/...`: orquesta la creacion y los almacena en su registro.
- `ProcedimientoDimensional ..> ObservacionDimensional`: procesa observaciones recibidas como argumento.
- `Muestra ..> EstadoMuestra`: tipado de estados.
- `Lote ..> EstadoLote`: tipado de estados.

#### Herencia (flecha triangulo `<|--`)
- `Procedimiento <|-- ProcedimientoDimensional`
- `Procedimiento <|-- ProcedimientoVisual`

---

## 5. Recapitulativo de especificidades Python

| Concepto Python | Donde | Por que |
|---|---|---|
| **`dict`** | Profesional, Lote, Empresa, conteo_por_tipo | Acceso O(1) por clave, la consigna lo pide |
| **`dict.get()`** | Profesional.tiene_certificacion_vigente, Lote.conteo_por_tipo, Empresa.obtener_* | Evita `KeyError` si la clave no existe |
| **`map()`** | Muestra.suma_gravedades, tiene_critico, Lote.porcentaje, Reporte copia | Transformacion funcional, la consigna lo pide |
| **`sum()`** | Muestra.suma_gravedades, Lote.capacidad, porcentaje | Agregacion sobre iterador |
| **`any()`** | Muestra.tiene_critico | Cortocircuito: se detiene en el primer True |
| **`all()`** | Lote.todas_cerradas | Cortocircuito: se detiene en el primer False |
| **`lambda`** | Todos los usos con map() | Funcion anonima inline |
| **`tuple()`** | Muestra.defectos, Lote.muestras, Reporte._defectos | Coleccion inmutable |
| **`**kwargs`** | Empresa.crear_registrar_procedimiento | Argumentos nombrados variables |
| **`Enum`** | EstadoMuestra, EstadoLote | Constantes tipadas |
| **`uuid.uuid4()`** | Todas las clases con id | Identificadores unicos universales |
| **`@property`** | Todas las clases | Encapsulacion solo lectura |
| **`f-strings`** | Todas las clases (repr, mensajes) | Interpolacion de variables |
| **`isinstance()`** | Validaciones, Profesional | Verificacion de tipo en ejecucion |
| **`date`/`timedelta`** | Equipo, Certificacion, Inspeccion | Calculos de fechas (consigna regla 88) |
| **Herencia** | Procedimiento --> Dimensional/Visual | Polimorfismo |
| **Excepciones custom** | excepciones.py | Errores de negocio (consigna regla 86) |

---

## 6. Tests -- Cobertura de reglas de negocio

| Test | Regla consigna |
|---|---|
| Identificadores duplicados, cantidades invalidas | Regla 1 |
| Muestras que exceden la capacidad del lote | Regla 2 |
| Gravedades 1, 5, fuera de rango | Regla 3 |
| Calibracion a 182 dias exacta y 183 dias | Regla 4 |
| Certificacion ausente, vencida, vigente en los limites | Regla 5 |
| Transicion PENDIENTE --> EN_INSPECCION unicamente | Regla 6 |
| Evaluacion polimorfica (dimensional + visual) | Regla 7 |
| Suma justo en el limite, por encima, defecto critico | Regla 8 |
| Modificar/reinspeccionar muestra cerrada --> error | Regla 9 |
| Contenido y unicidad del reporte | Regla 10 |
| Lote incompleto, exactamente 5%, por encima de 5% | Regla 11 |
| Conteo de criticos sin efectos secundarios | Regla 12 |
