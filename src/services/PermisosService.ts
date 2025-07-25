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

  constructor() {
    this.urlCrearSalida = `${environment.baseUrlApi}${environment.endPoint.permisos.crearSalida}`
    this.urlObtenerSalidasPorUsuario = `${environment.baseUrlApi}${environment.endPoint.permisos.obtenerSalidaPorUsuario}`
    this.urlObtenerTodasLasSalidas = `${environment.baseUrlApi}${environment.endPoint.permisos.todasLasSalidas}`
    this.urlAreaComunSalida = `${environment.baseUrlApi}${environment.endPoint.permisos.crearAreaComun}`
    this.urlObtenerAreaComunPorUsuario = `${environment.baseUrlApi}${environment.endPoint.permisos.obtenerAreaComunPorUsuario}`
    this.urlObtenerTodasLasAreaComun = `${environment.baseUrlApi}${environment.endPoint.permisos.todasLasAreaComun}`
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
}

export default new PermisosService()
