'''
Definición de la clase agente
'''
from time import perf_counter
from datetime import datetime
from pathlib import Path
from os import getenv
from decimal import Decimal
import csv
from json import loads, dumps
from src.log_gen import log
from src.pricing_estimates import MODEL_PRICING, MODEL_EMBEDDING_PRICING, guardar_metricas, guardar_metricas_embedding
from openai import OpenAI
import tiktoken
from pydantic import BaseModel, StringConstraints
from typing import Annotated
import chromadb

from openai.types.responses import ResponseInputItemParam



NumericString = Annotated[str, StringConstraints(pattern=r"^\d+$")]
class Answer(BaseModel):
    system_answer: str
    chunks_related: list[NumericString]

class Agent:
    '''
    Agente de soporte al cliente
    '''
    # Modelos permitidos
    ALLOWED_MODELS = [
        'gpt-4o-mini', # por defecto
        'gpt-4o',
        'gpt-5-mini',
    ]

    ALLOWED_EMBEDDING_MODELS = [
        'text-embedding-3-small', # por defecto
        'text-embedding-3-large',
    ]

    # Prices (USD) per 1M tokens
    # [15-02-2026] Fuente: https://developers.openai.com/api/docs/pricing

    def __init__(self, chroma_collection_name):
        '''
        Inicializa el modelo.
        '''
        try:
            # Inicializar libreria de OpenAI
            self.client = OpenAI()
            self.model = 'gpt-4o-mini' # por defecto
            self.temperature = 0.2 # por defecto

            # Setear modelo de embeddings correcto desde .env
            EMBEDDINGS_MODEL=str(getenv('EMBEDDINGS_MODEL'))
            self.embeddings_model = EMBEDDINGS_MODEL

            # tiktoken encoder
            self.enc = tiktoken.encoding_for_model(self.model)
            self.embedding_enc = tiktoken.encoding_for_model(self.embeddings_model)

            # Metrics
            self.metrics = []

            # Cargar Prompt principal
            with open('./prompts/main_prompt.txt') as prompt_file:
                self.system_prompt = prompt_file.read()

            # Cargar ChromaDB para el uso del agente
            CHROMADB_PATH=str(getenv('CHROMADB_PATH'))
            
            self.db_collection = chromadb.PersistentClient(
                path=CHROMADB_PATH
            ).get_or_create_collection(
                name=chroma_collection_name
                )
            
            log('Agente inicializado exitosamente.')
        except Exception as err:
            log(f'Falló la inicialización del agente: {err}', 'error')
    
        return

    def setmodel(self, model):
        '''
        Establece el modelo a consultar
        '''
        
        if model in self.ALLOWED_MODELS:
            self.model = model
            log(f'Modelo cambiado a: {model}')

            # Cambiar encoder al modelo correspondiente
            self.enc = tiktoken.encoding_for_model(self.model)

        else:
            raise Exception('Modelo no permitido.')

    def settemp(self, temp: float):
        '''
        Establece la temperatura del modelo
        '''

        if temp < 0 and temp > 1:
            raise Exception('Valor fuera de rango.')
        self.temperature = temp
        log(f'Temperatura cambiada a {self.temperature}.')

    def estimar_tokens_onetime(self, texto):
        '''
        Suma la cantidad total de tokens de una única consulta al modelo
        Incluye en el cálculo el system prompt.
        '''
        # Sumar tokens
        total = 11 # Base para un único mensaje (sin memoria)
        total += len(self.enc.encode(self.system_prompt))
        total += len(self.enc.encode(texto))
        return total

    def estimar_tokens_embedding(self, texto):
        '''
        Suma la cantidad total de tokens de una única consulta al modelo
        de embeddings.
        '''
        tokens = self.embedding_enc.encode(texto)
        return len(tokens)

    """ def validar_respuesta(self, response, retries):
        '''
        Se implementó validacion de campos con Pydantic.
        '''
        return True """
        
    def consultar_por_embedding(self, text, n_results=3):
        '''
        Recibe un texto (query del usuario) y la convierte en embeddings
        luego consulta en la coleccion de chromadb por documentos similares
        semanticamente.

        Antes de enviar la consulta, estima la cantidad de tokens de la entrada.
        
        Después enviar la consulta, registra la cantidad de tokens.
        '''
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        # Estimar tokens
        tokens_prompt = self.estimar_tokens_embedding(text)

        # Llamar api de OpenAI Embeddings
        
        t1 = perf_counter()
        response = self.client.embeddings.create(
            model=self.embeddings_model,
            input=text
        )
        t2 = perf_counter()
        response_time = (t2 - t1) * 1000

        # Log y guardado de métricas
        log(f'Respuesta de API Embeddings recibida | Tiempo: {response_time:.0f} ms | Tokens - prompt: {tokens_prompt}')
        guardar_metricas_embedding(timestamp, self.embeddings_model, tokens_prompt, response_time)

        # Consultar embedding en DB
        embedding = response.data[0].embedding
        results = self.db_collection.query(
            query_embeddings=[embedding],
            n_results=n_results
        )

        # Devolver resultados como dict
        unified_results = []
        for i in range(len(results['ids'][0])):
            unified_results.append(
                {
                    'id': results['ids'][0][i],
                    'chunk': results['documents'][0][i]
                }
            )
        return unified_results

    def consultar_por_embedding_id(self, ids):
        '''
        Recibe una lista de IDs, devuelve una lista con los fragmentos
        almacenados en base de datos
        '''

        results = self.db_collection.get(
            ids=ids,
            include=["documents"]
        )

        return results["documents"]


    def onetime_query_model(self, mensaje: str):
        '''
        Hace una única consulta al modelo (sin memoria) con RAG

        Antes de enviar la consulta, estima la cantidad de tokens de la entrada.
        
        Al enviar la consulta, registra la cantidad de tokens totales devueltos 
        por el modelo.
        '''

        # consultar por embeddings
        resultados_embeddings = self.consultar_por_embedding(mensaje)

        # Construir prompt con contexto
        contexto = ''
        for res in resultados_embeddings:
            contexto += str(res)+'\n'

        current_system_prompt = self.system_prompt.format(contexto=contexto)

        
        messages: list[ResponseInputItemParam] = [
            {"role": "system", "content": str(current_system_prompt)},
            {"role": "user", "content": str(mensaje)},
        ]

        estimacion_tokens = self.estimar_tokens_onetime(mensaje)
        log(f'Tokens estimados: {estimacion_tokens}')

        logtext_mensaje = mensaje.replace("\n", "\\n")
        logtext_system_prompt = self.system_prompt.replace("\n", "\\n")

        log(f'Consultando API... | Texto consulta: {logtext_mensaje} | Main Prompt: {logtext_system_prompt}')

        valid_answer = False
        retries = 0
        while not valid_answer and retries < 3:
            timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            t1 = perf_counter()
            
            if self.model == 'gpt-5-mini':  # No usar parametro de temperatura
                response = self.client.responses.parse(
                    model=self.model,
                    input=messages,
                    text_format=Answer,
                    #temperature=self.temperature,
                )
            else:
                response = self.client.responses.parse(
                    model=self.model,
                    input=messages,
                    temperature=self.temperature,
                    text_format=Answer,
                )

            t2 = perf_counter()
            response_time = (t2 - t1) * 1000
            
            # Uso
            tokens_prompt = response.usage.input_tokens
            tokens_completion = response.usage.output_tokens
            tokens_total = response.usage.total_tokens

            log(f'Respuesta de API recibida | Tiempo: {response_time:.0f} ms | Tokens - prompt: {tokens_prompt}, respuesta: {tokens_completion}, total: {tokens_total} | Respuesta: {response.output_text}')

            # Métricas
            guardar_metricas(timestamp, self.model, tokens_prompt, tokens_completion, tokens_total, response_time)

            # Verificar validez de respuesta (Formato JSON)
            valid_answer = True #self.validar_respuesta(response, retries) # Recibe retries para logging

            if not valid_answer:
                retries += 1
        
        if not valid_answer and retries >= 3:
            log(f'No se pudo generar una respuesta válida', 'error')
            return dumps({ 'Error': 'No se pudo generar una respuesta válida'})
        
        # Transformar respuesta a JSON y añadir campo user_question
        # Imprimir respuesta del agente
        respuesta = loads(response.output_text)
        respuesta['user_question'] = mensaje
        
        # Retornar texto de la respuesta si es válido
        return respuesta