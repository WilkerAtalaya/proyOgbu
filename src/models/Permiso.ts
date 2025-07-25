export interface Salida {
  estado: string
  fecha_regreso: string,
  fecha_salida: string,
  id: number,
  id_usuario: number,
  motivo: string
}

export interface AreaComun {
  estado: string
  fecha: string,
  horario: string,
  id: number,
  id_usuario: number,
  lugar: string
}
