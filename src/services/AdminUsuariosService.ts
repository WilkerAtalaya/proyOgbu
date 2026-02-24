import { environment } from '@/environment/environment'
import axios from 'axios'
import type { User } from '@/models/User'

type Paginated<T> = {
  items: T[]
  page: number
  per_page: number
  total: number
  pages: number
}

export type UserFilters = {
  nombre?: string
  rol?: string
  estado?: string
  residencia?: string
  fecha_registro_desde?: string
  fecha_registro_hasta?: string
  page?: number
  per_page?: number
}

export type CreateUserPayload = {
  nombre: string
  correo: string
  contrasena: string
  rol: string
  fecha_cumpleanos?: string
  estado?: 'activo' | 'inactivo'
  residencia?: 'Ciudad' | 'Tello'
  pabellon?: string
  habitacion?: string
}

export type UpdateUserPayload = Partial<Omit<CreateUserPayload, 'contrasena'>> & {
  contrasena?: string
}

class AdminUsuariosService {
  private baseUrl: string

  constructor() {
    this.baseUrl = `${environment.baseUrlApi}${environment.endPoint.administrarUsuarios.listar}`
  }

  // GET /admin/usuarios?nombre=...&rol=...&page=1...
  async listar(filters: UserFilters): Promise<Paginated<User>> {
    const res = await axios.get(this.baseUrl, { params: filters })
    return res.data
  }

  // GET /admin/usuarios/:id
  async obtenerPorId(id: number): Promise<User> {
    const res = await axios.get(`${this.baseUrl}/${id}`)
    return res.data
  }

  // POST /admin/usuarios
  async crear(payload: CreateUserPayload): Promise<User> {
    const res = await axios.post(this.baseUrl, payload)
    return res.data
  }

  // PATCH /admin/usuarios/:id
  async actualizar(id: number, payload: UpdateUserPayload): Promise<User> {
    const res = await axios.patch(`${this.baseUrl}/${id}`, payload)
    return res.data
  }

  // PATCH /admin/usuarios/:id/estado   body: { estado: "activo"|"inactivo" }
  async cambiarEstado(id: number, estado: 'activo' | 'inactivo'): Promise<User> {
    const res = await axios.patch(`${this.baseUrl}/${id}/estado`, { estado })
    return res.data
  }
}

export default new AdminUsuariosService()