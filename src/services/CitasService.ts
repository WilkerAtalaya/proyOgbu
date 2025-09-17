import { environment } from '@/environment/environment'
import type { CitaAlumno, CitaAdmin } from '@/models/Cita'
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

  constructor() {
    this.urlObtenerSolicitadasPorUsuario = `${environment.baseUrlApi}${environment.endPoint.citas.obtenerSolicitadasPorUsuario}`
    this.urlObtenerPendientes = `${environment.baseUrlApi}${environment.endPoint.citas.obtenerPendientes}`
    this.urlObtenerCulminadas = `${environment.baseUrlApi}${environment.endPoint.citas.obtenerCulminadas}`
    this.urlConsultar = `${environment.baseUrlApi}${environment.endPoint.citas.consultar}`
    this.urlCrear = `${environment.baseUrlApi}${environment.endPoint.citas.crear}`
    this.urlGetBusySchedules = `${environment.baseUrlApi}${environment.endPoint.citas.getBusySchedules}`
    this.urlGetAreas = `${environment.baseUrlApi}${environment.endPoint.area.getAreas}`
    this.urlGetReasons = `${environment.baseUrlApi}${environment.endPoint.reasons.getReasons}`
  }

  async obtenerCitasSolicitadasPorUsuario(usuarioId: number): Promise<CitaAlumno[]> {
    return axios
      .get<CitaAlumno[]>(`${this.urlObtenerSolicitadasPorUsuario}/${usuarioId}`)
      .then((res: { data: CitaAlumno[] }) => res.data)
  }

  async obtenerCitasPendientes(params: Record<string, any>): Promise<CitaAdmin[]> {
    const query = new URLSearchParams(params).toString()
    return axios
      .get<CitaAdmin[]>(`${this.urlObtenerPendientes}?${query}`)
      .then((res: { data: CitaAdmin[] }) => res.data)
  }

  async obtenerCitasCulminadas(params: Record<string, any>): Promise<CitaAdmin[]> {
    const query = new URLSearchParams(params).toString()
    return axios
      .get<CitaAdmin[]>(`${this.urlObtenerCulminadas}?${query}`)
      .then((res: { data: CitaAdmin[] }) => res.data)
  }

  async consultarCita(citaId: number): Promise<CitaAdmin[]> {
    return axios
      .get<CitaAdmin[]>(`${this.urlConsultar}/${citaId}`)
      .then((res: { data: CitaAdmin[] }) => res.data)
  }

  async obtenerCitaPorId(id: number): Promise<CitaAdmin> {
    return axios.get<CitaAdmin>(`${this.urlConsultar}/${id}`).then((res) => res.data)
  }

  async crearCita(body: Partial<CitaAdmin>): Promise<CitaAdmin> {
    return axios.post<CitaAdmin>(this.urlCrear, body).then((res) => res.data)
  }

  async getBusySchedules(params: any): Promise<CitaAdmin[]> {
    return axios.get<CitaAdmin[]>(this.urlGetBusySchedules, { params }).then((res) => res.data)
  }

  async getAreas(): Promise<any[]> {
    return axios.get<any[]>(`${this.urlGetAreas}`).then((res) => res.data)
  }

  async getReasons(): Promise<any[]> {
    return axios.get<any[]>(`${this.urlGetReasons}`).then((res) => res.data)
  }
}

export default new CitasService()
