<template>
  <ContainerView>
    <div class="page-wrap">
      <div class="content-panel">
        <div class="header">
          <h2 class="text-title">{{ isEdit ? 'Editar alumno' : 'Agregar alumno' }}</h2>
          <button class="btn ghost" @click="router.push('/alumnos')">Volver</button>
        </div>

        <div class="card">
          <div class="grid">
            <label>
              Nombre
              <input v-model="form.nombre" />
            </label>

            <label>
              Correo
              <input v-model="form.correo" type="email" />
            </label>

            <label>
              Rol
              <select v-model="form.rol">
                <option value="alumno">alumno</option>
                <option value="admin">admin</option>
                <option value="psicologia">psicologia</option>
                <option value="social">social</option>
              </select>
            </label>

            <label>
              Estado
              <select v-model="form.estado">
                <option value="activo">activo</option>
                <option value="inactivo">inactivo</option>
              </select>
            </label>

            <label>
              Residencia
              <select v-model="form.residencia">
                <option value="">(vacío)</option>
                <option value="Ciudad">Ciudad</option>
                <option value="Tello">Tello</option>
              </select>
            </label>

            <label>
              Fecha cumpleaños
              <input v-model="form.fecha_cumpleanos" type="date" />
            </label>

            <label>
              Pabellón
              <input v-model="form.pabellon" />
            </label>

            <label>
              Habitación
              <input v-model="form.habitacion" />
            </label>

            <label v-if="!isEdit">
              Contraseña
              <div class="password-wrap">
                <input v-model="form.contrasena" :type="passwordType" />
                <button
                  type="button"
                  class="eye-btn"
                  @click="showPassword = !showPassword"
                  :title="showPassword ? 'Ocultar' : 'Mostrar'"
                >
                  <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
            </label>

            <label v-else>
              Contraseña (opcional)
              <div class="password-wrap">
                <input
                  v-model="form.contrasena"
                  :type="passwordType"
                  placeholder="Dejar vacío para no cambiar"
                />
                <button
                  type="button"
                  class="eye-btn"
                  @click="showPassword = !showPassword"
                  :title="showPassword ? 'Ocultar' : 'Mostrar'"
                >
                  <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
                </button>
              </div>
            </label>
          </div>

          <div class="actions">
            <button class="btn primary" @click="save()">
              {{ isEdit ? 'Guardar cambios' : 'Crear alumno' }}
            </button>
          </div>
        </div>

      </div>
    </div>
  </ContainerView>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ContainerView from '@/components/layout/ContainerView.vue'
import AdminUsuariosService from '@/services/AdminUsuariosService'

const router = useRouter()
const route = useRoute()

const id = computed(() => Number(route.params.id))
const isEdit = computed(() => !!route.params.id)

const showPassword = ref(false)
const passwordType = computed(() => (showPassword.value ? 'text' : 'password'))

const form = reactive({
  nombre: '',
  correo: '',
  rol: 'alumno',
  estado: 'activo',
  residencia: '',
  fecha_cumpleanos: '',
  pabellon: '',
  habitacion: '',
  contrasena: '',
})

async function load() {
  if (!isEdit.value) return
  const u = await AdminUsuariosService.obtenerPorId(id.value)
  form.nombre = u.nombre ?? ''
  form.correo = u.correo ?? ''
  form.rol = (u.rol as any) ?? 'alumno'
  form.estado = (u.estado as any) ?? 'activo'
  form.residencia = (u.residencia as any) ?? ''
  form.fecha_cumpleanos = (u.fecha_cumpleanos as any) ?? ''
  form.pabellon = (u.pabellon as any) ?? ''
  form.habitacion = (u.habitacion as any) ?? ''
  form.contrasena = ''
}

async function save() {
  if (!form.nombre.trim() || !form.correo.trim() || !form.rol.trim()) {
    alert('Nombre, correo y rol son obligatorios.')
    return
  }

  if (!isEdit.value) {
    if (!form.contrasena.trim()) {
      alert('La contraseña es obligatoria para crear.')
      return
    }
    await AdminUsuariosService.crear({
      nombre: form.nombre,
      correo: form.correo,
      contrasena: form.contrasena,
      rol: form.rol,
      estado: form.estado as any,
      residencia: form.residencia as any,
      fecha_cumpleanos: form.fecha_cumpleanos || undefined,
      pabellon: form.pabellon || undefined,
      habitacion: form.habitacion || undefined,
    })
  } else {
    await AdminUsuariosService.actualizar(id.value, {
      nombre: form.nombre,
      correo: form.correo,
      rol: form.rol,
      estado: form.estado as any,
      residencia: form.residencia as any,
      fecha_cumpleanos: form.fecha_cumpleanos || undefined,
      pabellon: form.pabellon || undefined,
      habitacion: form.habitacion || undefined,
      ...(form.contrasena.trim() ? { contrasena: form.contrasena } : {}),
    })
  }

  router.push('/alumnos')
}

onMounted(load)
</script>

<style scoped>
.page-wrap{
  width: 100%;
}

/* Panel marronsito/oliva + separación a la derecha */
.content-panel{
  background: rgba(154, 154, 122, 0.35);
  border: 1px solid #A37801;
  border-radius: 16px;
  padding: 24px;
  margin: 24px 64px 24px 24px;
  backdrop-filter: blur(2px);
}

.header{
  display:flex;
  justify-content: space-between;
  align-items:center;
  gap: 12px;
  margin-bottom: 16px;
}

.text-title{
  color: white;
  font-size: 28px !important;
  text-transform: none;
  font-family: 'Righteous', cursive;
  margin: 0;
}

.card{
  background: transparent;
  border: 1px solid #A37801;
  border-radius: 16px;
  padding: 16px;
}

.grid{
  display:grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

label{
  display:flex;
  flex-direction: column;
  gap:6px;
  font-size: 13px;
  color: #111827;
}

input, select{
  padding: 12px;
  border-radius: 10px;
  border: 1px solid #A37801;
  background: #fff;
}

/* Botones */
.btn{
  border:none;
  border-radius: 14px;
  padding: 10px 14px;
  cursor:pointer;
  transition: all .2s ease;
  white-space: nowrap;
}

.btn.primary{
  background:#53696D;
  color: #fff;
}

.btn.ghost{
  background: #ffffffb8;
  border: 1px solid rgba(0,0,0,.12);
}

.actions{
  margin-top: 14px;
  display:flex;
  justify-content:flex-end;
}

/* Ojo contraseña */
.password-wrap{
  position: relative;
  display: flex;
  align-items: center;
}

.password-wrap input{
  width: 100%;
  padding-right: 44px;
}

.eye-btn{
  position: absolute;
  right: 10px;
  border: none;
  background: transparent;
  cursor: pointer;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display:flex;
  align-items:center;
  justify-content:center;
  color: #53696D;
}

.eye-btn:hover{
  background: #FFFBED;
}

/* Responsive */
@media (max-width: 1024px){
  .content-panel{
    margin: 16px;
  }
}

@media (max-width: 900px){
  .grid{
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px){
  .content-panel{
    padding: 16px;
    margin: 12px;
  }
  .text-title{
    font-size: 22px !important;
  }
}
</style>