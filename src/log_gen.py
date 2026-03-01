'''
Logging del PI
'''
import logging
from datetime import datetime
import os

# Crear nombre dinámico del archivo: log-YYYY-MM-DD.txt
fecha = datetime.now().strftime("%Y-%m-%d")
nombre_archivo = f"log-{fecha}.txt"

LOG_FOLDER = str(os.getenv('LOG_FOLDER'))
LOG_CONFIG = str(os.getenv('LOG_CONFIG')).upper()
LOG_LEVEL = str(os.getenv('LOG_LEVEL')).upper()

if LOG_FOLDER and LOG_CONFIG and LOG_LEVEL:

    if LOG_CONFIG not in ('PRINT', 'FILE', 'BOTH', 'NONE'):
        raise Exception('LOG_CONFIG no tiene valor correcto.')
    
    if LOG_LEVEL not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
        raise Exception('LOG_LEVEL no tiene valor correcto.')
    
    logging_levels =  {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL,
    }

    # Guardarlo en carpeta logs
    os.makedirs(LOG_FOLDER, exist_ok=True)
    ruta_log = os.path.join(LOG_FOLDER, nombre_archivo)

    # Configuración básica
    logging.basicConfig(
        filename=ruta_log,
        level=logging_levels[LOG_LEVEL],
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging_functions =  {
        'debug': logging.debug,
        'info': logging.info,
        'warning': logging.warning,
        'error': logging.error,
        'critical': logging.critical,
    }

    def log(logtxt: str, level: str = 'info'):
        '''
        Función para logging del proyecto

        Recibe logtxt como texto a loggear, opcionalmente level como el nivel de logging
        '''
        if LOG_CONFIG == 'NONE':
            return

        fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if LOG_CONFIG in ('PRINT', 'BOTH'):
            print(f'[{fecha_str} {level.upper()}] {logtxt}')
        if LOG_CONFIG in ('FILE', 'BOTH'):
            logging_functions[level](logtxt)
else:
    raise Exception('no estan definidas las variables de entorno LOG_LEVEL, LOG_FOLDER and LOG_CONFIG')