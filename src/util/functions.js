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

// Return: dd/mm/yyyy hh:mm para fechas ISO con timestamp
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