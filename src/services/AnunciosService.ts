import { environment } from '@/environment/environment'
import axios from 'axios'
import type { Anuncio } from '@/models/Anuncio'

export class AnunciosService {
  private urlListar: string
  private urlCrear: string
  private urlActualizar: string
  private urlEliminar: string

  constructor() {
    this.urlListar = `${environment.baseUrlApi}${environment.endPoint.anuncios.listar}`
    this.urlCrear = `${environment.baseUrlApi}${environment.endPoint.anuncios.crear}`
    this.urlActualizar = `${environment.baseUrlApi}/anuncios`
    this.urlEliminar = `${environment.baseUrlApi}/anuncios`
  }

  async listarAnuncios(): Promise<Anuncio[]> {
    return axios
      .get<Anuncio[]>(this.urlListar)
      .then((res: { data: Anuncio[] }) => res.data)
  }

  async crearAnuncio(anuncio: FormData): Promise<Anuncio> {
    return axios
      .post<Anuncio>(this.urlCrear, anuncio, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      .then((res: { data: Anuncio }) => res.data)
  }

  async actualizarAnuncio(id: number, anuncio: FormData): Promise<Anuncio> {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    return axios
      .put<Anuncio>(`${this.urlActualizar}/${id}`, anuncio, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-User-Id': user.id?.toString()
        }
      })
      .then((res: { data: Anuncio }) => res.data)
  }

  async actualizarAnuncioParcial(id: number, anuncio: FormData): Promise<Anuncio> {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    return axios
      .patch<Anuncio>(`${this.urlActualizar}/${id}`, anuncio, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'X-User-Id': user.id?.toString()
        }
      })
      .then((res: { data: Anuncio }) => res.data)
  }

  async eliminarAnuncio(id: number): Promise<void> {
    const user = JSON.parse(localStorage.getItem('user') || '{}')
    return axios
      .delete(`${this.urlEliminar}/${id}`, {
        headers: {
          'X-User-Id': user.id?.toString()
        }
      })
      .then(() => {})
  }
}

export default new AnunciosService()