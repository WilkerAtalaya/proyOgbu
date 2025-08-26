import { environment } from '@/environment/environment'
import type { AreaComun, Salida } from '@/models/Permiso'
import axios from 'axios'

export class PermisosService {
  private urlCrearSalida: string
  private urlObtenerSalidasPorUsuario: string
  private urlObtenerTodasLasSalidas: string
  private urlAreaComunSalida: string
  private urlObtenerAreaComunPorUsuario: string
  private urlObtenerTodasLasAreaComun: string
  private urlActualizarEstadoSalida: string
  private urlActualizarEstadoAreaComun: string

  constructor() {
    this.urlCrearSalida = `${environment.baseUrlApi}${environment.endPoint.permisos.crearSalida}`
    this.urlObtenerSalidasPorUsuario = `${environment.baseUrlApi}${environment.endPoint.permisos.obtenerSalidaPorUsuario}`
    this.urlObtenerTodasLasSalidas = `${environment.baseUrlApi}${environment.endPoint.permisos.todasLasSalidas}`
    this.urlAreaComunSalida = `${environment.baseUrlApi}${environment.endPoint.permisos.crearAreaComun}`
    this.urlObtenerAreaComunPorUsuario = `${environment.baseUrlApi}${environment.endPoint.permisos.obtenerAreaComunPorUsuario}`
    this.urlObtenerTodasLasAreaComun = `${environment.baseUrlApi}${environment.endPoint.permisos.todasLasAreaComun}`
    this.urlActualizarEstadoSalida = `${environment.baseUrlApi}${environment.endPoint.permisos.actualizarEstadoSalida}`
    this.urlActualizarEstadoAreaComun = `${environment.baseUrlApi}${environment.endPoint.permisos.actualizarEstadoAreaComun}`
  }

  async crearPermisoSalida(body: Partial<Salida>): Promise<Salida> {
    return axios
      .post<Salida>(this.urlCrearSalida, body)
      .then(res => res.data);
  }

  async obtenerPermisosDeSalidaPorUsuario(
    usuarioId: number,
  ): Promise<Salida[]> {
    return axios
      .get<Salida[]>(`${this.urlObtenerSalidasPorUsuario}/${usuarioId}`)
      .then((res: { data: Salida[] }) => res.data)
  }
  
  async obtenerTodosLosPermisosDeSalida(): Promise<Salida[]>
  {
    return axios
      .get<Salida[]>(this.urlObtenerTodasLasSalidas)
      .then((res: { data: Salida[] }) => res.data)
  }

  async crearPermisoAreaComun(body: Partial<AreaComun>): Promise<AreaComun> {
    return axios
      .post<AreaComun>(this.urlAreaComunSalida, body)
      .then(res => res.data);
  }

  async obtenerPermisosDeAreaComunPorUsuario(
    usuarioId: number,
  ): Promise<AreaComun[]> {
    return axios
      .get<AreaComun[]>(`${this.urlObtenerAreaComunPorUsuario}/${usuarioId}`)
      .then((res: { data: AreaComun[] }) => res.data)
  }
  
  async obtenerTodosLosPermisosDeAreaComun(): Promise<AreaComun[]>
  {
    return axios
      .get<AreaComun[]>(this.urlObtenerTodasLasAreaComun)
      .then((res: { data: AreaComun[] }) => res.data)
  }

  async actualizarEstadoPermisoSalida(id: number, estado: string): Promise<any> {
    return axios
      .put(`${this.urlActualizarEstadoSalida}/${id}/estado`, { estado })
      .then(res => res.data);
  }

  async actualizarEstadoPermisoAreaComun(id: number, estado: string): Promise<any> {
    return axios
      .put(`${this.urlActualizarEstadoAreaComun}/${id}/estado`, { estado })
      .then(res => res.data);
  }
}

export default new PermisosService()
