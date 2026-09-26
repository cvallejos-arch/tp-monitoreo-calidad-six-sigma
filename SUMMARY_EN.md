# Complete Project Summary -- TP Industrial Quality Monitoring (Six Sigma)

## 1. Project Context

### Scenario
The technology company **QuantumTech Precision** manufactures components in batches and evaluates samples through inspection procedures. Currently, it logs measurements, calibrations, and defects across disconnected documents. Consequently, it risks using equipment with expired calibrations, closing incomplete batches, and issuing reports that fail to explain which defects triggered rejections.

### Objective
Build a **prototype** that:
- Registers batches, samples, professionals, equipment, and procedures
- Verifies professional certifications and calibration validity **before** inspecting
- Executes procedures with **different** polymorphic evaluation behaviors
- Records defects and closes samples through **controlled state transitions**
- Issues fully traceable deviation reports
- Decides a batch **only** when all of its samples have been inspected

### Key Business Rules
- Severity: integer from 1 to 5 (5 = critical)
- Calibration validity: `fecha_inspeccion - fecha_calibracion <= 182 days` (inclusive boundaries)
- Conformity: `NO_CONFORME` if any critical defect exists OR sum of severities > threshold
- Batch decision: `RECHAZADO` if non-conforming percentage > 5%, otherwise `APROBADO` (exact 5% = APROBADO)

---

## 2. Global Operational Logic: Who creates what, in what order, and why?

To thoroughly understand the system architecture, it is essential to visualize the **operational lifecycle** of the industrial application: which component acts, who is responsible for instantiation, and why this strict chronological order is required to uphold domain rules.

```
       ┌────────────────────────────────────────────────────────┐
       │                  EMPRESA (Facade)                      │
       │ Single entry point to initialize and register entities │
       └────┬──────────────┬───────────────┬──────────────┬─────┘
            │ 1            │ 2             │ 3            │ 4
            ▼              ▼               ▼              ▼
       ┌─────────┐   ┌────────────┐   ┌─────────┐  ┌──────────────┐
       │  LOTE   │   │PROFESIONAL │   │ EQUIPO  │  │PROCEDIMIENTO │
       └────┬────┘   └─────┬──────┘   └────┬────┘  └──────┬───────┘
            │ creates      │ holds         │ ready        │ rules
            ▼ (compos.)    ▼               │              │
       ┌─────────┐   ┌────────────┐        │              │
       │ MUESTRA │   │CERTIFICAC. │        │              │
       └────┬────┘   └─────┬──────┘        │              │
            │              │               │              │
            └──────────────┼───────────────┼──────────────┘
                           │ 5. Launch
                           ▼
                  ┌──────────────────┐
                  │    INSPECCION    │ ───► Validates "Fail-Fast" prerequisites
                  └────────┬─────────┘      (calibration, certif, compatibility)
                           │ 6. Execution
                           ▼
                  ┌──────────────────┐
                  │ OBSERVACIONES    │ ───► Polymorphically evaluated
                  └────────┬─────────┘      generates DEFECTOS
                           │ 7. Closure
                           ▼
                  ┌──────────────────┐
                  │ MUESTRA (Close)  │ ───► CONFORME or NO_CONFORME
                  └────────┬─────────┘      (creates REPORTE if NO_CONFORME)
                           │ 8. Final Verdict
                           ▼
                  ┌──────────────────┐
                  │  LOTE (Decision) │ ───► APROBADO (<=5%) or RECHAZADO (>5%)
                  └──────────────────┘
```

### 2.1 Roles and Responsibilities in the Workflow

1. **The Facade (`Empresa`)**: The global orchestrator. Instead of external clients having to manually construct objects and know internal wiring, `Empresa` provides a unified API (`crear_registrar_*`, `lanzar_inspeccion`). It manages central registries stored in dictionaries.
2. **Production (`Lote` and `Muestra`)**: The manufacturing core. The batch represents the total manufactured quantity. Samples are subsets pulled for quality control.
3. **Inspection Resources (`Profesional` + `Certificacion`, `Equipo`)**: Human technicians and physical measurement instruments that must hold active, valid credentials on the inspection date.
4. **Regulatory Framework (`Procedimiento`)**: Technical evaluation standards (visual or dimensional) defining accumulated severity thresholds and measurement tolerances.
5. **The Transactional Event (`Inspeccion`)**: The control session tying together a sample, an authorized professional, calibrated equipment, and a procedure on a specific date.
6. **Documentary Backing (`Reporte` and `Defecto`)**: The tamper-proof, frozen evidence behind any rejection.

---

### 2.2 Detailed Chronological Lifecycle: Who creates what and why?

#### 1. Creation of Batch (`Lote`) followed by its Samples (`Muestra`) -- *Strict Composition*
- **Who creates?** The enterprise instantiates the `Lote` (`empresa.crear_registrar_lote`). To create samples, the enterprise **delegates creation directly to the batch** (`empresa.crear_registrar_muestra(cantidad, lote)`, which calls `lote.crear_muestra(cantidad)`).
- **Why this order?**
  - **Domain rationale**: A sample cannot float in a vacuum; by definition, it is a physical subset of a specific production batch.
  - **Rule 2 of assignment**: *"Cada muestra pertenece a exactamente un lote"*.
  - **Capacity verification**: The batch must exist beforehand to verify that the cumulative sample sizes do not exceed manufactured quantity (`capacidad_usada + cantidad <= cantidad_fabricada`).
  - **Linked lifecycle (Composition)**: The `_lote_id` is assigned at sample construction and is immutable.

#### 2. Registration of Inspectors (`Profesional`) and Certifications (`Certificacion`)
- **Who creates?** The enterprise registers the `Profesional`. Then, active certifications are appended to that professional (`prof.agregar_certificacion(cert)`).
- **Why this order?**
  - A certification only has meaning when assigned to an identified technician.
  - Certifications must exist **prior** to inspection so the system can verify credential validity on the scheduled test date.

#### 3. Registration of Measurement Instruments (`Equipo`) and Calibrations
- **Who creates?** The enterprise registers each instrument with its category (e.g., `"Visual"`, `"Dimensional"`) and calibration date.
- **Why this order?**
  - In Six Sigma / ISO standards, measurements are void if performed using unverified instruments. Instruments must be cataloged with their calibration dates before any inspection can run.

#### 4. Definition of Inspection Procedures (`Procedimiento`)
- **Who creates?** The enterprise configures concrete procedures (`ProcedimientoVisual`, `ProcedimientoDimensional`) using `**kwargs`.
- **Why this order?**
  - The procedure defines the rules of engagement: required equipment category, mandatory certification (e.g., `"ISO"`), and maximum permissible accumulated severity. Without this contract, an inspection has no evaluation criteria.

#### 5. Launching the Inspection (`Inspeccion`) -- *Cross "Fail-Fast" Validation*
- **Who creates?** The enterprise calls `empresa.lanzar_inspeccion(muestra, profesional, equipo, procedimiento, fecha)`.
- **Why here and how?**
  - This is the critical gatekeeping step. The `Inspeccion` constructor enforces the **Fail-Fast** principle:
    1. Verifies the sample is currently in `PENDIENTE` state.
    2. Verifies the professional possesses the required certification active on this date (`es_vigente(fecha)`).
    3. Verifies the equipment matches the procedure's required category (`es_compatible()`).
    4. Verifies the equipment was calibrated within the last 182 days (`esta_calibrado(fecha)`).
  - **If any rule is violated**: an explicit domain exception is raised immediately, the `Inspeccion` instance is never created, and the sample remains untouched in `PENDIENTE` (Rule 5).
  - **If valid**: the sample transitions to `EN_INSPECCION` and locks onto the inspection (`asignar_inspeccion`). The context is frozen for execution.

#### 6. Evaluating Observations and Detecting Defects (`Defecto`) -- *Polymorphism*
- **Who does what?** The inspector feeds observations to `inspeccion.ejecutar(observaciones)`.
- **Why polymorphism?**
  - The inspection remains agnostic to algorithmic details: it calls `self._procedimiento.evaluar(observaciones)`.
  - Dimensional procedures compare measurements against tolerances, computing severity based on deviations.
  - Visual procedures turn detected anomalies into visual defect instances.
  - Generated defects are appended to the sample (`muestra.agregar_defecto(defecto)`).

#### 7. Closing the Sample and Audit Trail (`Reporte`)
- **Who does what?** Calling `inspeccion.cerrar()` triggers `muestra.cerrar(limite_gravedad)`.
- **Why and what outcome?**
  - The sample determines its final state:
    - If it has at least one critical defect (severity = 5) OR total severities exceed the procedure limit $\rightarrow$ `NO_CONFORME`.
    - Otherwise $\rightarrow$ `CONFORME`.
  - **Automatic `Reporte` generation**: If `NO_CONFORME`, the sample immediately generates an official `Reporte` containing deep-copied, frozen defect records, date, batch ID, and inspector ID.
  - The sample is permanently closed (no further defects or inspections allowed).

#### 8. Final Decision on the Batch (`Lote.decidir()`) -- *Six Sigma Criteria*
- **Who decides?** The `Lote` itself.
- **Why at the end?**
  - An industrial quality decision cannot be made on an incomplete batch. It verifies that **100% of samples are closed** (`todas_cerradas() == True`).
  - It computes the non-conforming percentage (`porcentaje_no_conforme()`).
  - If $> 5\%$ $\rightarrow$ `RECHAZADO`. If $\le 5\%$ (exact 5% inclusive) $\rightarrow$ `APROBADO`.
  - The batch moves into an irrevocable terminal state.

---

## 3. Detailed Architecture and File Analysis

Having understood the operational flow, we can now examine each file under the hood, noting technical design decisions and Python idioms.

### 3.1 Base Files

#### `excepciones.py` -- Custom Exceptions
**Purpose**: Define explicit domain exceptions instead of generic `ValueError`.

**Python Specifics**:
- **Class Inheritance**: all inherit from `CalidadError`, which inherits from `Exception`
- **Exception Hierarchy**: allows catching `CalidadError` to trap ALL domain issues, or specific types for granular handling

**Why custom instead of ValueError?**
Mandated by assignment rule 86. Separates business violations from internal Python syntax errors.

**Classes**:
| Exception | Usage |
|---|---|
| `CalidadError` | Base domain exception |
| `DatosInvalidosError` | Out of range/format values (quantities, severities, empty strings) |
| `EquipoNoAptoError` | Uncalibrated equipment or incompatible category |
| `CertificacionNoVigenteError` | Absent or expired certification on inspection date |
| `TransicionIlegalError` | Illegal state transitions (closing closed sample, exceeding batch capacity) |
| `InspeccionInvalidaError` | Operations attempted on a closed inspection |

---

#### `validacion.py` -- Centralized Validation Functions
**Purpose**: Centralize all validation logic (DRY principle). Every class leverages these functions.

**Python Specifics**:
- **Pure Functions**: take a value, validate, and return it or raise an exception
- **`isinstance(valor, int) or isinstance(valor, bool)`**: in Python, `bool` is a subclass of `int` (`True == 1`). Booleans must be explicitly rejected
- **f-strings**: concise, efficient interpolation

**Why return the value?**
Enables clean one-liner assignment: `self._cantidad = validar_cantidad(cantidad)`.

**Functions**:
| Function | Validates | Returns |
|---|---|---|
| `validar_entero(valor)` | Is int (not bool) | The value |
| `validar_cantidad(cantidad)` | Int > 0 | The value |
| `validar_gravedad(gravedad)` | Int between 1 and 5 | The value |
| `validar_texto(texto)` | Non-empty alphabetic string | The value |
| `validar_descripcion(descripcion)` | Non-empty string (allows digits) | The value |
| `validar_fecha_tipo(fecha)` | Instance of `date` | The value |
| `validar_rango_fechas(inicio, fin)` | start <= end | None |
| `validar_rango_entero(valor, min, max)` | Int in [min, max] | The value |

---

### 3.2 Enums

#### `estado_muestra.py` and `estado_lote.py`
**Purpose**: Model finite states as immutable constants.
- **`Enum`**: prevents typos, compares by identity (`==`).
- **`.value`**: provides printable string representation.

---

### 3.3 Domain Classes

#### `defecto.py` -- Defecto
**Purpose**: Represents an observed deviation. Immutable once created.
- **`@property`**: read-only attributes (`tipo`, `descripcion`, `gravedad`).
- **Method `copia()`**: creates a new independent instance so `Reporte` can freeze defects without side-effects.
- **Method `es_critico()`**: returns `True` if gravity == 5 (Rule 8).

---

#### `certificacion.py` -- Certificacion
**Purpose**: Represents professional qualifications with validity dates.
- **Method `es_vigente(fecha)`**: checks `fecha_inicio <= fecha <= fecha_fin` (inclusive boundaries, Rule 5).

---

#### `equipo.py` -- Equipo
**Purpose**: Measurement instrument with category and calibration date.
- **`esta_calibrado(fecha)`**: `0 <= dias <= 182` (182-day legal limit, Rule 4).
- **`es_compatible(categoria)`**: checks compatibility against required procedure category.

---

#### `profesional.py` -- Profesional
**Purpose**: Quality inspector and credentials.
- **`dict` for `_certificaciones`**: O(1) lookup by certification name.
- **`dict.get(nombre)`**: safe lookup avoiding `KeyError`.
- **`dict(self._certificaciones)`**: exposes shallow copy protecting internal dictionary.

---

#### `muestra.py` -- Muestra
**Purpose**: Batch sample undergoing inspection.
- **Composition with `Lote`**: constructor requires `lote_id`. A sample cannot exist without its batch (Rule 2).
- **`tuple(self._defectos)`**: guarantees defect collection is immutable from caller code.
- **`sum(map(lambda d: d.gravedad, self._defectos))`**: functional summation required by assignment.
- **`any(map(lambda d: d.es_critico(), self._defectos))`**: short-circuit critical defect detection.
- **`asignar_inspeccion()`**: formal setter guarding encapsulation.

---

#### `lote.py` -- Lote
**Purpose**: Manufactured component batch holding samples and making final decision.
- **`crear_muestra(cantidad)`**: creates and stores samples internally (Composition), validating remaining capacity (`sum(map(...))`).
- **`dict` for `_muestras`**: O(1) lookup by sample UUID.
- **`all(map(...))`**: confirms 100% of samples are in a terminal state before deciding.
- **`conteo_por_tipo()`**: utilizes `dict.get(tipo, 0) + 1` idiom.

---

#### `reporte.py` -- Reporte
**Purpose**: Official tamper-proof document created upon sample rejection (`NO_CONFORME`).
- **`tuple(map(lambda d: d.copia(), defectos))`**: deep-copies defects and locks into an immutable tuple.

---

#### `inspeccion.py` -- Inspeccion
**Purpose**: Coordinates sample, technician, equipment, and procedure.
- **Fail-Fast Constructor**: validates date type, sample PENDIENTE state, certification, equipment compatibility, and calibration prior to object creation.

---

### 3.4 Procedures and Polymorphism

#### `procedimiento.py` -- Abstract Base Class
Defines `evaluar(observaciones)` interface raising `NotImplementedError` if not overridden.

#### `proc_dimensional.py` -- ProcedimientoDimensional
Evaluates numeric measurements against tolerances, computing severity from deviation.

#### `proc_visual.py` -- ProcedimientoVisual
Evaluates visual findings and produces visual defect objects.

---

### 3.5 Observations
- `ObservacionDimensional`: calculated properties `@property` for `desviacion` and `tolerancia`.
- `ObservacionVisual`: optional `gravedad=None` when no defect was found.

---

### 3.6 Facade (`empresa.py`)
- Single management entry point (**Facade** pattern).
- `crear_registrar_muestra(cantidad, lote)`: delegates sample creation to the batch (`lote.crear_muestra(cantidad)`) and registers it.
- `**kwargs` in `crear_registrar_procedimiento`: provides flexible parameter passing for diverse procedure constructors.

---

### 3.7 Execution (`main.py`)
10-step end-to-end simulation proving all business rules, fail-fast rejections, inspections, and batch acceptance under Six Sigma standards.

---

## 4. Class Relationships (UML Analysis)

### 4.1 UML Relationship Types

#### Composition (filled diamond `*--`): "part of" -- linked lifecycle
| Relationship | Explanation | In Code |
|---|---|---|
| `Lote *-- Muestra` | A sample strictly belongs to exactly one batch from birth (Rule 2). Batch creates and owns samples | `lote.crear_muestra(cantidad)` instantiates `Muestra(cantidad, self._id)` internally |
| `Muestra *-- Defecto` | Defects only exist in the context of a sample | `self._defectos = []` -- created and owned by Muestra |
| `Profesional *-- Certificacion` | Certifications have no meaning without the professional | `self._certificaciones = {}` -- created in Profesional |
| `Reporte *-- Defecto` | Report contains frozen copies of defects | `self._defectos = tuple(map(...))` -- copies created at construction |

#### Aggregation (hollow diamond `o--`): "contains" -- independent lifecycle
In this architecture, `Lote` / `Muestra` is **strict composition** (`*--`): orphan samples cannot exist without a batch (`lote_id` mandatory from instantiation).

#### Association (arrow `-->`): "uses / references"
| Relationship | Explanation | In Code |
|---|---|---|
| `Inspeccion --> Muestra` | Inspection references a sample | `self._muestra = muestra` |
| `Inspeccion --> Profesional` | Same | `self._profesional = profesional` |
| `Inspeccion --> Equipo` | Same | `self._equipo = equipo` |
| `Inspeccion --> Procedimiento` | Same | `self._procedimiento = procedimiento` |
| `Muestra --> Reporte` | Sample references its generated report | `self._reporte = Reporte(...)` |

#### Dependency (dashed arrow `..>`): "uses temporarily"
- `Empresa ..> Lote/Muestra/...`: creates and registers objects in memory.
- `ProcedimientoDimensional ..> ObservacionDimensional`: receives observations as parameter.
- `Muestra ..> EstadoMuestra`: state typing.
- `Lote ..> EstadoLote`: state typing.

#### Inheritance (triangle arrow `<|--`)
- `Procedimiento <|-- ProcedimientoDimensional`
- `Procedimiento <|-- ProcedimientoVisual`

---

## 5. Python Specifics Summary

| Python Concept | Where | Why |
|---|---|---|
| **`dict`** | Profesional, Lote, Empresa, conteo_por_tipo | O(1) access by key, assignment requires it |
| **`dict.get()`** | Profesional.tiene_certificacion_vigente, Lote.conteo_por_tipo, Empresa.obtener_* | Avoids `KeyError` if key doesn't exist |
| **`map()`** | Muestra.suma_gravedades, tiene_critico, Lote.porcentaje, Reporte copy | Functional transformation, assignment requires it |
| **`sum()`** | Muestra.suma_gravedades, Lote.capacidad, porcentaje | Aggregation over iterator |
| **`any()`** | Muestra.tiene_critico | Short-circuit: stops at first True |
| **`all()`** | Lote.todas_cerradas | Short-circuit: stops at first False |
| **`lambda`** | Everywhere with map() | Anonymous inline function |
| **`tuple()`** | Muestra.defectos, Lote.muestras, Reporte._defectos | Immutable collection |
| **`**kwargs`** | Empresa.crear_registrar_procedimiento | Variable named arguments |
| **`Enum`** | EstadoMuestra, EstadoLote | Typed constants |
| **`uuid.uuid4()`** | All classes with id | Universally unique identifiers |
| **`@property`** | All classes | Read-only encapsulation |
| **`f-strings`** | All classes (repr, messages) | Variable interpolation |
| **`isinstance()`** | Validations, Profesional | Runtime type checking |
| **`date`/`timedelta`** | Equipo, Certificacion, Inspeccion | Date calculations (assignment rule 88) |
| **Inheritance** | Procedimiento --> Dimensional/Visual | Polymorphism |
| **Custom exceptions** | excepciones.py | Business errors (assignment rule 86) |

---

## 6. Tests -- Business Rule Coverage

| Test | Assignment Rule |
|---|---|
| Duplicate identifiers, invalid quantities | Rule 1 |
| Samples exceeding batch capacity | Rule 2 |
| Severities 1, 5, out of range | Rule 3 |
| Calibration at exactly 182 days and 183 days | Rule 4 |
| Certification absent, expired, valid at boundaries | Rule 5 |
| Transition PENDIENTE --> EN_INSPECCION only | Rule 6 |
| Polymorphic evaluation (dimensional + visual) | Rule 7 |
| Sum at limit, above, critical defect | Rule 8 |
| Modify/reinspect closed sample --> error | Rule 9 |
| Report content and uniqueness | Rule 10 |
| Incomplete batch, exactly 5%, above 5% | Rule 11 |
| Critical count without side effects | Rule 12 |
