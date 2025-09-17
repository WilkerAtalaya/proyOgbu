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

const touched = reactive({
  username: false,
  password: false,
})

const form = reactive({
  username: '',
  password: '',
})

const usernameError = computed(() => {
  if (!touched.username) return ''
  return form.username ? '' : 'Este campo es requerido'
})

const passwordError = computed(() => {
  if (!touched.password) return ''
  return form.password ? '' : 'Este campo es requerido'
})

const markUsernameTouched = () => {
  touched.username = true
}

const markPasswordTouched = () => {
  touched.password = true
}

const snackbar = reactive({
  show: false,
  message: '',
  color: 'success',
})

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
  
  .gbu-logo {
    bottom: 20px;
  }
  
  .logo-image {
    width: 160px;
  }
}
</style>
