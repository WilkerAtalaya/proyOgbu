export interface Reconocimiento {
  descripcion: string
  fecha: string
  id: number
  id_alumno: number
  id_usuario: number
}

export interface Cumpleanos {
  fecha_cumpleaños: string
  nombre: string
  id: number
}

export interface Alumno {
  id: number
  nombre: string
  correo: string
}
