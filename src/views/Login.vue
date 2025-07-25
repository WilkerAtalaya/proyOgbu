<template>
  <div class="login-container">
    <!-- Imagen de fondo -->
    <div class="background-image"></div>

    <!-- Overlay para mejorar legibilidad -->
    <div class="overlay"></div>

    <!-- Contenido del login -->
    <div class="login-content">
      <v-container fluid class="fill-height">
        <v-row justify="center" align="center" class="fill-height">
          <v-col cols="12" sm="8" md="6" lg="4" xl="3">
            <div class="text-center mb-8">
              <h1 class="login-title mb-4">Bienvenido</h1>
            </div>

            <v-form @submit.prevent="handleLogin" class="glass-form">
              <!-- Campo Username -->
              <v-text-field
                v-model="form.username"
                label="Username"
                variant="outlined"
                class="glass-input mb-4"
                :rules="[rules.required]"
                hide-details="auto"
              ></v-text-field>

              <!-- Campo Password -->
              <v-text-field
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                label="Password"
                variant="outlined"
                class="glass-input mb-6"
                :rules="[rules.required]"
                hide-details="auto"
              >
                <template v-slot:append-inner>
                  <v-btn
                    icon
                    variant="text"
                    size="small"
                    @click="showPassword = !showPassword"
                    class="password-toggle"
                  >
                    <v-icon :icon="showPassword ? 'mdi-eye-off' : 'mdi-eye'"></v-icon>
                  </v-btn>
                </template>
              </v-text-field>

              <!-- Botón Sign In -->
              <v-btn type="submit" block size="large" class="sign-in-btn mb-4" :loading="loading">
                SIGN IN
              </v-btn>

              <!-- Remember Me y Forgot Password -->
              <v-row class="mb-6" align="center">
                <v-col cols="6">
                  <v-checkbox
                    v-model="form.rememberMe"
                    label="Remember Me"
                    class="remember-checkbox"
                    hide-details
                  ></v-checkbox>
                </v-col>
                <v-col cols="6" class="text-right">
                  <v-btn variant="text" class="forgot-password-btn" @click="handleForgotPassword">
                    Forgot Password
                  </v-btn>
                </v-col>
              </v-row>

              <!-- Divider -->
              <div class="social-divider mb-4">
                <span class="divider-text">— Or Sign In With —</span>
              </div>

              <!-- Botones de redes sociales -->
              <v-row class="social-buttons">
                <v-col cols="6">
                  <v-btn
                    block
                    variant="elevated"
                    class="social-btn facebook-btn"
                    @click="handleSocialLogin('facebook')"
                  >
                    <v-icon left class="me-2">mdi-facebook</v-icon>
                    Facebook
                  </v-btn>
                </v-col>
                <v-col cols="6">
                  <v-btn
                    block
                    variant="elevated"
                    class="social-btn twitter-btn"
                    @click="handleSocialLogin('twitter')"
                  >
                    <v-icon left class="me-2">mdi-twitter</v-icon>
                    Twitter
                  </v-btn>
                </v-col>
              </v-row>
            </v-form>
          </v-col>
        </v-row>
      </v-container>
    </div>

    <!-- Snackbar para notificaciones -->
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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const showPassword = ref(false)
const loading = ref(false)

// Formulario
const form = reactive({
  username: '',
  password: '',
  rememberMe: false,
})

// Reglas de validación
const rules = {
  required: (value) => !!value || 'Este campo es requerido',
}

// Estado del snackbar
const snackbar = reactive({
  show: false,
  message: '',
  color: 'success',
})

// Función para manejar login
const handleLogin = async () => {
  if (!form.username || !form.password) {
    snackbar.message = 'Por favor completa todos los campos'
    snackbar.color = 'error'
    snackbar.show = true
    return
  }

  loading.value = true

  try {
    // Llamar al servicio de autenticación
    const result = await LoginService.login({
      correo: form.username,
      contraseña: form.password,
    })
    if (result.success) {
      snackbar.message = `¡Bienvenido ${result.data.nombre}!`
      snackbar.color = 'success'
      snackbar.show = true

      // Redirigir al dashboard después del login exitoso
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
  position: relative;
  min-height: 100vh;
  overflow: hidden;
}

.background-image {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('src/assets/background-1.png'); 
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  z-index: 1;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.3);
  z-index: 2;
}

.login-content {
  position: relative;
  z-index: 3;
  min-height: 100vh;
}

.login-title {
  font-size: 2.5rem;
  font-weight: 300;
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.login-subtitle {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.9);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.glass-form {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 2rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.glass-input :deep(.v-field) {
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.glass-input :deep(.v-field--focused) {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.4);
}

.glass-input :deep(.v-field__input) {
  color: white;
}

.glass-input :deep(.v-label) {
  color: rgba(255, 255, 255, 0.8);
}

.glass-input :deep(.v-field__outline) {
  display: none;
}

.password-toggle {
  color: rgba(255, 255, 255, 0.7);
}

.sign-in-btn {
  background: linear-gradient(135deg, #ff9a8b, #fecfef, #fecfef);
  color: #333;
  font-weight: 600;
  border-radius: 25px;
  text-transform: uppercase;
  letter-spacing: 1px;
  box-shadow: 0 4px 15px rgba(255, 154, 139, 0.4);
  transition: all 0.3s ease;
}

.sign-in-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 154, 139, 0.6);
}

.remember-checkbox :deep(.v-label) {
  color: rgba(255, 255, 255, 0.9);
  font-size: 0.9rem;
}

.remember-checkbox :deep(.v-selection-control__input) {
  color: rgba(255, 255, 255, 0.8);
}

.forgot-password-btn {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: underline;
  text-transform: none;
  font-size: 0.9rem;
}

.social-divider {
  text-align: center;
  position: relative;
}

.divider-text {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 0 1rem;
  border-radius: 15px;
  backdrop-filter: blur(5px);
}

.social-btn {
  border-radius: 12px;
  text-transform: none;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.95);
  color: #333;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
}

.social-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.facebook-btn:hover {
  background: rgba(66, 103, 178, 0.1);
}

.twitter-btn:hover {
  background: rgba(29, 161, 242, 0.1);
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .glass-form {
    margin: 1rem;
    padding: 1.5rem;
  }

  .login-title {
    font-size: 2rem;
  }
}
</style>
