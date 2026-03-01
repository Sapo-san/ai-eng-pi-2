'''
División del documento de manera semántica

Esta estrategia toma en cuenta que faq_document es un archivo MARKDOWN donde 
cada pregunta está redactada con un header, por lo que dividimos el archivo
por headers para que cada chunk sea una única pregunta

Esta estrategia solo funcionará para documentos que tengan la misma estructura,
es decir, un header, una pregunta-respuesta.
'''

def semantic_chunking(document):
    '''
        Recibe un documento y retorna la lista de chunks con metadata
    '''
    chunks = [
        # Lista de chunks a retornar
    ]

    # Subdivide el documento segun headers
    subdivision = [x.strip() for x in document.split('#') if x != ""]

    id = 0

    # generar chunk y su metadata
    for fragment in subdivision:
        # Posición del fragmento en el documento:
        pos_start = document.find(fragment)
        pos_end = pos_start + len(fragment)

        chunk = {
            'id': str(id),
            'text': fragment,
            'metadata' : {
                'char_start': pos_start,
                'chat_end' : pos_end
            }
        }

        chunks.append(chunk)
        id += 1

    return chunks

if __name__ == '__main__':
    # Documento pequeño de prueba
    test_document = '# Titulo\n## pregunta 1\nrespuesta1\n## pregunta 2\nrespuesta 2\n'
    print(semantic_chunking(test_document))
