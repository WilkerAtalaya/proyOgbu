// Return: 12 de junio de 2025
export function dateFormatV1(value) {
  const date = new Date(value)
  const options = { day: '2-digit', month: 'long', year: 'numeric' }
  return date.toLocaleDateString('es-ES', options)
}

// Return: dd/mm/yyyy (Actual)
export function currentDate() {
  const fecha = new Date()
  const dia = fecha.getDate().toString().padStart(2, '0')
  const mes = (fecha.getMonth() + 1).toString().padStart(2, '0')
  const anio = fecha.getFullYear()
  return `${dia}/${mes}/${anio}`
}

// Return: yyyy-mm-dd
export function dateFormatDB(fecha) {
  if (!fecha) return ''
  const [dia, mes, anio] = fecha.split('/')
  return `${anio}-${mes.padStart(2, '0')}-${dia.padStart(2, '0')}`
}

// Return: dd/mm/yyyy
export function dateFormatV2(fecha) {
  if (!fecha) return ''
  const partes = fecha.split('-')
  return `${partes[2]}/${partes[1]}/${partes[0]}`
}

export function dateFormatV3(value) {
  const fecha = new Date(value);
  const horas = fecha.getHours();
  const minutos = fecha.getMinutes();
  const segundos = fecha.getSeconds();
  return `${horas}:${minutos}.${segundos}`;
}

// Return: dd/mm/yyyy hh:mm para fechas ISO UTC del backend (convierte a timezone local)
export function dateFormatISO(value) {
  if (!value) return ''
  
  const fecha = new Date(value)
  const dia = fecha.getDate().toString().padStart(2, '0')
  const mes = (fecha.getMonth() + 1).toString().padStart(2, '0')
  const anio = fecha.getFullYear()
  const horas = fecha.getHours().toString().padStart(2, '0')
  const minutos = fecha.getMinutes().toString().padStart(2, '0')
  return `${dia}/${mes}/${anio} ${horas}:${minutos}`
}

// Extrae solo la hora de un timestamp UTC (convierte a timezone local)
export function extractTime(fechaISO) {
  if (!fechaISO) return '00:00'
  
  const fecha = new Date(fechaISO)
  const horas = fecha.getHours().toString().padStart(2, '0')
  const minutos = fecha.getMinutes().toString().padStart(2, '0')
  return `${horas}:${minutos}`
}

// Extrae solo la fecha de un timestamp UTC (convierte a timezone local)
export function extractDate(fechaISO) {
  if (!fechaISO) return ''
  
  const fecha = new Date(fechaISO)
  const dia = fecha.getDate().toString().padStart(2, '0')
  const mes = (fecha.getMonth() + 1).toString().padStart(2, '0')
  const anio = fecha.getFullYear()
  return `${dia}/${mes}/${anio}`
}

// Convierte timestamp del backend a formato display en timezone local
export function formatBackendDate(fechaBackend, includeTime = true) {
  if (!fechaBackend) return ''
  
  return includeTime ? dateFormatISO(fechaBackend) : extractDate(fechaBackend)
}

// Convierte fecha y hora local del usuario a UTC para enviar al backend
export function convertLocalDateTimeToUTC(fechaLocal, horaLocal = '00:00') {
  if (!fechaLocal) return { fecha_utc: '', hora_utc: '00:00', iso_utc: '', timestamp_utc: null }
  
  let fechaString = ''
  
  // Manejar diferentes formatos de fecha
  if (fechaLocal instanceof Date) {
    const year = fechaLocal.getFullYear()
    const month = String(fechaLocal.getMonth() + 1).padStart(2, '0')
    const day = String(fechaLocal.getDate()).padStart(2, '0')
    fechaString = `${year}-${month}-${day}`
  } else if (typeof fechaLocal === 'string') {
    if (fechaLocal.includes('/')) {
      // Formato dd/mm/yyyy
      const [dia, mes, anio] = fechaLocal.split('/')
      if (dia && mes && anio) {
        fechaString = `${anio}-${mes.padStart(2, '0')}-${dia.padStart(2, '0')}`
      }
    } else {
      // Asumir que ya está en formato YYYY-MM-DD
      fechaString = fechaLocal
    }
  }
  
  if (!fechaString) return { fecha_utc: '', hora_utc: '00:00', iso_utc: '', timestamp_utc: null }
  
  let horaString = '00:00'
  if (horaLocal) {
    if (horaLocal instanceof Date) {
      horaString = horaLocal.toTimeString().slice(0, 5)
    } else if (typeof horaLocal === 'object' && horaLocal.hours !== undefined) {
      const hours = String(horaLocal.hours).padStart(2, '0')
      const minutes = String(horaLocal.minutes || 0).padStart(2, '0')
      horaString = `${hours}:${minutes}`
    } else if (typeof horaLocal === 'string' && horaLocal.trim() !== '') {
      horaString = horaLocal
    }
  }
  
  const [year, month, day] = fechaString.split('-').map(Number)
  const [hours, minutes] = horaString.split(':').map(Number)
  
  const fechaLocalCompleta = new Date(year, month - 1, day, hours, minutes, 0, 0)
  
  const timestampUTC = fechaLocalCompleta.getTime()
  
  const fechaUTC = new Date(timestampUTC)
  
  const fechaUTCString = fechaUTC.toISOString().split('T')[0] // YYYY-MM-DD
  const horaUTCString = fechaUTC.toISOString().split('T')[1].slice(0, 5) // HH:MM
  const isoUTCString = fechaUTC.toISOString() // Formato ISO completo
  
  return {
    fecha_utc: fechaUTCString,
    hora_utc: horaUTCString,
    iso_utc: isoUTCString,
    timestamp_utc: timestampUTC
  }
}