export interface Archivo {
  bucket: string
  mime: string | null
  original_name: string
  size: number | null
  stored_name: string
  url: string
}

export interface Queja {
  id?: number
  asunto: string
  codigo: string,
  descripcion: string,
  estado: string,
  fecha: string,
  motivo: string
  archivo: Archivo | null
  prueba?: string
}
