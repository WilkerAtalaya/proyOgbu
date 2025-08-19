export interface Salida {
  estado: string
  fecha_regreso: string,
  fecha_salida: string,
  id: number,
  id_usuario: number,
  motivo: string,
  archivo_justificacion?: string,
  Fecha_solicitada: string,
  nombre_usuario?: string
}

export interface AreaComun {
  estado: string
  fecha: string,
  horario: string,
  id: number,
  id_usuario: number,
  lugar: string,
  motivo?: string,
  Fecha_solicitada: string,
  nombre_usuario?: string
}
