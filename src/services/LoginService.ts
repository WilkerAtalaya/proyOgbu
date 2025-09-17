import { environment } from '@/environment/environment'
import axios from 'axios'

export class LoginService {
  private urlLogin: string

  constructor() {
    this.urlLogin = `${environment.baseUrlApi}${environment.endPoint.login.crear}`
  }

  async login(credentials: any) {
    try {
      const response = await fetch(`${this.urlLogin}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      })

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`)
      }

      const data = await response.json()
      console.log('Datos del usuario:', data)
      // Guardar los datos del usuario en localStorage
      localStorage.setItem('user', JSON.stringify(data))

      return {
        success: true,
        data: data,
        message: 'Login exitoso',
      }
    } catch (error) {
      console.error('Error en login:', error)
      return {
        success: false,
        data: null,
        message: error || 'Error al iniciar sesión',
      }
    }
  }
  getCurrentUser() {
    try {
      const userData = localStorage.getItem('user')
      return userData ? JSON.parse(userData) : null
    } catch (error) {
      console.error('Error al obtener usuario:', error)
      return null
    }
  }

  isAuthenticated() {
    return this.getCurrentUser() !== null
  }

  logout() {
    localStorage.removeItem('user')
  }

  // Función para obtener el rol del usuario
  getUserRole() {
    const user = this.getCurrentUser()
    return user ? user.rol : null
  }

  isAdmin() {
    const user = this.getCurrentUser()
    return user.rol === 'admin'
  }

  // Función para obtener el nombre del usuario
  getUserName() {
    const user = this.getCurrentUser()
    return user ? user.nombre : null
  }
}

export default new LoginService()
