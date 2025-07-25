import { environment } from '@/environment/environment'
import type { Actividad } from '@/models/Actividad'
import axios from 'axios'

export class ActividadesService {
  private urlObtenerPorUsuario: string
  private urlObtenerAprobadas: string
  private urlObtenerTodas: string
  private urlObtenerPorId: string
  private urlCrear: string
  private urlActualizar: string
  private urlEliminar: string

  constructor() {
    this.urlObtenerPorUsuario = `${environment.baseUrlApi}${environment.endPoint.actividades.obtenerPorUsuario}`
    this.urlObtenerTodas = `${environment.baseUrlApi}${environment.endPoint.actividades.obtenerTodas}`
    this.urlObtenerAprobadas = `${environment.baseUrlApi}${environment.endPoint.actividades.obtenerAprobadas}`
    this.urlObtenerPorId = `${environment.baseUrlApi}${environment.endPoint.actividades.obtenerPorId}`
    this.urlCrear = `${environment.baseUrlApi}${environment.endPoint.actividades.crear}`
    this.urlActualizar = `${environment.baseUrlApi}${environment.endPoint.actividades.actualizar}`
    this.urlEliminar = `${environment.baseUrlApi}${environment.endPoint.actividades.eliminar}`
  }

  async obtenerTodas(): Promise<Actividad[]> {
    return axios
      .get<Actividad[]>(this.urlObtenerTodas)
      .then((res: { data: Actividad[] }) => res.data)
  }

  async obtenerActividadesPorUsuario(usuarioId: number): Promise<Actividad[]> {
    return axios
      .get<Actividad[]>(`${this.urlObtenerPorUsuario}/${usuarioId}`)
      .then((res: { data: Actividad[] }) => res.data)
  }

  async obtenerActividadesAprobadas(): Promise<Actividad[]> {
    return axios
      .get<Actividad[]>(this.urlObtenerAprobadas)
      .then((res: { data: Actividad[] }) => res.data)
  }

  //   obtenerActividadPorId(id: number): Promise<Queja> {
  //     return axios
  //       .get<Queja>(`${this.urlObtenerPorId}/${id}`)
  //       .then(res => res.data);
  //   }

  async crearActividad(body: Partial<Actividad>): Promise<Actividad> {
    return axios
      .post<Actividad>(this.urlCrear, body, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      .then((res) => res.data)
  }

  //   actualizarActividad(id: number, body: Partial<Queja>): Promise<Queja> {
  //     return axios
  //       .put<Queja>(`${this.urlActualizar}/${id}`, body)
  //       .then(res => res.data);
  //   }

  //   eliminarActividad(id: number): Promise<void> {
  //     return axios
  //       .delete(`${this.urlEliminar}/${id}`)
  //       .then(() => undefined);
  //   }
}

export default new ActividadesService()
