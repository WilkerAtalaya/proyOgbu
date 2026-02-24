export interface User {
  id_usuario: number
  nombre: string
  correo: string
  estado?: 'activo' | 'inactivo' | null
  residencia?: 'Ciudad' | 'Tello' | null
  pabellon?: string | null
  habitacion?: string | null
  fecha_cumpleanos?: string | null 
  rol?: string | null              
}