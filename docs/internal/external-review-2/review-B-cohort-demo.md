Creo que aquí hay una oportunidad para hacer la demo mucho más potente.

Después de leer el PDF de Matías varias veces, **no creo que el mejor ejemplo sea un paciente individual**. El PDF no trata de medicina personalizada, sino de **investigación mecanística**.

El jurado debería entender en menos de un minuto qué problema resuelve el agente.

**El ejemplo que yo elegiría (10/10)**

**El investigador llega con una pregunta**

No llega con un paciente.

Llega con una hipótesis.

Por ejemplo, Pedro Guitián dice:

**"Durante años he visto pacientes con diabetes, periodontitis y artritis reumatoide. Algunos reciben tocilizumab y otros no. Quiero saber si la evolución del eje inflamatorio IL-6/CRP sigue un patrón diferente entre ambos grupos."**

Esa pregunta es excelente porque utiliza exactamente todas las piezas del PDF:

* enfermedad periodontal;  
* diabetes;  
* IL-6;  
* CRP;  
* tocilizumab;  
* investigación;  
* hipótesis falsable.

Y además **no menciona Alzheimer como objetivo**, dejando el eje neuro como exploratorio, tal como hace el documento.

---

**Lo que ocurre hoy**

Pedro tendría que revisar manualmente cientos de documentos.

Por ejemplo:

438 periodontogramas

213 analíticas

167 informes de reumatología

92 CBCT

41 informes médicos externos

Probablemente tardaría semanas.

---

**Lo que hace HISTORA**

Pedro escribe:

**"Encuentra pacientes con:**

* periodontitis estadio III o IV;  
* diabetes tipo 2;  
* artritis reumatoide;  
* tratamiento con tocilizumab o sin él;  
* al menos dos PCR;  
* seguimiento superior a un año."

Claude responde.

---

**Paso 1**

Identifica automáticamente

Base total

↓

2.846 pacientes

↓

Periodontitis III-IV

↓

148

↓

Diabetes

↓

57

↓

Artritis

↓

21

↓

Tocilizumab

↓

11

Ya aquí el jurado entiende el valor.

---

**Paso 2**

Construye automáticamente

Paciente

↓

Timeline

↓

Periodontograma

↓

HbA1c

↓

PCR

↓

Inicio Tocilizumab

↓

Tratamiento periodontal

↓

Nueva PCR

↓

Nueva HbA1c

Para los 11 pacientes.

---

**Paso 3**

El agente detecta

Paciente 3

↓

Falta PCR posterior

Paciente 7

↓

No existe HbA1c

Paciente 9

↓

No hay seguimiento

Paciente 11

↓

No consta tratamiento periodontal

Eso me parece espectacular.

Porque ningún investigador quiere descubrir eso después de tres meses.

---

**Paso 4**

Claude genera

No una conclusión.

Sino

una hipótesis.

Por ejemplo.

**"Se identificó una cohorte de pacientes con información suficiente para estudiar la relación entre la evolución periodontal y los cambios en PCR en pacientes expuestos y no expuestos a bloqueo del receptor IL-6. Los datos disponibles permiten plantear la hipótesis, pero son insuficientes para establecer un efecto causal."**

Eso es exactamente el espíritu del PDF.

---

**Después añade la genética**

Y aquí viene la parte brillante.

Claude dice.

**"La hipótesis propuesta es consistente con la evidencia genética disponible sobre IL-6R descrita mediante randomización mendeliana, pero requiere validación clínica en esta cohorte."**

No está utilizando la genética para diagnosticar.

La utiliza para reforzar la plausibilidad biológica.

Eso es elegantísimo.

---

**Y Alzheimer**

Aquí no haría absolutamente nada más.

Simplemente una frase.

**"El eje neuro se mantiene como exploratorio y no forma parte de las conclusiones de esta cohorte."**

Eso demuestra disciplina científica.

---

**¿Por qué creo que este ejemplo es un 10/10?**

Porque utiliza **todos los elementos del PDF** sin añadir nada nuevo:

* ✅ periodontitis;  
* ✅ IL-6;  
* ✅ CRP;  
* ✅ diabetes;  
* ✅ tocilizumab;  
* ✅ randomización mendeliana;  
* ✅ hipótesis falsable;  
* ✅ datos fragmentados;  
* ✅ Claude;  
* ✅ guardrail;  
* ✅ investigación;  
* ✅ no diagnóstico.

No hace falta hablar de wearables, gemelos digitales o biomarcadores salivales para que la historia funcione.

---

**Mi única mejora respecto al PDF**

Solo añadiría una escena inicial muy visual.

En lugar de empezar con IL-6, empezaría con Pedro diciendo:

**"Tengo una hipótesis de investigación. Sé que los datos están en la clínica, pero están repartidos en cientos de documentos y no puedo construir la cohorte sin dedicar semanas a revisar historias clínicas."**

Cinco segundos después aparece Claude y responde:

**"He encontrado 11 pacientes que cumplen los criterios. Ya he reconstruido su historia longitudinal, detectado los datos que faltan y preparado una cohorte lista para investigar la hipótesis."**

Y **solo entonces** aparece el esquema mecanístico **IL-6 → CRP → ejes cardiovascular, metabólico y neuro (exploratorio)**.

Ese orden cambia por completo la narrativa:

* primero se presenta un **problema real de investigación clínica**;  
* después se demuestra cómo el agente elimina el cuello de botella;  
* finalmente se explica el mecanismo biológico que da sentido científico a la hipótesis.

Creo que esa secuencia hará que el proyecto resulte mucho más intuitivo para un jurado que no sea especialista en inmunología, sin perder el rigor científico del PDF de Matías.

