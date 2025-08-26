import { environment } from '@/environment/environment'
import type { Reconocimiento, Cumpleanos, Alumno } from '@/models/Reconocimiento'
import axios from 'axios'

export class ReconocimientosService {
  private urlObtenerReconocimientos: string
  private urlObtenerCumpleanos: string
  private urlCrearReconocimiento: string
  private urlBuscarAlumnos: string
  private urlEliminarReconocimiento: string

  constructor() {
    this.urlObtenerReconocimientos = `${environment.baseUrlApi}${environment.endPoint.reconocimientos.obtenerReconocimientos}`
    this.urlObtenerCumpleanos = `${environment.baseUrlApi}${environment.endPoint.reconocimientos.obtenerCumpleanos}`
    this.urlCrearReconocimiento = `${environment.baseUrlApi}${environment.endPoint.reconocimientos.crearReconocimiento}`
    this.urlBuscarAlumnos = `${environment.baseUrlApi}${environment.endPoint.reconocimientos.buscarAlumnos}`
    this.urlEliminarReconocimiento = `${environment.baseUrlApi}${environment.endPoint.reconocimientos.eliminarReconocimiento}`
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

  async buscarAlumnos(termino: string): Promise<Alumno[]> {
    return axios
      .get<Alumno[]>(`${this.urlBuscarAlumnos}?q=${encodeURIComponent(termino)}`)
      .then((res: { data: Alumno[] }) => res.data)
  }

  async eliminarReconocimiento(id: number): Promise<void> {
    return axios
      .delete(`${this.urlEliminarReconocimiento}/${id}`)
      .then(() => {})
  }
}

export default new ReconocimientosService()
