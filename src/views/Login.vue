<template>
  <div class="login-container">
    <div class="background-image">
      <img 
        src="../assets/residencia-universitaria.png" 
        alt="Residencia Universitaria"
        class="building-image"
      />
      <div class="overlay"></div>
    </div>

    <div class="login-panel">
      <div class="login-form">
        <div v-if="!showChangePassword">
          <h2 class="login-title">Iniciar Sesión</h2>
          
          <form @submit.prevent="handleLogin">
            <div class="input-group">
              <input
                v-model="form.username"
                type="text"
                placeholder="Usuario"
                class="login-input"
                :class="{ 'error': usernameError }"
                @blur="markUsernameTouched"
                required
              />
              <div v-if="usernameError" class="error-message">{{ usernameError }}</div>
            </div>
            
            <div class="input-group">
              <div class="password-input-container">
                <input
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="Contraseña"
                  class="login-input"
                  :class="{ 'error': passwordError }"
                  @blur="markPasswordTouched"
                  required
                />
                <button 
                  type="button" 
                  @click="showPassword = !showPassword"
                  class="password-toggle-btn"
                >
                  <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
              <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
            </div>
            
            <button type="submit" class="login-button" :disabled="loading">
              <span v-if="loading" class="spinner"></span>
              {{ loading ? 'Ingresando...' : 'Ingresar' }}
            </button>
          </form>

          <div class="forgot-password">
            <button 
              type="button" 
              @click="showChangePassword = true"
              class="forgot-password-btn"
            >
              ¿Quieres cambiar tu contraseña?
            </button>
          </div>
        </div>

        <div v-else>
          <h2 class="login-title">Cambiar Contraseña</h2>
          
          <form @submit.prevent="handleChangePassword">
            <div class="input-group">
              <input
                v-model="changePasswordForm.correo"
                type="email"
                placeholder="Correo electrónico"
                class="login-input"
                :class="{ 'error': emailError }"
                @blur="markEmailTouched"
                required
              />
              <div v-if="emailError" class="error-message">{{ emailError }}</div>
            </div>
            
            <div class="input-group">
              <div class="password-input-container">
                <input
                  v-model="changePasswordForm.contraseña_actual"
                  :type="showCurrentPassword ? 'text' : 'password'"
                  placeholder="Contraseña actual"
                  class="login-input"
                  :class="{ 'error': currentPasswordError }"
                  @blur="markCurrentPasswordTouched"
                  required
                />
                <button 
                  type="button" 
                  @click="showCurrentPassword = !showCurrentPassword"
                  class="password-toggle-btn"
                >
                  <i :class="showCurrentPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
              <div v-if="currentPasswordError" class="error-message">{{ currentPasswordError }}</div>
            </div>

            <div class="input-group">
              <div class="password-input-container">
                <input
                  v-model="changePasswordForm.nueva_contraseña"
                  :type="showNewPassword ? 'text' : 'password'"
                  placeholder="Nueva contraseña"
                  class="login-input"
                  :class="{ 'error': newPasswordError }"
                  @blur="markNewPasswordTouched"
                  required
                />
                <button 
                  type="button" 
                  @click="showNewPassword = !showNewPassword"
                  class="password-toggle-btn"
                >
                  <i :class="showNewPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
              <div v-if="newPasswordError" class="error-message">{{ newPasswordError }}</div>
            </div>

            <div class="input-group">
              <div class="password-input-container">
                <input
                  v-model="confirmPassword"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  placeholder="Confirmar nueva contraseña"
                  class="login-input"
                  :class="{ 'error': confirmPasswordError }"
                  @blur="markConfirmPasswordTouched"
                  required
                />
                <button 
                  type="button" 
                  @click="showConfirmPassword = !showConfirmPassword"
                  class="password-toggle-btn"
                >
                  <i :class="showConfirmPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
              <div v-if="confirmPasswordError" class="error-message">{{ confirmPasswordError }}</div>
            </div>
            
            <button type="submit" class="login-button" :disabled="loadingChangePassword">
              <span v-if="loadingChangePassword" class="spinner"></span>
              {{ loadingChangePassword ? 'Cambiando...' : 'Cambiar Contraseña' }}
            </button>
          </form>

          <div class="back-to-login">
            <button 
              type="button" 
              @click="goBackToLogin"
              class="back-to-login-btn"
            >
              Volver al inicio de sesión
            </button>
          </div>
        </div>
      </div>
      
      <div class="gbu-logo">
        <img 
          src="/src/assets/OGBU-logo.png" 
          alt="OGBU Logo"
          class="logo-image"
        />
      </div>
    </div>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="4000" location="top">
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false"> Cerrar </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup>
import LoginService from '@/services/LoginService'
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const showPassword = ref(false)
const loading = ref(false)

const showChangePassword = ref(false)
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)
const loadingChangePassword = ref(false)
const confirmPassword = ref('')

const touched = reactive({
  username: false,
  password: false,
  email: false,
  currentPassword: false,
  newPassword: false,
  confirmPassword: false,
})

const form = reactive({
  username: '',
  password: '',
})

const changePasswordForm = reactive({
  correo: '',
  contraseña_actual: '',
  nueva_contraseña: '',
})

const usernameError = computed(() => {
  if (!touched.username) return ''
  return form.username ? '' : 'Este campo es requerido'
})

const passwordError = computed(() => {
  if (!touched.password) return ''
  return form.password ? '' : 'Este campo es requerido'
})

const emailError = computed(() => {
  if (!touched.email) return ''
  if (!changePasswordForm.correo) return 'Este campo es requerido'
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(changePasswordForm.correo) ? '' : 'Formato de correo inválido'
})

const currentPasswordError = computed(() => {
  if (!touched.currentPassword) return ''
  return changePasswordForm.contraseña_actual ? '' : 'Este campo es requerido'
})

const newPasswordError = computed(() => {
  if (!touched.newPassword) return ''
  if (!changePasswordForm.nueva_contraseña) return 'Este campo es requerido'
  if (changePasswordForm.nueva_contraseña.length < 6) return 'La contraseña debe tener al menos 6 caracteres'
  return ''
})

const confirmPasswordError = computed(() => {
  if (!touched.confirmPassword) return ''
  if (!confirmPassword.value) return 'Este campo es requerido'
  return confirmPassword.value === changePasswordForm.nueva_contraseña ? '' : 'Las contraseñas no coinciden'
})

const markUsernameTouched = () => {
  touched.username = true
}

const markPasswordTouched = () => {
  touched.password = true
}

const markEmailTouched = () => {
  touched.email = true
}

const markCurrentPasswordTouched = () => {
  touched.currentPassword = true
}

const markNewPasswordTouched = () => {
  touched.newPassword = true
}

const markConfirmPasswordTouched = () => {
  touched.confirmPassword = true
}

const snackbar = reactive({
  show: false,
  message: '',
  color: 'success',
})

const goBackToLogin = () => {
  showChangePassword.value = false
  changePasswordForm.correo = ''
  changePasswordForm.contraseña_actual = ''
  changePasswordForm.nueva_contraseña = ''
  confirmPassword.value = ''
  touched.email = false
  touched.currentPassword = false
  touched.newPassword = false
  touched.confirmPassword = false
}

const handleLogin = async () => {
  touched.username = true
  touched.password = true
  
  if (!form.username || !form.password) {
    snackbar.message = 'Por favor completa todos los campos'
    snackbar.color = 'error'
    snackbar.show = true
    return
  }

  loading.value = true

  try {
    const result = await LoginService.login({
      correo: form.username,
      contraseña: form.password,
    })
    if (result.success) {
      snackbar.message = `¡Bienvenido ${result.data.nombre}!`
      snackbar.color = 'success'
      snackbar.show = true

      setTimeout(() => {
        router.push('/anuncios')
      }, 1000)

      console.log('Login exitoso:', result.data)
    } else {
      snackbar.message = result.message || 'Error al iniciar sesión'
      snackbar.color = 'error'
      snackbar.show = true
    }
  } catch (error) {
    console.error('Error en login:', error)
    snackbar.message = 'Error de conexión. Verifica tu conexión a internet.'
    snackbar.color = 'error'
    snackbar.show = true
  } finally {
    loading.value = false
  }
}

const handleChangePassword = async () => {
  touched.email = true
  touched.currentPassword = true
  touched.newPassword = true
  touched.confirmPassword = true
  
  if (!changePasswordForm.correo || !changePasswordForm.contraseña_actual || 
      !changePasswordForm.nueva_contraseña || !confirmPassword.value) {
    snackbar.message = 'Por favor completa todos los campos'
    snackbar.color = 'error'
    snackbar.show = true
    return
  }

  if (emailError.value || currentPasswordError.value || newPasswordError.value || confirmPasswordError.value) {
    snackbar.message = 'Por favor corrige los errores en el formulario'
    snackbar.color = 'error'
    snackbar.show = true
    return
  }

  loadingChangePassword.value = true

  try {
    const result = await LoginService.cambiarContrasena({
      correo: changePasswordForm.correo,
      contraseña_actual: changePasswordForm.contraseña_actual,
      nueva_contraseña: changePasswordForm.nueva_contraseña,
    })

    if (result.success) {
      snackbar.message = 'Contraseña cambiada exitosamente'
      snackbar.color = 'success'
      snackbar.show = true

      setTimeout(() => {
        goBackToLogin()
      }, 2000)
    } else {
      snackbar.message = result.message || 'Error al cambiar la contraseña'
      snackbar.color = 'error'
      snackbar.show = true
    }
  } catch (error) {
    console.error('Error al cambiar contraseña:', error)
    snackbar.message = 'Error de conexión. Verifica tu conexión a internet.'
    snackbar.color = 'error'
    snackbar.show = true
  } finally {
    loadingChangePassword.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  height: 100vh;
  font-family: Arial, sans-serif;
}

.background-image {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.building-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: 20% 0%;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
}


.login-panel {
  width: 540px;
  background: #B8BAA3;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.login-form {
  padding: 40px 60px;
  width: 100%;
  position: relative;
}

.login-title {
  text-align: center;
  color: #F2F2F2;
  -webkit-filter: drop-shadow(0px 4px 4px 0px #000);
  filter: drop-shadow(0px 4px 4px 0px #000);
  text-shadow: 0px 4px 4px #000;
  margin-bottom: 30px;
  font-size: 40px;
  font-weight: 400;
}

.input-group {
  margin-bottom: 20px;
}

.password-input-container {
  position: relative;
}

.login-input {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
  background: white;
}

.login-input:focus {
  outline: none;
  border-color: #ddd;
  box-shadow: 0 0 0 2px rgba(0, 0, 0, 0.1);
}

.login-input.error {
  border-color: #dc3545;
}

.login-input::placeholder {
  color: #999;
}

.password-toggle-btn {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: #999;
  padding: 5px;
  border-radius: 4px;
  transition: color 0.3s ease;
}

.password-toggle-btn:hover {
  color: #333;
}

.error-message {
  color: #dc3545;
  font-size: 12px;
  margin-top: 5px;
}

.login-button {
  width: 100%;
  padding: 15px;
  background: #333;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s ease;
  margin-top: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.login-button:hover:not(:disabled) {
  background: #555;
}

.login-button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.forgot-password {
  text-align: center;
  margin-top: 15px;
}

.forgot-password-btn {
  background: none;
  border: none;
  color: #F2F2F2;
  text-decoration: underline;
  cursor: pointer;
  font-size: 14px;
  transition: color 0.3s ease;
}

.forgot-password-btn:hover {
  color: #ddd;
}

.back-to-login {
  text-align: center;
  margin-top: 15px;
}

.back-to-login-btn {
  background: none;
  border: 1px solid #F2F2F2;
  color: #F2F2F2;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.back-to-login-btn:hover {
  background: #F2F2F2;
  color: #333;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid #ffffff;
  border-top: 2px solid transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.gbu-logo {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  display: flex;
  justify-content: center;
}

.logo-image {
  width: 230px;
  height: auto;
}

/* Responsive design */
@media (max-width: 768px) {
  .login-container {
    position: relative;
    flex-direction: column;
  }
  
  .background-image {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100vh;
    z-index: 1;
  }
  
  .login-panel {
    position: relative;
    z-index: 3;
    width: 100%;
    height: 100vh;
    background: transparent;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    box-sizing: border-box;
  }
  
  .login-form {
    background: #B8BAA3;
    border-radius: 15px;
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.3);
    padding: 40px 30px;
    width: 100%;
    max-width: 400px;
    position: relative;
    margin-bottom: 100px;
  }
  
  .login-title {
    font-size: 32px;
  }
  
  .forgot-password-btn,
  .back-to-login-btn {
    font-size: 13px;
  }
  
  .back-to-login-btn {
    padding: 8px 16px;
  }
  
  .gbu-logo {
    position: fixed;
    bottom: 30px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 4;
  }
  
  .logo-image {
    width: 180px;
  }
}

@media (max-width: 480px) {
  .login-form {
    padding: 30px 20px;
    margin: 20px;
    margin-bottom: 120px;
  }
  
  .login-title {
    font-size: 28px;
  }
  
  .forgot-password-btn,
  .back-to-login-btn {
    font-size: 12px;
  }
  
  .back-to-login-btn {
    padding: 6px 12px;
  }
  
  .gbu-logo {
    bottom: 20px;
  }
  
  .logo-image {
    width: 160px;
  }
}
</style>
