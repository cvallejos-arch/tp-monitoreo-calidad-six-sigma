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
- Decida un lote **solo** cuando todas sus muestras esten inspeccionadas

### Reglas de negocio clave
- Gravedad: entero de 1 a 5 (5 = critico)
- Calibracion valida: `fecha_inspeccion - fecha_calibracion <= 182 dias` (bornes inclusivos)
- Conformidad: `NO_CONFORME` si defecto critico O suma gravedades > limite
- Decision del lote: `RECHAZADO` si % no conforme > 5%, sino `APROBADO` (5% exacto = APROBADO)

---

## 2. Arquitectura y Archivos

### 2.1 Archivos base

#### `excepciones.py` -- Excepciones custom
**Utilidad**: Definir excepciones de dominio especificas en lugar de usar `ValueError` generico.

**Especificidades Python**:
- **Herencia de clases**: todas heredan de `CalidadError` que hereda de `Exception`
- **Jerarquia de excepciones**: permite capturar `CalidadError` para atrapar TODOS los errores del dominio, o capturar una excepcion especifica

**Por que custom en lugar de ValueError?**
La consigna lo exige (regla 86). Ademas, permite distinguir los errores de negocio de los errores estandar de Python. Por ejemplo, `pytest.raises(TransicionIlegalError)` es mas explicito que `pytest.raises(ValueError)`.

**Clases**:
| Excepcion | Uso |
|---|---|
| `CalidadError` | Base comun |
| `DatosInvalidosError` | Datos invalidos (cantidades, gravedades, textos vacios) |
| `EquipoNoAptoError` | Equipo no calibrado o categoria incompatible |
| `CertificacionNoVigenteError` | Certificacion ausente o vencida |
| `TransicionIlegalError` | Transiciones de estado ilegales (cerrar una muestra ya cerrada) |
| `InspeccionInvalidaError` | Operaciones sobre inspeccion cerrada |

---

#### `validacion.py` -- Funciones de validacion centralizadas
**Utilidad**: Centralizar TODA la logica de validacion en un solo lugar (principio DRY). Cada clase llama a estas funciones en lugar de duplicar las verificaciones.

**Especificidades Python**:
- **Funciones puras** (sin clases): cada funcion toma un valor, lo valida y lo retorna o lanza una excepcion
- **`isinstance(valor, int) or isinstance(valor, bool)`**: en Python, `bool` es subclase de `int` (`True == 1`). Hay que excluir explicitamente los booleanos
- **f-strings**: `f"El campo '{nombre_campo}'..."` -- interpolacion de variables en cadenas

**Por que retornar el valor?**
Para poder escribir `self._cantidad = validar_cantidad(cantidad)` en una sola linea (patron "validate and assign").

**Funciones**:
| Funcion | Valida | Retorna |
|---|---|---|
| `validar_entero(valor)` | Es un int (no bool) | El valor |
| `validar_cantidad(cantidad)` | Int > 0 | El valor |
| `validar_gravedad(gravedad)` | Int entre 1 y 5 | El valor |
| `validar_texto(texto)` | String no vacio, solo letras | El valor |
| `validar_descripcion(descripcion)` | String no vacio (acepta numeros) | El valor |
| `validar_fecha_tipo(fecha)` | Instancia de `date` | El valor |
| `validar_rango_fechas(inicio, fin)` | inicio <= fin | Nada |
| `validar_rango_entero(valor, min, max)` | Int en [min, max] | El valor |

---

### 2.2 Enums

#### `estado_muestra.py` y `estado_lote.py`
**Utilidad**: Representar los estados posibles de una muestra y un lote como constantes inmutables.

**Especificidades Python**:
- **`Enum`** (de `enum`): impide usar strings crudos como `"PENDIENTE"`. Compara por identidad (`==`) en lugar de comparar strings
- **`.value`**: retorna el string asociado (para visualizacion)

**Por que Enum en lugar de strings?**
- Autocompletado en el IDE
- Error de compilacion si se escribe `EstadoMuestra.PENDIETE` (typo) vs sin error con `"PENDIETE"`
- Garantia de que solo los valores definidos son posibles

---

### 2.3 Clases de dominio

#### `defecto.py` -- Defecto
**Utilidad**: Representa una desviacion observada. Inmutable despues de la creacion.

**Especificidades Python**:
- **`@property`**: expone atributos en solo lectura. `d.tipo` funciona pero `d.tipo = "x"` lanza `AttributeError`
- **Prefijo `_`** (convencion): atributos privados. Python no los protege realmente, es una convencion

**Metodo `copia()`**:
Crea una nueva instancia independiente. Usado por `Reporte` para "congelar" los defectos al momento del reporte. Si no se copiara, modificar la lista original modificaria tambien el reporte.

**Metodo `es_critico()`**:
Retorna `True` si gravedad == 5. Encapsula la regla de negocio (Consigna regla 8).

---

#### `certificacion.py` -- Certificacion
**Utilidad**: Representa una certificacion de un profesional con fechas de validez.

**Metodo `es_vigente(fecha)`**:
Verifica `fecha_inicio <= fecha <= fecha_fin` (bornes inclusivos, consigna regla 5).

---

#### `equipo.py` -- Equipo
**Utilidad**: Representa un instrumento de medicion con su categoria y fecha de calibracion.

**Especificidades Python**:
- **`uuid.uuid4()`**: genera un identificador unico universal. No es necesario gestionar duplicados
- **`timedelta` implicito**: `(fecha - self._fecha_calibracion).days` -- la resta de dos `date` retorna un `timedelta`, `.days` extrae el numero de dias

**Metodo `esta_calibrado(fecha)`**:
`0 <= dias <= 182` -- verifica que la calibracion esta en el pasado (no futura) y dentro de los 182 dias (consigna regla 4).

**Metodo `es_compatible(categoria)`**:
Simple comparacion de igualdad de strings.

---

#### `profesional.py` -- Profesional
**Utilidad**: Representa un inspector con sus certificaciones.

**Especificidades Python**:
- **`dict` para `_certificaciones`** en lugar de `list`: acceso O(1) por nombre en lugar de O(n) con un bucle
- **`dict.get(nombre)`**: retorna `None` si la clave no existe (en lugar de lanzar `KeyError`)
- **`dict(self._certificaciones)`**: retorna una copia superficial del dict (protege el interno)

**Por que dict en lugar de list?**
La consigna pide usar `dict`. Ademas:
```python
# Con list (O(n)) -- codigo anterior:
for cert in self._certificaciones:
    if cert.nombre == nombre and cert.es_vigente(fecha):
        return True

# Con dict (O(1)) -- codigo nuevo:
cert = self._certificaciones.get(nombre)
return cert is not None and cert.es_vigente(fecha)
```

**Por que `dict()` copia en lugar de retornar directamente?**
Si se retorna `self._certificaciones`, el codigo externo podria modificar el dict interno:
```python
prof.certificaciones["FAKE"] = "x"  # Modificaria el interno!
```
Con `dict(self._certificaciones)`, es una copia: modificar la copia no cambia el original.

---

#### `muestra.py` -- Muestra
**Utilidad**: Representa un subconjunto del lote. Gestiona sus propias transiciones de estado.

**Especificidades Python**:
- **`tuple(self._defectos)`**: retorna una version inmutable de la lista. Impide `muestra.defectos.append(x)` desde afuera
- **`sum(map(lambda d: d.gravedad, self._defectos))`**:
  - `map()` aplica la lambda a cada defecto, produciendo un iterador de gravedades
  - `sum()` suma todos los valores
- **`any(map(lambda d: d.es_critico(), self._defectos))`**:
  - `any()` retorna `True` en cuanto un elemento es `True` (cortocircuito)
  - Mas eficiente que un bucle for clasico

**Por que `tuple` en lugar de `list` para `defectos`?**
La consigna (regla 9) dice: "despues del cierre no se pueden agregar, quitar ni reemplazar defectos". Un tuple es **inmutable**: no tiene `.append()`, `.remove()`, `[i] = x`. Es la garantia estructural de que el codigo llamante no puede modificar la coleccion.

**Por que `sum(map(...))` en lugar de un bucle for?**
- Mas conciso y declarativo
- La consigna pide usar `map()`
- Funcionalmente equivalente, pero mas "pythonico"

**Transiciones de estado**:
```
PENDIENTE  -->  EN_INSPECCION  -->  CONFORME
                                -->  NO_CONFORME
```
Cada transicion esta protegida por una verificacion del estado actual. Un estado final (CONFORME/NO_CONFORME) bloquea toda modificacion futura.

**Metodo `asignar_inspeccion()`**:
Existe para **respetar la encapsulacion**. En lugar de `muestra._inspeccion = self` (acceso directo a un atributo privado), se pasa por un metodo publico que puede validar.

---

#### `lote.py` -- Lote
**Utilidad**: Representa un lote de componentes. Contiene muestras y decide la aprobacion/rechazo.

**Especificidades Python**:
- **`dict` para `_muestras`**: `{muestra.id: muestra}` -- acceso O(1) por UUID
- **`sum(map(lambda m: m.cantidad, self._muestras.values()))`**: calcula la capacidad utilizada
- **`all(map(...))`**: verifica que TODAS las muestras esten en un estado final
- **`dict.get(tipo, 0)`** en `conteo_por_tipo()`: retorna 0 si la clave no existe

**Por que `dict.get(tipo, 0) + 1` en lugar de `if/else`?**
```python
# Codigo anterior (4 lineas):
if d.tipo in conteo:
    conteo[d.tipo] += 1
else:
    conteo[d.tipo] = 1

# Codigo nuevo (1 linea):
conteo[d.tipo] = conteo.get(d.tipo, 0) + 1
```
`dict.get(clave, valor_por_defecto)` es un idioma Python estandar que reemplaza el patron if/else.

**Decision del lote**:
- Verifica que el lote este en `EN_PRODUCCION` (no ya decidido)
- Verifica que tenga al menos una muestra
- Verifica que todas las muestras esten cerradas
- Calcula el %: `no_conforme_count / total * 100`
- `> 5` --> RECHAZADO, `<= 5` --> APROBADO

---

#### `reporte.py` -- Reporte
**Utilidad**: Documento de respaldo para una muestra NO_CONFORME. Contiene una copia fija de los defectos.

**Especificidades Python**:
- **`tuple(map(lambda d: d.copia(), defectos))`**:
  - `map()`: aplica `copia()` a cada defecto (crea una nueva instancia)
  - `tuple()`: hace el resultado inmutable
  - Doble proteccion: los objetos son copiados Y la coleccion es un tuple

**Por que copiar los defectos?**
Si se almacenaran las referencias originales, modificar un defecto despues del reporte modificaria tambien el reporte. La copia garantiza que el reporte permanece como una "foto" fiel del momento en que la muestra fue cerrada.

---

#### `inspeccion.py` -- Inspeccion
**Utilidad**: Coordina el proceso de inspeccion. Valida los prerequisitos cruzados ANTES de iniciar.

**Validaciones en el constructor** (orden importante):
1. Fecha es un objeto `date`
2. Muestra esta en estado PENDIENTE
3. Profesional tiene la certificacion requerida (si el procedimiento exige una)
4. Equipo es de la categoria correcta
5. Equipo esta calibrado

**Especificidades Python**:
- **Validacion en `__init__`**: si una validacion falla, la excepcion se lanza y el objeto nunca se crea. La muestra permanece en estado PENDIENTE (consigna regla 5)
- **`@property cerrada`**: expone el estado cerrado en solo lectura

**Por que validar en el constructor?**
Es el patron **"fail fast"**. Si los prerequisitos no se cumplen, nunca hay un objeto `Inspeccion` invalido en memoria.

---

### 2.4 Procedimientos y polimorfismo

#### `procedimiento.py` -- Procedimiento (clase abstracta)
**Utilidad**: Define la interfaz comun para todos los tipos de procedimientos.

**Especificidades Python**:
- **`raise NotImplementedError`** en `evaluar()`: fuerza a las subclases a implementar el metodo. Es el equivalente Python de un metodo abstracto
- **Herencia**: `ProcedimientoDimensional(Procedimiento)` -- hereda de la clase base

#### `proc_dimensional.py` -- ProcedimientoDimensional
**Utilidad**: Evalua observaciones basadas en mediciones fisicas (valor vs tolerancias).

**Metodo `evaluar(observaciones)`**:
Para cada observacion con `desviacion > 0`, calcula la gravedad basada en el ratio desviacion/tolerancia y crea un `Defecto` de tipo "DIMENSIONAL".

#### `proc_visual.py` -- ProcedimientoVisual
**Utilidad**: Evalua observaciones visuales.

**Metodo `evaluar(observaciones)`**:
Para cada observacion con `defecto_detectado == True`, crea un `Defecto` de tipo "VISUAL" con la gravedad indicada.

#### Polimorfismo en accion
```python
# En Inspeccion.ejecutar():
defectos = self._procedimiento.evaluar(observaciones)
```
Sea `self._procedimiento` un `ProcedimientoDimensional` o `ProcedimientoVisual`, es la **misma interfaz** (`evaluar()`). El comportamiento cambia segun el tipo concreto. Es el **polimorfismo por herencia**.

---

### 2.5 Observaciones

#### `observacion_dimensional.py` -- ObservacionDimensional
**Especificidades Python**:
- **Propiedades calculadas** `desviacion` y `tolerancia`: no son atributos almacenados, sino valores calculados en cada acceso. El `@property` hace que `obs.desviacion` parezca un atributo pero ejecuta codigo

#### `observacion_visual.py` -- ObservacionVisual
**Especificidades Python**:
- **Parametro opcional** `gravedad=None`: la gravedad solo es requerida si `defecto_detectado` es `True`

---

### 2.6 Fachada

#### `empresa.py` -- Empresa
**Utilidad**: Punto de entrada para crear y registrar todos los objetos. Patron **Fachada (Facade)**.

**Especificidades Python**:
- **`dict` de `dict`**: `self._registros = {"lotes": {}, "muestras": {}, ...}` -- un registro central organizado por categoria
- **`**kwargs`** en `crear_registrar_procedimiento`: permite pasar argumentos nombrados variables

```python
# La llamada:
empresa.crear_registrar_procedimiento(
    ProcedimientoVisual,
    limite_gravedad_acumulada=5,
    categoria_equipo_requerida="Visual",
    certificacion_requerida="ISO"
)

# Recibe en el metodo:
def crear_registrar_procedimiento(self, tipo_procedimiento, **kwargs):
    procedimiento = tipo_procedimiento(**kwargs)  # descomprime los kwargs
```

**Por que `**kwargs`?**
Cada tipo de procedimiento puede tener parametros diferentes. `**kwargs` permite pasar cualquier argumento sin modificar la firma del metodo. Es la **flexibilidad** requerida por el polimorfismo.

---

### 2.7 Ejecucion

#### `main.py`
**Utilidad**: Demuestra el flujo completo en 10 etapas secuenciales:

1. Crear un lote + 20 muestras
2. Crear profesionales con certificaciones
3. Crear equipos calibrados
4. Crear procedimientos (visual + dimensional) via `**kwargs`
5. Demostrar validaciones que rechazan (certificacion ausente, calibracion vencida, categoria incompatible)
6. Ejecutar inspecciones visuales
7. Ejecutar una inspeccion dimensional
8. Consultar estadisticas del lote (sin efectos secundarios)
9. Decidir el lote
10. Mostrar resumen con reportes

---

## 3. Relaciones entre las clases

### 3.1 Tipos de relaciones UML

#### Composicion (rombo negro `*--`): "forma parte de" -- ciclo de vida ligado
**Si el contenedor se destruye, los contenidos se destruyen tambien.**

| Relacion | Explicacion | En el codigo |
|---|---|---|
| `Muestra *-- Defecto` | Los defectos solo existen en el contexto de una muestra | `self._defectos = []` -- la lista se crea en Muestra y pertenece a Muestra |
| `Profesional *-- Certificacion` | Las certificaciones no tienen sentido sin el profesional | `self._certificaciones = {}` -- el dict se crea en Profesional |
| `Reporte *-- Defecto` | El reporte contiene copias fijas de los defectos | `self._defectos = tuple(map(...))` -- copias creadas en la construccion |

#### Agregacion (rombo blanco `o--`): "contiene" -- ciclo de vida independiente
**Los contenidos pueden existir sin el contenedor.**

| Relacion | Explicacion | En el codigo |
|---|---|---|
| `Lote o-- Muestra` | Una muestra se crea antes de ser agregada al lote. Podria teoricamente existir sola | `lote.agregar_muestra(muestra)` -- la muestra ya existe |

#### Asociacion (flecha `-->`): "usa / referencia"
**Simple referencia, sin ciclo de vida ligado.**

| Relacion | Explicacion | En el codigo |
|---|---|---|
| `Inspeccion --> Muestra` | La inspeccion referencia una muestra pero no la "posee" | `self._muestra = muestra` |
| `Inspeccion --> Profesional` | Idem | `self._profesional = profesional` |
| `Inspeccion --> Equipo` | Idem | `self._equipo = equipo` |
| `Inspeccion --> Procedimiento` | Idem | `self._procedimiento = procedimiento` |
| `Muestra --> Reporte` | La muestra referencia su reporte | `self._reporte = Reporte(...)` |

#### Dependencia (flecha punteada `..>`): "usa temporalmente"
**Sin referencia almacenada, solo uso en un metodo.**

| Relacion | Explicacion |
|---|---|
| `Empresa ..> Lote/Muestra/...` | Empresa crea estos objetos pero no los "posee" en el sentido OO -- viven en un dict |
| `ProcedimientoDimensional ..> ObservacionDimensional` | El procedimiento recibe las observaciones como parametro de `evaluar()` |
| `Muestra ..> EstadoMuestra` | Muestra usa el enum para su estado |

#### Herencia (flecha triangulo `<|--`)

| Relacion | En el codigo |
|---|---|
| `Procedimiento <\|-- ProcedimientoDimensional` | `class ProcedimientoDimensional(Procedimiento):` |
| `Procedimiento <\|-- ProcedimientoVisual` | `class ProcedimientoVisual(Procedimiento):` |

---

## 4. Recapitulativo de especificidades Python

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

## 5. Flujo global de ejecucion

```
1. Empresa crea Lote(nombre, cantidad)
2. Empresa crea Muestra(cantidad) x N
3. Lote.agregar_muestra(muestra) -- verifica capacidad, asigna lote_id
4. Empresa crea Profesional(nombre)
5. Profesional.agregar_certificacion(Certificacion(nombre, inicio, fin))
6. Empresa crea Equipo(categoria, fecha_calibracion)
7. Empresa crea Procedimiento (Dimensional o Visual via **kwargs)
8. Empresa.lanzar_inspeccion(muestra, prof, equipo, proc, fecha)
   --> Inspeccion.__init__ valida todo, pasa muestra a EN_INSPECCION
9. Inspeccion.ejecutar(observaciones)
   --> Procedimiento.evaluar(obs) -- polimorfismo
   --> Muestra.agregar_defecto(defecto) por cada defecto encontrado
10. Inspeccion.cerrar()
    --> Muestra.cerrar(limite) -- determina CONFORME o NO_CONFORME
    --> Si NO_CONFORME: Reporte creado con copia de los defectos
11. Lote.decidir()
    --> Calcula porcentaje_no_conforme()
    --> APROBADO (<= 5%) o RECHAZADO (> 5%)
```

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
