export interface ArchivoAnuncio {
  bucket: string
  mime: string | null
  original_name: string
  size: number | null
  stored_name: string
  url: string
}

export interface Anuncio {
  id: number
  fecha_publicacion: string
  descripcion: string
  titulo: string
  archivo: ArchivoAnuncio | null
}