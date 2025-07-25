import { environment } from '@/environment/environment'
import type { Reconocimiento, Cumpleanos } from '@/models/Reconocimiento'
import axios from 'axios'

export class ReconocimientosService {
  private urlObtenerReconocimientos: string
  private urlObtenerCumpleanos: string
  private urlCrearReconocimiento: string

  constructor() {
    this.urlObtenerReconocimientos = `${environment.baseUrlApi}${environment.endPoint.reconocimientos.obtenerReconocimientos}`
    this.urlObtenerCumpleanos = `${environment.baseUrlApi}${environment.endPoint.reconocimientos.obtenerCumpleanos}`
    this.urlCrearReconocimiento = `${environment.baseUrlApi}${environment.endPoint.reconocimientos.crearReconocimiento}`
  }

  async obtenerReconocimientos(): Promise<Reconocimiento[]> {
    return axios
      .get<Reconocimiento[]>(this.urlObtenerReconocimientos)
      .then((res: { data: Reconocimiento[] }) => res.data)
  }

  async crearReconocimiento(body: Partial<Reconocimiento>): Promise<Reconocimiento> {
    return axios
      .post<Reconocimiento>(this.urlCrearReconocimiento, body)
      .then(res => res.data);
  }

  async obtenerCumpleanos(): Promise<Cumpleanos[]> {
    return axios
      .get<Cumpleanos[]>(this.urlObtenerCumpleanos)
      .then((res: { data: Cumpleanos[] }) => res.data)
  }
}

export default new ReconocimientosService()
