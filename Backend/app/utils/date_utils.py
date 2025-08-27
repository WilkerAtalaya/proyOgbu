from datetime import datetime, timezone

def get_current_utc_time():
    """
    Obtiene la fecha y hora actual en UTC para almacenar en BD
    
    Returns:
        datetime: fecha actual en UTC
    """
    return datetime.now(timezone.utc)

def format_datetime_for_frontend(dt):
    """
    Convierte datetime a timestamp ISO en UTC con indicador 'Z' para que el frontend sepa que es UTC
    
    Args:
        dt: datetime object (UTC from database)
    
    Returns:
        str: timestamp en formato ISO UTC (ej: "2025-08-27T15:30:00Z")
    """
    if not dt:
        return ''
    
    # Si el datetime no tiene timezone info, asumimos que es UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Convertir a UTC y enviar con 'Z' para indicar que es UTC
    utc_time = dt.astimezone(timezone.utc)
    return utc_time.strftime('%Y-%m-%dT%H:%M:%SZ')

def parse_date_from_frontend(date_str):
    """
    Convierte una fecha del frontend a datetime UTC para almacenar en BD
    
    Args:
        date_str: str en formato ISO o formatos comunes
    
    Returns:
        datetime: objeto datetime en UTC
    """
    if not date_str:
        return None
    
    try:
        # Intentar formato ISO primero
        if 'T' in date_str:
            # Formato ISO: 2025-08-27T15:30:00 o 2025-08-27T15:30:00Z
            clean_date = date_str.replace('Z', '').replace('+00:00', '')
            dt = datetime.fromisoformat(clean_date)
            return dt.replace(tzinfo=timezone.utc)
        
        # Formatos para filtros de admin
        formats = [
            '%Y-%m-%d',        # yyyy-mm-dd
            '%d/%m/%Y',        # dd/mm/yyyy
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
                
        return None
        
    except Exception as e:
        print(f"Error parsing date '{date_str}': {e}")
        return None
