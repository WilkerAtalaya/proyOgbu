export interface CitaAlumno {
  area: string
  estado: string
  fecha: string
  horario: string
  id: number
  motivo: string
  descripcion: string
}

export interface CitaAdmin {
  area: string
  estado: string
  fecha: string
  horario: string
  id: number
  id_alumno: number
  motivo: string
  nombre: string
}