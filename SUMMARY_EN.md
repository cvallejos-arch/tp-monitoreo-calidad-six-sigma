# Complete Project Summary -- TP Monitoreo Calidad Six Sigma

## 1. Project Context

### Situation
The company **QuantumTech Precision** manufactures components in batches and evaluates samples through inspection procedures. Currently, it records measurements, calibrations and defects in separate documents. Consequence: it can use equipment with expired calibration, close incomplete batches, and produce reports that don't explain which defects caused the rejection.

### Objective
Build a **prototype** that:
- Registers batches, samples, professionals, equipment and procedures
- Verifies certifications and calibration validity **before** inspecting
- Executes procedures with **different** evaluation behaviors (polymorphism)
- Records defects and closes samples through **controlled state transitions**
- Issues traceable deviation reports
- Decides a batch **only** when all its samples have been inspected

### Key Business Rules
- Severity: integer from 1 to 5 (5 = critical)
- Valid calibration: `inspection_date - calibration_date <= 182 days` (inclusive bounds)
- Conformity: `NO_CONFORME` if critical defect OR sum of severities > limit
- Batch decision: `RECHAZADO` if non-conforming % > 5%, otherwise `APROBADO` (exactly 5% = APROBADO)

---

## 2. Architecture and Files

### 2.1 Base Files

#### `excepciones.py` -- Custom Exceptions
**Purpose**: Define domain-specific exceptions instead of using generic `ValueError`.

**Python Specifics**:
- **Class inheritance**: all inherit from `CalidadError` which inherits from `Exception`
- **Exception hierarchy**: allows catching `CalidadError` to catch ALL domain errors, or catching a specific exception

**Why custom instead of ValueError?**
The assignment requires it (rule 86). Additionally, it distinguishes business errors from standard Python errors. For example, `pytest.raises(TransicionIlegalError)` is more explicit than `pytest.raises(ValueError)`.

**Classes**:
| Exception | Usage |
|---|---|
| `CalidadError` | Common base |
| `DatosInvalidosError` | Invalid data (quantities, severities, empty texts) |
| `EquipoNoAptoError` | Equipment not calibrated or incompatible category |
| `CertificacionNoVigenteError` | Certification absent or expired |
| `TransicionIlegalError` | Illegal state transitions (closing an already closed sample) |
| `InspeccionInvalidaError` | Operations on a closed inspection |

---

#### `validacion.py` -- Centralized Validation Functions
**Purpose**: Centralize ALL validation logic in one place (DRY principle). Each class calls these functions instead of duplicating checks.

**Python Specifics**:
- **Pure functions** (no classes): each function takes a value, validates it, and returns it or raises an exception
- **`isinstance(valor, int) or isinstance(valor, bool)`**: in Python, `bool` is a subclass of `int` (`True == 1`). Booleans must be explicitly excluded
- **f-strings**: `f"The field '{nombre_campo}'..."` -- variable interpolation in strings

**Why return the value?**
To be able to write `self._cantidad = validar_cantidad(cantidad)` in a single line ("validate and assign" pattern).

**Functions**:
| Function | Validates | Returns |
|---|---|---|
| `validar_entero(valor)` | Is an int (not bool) | The value |
| `validar_cantidad(cantidad)` | Int > 0 | The value |
| `validar_gravedad(gravedad)` | Int between 1 and 5 | The value |
| `validar_texto(texto)` | Non-empty string, letters only | The value |
| `validar_descripcion(descripcion)` | Non-empty string (accepts digits) | The value |
| `validar_fecha_tipo(fecha)` | Instance of `date` | The value |
| `validar_rango_fechas(inicio, fin)` | inicio <= fin | Nothing |
| `validar_rango_entero(valor, min, max)` | Int in [min, max] | The value |

---

### 2.2 Enums

#### `estado_muestra.py` and `estado_lote.py`
**Purpose**: Represent the possible states of a sample and a batch as immutable constants.

**Python Specifics**:
- **`Enum`** (from `enum`): prevents using raw strings like `"PENDIENTE"`. Compares by identity (`==`) instead of comparing strings
- **`.value`**: returns the associated string (for display)

**Why Enum instead of strings?**
- IDE autocompletion
- Compile-time error if you write `EstadoMuestra.PENDIETE` (typo) vs no error with `"PENDIETE"`
- Guarantee that only defined values are possible

---

### 2.3 Domain Classes

#### `defecto.py` -- Defecto
**Purpose**: Represents an observed deviation. Immutable after creation.

**Python Specifics**:
- **`@property`**: exposes attributes as read-only. `d.tipo` works but `d.tipo = "x"` raises `AttributeError`
- **`_` prefix** (convention): private attributes. Python doesn't truly protect them, it's a convention

**Method `copia()`**:
Creates a new independent instance. Used by `Reporte` to "freeze" defects at report time. Without copying, modifying the original list would also modify the report.

**Method `es_critico()`**:
Returns `True` if severity == 5. Encapsulates the business rule (Assignment rule 8).

---

#### `certificacion.py` -- Certificacion
**Purpose**: Represents a professional's certification with validity dates.

**Method `es_vigente(fecha)`**:
Checks `fecha_inicio <= fecha <= fecha_fin` (inclusive bounds, assignment rule 5).

---

#### `equipo.py` -- Equipo
**Purpose**: Represents a measurement instrument with its category and calibration date.

**Python Specifics**:
- **`uuid.uuid4()`**: generates a universally unique identifier. No need to manage duplicates
- **Implicit `timedelta`**: `(fecha - self._fecha_calibracion).days` -- subtracting two `date` objects returns a `timedelta`, `.days` extracts the number of days

**Method `esta_calibrado(fecha)`**:
`0 <= dias <= 182` -- verifies that calibration is in the past (not future) and within 182 days (assignment rule 4).

**Method `es_compatible(categoria)`**:
Simple string equality comparison.

---

#### `profesional.py` -- Profesional
**Purpose**: Represents an inspector with their certifications.

**Python Specifics**:
- **`dict` for `_certificaciones`** instead of `list`: O(1) access by name instead of O(n) with a loop
- **`dict.get(nombre)`**: returns `None` if the key doesn't exist (instead of raising `KeyError`)
- **`dict(self._certificaciones)`**: returns a shallow copy of the dict (protects internals)

**Why dict instead of list?**
The assignment requires using `dict`. Additionally:
```python
# With list (O(n)) -- old code:
for cert in self._certificaciones:
    if cert.nombre == nombre and cert.es_vigente(fecha):
        return True

# With dict (O(1)) -- new code:
cert = self._certificaciones.get(nombre)
return cert is not None and cert.es_vigente(fecha)
```

**Why `dict()` copy instead of returning directly?**
If you return `self._certificaciones`, external code could modify the internal dict:
```python
prof.certificaciones["FAKE"] = "x"  # Would modify internals!
```
With `dict(self._certificaciones)`, it's a copy: modifying the copy doesn't change the original.

---

#### `muestra.py` -- Muestra
**Purpose**: Represents a sample from the batch. Manages its own state transitions.

**Python Specifics**:
- **`tuple(self._defectos)`**: returns an immutable version of the list. Prevents `muestra.defectos.append(x)` from outside
- **`sum(map(lambda d: d.gravedad, self._defectos))`**:
  - `map()` applies the lambda to each defect, producing an iterator of severities
  - `sum()` adds up all values
- **`any(map(lambda d: d.es_critico(), self._defectos))`**:
  - `any()` returns `True` as soon as one element is `True` (short-circuit)
  - More efficient than a classic for loop

**Why `tuple` instead of `list` for `defectos`?**
The assignment (rule 9) says: "after closing, defects cannot be added, removed or replaced." A tuple is **immutable**: no `.append()`, `.remove()`, `[i] = x`. It's the structural guarantee that calling code cannot modify the collection.

**Why `sum(map(...))` instead of a for loop?**
- More concise and declarative
- The assignment requires using `map()`
- Functionally equivalent, but more "Pythonic"

**State Transitions**:
```
PENDIENTE  -->  EN_INSPECCION  -->  CONFORME
                                -->  NO_CONFORME
```
Each transition is protected by a check of the current state. A final state (CONFORME/NO_CONFORME) blocks all future modifications.

**Method `asignar_inspeccion()`**:
Exists to **respect encapsulation**. Instead of `muestra._inspeccion = self` (direct access to a private attribute), we go through a public method that can validate.

---

#### `lote.py` -- Lote
**Purpose**: Represents a batch of components. Contains samples and decides approval/rejection.

**Python Specifics**:
- **`dict` for `_muestras`**: `{muestra.id: muestra}` -- O(1) access by UUID
- **`sum(map(lambda m: m.cantidad, self._muestras.values()))`**: calculates used capacity
- **`all(map(...))`**: verifies that ALL samples are in a final state
- **`dict.get(tipo, 0)`** in `conteo_por_tipo()`: returns 0 if the key doesn't exist

**Why `dict.get(tipo, 0) + 1` instead of `if/else`?**
```python
# Old code (4 lines):
if d.tipo in conteo:
    conteo[d.tipo] += 1
else:
    conteo[d.tipo] = 1

# New code (1 line):
conteo[d.tipo] = conteo.get(d.tipo, 0) + 1
```
`dict.get(key, default_value)` is a standard Python idiom that replaces the if/else pattern.

**Batch Decision**:
- Verifies the batch is in `EN_PRODUCCION` (not already decided)
- Verifies it has at least one sample
- Verifies all samples are closed
- Calculates the %: `no_conforme_count / total * 100`
- `> 5` --> RECHAZADO, `<= 5` --> APROBADO

---

#### `reporte.py` -- Reporte
**Purpose**: Backup document for a NO_CONFORME sample. Contains a frozen copy of the defects.

**Python Specifics**:
- **`tuple(map(lambda d: d.copia(), defectos))`**:
  - `map()`: applies `copia()` to each defect (creates a new instance)
  - `tuple()`: makes the result immutable
  - Double protection: objects are copied AND the collection is a tuple

**Why copy the defects?**
If original references were stored, modifying a defect after the report would also modify the report. The copy guarantees the report remains a faithful "snapshot" of the moment the sample was closed.

---

#### `inspeccion.py` -- Inspeccion
**Purpose**: Coordinates the inspection process. Validates cross-prerequisites BEFORE starting.

**Validations in the constructor** (order matters):
1. Date is a `date` object
2. Sample is in PENDIENTE state
3. Professional has the required certification (if the procedure requires one)
4. Equipment is of the correct category
5. Equipment is calibrated

**Python Specifics**:
- **Validation in `__init__`**: if a validation fails, the exception is raised and the object is never created. The sample remains in PENDIENTE state (assignment rule 5)
- **`@property cerrada`**: exposes the closed state as read-only

**Why validate in the constructor?**
It's the **"fail fast"** pattern. If prerequisites are not met, there is never an invalid `Inspeccion` object in memory.

---

### 2.4 Procedures and Polymorphism

#### `procedimiento.py` -- Procedimiento (abstract class)
**Purpose**: Defines the common interface for all procedure types.

**Python Specifics**:
- **`raise NotImplementedError`** in `evaluar()`: forces subclasses to implement the method. It's the Python equivalent of an abstract method
- **Inheritance**: `ProcedimientoDimensional(Procedimiento)` -- inherits from the base class

#### `proc_dimensional.py` -- ProcedimientoDimensional
**Purpose**: Evaluates observations based on physical measurements (value vs tolerances).

**Method `evaluar(observaciones)`**:
For each observation with `desviacion > 0`, calculates severity based on the desviacion/tolerancia ratio and creates a `Defecto` of type "DIMENSIONAL".

#### `proc_visual.py` -- ProcedimientoVisual
**Purpose**: Evaluates visual observations.

**Method `evaluar(observaciones)`**:
For each observation with `defecto_detectado == True`, creates a `Defecto` of type "VISUAL" with the indicated severity.

#### Polymorphism in Action
```python
# In Inspeccion.ejecutar():
defectos = self._procedimiento.evaluar(observaciones)
```
Whether `self._procedimiento` is a `ProcedimientoDimensional` or `ProcedimientoVisual`, it's the **same interface** (`evaluar()`). The behavior changes based on the concrete type. This is **inheritance-based polymorphism**.

---

### 2.5 Observations

#### `observacion_dimensional.py` -- ObservacionDimensional
**Python Specifics**:
- **Computed properties** `desviacion` and `tolerancia`: these are not stored attributes but values calculated on each access. The `@property` decorator makes `obs.desviacion` look like an attribute but executes code

#### `observacion_visual.py` -- ObservacionVisual
**Python Specifics**:
- **Optional parameter** `gravedad=None`: severity is only required when `defecto_detectado` is `True`

---

### 2.6 Facade

#### `empresa.py` -- Empresa
**Purpose**: Entry point for creating and registering all objects. **Facade** pattern.

**Python Specifics**:
- **`dict` of `dict`**: `self._registros = {"lotes": {}, "muestras": {}, ...}` -- a central registry organized by category
- **`**kwargs`** in `crear_registrar_procedimiento`: allows passing variable named arguments

```python
# The call:
empresa.crear_registrar_procedimiento(
    ProcedimientoVisual,
    limite_gravedad_acumulada=5,
    categoria_equipo_requerida="Visual",
    certificacion_requerida="ISO"
)

# Received in the method:
def crear_registrar_procedimiento(self, tipo_procedimiento, **kwargs):
    procedimiento = tipo_procedimiento(**kwargs)  # unpacks the kwargs
```

**Why `**kwargs`?**
Each procedure type may have different parameters. `**kwargs` allows passing any arguments without modifying the method signature. It's the **flexibility** required by polymorphism.

---

### 2.7 Execution

#### `main.py`
**Purpose**: Demonstrates the complete workflow in 10 sequential steps:

1. Create a batch + 20 samples
2. Create professionals with certifications
3. Create calibrated equipment
4. Create procedures (visual + dimensional) via `**kwargs`
5. Demonstrate validations that reject (absent certification, expired calibration, incompatible category)
6. Execute visual inspections
7. Execute a dimensional inspection
8. Query batch statistics (without side effects)
9. Decide the batch
10. Display summary with reports

---

## 3. Class Relationships

### 3.1 UML Relationship Types

#### Composition (filled diamond `*--`): "part of" -- linked lifecycle
**If the container is destroyed, the contents are destroyed too.**

| Relationship | Explanation | In Code |
|---|---|---|
| `Muestra *-- Defecto` | Defects only exist in the context of a sample | `self._defectos = []` -- the list is created in Muestra and belongs to Muestra |
| `Profesional *-- Certificacion` | Certifications have no meaning without the professional | `self._certificaciones = {}` -- the dict is created in Profesional |
| `Reporte *-- Defecto` | The report contains frozen copies of defects | `self._defectos = tuple(map(...))` -- copies created at construction |

#### Aggregation (hollow diamond `o--`): "contains" -- independent lifecycle
**Contents can exist without the container.**

| Relationship | Explanation | In Code |
|---|---|---|
| `Lote o-- Muestra` | A sample is created before being added to a batch. It could theoretically exist alone | `lote.agregar_muestra(muestra)` -- the sample already exists |

#### Association (arrow `-->`): "uses / references"
**Simple reference, no linked lifecycle.**

| Relationship | Explanation | In Code |
|---|---|---|
| `Inspeccion --> Muestra` | The inspection references a sample but doesn't "own" it | `self._muestra = muestra` |
| `Inspeccion --> Profesional` | Same | `self._profesional = profesional` |
| `Inspeccion --> Equipo` | Same | `self._equipo = equipo` |
| `Inspeccion --> Procedimiento` | Same | `self._procedimiento = procedimiento` |
| `Muestra --> Reporte` | The sample references its report | `self._reporte = Reporte(...)` |

#### Dependency (dashed arrow `..>`): "uses temporarily"
**No stored reference, just usage in a method.**

| Relationship | Explanation |
|---|---|
| `Empresa ..> Lote/Muestra/...` | Empresa creates these objects but doesn't "own" them in the OO sense -- they live in a dict |
| `ProcedimientoDimensional ..> ObservacionDimensional` | The procedure receives observations as parameter of `evaluar()` |
| `Muestra ..> EstadoMuestra` | Muestra uses the enum for its state |

#### Inheritance (triangle arrow `<|--`)

| Relationship | In Code |
|---|---|
| `Procedimiento <\|-- ProcedimientoDimensional` | `class ProcedimientoDimensional(Procedimiento):` |
| `Procedimiento <\|-- ProcedimientoVisual` | `class ProcedimientoVisual(Procedimiento):` |

---

## 4. Python Specifics Summary

| Python Concept | Where | Why |
|---|---|---|
| **`dict`** | Profesional, Lote, Empresa, conteo_por_tipo | O(1) access by key, assignment requires it |
| **`dict.get()`** | Profesional.tiene_certificacion_vigente, Lote.conteo_por_tipo, Empresa.obtener_* | Avoids `KeyError` if key doesn't exist |
| **`map()`** | Muestra.suma_gravedades, tiene_critico, Lote.porcentaje, Reporte copy | Functional transformation, assignment requires it |
| **`sum()`** | Muestra.suma_gravedades, Lote.capacity, porcentaje | Aggregation over iterator |
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

## 5. Global Execution Flow

```
1. Empresa creates Lote(name, quantity)
2. Empresa creates Muestra(quantity) x N
3. Lote.agregar_muestra(muestra) -- checks capacity, assigns lote_id
4. Empresa creates Profesional(name)
5. Profesional.agregar_certificacion(Certificacion(name, start, end))
6. Empresa creates Equipo(category, calibration_date)
7. Empresa creates Procedimiento (Dimensional or Visual via **kwargs)
8. Empresa.lanzar_inspeccion(muestra, prof, equipo, proc, fecha)
   --> Inspeccion.__init__ validates everything, moves muestra to EN_INSPECCION
9. Inspeccion.ejecutar(observaciones)
   --> Procedimiento.evaluar(obs) -- polymorphism
   --> Muestra.agregar_defecto(defecto) for each found defect
10. Inspeccion.cerrar()
    --> Muestra.cerrar(limite) -- determines CONFORME or NO_CONFORME
    --> If NO_CONFORME: Reporte created with copy of defects
11. Lote.decidir()
    --> Calculates porcentaje_no_conforme()
    --> APROBADO (<= 5%) or RECHAZADO (> 5%)
```

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
