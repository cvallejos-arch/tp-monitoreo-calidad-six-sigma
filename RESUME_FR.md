# Resume Complet du Projet -- TP Monitoreo Calidad Six Sigma

## 1. Contexte du Projet

### Situation
L'entreprise **QuantumTech Precision** fabrique des composants en lots et evalue des echantillons via des procedures d'inspection. Actuellement, elle enregistre mesures, calibrations et defauts dans des documents separes. Consequence : elle peut utiliser des equipements avec calibration perimee, fermer des lots incomplets, et produire des rapports qui n'expliquent pas quels defauts ont cause le rejet.

### Objectif
Construire un **prototype** qui :
- Enregistre lots, echantillons, professionnels, equipements et procedures
- Verifie certifications et validite de calibration **avant** d'inspecter
- Execute des procedures avec des comportements d'evaluation **differents** (polymorphisme)
- Enregistre des defauts et ferme les echantillons via des **transitions d'etat controlees**
- Emet des rapports de deviation tracables
- Decide un lot **uniquement** quand tous ses echantillons sont inspectes

### Regles de negocio cles
- Gravite : entier de 1 a 5 (5 = critique)
- Calibration valide : `fecha_inspeccion - fecha_calibracion <= 182 jours` (bornes inclusives)
- Conformite : `NO_CONFORME` si defaut critique OU somme gravedades > limite
- Decision du lot : `RECHAZADO` si % non conforme > 5%, sinon `APROBADO` (5% exact = APROBADO)

---

## 2. Logique de Fonctionnement Globale : Qui cree quoi, dans quel ordre et pourquoi ?

Pour bien comprendre l'architecture du projet, il est essentiel de visualiser le **cycle de vie operationnel** de l'application industrielle : quel composant intervient, qui est responsable de l'instanciation, et pourquoi cet ordre chronologique est indispensable pour respecter les regles metier.

```
       ┌────────────────────────────────────────────────────────┐
       │                  EMPRESA (Façade)                      │
       │ Point d'entree unique pour initialiser et enregistrer  │
       └────┬──────────────┬───────────────┬──────────────┬─────┘
            │ 1            │ 2             │ 3            │ 4
            ▼              ▼               ▼              ▼
       ┌─────────┐   ┌────────────┐   ┌─────────┐  ┌──────────────┐
       │  LOTE   │   │PROFESIONAL │   │ EQUIPO  │  │PROCEDIMIENTO │
       └────┬────┘   └─────┬──────┘   └────┬────┘  └──────┬───────┘
            │ cree         │ possede       │ apte         │ regles
            ▼ (compos.)    ▼               │              │
       ┌─────────┐   ┌────────────┐        │              │
       │ MUESTRA │   │CERTIFICAC. │        │              │
       └────┬────┘   └─────┬──────┘        │              │
            │              │               │              │
            └──────────────┼───────────────┼──────────────┘
                           │ 5. Lancement
                           ▼
                  ┌──────────────────┐
                  │    INSPECCION    │ ───► Valide prerequis "Fail-Fast"
                  └────────┬─────────┘      (calibration, certif, compatibilite)
                           │ 6. Execution
                           ▼
                  ┌──────────────────┐
                  │ OBSERVACIONES    │ ───► Evaluees polymorphiquement
                  └────────┬─────────┘      genere des DEFECTOS
                           │ 7. Cloture
                           ▼
                  ┌──────────────────┐
                  │ MUESTRA (Cierre) │ ───► CONFORME ou NO_CONFORME
                  └────────┬─────────┘      (cree REPORTE si NO_CONFORME)
                           │ 8. Veredicte final
                           ▼
                  ┌──────────────────┐
                  │  LOTE (Decision) │ ───► APROBADO (<=5%) ou RECHAZADO (>5%)
                  └──────────────────┘
```

### 2.1 Les Acteurs et leurs Responsabilites dans le flux

1. **La Façade (`Empresa`)** : C'est le chef d'orchestre global. Au lieu que le monde exterieur doive instancier manuellement chaque objet en connaissant les details internes, `Empresa` propose une API unifiee (`crear_registrar_*`, `lanzar_inspeccion`). Elle centralise tous les registres de l'usine dans des dictionnaires.
2. **La Production (`Lote` et `Muestra`)** : Le coeur manufacturier. Le lot represente la quantite totale fabriquee. Les echantillons sont les sous-ensembles preleves pour test.
3. **Les Ressources d'Inspection (`Profesional` + `Certificacion`, `Equipo`)** : Les operateurs humains et les bancs de test physiques qui doivent etre habilites et calibres a la date du controle.
4. **Le Cadre Normatif (`Procedimiento`)** : Les regles d'evaluation techniques (visuelles ou dimensionnelles) avec leurs tolerances et limites de gravite.
5. **L'Evenement Transactionnel (`Inspeccion`)** : L'acte de controle liant un echantillon, un operateur, un equipement et un procede a une date donnee.
6. **La Preuve Documentaire (`Reporte` et `Defecto`)** : La "photo" inalterable des causes de non-conformite certifiees.

---

### 2.2 Deroulement chronologique detaille : Qui cree quoi et pourquoi ?

#### 1. Creation du Lot (`Lote`) puis de ses Echantillons (`Muestra`) -- *Composition stricte*
- **Qui cree ?** L'entreprise instancie le `Lote` (`empresa.crear_registrar_lote`). Ensuite, pour creer les echantillons, l'entreprise **delegue la creation au lot** (`empresa.crear_registrar_muestra(cantidad, lote)` qui appelle `lote.crear_muestra(cantidad)`).
- **Pourquoi dans cet ordre ?**
  - **Sens metier** : Un echantillon ne peut pas flotter dans le vide sans appartenir a une production reelle.
  - **Regle 2 de la consigne** : *"Cada muestra pertenece a exactamente un lote"*.
  - **Validation de capacite** : Le lot doit exister au prealable afin de verifier que la somme des quantites d'echantillons ne depasse pas la capacite totale fabriquee (`capacidad_usada + cantidad <= cantidad_fabricada`).
  - **Cycle de vie lie (Composition)** : L'identifiant `_lote_id` est injecte des la naissance de la muestra et devient immuable.

#### 2. Enregistrement des Inspecteurs (`Profesional`) et de leurs Certifications (`Certificacion`)
- **Qui cree ?** L'entreprise enregistre le `Profesional`. Ensuite, on associe les certifications a l'inspecteur (`prof.agregar_certificacion(cert)`).
- **Pourquoi dans cet ordre ?**
  - Une certification n'a de validite que rattachee a une personne identifiee.
  - Les inspecteurs et leurs habilitations doivent etre connus **avant** toute tentative de controle pour que le systeme puisse verifier la validite des competences aux dates d'inspection.

#### 3. Enregistrement des Instruments de Mesure (`Equipo`) et Calibration
- **Qui cree ?** L'entreprise enregistre chaque equipement avec sa categorie technique (ex: `"Visual"`, `"Dimensional"`) et sa date de derniere calibration.
- **Pourquoi dans cet ordre ?**
  - Dans l'industrie (Six Sigma / ISO), aucun test n'a de valeur legale si l'outil de mesure n'est pas prereference et verifie. L'equipement doit exister et posseder son historique de calibration avant de pouvoir etre mobilise.

#### 4. Definition des Procedures d'Inspection (`Procedimiento`)
- **Qui cree ?** L'entreprise configure les procedures concretes (`ProcedimientoVisual`, `ProcedimientoDimensional`) via `**kwargs`.
- **Pourquoi dans cet ordre ?**
  - La procedure definit le protocole : la categorie d'equipement requise, la certification eventuellement exigee (ex: `"ISO"`), et le seuil de gravite cumulee admissible. Sans ce referentiel, aucune inspection ne sait quelles regles appliquer.

#### 5. Lancement de l'Inspection (`Inspeccion`) -- *Validation croisee "Fail-Fast"*
- **Qui cree ?** L'entreprise appelle `empresa.lanzar_inspeccion(muestra, profesional, equipo, procedimiento, fecha)`.
- **Pourquoi ici et comment ?**
  - C'est le point d'assemblage critique. Le constructeur de `Inspeccion` applique le principe de **Fail-Fast** :
    1. Verifie que la muestra est bien libre et en attente (`PENDIENTE`).
    2. Verifie que le professionnel possede la certification requise active a cette date (`es_vigente(fecha)`).
    3. Verifie que l'equipement est de la categorie attendue par le procede (`es_compatible()`).
    4. Verifie que l'equipement est etalonne depuis moins de 182 jours (`esta_calibrado(fecha)`).
  - **Si une regle est enfreinte** : une exception metier est levee immediatement, l'objet `Inspeccion` n'est pas cree, et la `Muestra` reste intacte a l'etat `PENDIENTE` (Regle 5 de la consigne).
  - **Si tout est conforme** : l'echantillon passe a l'etat `EN_INSPECCION` et se lie a l'inspection (`asignar_inspeccion`). Le contexte est verrouille pour la duree du test.

#### 6. Evaluation des Observations et Detection des Defauts (`Defecto`) -- *Polymorphisme*
- **Qui fait quoi ?** L'inspecteur soumet des observations a `inspeccion.ejecutar(observaciones)`.
- **Pourquoi le polymorphisme ?**
  - L'inspection ne connait pas le detail algorithmique du controle : elle appelle `self._procedimiento.evaluar(observaciones)`.
  - Si c'est un procede dimensionnel, il compare mesures et tolerances, calculant une gravite proportionnelle a l'ecart.
  - Si c'est un procede visuel, il convertit les anomalies constatees en defauts visuels.
  - Tous les defauts generes sont ajoutes a la muestra (`muestra.agregar_defecto(defecto)`).

#### 7. Cloture de l'Echantillon et Tracabilite (`Reporte`)
- **Qui fait quoi ?** On appelle `inspeccion.cerrar()`, qui declenche `muestra.cerrar(limite_gravedad)`.
- **Pourquoi et quel resultat ?**
  - La muestra applique la regle de conformite :
    - Si elle possede au moins un defaut critique (gravite = 5) OU si la somme de ses gravites depasse le seuil du procede $\rightarrow$ etat `NO_CONFORME`.
    - Sinon $\rightarrow$ etat `CONFORME`.
  - **Creation automatique du `Reporte`** : Si l'echantillon est `NO_CONFORME`, la muestra genere immediatement son `Reporte` officiel qui capture une copie inalterable des defauts, du responsable, du lot et de la date.
  - L'echantillon est definitivement gele (interdiction d'ajouter des defauts ou de le reinspecter).

#### 8. Decision Finale sur le Lot (`Lote.decidir()`) -- *Criteres Six Sigma*
- **Qui decide ?** Le `Lote` lui-meme.
- **Pourquoi a la fin ?**
  - Une decision industrielle ne peut jamais etre prise sur un lot incomplet. Le lot verifie d'abord que **100% de ses echantillons sont fermes** (`todas_cerradas() == True`).
  - Il calcule le pourcentage de non-conformite (`porcentaje_no_conforme()`).
  - Si le pourcentage depasse 5% $\rightarrow$ `RECHAZADO`. Si le pourcentage est $\le 5\%$ (5% exact inclus) $\rightarrow$ `APROBADO`.
  - Le lot bascule dans un etat terminal irrevocable.

---

## 3. Architecture Detailee et Analyse des Fichiers

Apres avoir compris la logique operationnelle globale, nous pouvons analyser chaque fichier sous le capot, ses choix techniques et ses specificites Python.

### 3.1 Fichiers de base

#### `excepciones.py` -- Exceptions custom
**Utilite** : Definir des exceptions de domaine specifiques au lieu d'utiliser `ValueError` generique.

**Specificites Python** :
- **Heritage de classes** : toutes heritent de `CalidadError` qui herite de `Exception`
- **Hierarchie d'exceptions** : permet de catcher `CalidadError` pour attraper TOUTES les erreurs du domaine, ou catcher une exception specifique

**Pourquoi custom au lieu de ValueError ?**
La consigne l'exige (regle 86). En plus, ca permet de distinguer les erreurs metier des erreurs Python standard. Par exemple, `pytest.raises(TransicionIlegalError)` est plus explicite que `pytest.raises(ValueError)`.

**Classes** :
| Exception | Usage |
|---|---|
| `CalidadError` | Base commune de toutes les exceptions metier |
| `DatosInvalidosError` | Donnees invalides (quantites, gravedades, textes vides) |
| `EquipoNoAptoError` | Equipement non calibre ou categorie incompatible |
| `CertificacionNoVigenteError` | Certification absente ou perimee a la date voulue |
| `TransicionIlegalError` | Transitions d'etat illegales (fermer une muestra deja fermee, capacite depassee) |
| `InspeccionInvalidaError` | Operations sur inspection fermee |

---

#### `validacion.py` -- Fonctions de validation centralisees
**Utilite** : Centraliser TOUTE la logique de validation dans un seul endroit (principe DRY). Chaque classe appelle ces fonctions au lieu de dupliquer les verifications.

**Specificites Python** :
- **Fonctions pures** (pas de classes) : chaque fonction prend une valeur, la valide, et la retourne ou leve une exception
- **`isinstance(valor, int) or isinstance(valor, bool)`** : en Python, `bool` est une sous-classe de `int` (`True == 1`). Il faut explicitement exclure les booleens
- **f-strings** : `f"Le champ '{nombre_campo}'..."` -- interpolation propre et performante

**Pourquoi retourner la valeur ?**
Pour pouvoir ecrire `self._cantidad = validar_cantidad(cantidad)` en une seule ligne (pattern "validate and assign").

**Fonctions** :
| Fonction | Valide | Retourne |
|---|---|---|
| `validar_entero(valor)` | Est un int (pas bool) | La valeur |
| `validar_cantidad(cantidad)` | Int > 0 | La valeur |
| `validar_gravedad(gravedad)` | Int entre 1 et 5 | La valeur |
| `validar_texto(texto)` | String non vide, lettres uniquement | La valeur |
| `validar_descripcion(descripcion)` | String non vide (accepte chiffres) | La valeur |
| `validar_fecha_tipo(fecha)` | Instance de `date` | La valeur |
| `validar_rango_fechas(inicio, fin)` | inicio <= fin | Rien |
| `validar_rango_entero(valor, min, max)` | Int dans [min, max] | La valeur |

---

### 3.2 Enums

#### `estado_muestra.py` et `estado_lote.py`
**Utilite** : Representer les etats possibles d'une muestra et d'un lote sous forme de constantes immuables.

**Specificites Python** :
- **`Enum`** (de `enum`) : empeche d'utiliser des strings brutes comme `"PENDIENTE"`. Compare par identite (`==`) au lieu de comparer des strings
- **`.value`** : retourne le string associe (pour affichage)

**Pourquoi Enum au lieu de strings ?**
- Autocompletion dans l'IDE
- Erreur a l'analyse si faute de frappe
- Garantie que seules les valeurs definies sont possibles

---

### 3.3 Classes de domaine

#### `defecto.py` -- Defecto
**Utilite** : Represente une deviation observee. Immutable apres creation.

**Specificites Python** :
- **`@property`** : expose les attributs en lecture seule (`tipo`, `descripcion`, `gravedad`). Modifier `d.tipo = "x"` leve une exception `AttributeError`
- **`_` prefix** (convention) : attributs prives

**Methode `copia()`** :
Cree une nouvelle instance independante. Utilisee par `Reporte` pour "congeler" les defauts au moment du rapport. Si on ne copiait pas, modifier la liste originale modifierait aussi le rapport.

**Methode `es_critico()`** :
Retourne `True` si gravite == 5. Encapsule la regle metier (Consigne regle 8).

---

#### `certificacion.py` -- Certificacion
**Utilite** : Represente une certification d'un professionnel avec dates de validite.

**Methode `es_vigente(fecha)`** :
Verifie `fecha_inicio <= fecha <= fecha_fin` (bornes inclusives, consigne regle 5).

---

#### `equipo.py` -- Equipo
**Utilite** : Represente un instrument de mesure avec sa categorie et date de calibration.

**Specificites Python** :
- **`uuid.uuid4()`** : genere un identifiant unique universel
- **`timedelta`** implicite : `(fecha - self._fecha_calibracion).days` -- soustraction de deux `date` retourne un `timedelta`, `.days` extrait le nombre de jours

**Methode `esta_calibrado(fecha)`** :
`0 <= dias <= 182` -- verifie que la calibration est dans le passe (pas future) et dans les 182 jours (consigne regle 4).

**Methode `es_compatible(categoria)`** :
Simple comparaison d'egalite de strings.

---

#### `profesional.py` -- Profesional
**Utilite** : Represente un inspecteur avec ses certifications.

**Specificites Python** :
- **`dict` pour `_certificaciones`** au lieu de `list` : acces O(1) par nom au lieu de O(n) avec une boucle
- **`dict.get(nombre)`** : retourne `None` si la cle n'existe pas (au lieu de lever `KeyError`)
- **`dict(self._certificaciones)`** : retourne une copie superficielle du dict (protege l'interne)

**Pourquoi dict au lieu de list ?**
La consigne demande d'utiliser des `dict`. En plus, la recherche devient instantanee :
```python
cert = self._certificaciones.get(nombre)
return cert is not None and cert.es_vigente(fecha)
```

---

#### `muestra.py` -- Muestra
**Utilite** : Represente un echantillon du lot. Gere ses propres transitions d'etat.

**Lien fort avec `Lote` (Composition)** :
- `Muestra(cantidad, lote_id)` exige obligatoirement `lote_id` des la construction.
- Une muestra **ne peut jamais exister sans lot** (Regle 2 de la consigne : *"Cada muestra pertenece a exactamente un lote"*). L'attribut `_lote_id` est immutable et expose en lecture seule via `@property lote_id`.

**Specificites Python** :
- **`tuple(self._defectos)`** : retourne une version immutable de la liste. Empeche `muestra.defectos.append(x)` depuis l'exterieur
- **`sum(map(lambda d: d.gravedad, self._defectos))`** :
  - `map()` applique la lambda a chaque defaut, produisant un iterateur de gravedades
  - `sum()` additionne toutes les valeurs
- **`any(map(lambda d: d.es_critico(), self._defectos))`** :
  - `any()` retourne `True` des qu'un element est `True` (court-circuit)
  - Plus efficace qu'une boucle for classique

**Pourquoi `tuple` au lieu de `list` pour `defectos` ?**
La consigne (regle 9) dit : "apres fermeture, on ne peut pas ajouter/retirer/remplacer de defauts". Un tuple est **immutable** : pas de `.append()`, `.remove()`, `[i] = x`. C'est la garantie structurelle que le code appelant ne peut pas modifier la collection.

**Pourquoi `sum(map(...))` au lieu d'une boucle for ?**
- Plus concis et declaratif
- La consigne demande explicitement d'utiliser `map()`
- Fonctionnellement equivalent, mais plus "pythonique"

**Transitions d'etat** :
```
PENDIENTE  -->  EN_INSPECCION  -->  CONFORME
                                -->  NO_CONFORME
```
Chaque transition est protegee par une verification de l'etat actuel. Un etat final (CONFORME/NO_CONFORME) bloque toute modification future.

**Methode `asignar_inspeccion()`** :
Existe pour **respecter l'encapsulation**. Au lieu de `muestra._inspeccion = self` (acces direct a un attribut prive), on passe par une methode publique qui peut valider qu'aucune inspection n'etait deja associee.

---

#### `lote.py` -- Lote
**Utilite** : Represente un lot de composants. Contient des echantillons et decide l'approbation/rejet.

**Methode `crear_muestra(cantidad)` (Composition)** :
C'est le `Lote` qui cree lui-meme ses echantillons :
1. Valide la quantite avec `validar_cantidad(cantidad)`
2. Calcule la capacite deja utilisee via `sum(map(lambda m: m.cantidad, self._muestras.values()))`
3. Verifie que `capacidad_usada + cantidad <= cantidad_fabricada` (leve `TransicionIlegalError` sinon)
4. Instancie `Muestra(cantidad, self._id)` et l'enregistre dans son dict `_muestras`
5. Retourne l'instance de `Muestra`

**Specificites Python** :
- **`dict` pour `_muestras`** : `{muestra.id: muestra}` -- acces O(1) par UUID
- **`sum(map(lambda m: m.cantidad, self._muestras.values()))`** : calcule la capacite utilisee
- **`all(map(...))`** : verifie que TOUTES les muestras sont dans un etat final
- **`dict.get(tipo, 0)`** dans `conteo_por_tipo()` : retourne 0 si la cle n'existe pas

**Pourquoi `dict.get(tipo, 0) + 1` au lieu de `if/else` ?**
```python
conteo[d.tipo] = conteo.get(d.tipo, 0) + 1
```
`dict.get(cle, valeur_par_defaut)` est un idiome Python standard qui remplace elegamment le pattern if/else.

**Decision du lot** :
- Verifie que le lot est en `EN_PRODUCCION` (pas deja decide)
- Verifie qu'il a au moins une muestra
- Verifie que toutes les muestras sont fermees
- Calcule le % : `no_conforme_count / total * 100`
- `> 5` --> `RECHAZADO`, `<= 5` --> `APROBADO`

---

#### `reporte.py` -- Reporte
**Utilite** : Document de respaldo pour une muestra `NO_CONFORME`. Contient une copie figee des defauts.

**Specificites Python** :
- **`tuple(map(lambda d: d.copia(), defectos))`** :
  - `map()` : applique `copia()` a chaque defaut (cree une nouvelle instance)
  - `tuple()` : rend le resultat immutable
  - Double protection : les objets sont copies ET la collection est un tuple

**Pourquoi copier les defauts ?**
Si on stockait les references originales, modifier un defaut apres le rapport modifierait aussi le rapport. La copie garantit que le rapport reste une "photo" fidele du moment ou la muestra a ete fermee.

---

#### `inspeccion.py` -- Inspeccion
**Utilite** : Coordonne le processus d'inspection. Valide les prerequis croises AVANT de demarrer.

**Validations dans le constructeur** (ordre important) :
1. Date est bien un objet `date`
2. Muestra est en etat `PENDIENTE`
3. Professionnel a la certification requise (si le procedimiento en exige une)
4. Equipement est de la bonne categorie
5. Equipement est calibre ($\le 182$ jours)

**Specificites Python** :
- **Validation dans `__init__`** : si une validation echoue, l'exception est levee et l'objet n'est jamais cree. La muestra reste en etat `PENDIENTE` (consigne regle 5)
- **`@property cerrada`** : expose l'etat ferme en lecture seule

**Pourquoi valider dans le constructeur ?**
C'est le pattern **"fail fast"**. Si les prerequis ne sont pas remplis, on n'a jamais d'objet `Inspeccion` invalide en memoire.

---

### 3.4 Procedures et polymorphisme

#### `procedimiento.py` -- Procedimiento (classe abstraite)
**Utilite** : Definit l'interface commune pour tous les types de procedures.

**Specificites Python** :
- **`raise NotImplementedError`** dans `evaluar()` : force les sous-classes a implementer la methode. C'est l'equivalent Python d'une methode abstraite
- **Heritage** : `ProcedimientoDimensional(Procedimiento)` -- herite de la classe de base

#### `proc_dimensional.py` -- ProcedimientoDimensional
**Utilite** : Evalue des observations basees sur des mesures physiques (valeur vs tolerances).
Pour chaque observation avec `desviacion > 0`, calcule la gravite basee sur le ratio desviacion/tolerancia et cree un `Defecto` de type `"DIMENSIONAL"`.

#### `proc_visual.py` -- ProcedimientoVisual
**Utilite** : Evalue des observations visuelles.
Pour chaque observation avec `defecto_detectado == True`, cree un `Defecto` de type `"VISUAL"` avec la gravite indiquee.

#### Polymorphisme en action
```python
defectos = self._procedimiento.evaluar(observaciones)
```
Que `self._procedimiento` soit un `ProcedimientoDimensional` ou `ProcedimientoVisual`, c'est la **meme interface** (`evaluar()`). Le comportement change selon le type concret. C'est le **polymorphisme par heritage**.

---

### 3.5 Observations

#### `observacion_dimensional.py` -- ObservacionDimensional
**Specificites Python** :
- **Proprietes calculees** `desviacion` et `tolerancia` : ce ne sont pas des attributs stockes, mais des valeurs calculees a chaque acces via `@property`.

#### `observacion_visual.py` -- ObservacionVisual
**Specificites Python** :
- **Parametre optionnel** `gravedad=None` : la gravite n'est requise que si `defecto_detectado` est `True`.

---

### 3.6 Façade

#### `empresa.py` -- Empresa
**Utilite** : Point d'entree pour creer et enregistrer tous les objets. Pattern **Facade**.

**Delegation de creation pour la composition** :
- `crear_registrar_muestra(cantidad, lote)` : Empresa delegue la creation au `lote` via `lote.crear_muestra(cantidad)`, puis enregistre l'instance dans son registre `self._registros["muestras"][muestra.id]`. Le lot reste le proprietaire direct de la muestra.

**Specificites Python** :
- **`dict` de `dict`** : `self._registros = {"lotes": {}, "muestras": {}, ...}` -- un registre central organise par categorie
- **`**kwargs`** dans `crear_registrar_procedimiento` : permet de passer des arguments nommes variables sans figer la signature

```python
empresa.crear_registrar_procedimiento(
    ProcedimientoVisual,
    limite_gravedad_acumulada=5,
    categoria_equipo_requerida="Visual",
    certificacion_requerida="ISO"
)
```

---

### 3.7 Execution

#### `main.py`
**Utilite** : Demontre le flux complet en 10 etapes sequentielles :
1. Creer un lot + 20 echantillons via `empresa.crear_registrar_muestra(50, lote)` (composition)
2. Creer des professionnels avec certifications
3. Creer des equipements calibres
4. Creer des procedures (visual + dimensional) via `**kwargs`
5. Demontrer les validations qui rejettent (certification absente, calibration perimee, categorie incompatible)
6. Executer des inspections visuelles
7. Executer une inspection dimensionnelle
8. Consulter les statistiques du lot (sans effets de bord)
9. Decider le lot
10. Afficher le resume avec les rapports

---

## 4. Relations entre les classes (Analyse UML)

### 4.1 Types de relations UML

#### Composition (losange noir `*--`) : "fait partie de" -- cycle de vie lie
**Si le conteneur est detruit, les contenus sont detruits aussi.**

| Relation | Explication | Dans le code |
|---|---|---|
| `Lote *-- Muestra` | Une muestra appartient obligatoirement a exactement un lot des sa creation (Regle 2). Le lot cree et controle lui-meme ses echantillons | `lote.crear_muestra(cantidad)` instancie `Muestra(cantidad, self._id)` en interne |
| `Muestra *-- Defecto` | Les defauts n'existent que dans le contexte d'une muestra | `self._defectos = []` -- la liste est creee dans Muestra et appartient a Muestra |
| `Profesional *-- Certificacion` | Les certifications n'ont pas de sens sans le professionnel | `self._certificaciones = {}` -- le dict est cree dans Profesional |
| `Reporte *-- Defecto` | Le rapport contient des copies figees des defauts | `self._defectos = tuple(map(...))` -- copies creees a la construction |

#### Agregation (losange blanc `o--`) : "contient" -- cycle de vie independant
**Les contenus peuvent exister sans le conteneur.**

Dans cette architecture, la relation `Lote` / `Muestra` est une **composition stricte** (`*--`) et non une agregation : une `Muestra` ne peut jamais exister sans son `Lote` (cycle de vie lie, `lote_id` obligatoire des l'instanciation, respectant la Regle 2 du domaine).

#### Association (fleche `-->`) : "utilise / reference"
**Simple reference, pas de cycle de vie lie.**

| Relation | Explication | Dans le code |
|---|---|---|
| `Inspeccion --> Muestra` | L'inspection reference une muestra mais ne la "possede" pas | `self._muestra = muestra` |
| `Inspeccion --> Profesional` | Idem | `self._profesional = profesional` |
| `Inspeccion --> Equipo` | Idem | `self._equipo = equipo` |
| `Inspeccion --> Procedimiento` | Idem | `self._procedimiento = procedimiento` |
| `Muestra --> Reporte` | La muestra reference son rapport | `self._reporte = Reporte(...)` |

#### Dependance (fleche pointillee `..>`) : "utilise temporairement"
**Pas de reference stockee, juste un usage dans une methode.**

| Relation | Explication |
|---|---|
| `Empresa ..> Lote/Muestra/...` | Empresa cree ces objets mais ne les "possede" pas au sens objet -- ils vivent dans un dict |
| `ProcedimientoDimensional ..> ObservacionDimensional` | Le procedimiento recoit les observations en parametre de `evaluar()` |
| `Muestra ..> EstadoMuestra` | Muestra utilise l'enum pour son etat |
| `Lote ..> EstadoLote` | Lote utilise l'enum pour son etat |

#### Heritage (fleche triangle `<|--`)

| Relation | Dans le code |
|---|---|
| `Procedimiento <\|-- ProcedimientoDimensional` | `class ProcedimientoDimensional(Procedimiento):` |
| `Procedimiento <\|-- ProcedimientoVisual` | `class ProcedimientoVisual(Procedimiento):` |

---

## 5. Recapitulatif des specificites Python

| Concept Python | Ou | Pourquoi |
|---|---|---|
| **`dict`** | Profesional, Lote, Empresa, conteo_por_tipo | Acces O(1) par cle, la consigne le demande |
| **`dict.get()`** | Profesional.tiene_certificacion_vigente, Lote.conteo_por_tipo, Empresa.obtener_* | Evite `KeyError` si la cle n'existe pas |
| **`map()`** | Muestra.suma_gravedades, tiene_critico, Lote.porcentaje, Reporte copie | Transformation fonctionnelle, la consigne le demande |
| **`sum()`** | Muestra.suma_gravedades, Lote.capacidad, porcentaje | Agregation sur iterateur |
| **`any()`** | Muestra.tiene_critico | Court-circuit : s'arrete au premier True |
| **`all()`** | Lote.todas_cerradas | Court-circuit : s'arrete au premier False |
| **`lambda`** | Partout avec map() | Fonction anonyme inline |
| **`tuple()`** | Muestra.defectos, Lote.muestras, Reporte._defectos | Collection immutable |
| **`**kwargs`** | Empresa.crear_registrar_procedimiento | Arguments nommes variables |
| **`Enum`** | EstadoMuestra, EstadoLote | Constantes typees |
| **`uuid.uuid4()`** | Toutes les classes avec id | Identifiants uniques universels |
| **`@property`** | Toutes les classes | Encapsulation lecture seule |
| **`f-strings`** | Toutes les classes (repr, messages) | Interpolation de variables |
| **`isinstance()`** | Validations, Profesional | Verification de type a l'execution |
| **`date`/`timedelta`** | Equipo, Certificacion, Inspeccion | Calculs de dates (consigne regle 88) |
| **Heritage** | Procedimiento --> Dimensional/Visual | Polymorphisme |
| **Exceptions custom** | excepciones.py | Erreurs metier (consigne regle 86) |

---

## 6. Tests -- Couverture des regles de negocio

| Test | Regle consigne |
|---|---|
| Identifiants dupliques, quantites invalides | Regle 1 |
| Muestras excedant la capacite du lot | Regle 2 |
| Gravedades 1, 5, hors range | Regle 3 |
| Calibration a 182 jours exacte et 183 jours | Regle 4 |
| Certification absente, perimee, valide aux bornes | Regle 5 |
| Transition PENDIENTE --> EN_INSPECCION uniquement | Regle 6 |
| Evaluation polymorphe (dimensional + visual) | Regle 7 |
| Somme au limite, au-dessus, defaut critique | Regle 8 |
| Modifier/reinspecter muestra fermee --> erreur | Regle 9 |
| Contenu et unicite du rapport | Regle 10 |
| Lot incomplet, exactement 5%, au-dessus 5% | Regle 11 |
| Comptage critiques sans effets secondaires | Regle 12 |
