import { environment } from '@/environment/environment'
import type { Asistencia } from '@/models/Asistencia'
import axios from 'axios'

export class AsistenciaService {
  private urlObtenerFechasMarcadasPorUsuario: string
  private urlObtenerDetallePorFechaYUsuario: string

  constructor() {
    this.urlObtenerFechasMarcadasPorUsuario = `${environment.baseUrlApi}${environment.endPoint.asistencia.obtenerFechasMarcadasPorUsuario}`
    this.urlObtenerDetallePorFechaYUsuario = `${environment.baseUrlApi}${environment.endPoint.asistencia.obtenerDetallePorFechaYUsuario}`
  }

  async obtenerFechasMarcadasPorUsuario(usuarioId: number): Promise<string[]> {
    return axios
      .get<string[]>(`${this.urlObtenerFechasMarcadasPorUsuario}/${usuarioId}`)
      .then(res => res.data)
  }

  async obtenerAsistenciaPorFechaYUsuario(usuarioId: number, fecha: string): Promise<Asistencia[]> {
    return axios
      .get<Asistencia[]>(`${this.urlObtenerDetallePorFechaYUsuario}/${usuarioId}/${fecha}`)
      .then((res: { data: Asistencia[] }) => res.data)
  }
}

export default new AsistenciaService()
