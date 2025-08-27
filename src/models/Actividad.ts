export interface ArchivoActividad {
  bucket: string
  mime: string | null
  original_name: string
  size: number | null
  stored_name: string
  url: string
}

export interface Actividad {
  id?: number
  titulo: string
  descripcion: string
  tipo: string
  stock: number
  cupos_restantes?: number
  fecha_actividad: string
  archivo_obj: ArchivoActividad | null
  id_usuario?: number
  estado?: string
  fecha_solicitud?: string
  motivo_cancelacion?: string | null
  nombre_creador?: string
}

export interface ActividadInscrita {
  id_actividad: number
  id_inscripcion: number
  titulo: string
  tipo: string
  descripcion: string
  fecha_actividad: string
  fecha_registro: string
  estado_actividad: string
  archivo_obj: ArchivoActividad | null
}
