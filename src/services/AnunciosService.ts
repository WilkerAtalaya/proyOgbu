import { environment } from '@/environment/environment'
import axios from 'axios'
import type { Anuncio } from '@/models/Anuncio'

export class AnunciosService {
  private urlListar: string
  private urlCrear: string

  constructor() {
    this.urlListar = `${environment.baseUrlApi}${environment.endPoint.anuncios.listar}`
    this.urlCrear = `${environment.baseUrlApi}${environment.endPoint.anuncios.crear}`
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
}

export default new AnunciosService()