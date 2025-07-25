import { environment } from '@/environment/environment'
import type { Actividad } from '@/models/Actividad'
import axios from 'axios'

export class ActividadesService {
  private urlObtenerPorUsuario: string
  private urlObtenerAprobadas: string
  private urlObtenerTodas: string
  private urlObtenerPorId: string
  private urlCrearActividad: string
  private urlCrearSolicitud: string
  private urlActualizar: string
  private urlEliminar: string

  constructor() {
    this.urlObtenerPorUsuario = `${environment.baseUrlApi}${environment.endPoint.actividades.obtenerPorUsuario}`
    this.urlObtenerTodas = `${environment.baseUrlApi}${environment.endPoint.actividades.obtenerTodas}`
    this.urlObtenerAprobadas = `${environment.baseUrlApi}${environment.endPoint.actividades.obtenerAprobadas}`
    this.urlObtenerPorId = `${environment.baseUrlApi}${environment.endPoint.actividades.obtenerPorId}`
    this.urlCrearActividad = `${environment.baseUrlApi}${environment.endPoint.actividades.crearActividad}`
    this.urlCrearSolicitud = `${environment.baseUrlApi}${environment.endPoint.actividades.crearSolicitud}`
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

  async crearSolicitud(body: Partial<Actividad>): Promise<Actividad> {
    return axios
      .post<Actividad>(this.urlCrearSolicitud, body, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      .then((res) => res.data)
  }

  async crearActividad(body: Partial<Actividad>): Promise<Actividad> {
    return axios
      .post<Actividad>(this.urlCrearActividad, body, {
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
