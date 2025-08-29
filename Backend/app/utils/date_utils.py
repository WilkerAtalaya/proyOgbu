from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo

LIMA_TZ = ZoneInfo("America/Lima")

def get_current_utc_time():
    """
    Obtiene la fecha y hora actual en UTC para almacenar en BD
    
    Returns:
        datetime: fecha actual en UTC
    """
    return datetime.now(timezone.utc)

def format_datetime_for_frontend(dt, tz: ZoneInfo = LIMA_TZ, iso: bool = True, assume_naive: str = "utc"):
    """
    assume_naive: "utc" (por defecto) o "lima"
      - "utc": si dt es naive, se interpreta como UTC y luego se convierte a tz
      - "lima": si dt es naive, se interpreta como hora de Lima directamente
    """
    if dt is None:
        return None

    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except Exception:
            return dt

    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime.combine(dt, datetime.min.time())

    if dt.tzinfo is None:
        if assume_naive.lower() == "lima":
            dt = dt.replace(tzinfo=tz)  # << interpretar naive como Lima
        else:
            dt = dt.replace(tzinfo=timezone.utc)

    local = dt.astimezone(tz)
    return local.isoformat(timespec="seconds") if iso else local.strftime("%Y-%m-%d %H:%M:%S")

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
