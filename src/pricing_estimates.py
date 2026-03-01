from decimal import Decimal
import csv
from pathlib import Path
from os import getenv
from src.log_gen import log

# Prices (USD) per 1M tokens
# [15-02-2026] Fuente: https://developers.openai.com/api/docs/pricing
MODEL_PRICING = {
    'gpt-4o-mini' : { # Modelo Barato
        'in': Decimal("0.15"),
        'out': Decimal("0.60"),
    }, 
    'gpt-4o' : { # Modelo caro, Oof
        'in': Decimal("2.50"),
        'out': Decimal("10.00"),
    },
    'gpt-5-mini' : {
        'in': Decimal("0.25"),
        'out': Decimal("2.00"),
    },
}

MODEL_EMBEDDING_PRICING = {
    'text-embedding-3-small' : { # Modelo Barato
        'in': Decimal("0.02"),
    }, 
    'text-embedding-3-large' : { # Modelo caro
        'in': Decimal("0.13"),
    },
}

def guardar_metricas(timestamp, model, tokens_prompt, tokens_completion, tokens_total, response_time):
        '''
        guarda métricas en la memoria del agente como una lista
        
        recibe:
        - timestamp (str)
        - tokens_prompt => autoexplicativo
        - tokens_completion => tokens respuesta
        - tokens_total => suma de los dos anteriores
        - response_time => latencia

        adicionalmente, dependiendo del modelo actual, calcula el costo de la llamada en USD
        '''
        in_price = MODEL_PRICING[model]['in']
        out_price = MODEL_PRICING[model]['out']

        cost_call = ((Decimal(tokens_prompt) * in_price ) + (Decimal(tokens_completion) * out_price)) / Decimal("1000000")

        metricas_llamada = [
            timestamp,
            tokens_prompt,
            tokens_completion,
            tokens_total,
            f"{response_time:.0f}",
            f"{cost_call}USD"
        ]

        try:
            METRICS_FOLDER = str(getenv('METRICS_FOLDER'))
            
            if METRICS_FOLDER == 'None':
                raise Exception('METRICS_FOLDER inválida.')

            metrics_path = Path(METRICS_FOLDER)

            ruta = metrics_path / "metrics.csv"
            
            with ruta.open("a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Si el archivo está vacío → escribir header
                if ruta.stat().st_size == 0:
                    writer.writerow(
                        ["timestamp",
                         "tokens_prompt", 
                         "tokens_completion",
                         "tokens_total",
                         "response_time",
                         "estimated_cost_usd"]
                    )
                writer.writerow(metricas_llamada)
            
            log(f'Métricas escritas: {metricas_llamada}')

        except Exception as err:
            log(f'Error intentando escribir métricas: {err}', 'error')
            
        return
    
def guardar_metricas_embedding(timestamp, model, tokens_prompt, response_time):
    '''
    guarda métricas en la memoria del agente como una lista
    
    recibe:
    - timestamp (str)
    - tokens_prompt => autoexplicativo
    - response_time => latencia

    adicionalmente, dependiendo del modelo actual, calcula el costo de la llamada en USD
    '''
    in_price = MODEL_EMBEDDING_PRICING[model]['in']

    cost_call = ((Decimal(tokens_prompt) * in_price )) / Decimal("1000000")

    metricas_llamada = [
        timestamp,
        tokens_prompt,
        0,
        tokens_prompt,
        f"{response_time:.0f}",
        f"{cost_call}USD"
    ]

    try:
        METRICS_FOLDER = str(getenv('METRICS_FOLDER'))
        
        if METRICS_FOLDER == 'None':
            raise Exception('METRICS_FOLDER inválida.')

        metrics_path = Path(METRICS_FOLDER)

        ruta = metrics_path / "metrics.csv"
        
        with ruta.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Si el archivo está vacío → escribir header
            if ruta.stat().st_size == 0:
                writer.writerow(
                    ["timestamp",
                        "tokens_prompt", 
                        "tokens_completion",
                        "tokens_total",
                        "response_time",
                        "estimated_cost_usd"]
                )
            writer.writerow(metricas_llamada)
        
        log(f'Métricas escritas: {metricas_llamada}')

    except Exception as err:
        log(f'Error intentando escribir métricas: {err}', 'error')
        
    return
