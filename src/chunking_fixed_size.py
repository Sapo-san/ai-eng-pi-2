'''
División del documento con fixed size chunking

Esta es una de las estrategias pasadas en clase y 
'''

def fixed_size_chunking(document, chunk_size, overlap):
    '''
        Recibe un documento y retorna la lista de chunks con metadata

        chunk_size y overlap son dos integers que indican numero de palabras

        Este código esta basado en el visto en la lecture, pero modificado para
        incorporar metadata en los chunks.

    '''
    chunks = [
        # Lista de chunks a retornar
    ]
    palabras = document.split(' ') # Separar por espacios

    # Id del chunk
    id = 0

    # Palabra de inicio
    start = 0
    
    # Inicio del recorrido
    while start < len(palabras):

        # Largo en palabras del chunk
        end = start + chunk_size


        # Fragmento de texto a partir del chunk
        fragment = ' '.join(palabras[start:end])

        # Metadata
        char_start = document.find(fragment)
        char_end = char_start + len(fragment)

        # Chunk con metadata
        chunk = {
            'id': str(id),
            'text': fragment,
            'metadata' : {
                'char_start': char_start,
                'chat_end' : char_end
            }
        }

        # Añadir a la lista
        chunks.append(
            chunk
        )

        # Siguiente iteración
        id += 1
        start += chunk_size - overlap

    return chunks

if __name__ == '__main__':
    # Ejecución de prueba (Ejecutar este modulo desde carpeta raiz del proyecto)
    test_document = open('./data/faq_document.md', mode='r').read()
    
    chunks = fixed_size_chunking(test_document, 60, 5)

    for c in chunks:
        print('#'*30)
        print(c)

    print(f'Cantidad de chunks: {len(chunks)}')