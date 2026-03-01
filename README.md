# Projecto individual M2 - Curso AI Engineering

## Setup

El entorno de desarrollo donde se creó y desarrolló este repositorio es WSL (Ubuntu) dentro de Windows 11 con `uv` y Python 3.12 instalado.

**Configurar variables de entorno:**

```bash
cp .env.example .env
```

Nota: Completar variable `OPENAI_API_KEY` en `.env` y borrar comentarios.

---

**Para instalar dependencias** detalladas en uv.lock

```bash
# Instalar dependencias
uv sync

# Activar entorno virtual
source .venv/bin/activate
```

## Ejecución

Para ejecutar el pipeline de datos, utilizar el notebook `00 data-pipeline.ipynb`.

Para ejecutar el pipeline de querys, utilizar el notebook `01 query-pipeline.ipynb`

**Nota: Para que el funcionamiento de ambos archivos sea coherente, asegurarse de escoger las mismas variables de control en ambos notebooks**, es decir, si se escoge como estrategia de chunking `"FIXED_SIZE"` en el pipeline de datos, se debe escoger también `"FIXED_SIZE"` en el pipeline de querys.

## Consideraciones y otros

Para el desarrollo de este PI seguí lo indicado en `instrucciones.md` que es un copiar-pegar de lo ubicado en la lecture [M2PI | Proyecto](https://www.app.soyhenry.com/my-cohort/c1be21ab-e806-4e47-9052-446e5dcff8f8/lecture/b97aa635-bce6-4667-982b-75d4eb9e0d6e)

Para generar el documento `faq_document.md` (escogí formato Markdown por conveniencia) utilicé el prompt guardado en `prompt.txt` (ambos archivos en la carpeta `data`) y el resultado fue ajustado un poco por mí. 

Para esta tarea decidí implementar dos estrategias de chunking, semántico y tamaño fijo:

- **Semántico:** Dado que el documento es un archivo markdown donde las preguntas son headers y las respuestas el texto a continuación, me aprovecho de ese formato y separo el documento por los caracteres `#`. Esta estrageia es conveniente para este caso ya que de esta forma me aseguro que cad chunk corresponda a una sola pregunta y no se pierda la pregunta o respuesta en el chunking. Utilizando esta estrategia se obtienen un **total de 24 chunks** a partir del documento.
- **Tamaño fijo:** Decidí implementar también esta esta estrategia para comparar. Utilicé como base el primer codigo que aparece en la lectures pero lo modifiqué para que devuelva la metadata necesaria para la recuperación del fragmento de texto y su ubicación en el documento original. En el código está implementado que el chunking se haga por cantidad de palabras, con un tamaño de 50 palabras cada chunk y con un solapado de 15 palabras, eso da como resultado **un total de 36 chunks**.

Los embeddings se generan con el la API de OpenAI, usando el modelo indicado en el `.env`. Los modelos permitidos son `text-embedding-3-small` y `text-embedding-3-large`.

Para el storage de los embeddings, utilicé *ChromaDB* y la búsqueda de vectores es por ANN usando similitud de coseno (Se configuró ChromaDB para que así sea.)

Para asegurar que el modelo devuelva los campos requeridos (`system_answer` y `chunks_related`), utilicé `Pydantic` y el campo `user_question` se lo agrego manualmente en la respuesta, ya es redundante solicitar que el modelo devuelva por generación la user question además de que eso significa tokens adicionales en la respuesta.

Generé dos archivos de output, `sample_output_{nombre_metodo_chunking}.json`, para dejar registrado que ambos metodos de chunking funcionan.

Escogí hacer dos notebooks por separado (`00 data-pipeline` y `01 query-pipeline`) para separar claramente la ingesta de datos de la ejecución de las queries y para hacer mas interactiva la ejecución.

_Por temas de tiempo no implementé el Agente Evaluador mencionado en la rúbrica (¿imagino que es el bonus de la tarea?)._