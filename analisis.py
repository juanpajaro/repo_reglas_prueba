import pandas as pd
import re


def cargar_diccionario(ruta_archivo='diccionario.csv'):
    """
    Carga el archivo diccionario.csv que contiene el diccionario de datos de REDCap.
    
    Parámetros:
    -----------
    ruta_archivo : str, opcional
        Ruta al archivo CSV del diccionario. Por defecto es 'diccionario.csv'
    
    Retorna:
    --------
    pandas.DataFrame
        DataFrame con el contenido del diccionario de datos
    """
    try:
        # Cargar el archivo CSV
        df = pd.read_csv(ruta_archivo)
        
        print(f"Diccionario cargado exitosamente!")
        print(f"Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
        print(f"\nColumnas disponibles: {list(df.columns)}")
        
        return df
        
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta_archivo}'")
        return None
    except Exception as e:
        print(f"Error al cargar el archivo: {str(e)}")
        return None


def extraer_columnas_diccionario(df_diccionario):
    """
    Extrae columnas específicas del diccionario de datos de REDCap.
    
    Parámetros:
    -----------
    df_diccionario : pandas.DataFrame
        DataFrame con el diccionario completo
    
    Retorna:
    --------
    pandas.DataFrame o None
        DataFrame con las columnas seleccionadas, o None si hay error
    """
    # Columnas requeridas
    columnas_requeridas = [
        "Variable / Field Name",
        "Field Type",
        "Field Label",
        "Choices, Calculations, OR Slider Labels"
    ]
    
    try:
        # Verificar que el DataFrame no sea None
        if df_diccionario is None:
            print("Error: El diccionario proporcionado es None")
            return None
        
        # Obtener las columnas disponibles en el DataFrame
        columnas_disponibles = list(df_diccionario.columns)
        
        # Verificar que todas las columnas requeridas existen
        columnas_faltantes = []
        for col in columnas_requeridas:
            if col not in columnas_disponibles:
                columnas_faltantes.append(col)
        
        if columnas_faltantes:
            print("Error: Las siguientes columnas no se encuentran en el diccionario:")
            for col in columnas_faltantes:
                print(f"  - {col}")
            print(f"\nColumnas disponibles en el diccionario:")
            for col in columnas_disponibles:
                print(f"  - {col}")
            return None
        
        # Extraer las columnas requeridas
        df_extraido = df_diccionario[columnas_requeridas].copy()
        
        print(f"Columnas extraídas exitosamente!")
        print(f"Dimensiones: {df_extraido.shape[0]} filas x {df_extraido.shape[1]} columnas")
        print(f"\nColumnas en el DataFrame resultante:")
        for col in df_extraido.columns:
            print(f"  - {col}")
        
        return df_extraido
        
    except Exception as e:
        print(f"Error al extraer las columnas: {str(e)}")
        return None


def guardar_dataframe(df, nombre_archivo='diccionario_extraido.csv', formato='csv'):
    """
    Guarda un DataFrame en un archivo.
    
    Parámetros:
    -----------
    df : pandas.DataFrame
        DataFrame a guardar
    nombre_archivo : str, opcional
        Nombre del archivo de salida. Por defecto es 'diccionario_extraido.csv'
    formato : str, opcional
        Formato del archivo ('csv', 'excel', 'json'). Por defecto es 'csv'
    
    Retorna:
    --------
    bool
        True si se guardó exitosamente, False en caso contrario
    """
    try:
        # Verificar que el DataFrame no sea None
        if df is None:
            print("Error: El DataFrame proporcionado es None")
            return False
        
        # Verificar que el DataFrame no esté vacío
        if df.empty:
            print("Advertencia: El DataFrame está vacío")
        
        # Guardar según el formato especificado
        if formato.lower() == 'csv':
            df.to_csv(nombre_archivo, index=False, encoding='utf-8-sig')
            print(f"DataFrame guardado exitosamente en '{nombre_archivo}'")
            print(f"Formato: CSV")
            
        elif formato.lower() == 'excel':
            if not nombre_archivo.endswith(('.xlsx', '.xls')):
                nombre_archivo = nombre_archivo.replace('.csv', '.xlsx')
            df.to_excel(nombre_archivo, index=False, engine='openpyxl')
            print(f"DataFrame guardado exitosamente en '{nombre_archivo}'")
            print(f"Formato: Excel")
            
        elif formato.lower() == 'json':
            if not nombre_archivo.endswith('.json'):
                nombre_archivo = nombre_archivo.replace('.csv', '.json')
            df.to_json(nombre_archivo, orient='records', force_ascii=False, indent=2)
            print(f"DataFrame guardado exitosamente en '{nombre_archivo}'")
            print(f"Formato: JSON")
            
        else:
            print(f"Error: Formato '{formato}' no reconocido. Use 'csv', 'excel' o 'json'")
            return False
        
        print(f"Registros guardados: {len(df)}")
        return True
        
    except Exception as e:
        print(f"Error al guardar el archivo: {str(e)}")
        return False


def buscar_por_patron(df, columna='Field Label', patron='nombre', case_sensitive=False):
    """
    Busca registros en un DataFrame usando expresiones regulares.
    
    Parámetros:
    -----------
    df : pandas.DataFrame
        DataFrame donde buscar
    columna : str, opcional
        Nombre de la columna donde buscar. Por defecto es 'Field Label'
    patron : str, opcional
        Patrón de búsqueda (expresión regular). Por defecto es 'nombre'
    case_sensitive : bool, opcional
        Si la búsqueda distingue mayúsculas/minúsculas. Por defecto es False
    
    Retorna:
    --------
    pandas.DataFrame
        DataFrame filtrado con los registros que coinciden con el patrón
    """
    try:
        # Verificar que el DataFrame no sea None
        if df is None:
            print("Error: El DataFrame proporcionado es None")
            return pd.DataFrame()
        
        # Verificar que el DataFrame no esté vacío
        if df.empty:
            print("Advertencia: El DataFrame está vacío")
            return pd.DataFrame()
        
        # Verificar que la columna existe
        if columna not in df.columns:
            print(f"Error: La columna '{columna}' no existe en el DataFrame")
            print(f"Columnas disponibles: {list(df.columns)}")
            return pd.DataFrame()
        
        # Crear patrón de expresión regular para "nombre" y variaciones
        # Incluye: nombre, nombres, name, names, apellido, apellidos, etc.
        patron_extendido = r'\b(nombre[s]?|name[s]?|apellido[s]?|surname[s]?|full\s*name|primer\s*nombre|segundo\s*nombre|nombre\s*completo|nombre\s*impreso)\b'
        
        # Si se proporciona un patrón personalizado, usarlo
        if patron != 'nombre':
            patron_extendido = patron
        
        # Configurar flags para case insensitive si es necesario
        flags = 0 if case_sensitive else re.IGNORECASE
        
        # Filtrar el DataFrame
        # Convertir la columna a string para evitar errores con NaN
        mascara = df[columna].astype(str).str.contains(patron_extendido, regex=True, flags=flags, na=False)
        df_filtrado = df[mascara].copy()
        
        # Mostrar resultados
        print(f"Búsqueda realizada en la columna: '{columna}'")
        print(f"Patrón utilizado: {patron_extendido}")
        print(f"Coincidencias encontradas: {len(df_filtrado)}")
        
        if len(df_filtrado) > 0:
            print(f"\nRegistros encontrados:")
            print(f"Índices: {list(df_filtrado.index)}")
        else:
            print("\nNo se encontraron coincidencias con el patrón especificado")
        
        return df_filtrado
        
    except Exception as e:
        print(f"Error al buscar el patrón: {str(e)}")
        return pd.DataFrame()


def buscar_correo_electronico(df, columna='Field Label', mostrar_resultados=False):
    """
    Busca campos relacionados con correo electrónico usando expresiones regulares.
    
    Parámetros:
    -----------
    df : pandas.DataFrame
        DataFrame donde buscar
    columna : str, opcional
        Nombre de la columna donde buscar. Por defecto es 'Field Label'
    mostrar_resultados : bool, opcional
        Si es True, imprime los resultados de la búsqueda. Por defecto es False
    
    Retorna:
    --------
    pandas.DataFrame
        DataFrame filtrado con los registros relacionados con correo electrónico
    """
    try:
        # Verificar que el DataFrame no sea None
        if df is None:
            if mostrar_resultados:
                print("Error: El DataFrame proporcionado es None")
            return pd.DataFrame()
        
        # Verificar que el DataFrame no esté vacío
        if df.empty:
            if mostrar_resultados:
                print("Advertencia: El DataFrame está vacío")
            return pd.DataFrame()
        
        # Verificar que la columna existe
        if columna not in df.columns:
            if mostrar_resultados:
                print(f"Error: La columna '{columna}' no existe en el DataFrame")
                print(f"Columnas disponibles: {list(df.columns)}")
            return pd.DataFrame()
        
        # Patrón de expresión regular para "correo electrónico" y variaciones
        # Incluye: correo, correo electrónico, email, e-mail, mail, electronic mail, etc.
        patron_correo = r'\b(correo[s]?(\s*(electr[oó]nico|electr[oó]nica))?|e-?mail[s]?|electronic\s*mail[s]?|mail[s]?|direcci[oó]n\s*de\s*correo|contact\s*email)\b'
        
        # Filtrar el DataFrame (case insensitive)
        mascara = df[columna].astype(str).str.contains(
            patron_correo, 
            regex=True, 
            flags=re.IGNORECASE, 
            na=False
        )
        df_filtrado = df[mascara].copy()
        
        # Mostrar resultados solo si se solicita
        if mostrar_resultados:
            print(f"Búsqueda de correo electrónico en la columna: '{columna}'")
            print(f"Patrón utilizado: {patron_correo}")
            print(f"Coincidencias encontradas: {len(df_filtrado)}")
            
            if len(df_filtrado) > 0:
                print(f"\nRegistros encontrados:")
                print(f"Índices: {list(df_filtrado.index)}")
                print("\n--- Campos de correo electrónico encontrados ---")
                for idx, row in df_filtrado.iterrows():
                    print(f"\n{idx + 1}. Variable: {row['Variable / Field Name']}")
                    print(f"   Tipo: {row['Field Type']}")
                    print(f"   Etiqueta: {row['Field Label']}")
            else:
                print("\nNo se encontraron campos relacionados con correo electrónico")
        
        return df_filtrado
        
    except Exception as e:
        if mostrar_resultados:
            print(f"Error al buscar correo electrónico: {str(e)}")
        return pd.DataFrame()


def extraer_contexto_patron(df, indice, columna='Field Label', patron='nombre', num_palabras=4):
    """
    Extrae el contexto alrededor de una coincidencia del patrón en un registro específico.
    
    Parámetros:
    -----------
    df : pandas.DataFrame
        DataFrame con los resultados de búsqueda
    indice : int
        Índice del registro a revisar
    columna : str, opcional
        Nombre de la columna donde buscar el patrón. Por defecto es 'Field Label'
    patron : str, opcional
        Patrón de búsqueda (expresión regular). Por defecto es 'nombre'
    num_palabras : int, opcional
        Número de palabras a extraer antes y después de la coincidencia. Por defecto es 4
    
    Retorna:
    --------
    dict
        Diccionario con información sobre las coincidencias encontradas:
        - 'indice': índice del registro
        - 'texto_completo': texto completo donde se buscó
        - 'coincidencias': lista de contextos extraídos
        - 'patron_usado': patrón utilizado en la búsqueda
    """
    try:
        # Verificar que el DataFrame no sea None
        if df is None:
            print("Error: El DataFrame proporcionado es None")
            return None
        
        # Verificar que el DataFrame no esté vacío
        if df.empty:
            print("Error: El DataFrame está vacío")
            return None
        
        # Verificar que el índice existe
        if indice not in df.index:
            print(f"Error: El índice {indice} no existe en el DataFrame")
            print(f"Índices disponibles: {list(df.index)}")
            return None
        
        # Verificar que la columna existe
        if columna not in df.columns:
            print(f"Error: La columna '{columna}' no existe en el DataFrame")
            print(f"Columnas disponibles: {list(df.columns)}")
            return None
        
        # Obtener el texto del registro
        texto = str(df.loc[indice, columna])
        
        if pd.isna(df.loc[indice, columna]) or texto == 'nan':
            print(f"Advertencia: El campo en el índice {indice} está vacío")
            return {
                'indice': indice,
                'texto_completo': '',
                'coincidencias': [],
                'patron_usado': patron
            }
        
        # Crear patrón extendido si es "nombre"
        if patron == 'nombre':
            patron_busqueda = r'\b(nombre[s]?|name[s]?|apellido[s]?|surname[s]?|full\s*name|primer\s*nombre|segundo\s*nombre|nombre\s*completo|nombre\s*impreso)\b'
        else:
            patron_busqueda = patron
        
        # Buscar todas las coincidencias con el patrón
        coincidencias_encontradas = []
        
        # Encontrar todas las coincidencias
        for match in re.finditer(patron_busqueda, texto, re.IGNORECASE):
            palabra_encontrada = match.group()
            inicio = match.start()
            fin = match.end()
            
            # Extraer palabras antes y después
            # Dividir el texto en palabras
            texto_antes = texto[:inicio]
            texto_despues = texto[fin:]
            
            # Obtener palabras antes
            palabras_antes = re.findall(r'\S+', texto_antes)
            palabras_antes = palabras_antes[-num_palabras:] if len(palabras_antes) >= num_palabras else palabras_antes
            
            # Obtener palabras después
            palabras_despues = re.findall(r'\S+', texto_despues)
            palabras_despues = palabras_despues[:num_palabras] if len(palabras_despues) >= num_palabras else palabras_despues
            
            # Construir el contexto
            contexto_antes = ' '.join(palabras_antes)
            contexto_despues = ' '.join(palabras_despues)
            
            contexto_completo = f"{contexto_antes} [{palabra_encontrada}] {contexto_despues}".strip()
            
            coincidencias_encontradas.append({
                'palabra': palabra_encontrada,
                'posicion': (inicio, fin),
                'contexto': contexto_completo,
                'antes': contexto_antes,
                'despues': contexto_despues
            })
        
        resultado = {
            'indice': indice,
            'texto_completo': texto,
            'coincidencias': coincidencias_encontradas,
            'patron_usado': patron_busqueda,
            'num_coincidencias': len(coincidencias_encontradas)
        }
        
        return resultado
        
    except Exception as e:
        print(f"Error al extraer contexto: {str(e)}")
        return None


if __name__ == "__main__":
    # Ejemplo de uso
    diccionario = cargar_diccionario()
    
    if diccionario is not None:
        print("\nPrimeras 5 filas del diccionario:")
        print(diccionario.head())
        
        print("\n" + "="*60)
        print("\nExtrayendo columnas específicas...")
        print("="*60)
        
        df_extraido = extraer_columnas_diccionario(diccionario)
        
        if df_extraido is not None:
            print("\nPrimeras 10 filas del DataFrame extraído:")
            print(df_extraido.head(10))
            
            print("\n" + "="*60)
            print("\nGuardando DataFrame extraído...")
            print("="*60)
            
            # Guardar el DataFrame en formato CSV
            guardar_dataframe(df_extraido, 'diccionario_extraido.csv', formato='csv')
            
            print("\n" + "="*60)
            print("\nBuscando campos relacionados con 'nombre'...")
            print("="*60)
            
            # Buscar campos que contengan "nombre" o similares
            df_nombres = buscar_por_patron(df_extraido, columna='Field Label', patron='nombre')
            
            if not df_nombres.empty:
                print("\n--- Campos encontrados ---")
                print("numero de campos encontrados:", len(df_nombres))
                #print(df_nombres)
            
            print("\n" + "="*60)
            print("\nBuscando campos relacionados con 'correo electrónico'...")
            print("="*60)
            
            # Buscar campos que contengan "correo" o "email" (con resultados visibles)
            df_correos = buscar_correo_electronico(df_extraido, columna='Field Label', mostrar_resultados=False)
            
            if not df_correos.empty:
                print(f"\nTotal de campos de correo encontrados: {len(df_correos)}")
            
            print("\n" + "="*60)
            print("\nExtrayendo contexto de coincidencias...")
            print("="*60)
            
            # Ejemplo: extraer contexto del primer registro encontrado en df_nombres
            if not df_nombres.empty:
                primer_indice = df_nombres.index[0]
                print(f"\nExtrayendo contexto del registro en índice {primer_indice}:")
                
                contexto = extraer_contexto_patron(df_nombres, primer_indice, columna='Field Label', patron='nombre', num_palabras=4)
                
                if contexto:
                    print(f"\nTexto completo: {contexto['texto_completo'][:200]}...")
                    print(f"Número de coincidencias: {contexto['num_coincidencias']}")
                    
                    for i, coincidencia in enumerate(contexto['coincidencias'], 1):
                        print(f"\n--- Coincidencia {i} ---")
                        print(f"Palabra encontrada: {coincidencia['palabra']}")
                        print(f"Contexto: {coincidencia['contexto']}")

