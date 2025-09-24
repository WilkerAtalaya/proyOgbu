import { environment } from '@/environment/environment'
import type { Cita } from '@/models/Cita'
import axios from 'axios'

export class CitasService {
  private urlObtenerSolicitadasPorUsuario: string
  private urlObtenerPendientes: string
  private urlObtenerCulminadas: string
  private urlConsultar: string
  private urlCrear: string
  private urlGetBusySchedules: string
  private urlGetAreas: string
  private urlGetReasons: string
  private urlUpdateStatus: string
  private urlReschedule: string

  constructor() {
    this.urlObtenerSolicitadasPorUsuario = `${environment.baseUrlApi}${environment.endPoint.citas.obtenerSolicitadasPorUsuario}`
    this.urlObtenerPendientes = `${environment.baseUrlApi}${environment.endPoint.citas.obtenerPendientes}`
    this.urlObtenerCulminadas = `${environment.baseUrlApi}${environment.endPoint.citas.obtenerCulminadas}`
    this.urlConsultar = `${environment.baseUrlApi}${environment.endPoint.citas.consultar}`
    this.urlCrear = `${environment.baseUrlApi}${environment.endPoint.citas.crear}`
    this.urlGetBusySchedules = `${environment.baseUrlApi}${environment.endPoint.citas.getBusySchedules}`
    this.urlGetAreas = `${environment.baseUrlApi}${environment.endPoint.area.getAreas}`
    this.urlGetReasons = `${environment.baseUrlApi}${environment.endPoint.reasons.getReasons}`
    this.urlUpdateStatus = `${environment.baseUrlApi}${environment.endPoint.citas.updateStatus}`
    this.urlReschedule = `${environment.baseUrlApi}${environment.endPoint.citas.reschedule}`
  }

  async obtenerCitasSolicitadasPorUsuario(usuarioId: number): Promise<Cita[]> {
    return axios
      .get<Cita[]>(`${this.urlObtenerSolicitadasPorUsuario}/${usuarioId}`)
      .then((res: { data: Cita[] }) => res.data)
  }

  async obtenerCitasPendientes(params: Record<string, any>): Promise<Cita[]> {
    const query = new URLSearchParams(params).toString()
    return axios
      .get<Cita[]>(`${this.urlObtenerPendientes}?${query}`)
      .then((res: { data: Cita[] }) => res.data)
  }

  async obtenerCitasCulminadas(params: Record<string, any>): Promise<Cita[]> {
    const query = new URLSearchParams(params).toString()
    return axios
      .get<Cita[]>(`${this.urlObtenerCulminadas}?${query}`)
      .then((res: { data: Cita[] }) => res.data)
  }

  async consultarCita(citaId: number): Promise<Cita[]> {
    return axios
      .get<Cita[]>(`${this.urlConsultar}/${citaId}`)
      .then((res: { data: Cita[] }) => res.data)
  }

  async obtenerCitaPorId(id: number, params: any): Promise<Cita> {
    return axios.get<Cita>(`${this.urlConsultar}/${id}`, { params }).then((res) => res.data)
  }

  async crearCita(body: Partial<Cita>): Promise<Cita> {
    return axios.post<Cita>(this.urlCrear, body).then((res) => res.data)
  }

  async updateStatus(id: number, body: Partial<Cita>, params: any): Promise<any> {
    return axios
      .put<Cita>(`${this.urlUpdateStatus}/${id}/estado`, body, { params })
      .then((res) => res.data)
  }

  async rescheduleAppointment(id: number, body: Partial<Cita>, params: any): Promise<any> {
    return axios
      .put<Cita>(`${this.urlReschedule}/${id}/reprogramar`, body, { params })
      .then((res) => res.data)
  }

  async getBusySchedules(params: any): Promise<Cita[]> {
    return axios.get<Cita[]>(this.urlGetBusySchedules, { params }).then((res) => res.data)
  }

  async getAreas(): Promise<any[]> {
    return axios.get<any[]>(`${this.urlGetAreas}`).then((res) => res.data)
  }

  async getReasons(): Promise<any[]> {
    return axios.get<any[]>(`${this.urlGetReasons}`).then((res) => res.data)
  }
}

export default new CitasService()
