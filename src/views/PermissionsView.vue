<template>
  <!-- Vista para estudiantes -->
  <ContainerView v-if="!isAdmin" background-color="transparent" padding="0px">
    <v-row>
      <v-col cols="12" md="6">
        <v-card class="pa-4" style="border-radius: 16px; background-color: #BBBDA7">
          <v-tabs v-model="activeTab" class="mb-4">
            <v-tab value="solicitud" class="custom-tab">
              <h3 :class="{ 'active-tab-text': activeTab === 'solicitud' }">
                Solicitud de vivienda
              </h3>
            </v-tab>
            <v-tab value="area-comun" class="custom-tab">
              <h3 :class="{ 'active-tab-text': activeTab === 'area-comun' }">Área común</h3>
            </v-tab>
          </v-tabs>

          <v-tabs-window v-model="activeTab">
            <v-tabs-window-item value="solicitud">
              <div class="mb-4"
                style="background-color: #EDEEE2F2; border-radius: 25px; padding: 20px 16px 46px; overflow: auto;">
                <p style="font-size: 18px; color: black; font-weight: 400;" class="mb-4">
                  Registre el rango de días que estarás fuera de la vivienda universitaria:
                </p>
                <v-form @submit.prevent="submitSolicitudVivienda">
                  <div class="mb-3">
                    <label style="font-size: 18px; color: black; font-weight: 400;"> Rango de fechas </label>
                    <VueDatePicker v-model="form.rangoFechas" locale="es" format="dd/MM/yyyy" range
                      :enable-time-picker="false" :min-date="new Date()" placeholder="Selecciona el rango de fechas"
                      :ui="{ input: 'custom-datepicker' }" />
                  </div>
                  <div class="mb-4">
                    <label style="font-size: 18px; color: black; font-weight: 400;"> Motivo </label>
                    <v-textarea v-model="form.motivo" variant="outlined" rows="4" hide-details
                      class="custom-textarea"></v-textarea>
                  </div>
                  <div class="d-flex justify-center mt-4">
                    <v-btn type="submit" color="#A80038" size="large" style="
                        border-radius: 13px;
                        text-transform: none;
                        font-weight: 600;
                        color: #fff;
                      " min-width="100px">
                      Enviar
                    </v-btn>
                  </div>
                </v-form>
              </div>
            </v-tabs-window-item>
            <v-tabs-window-item value="area-comun">
              <div class="mb-4">
                <p style="font-size: 18px; color: black; font-weight: 400;" class="mb-4">
                  Registre el lugar, fecha y horario que quieres reservar:
                </p>
                <v-form @submit.prevent="submitAreaComun">
                  <div class="mb-3">
                    <label style="font-size: 18px; color: black; font-weight: 400;">Lugar</label>
                    <v-select v-model="form.lugar" :items="siteOptions" variant="outlined" density="comfortable"
                      hide-details class="custom-select"></v-select>
                  </div>
                  <div class="mb-3">
                    <label style="font-size: 18px; color: black; font-weight: 400;">Fecha</label>
                    <VueDatePicker v-model="form.fechaAreaComun" locale="es" format="dd/MM/yyyy"
                      :enable-time-picker="false" :min-date="new Date()" placeholder="Selecciona la fecha"
                      :ui="{ input: 'custom-datepicker' }" />
                  </div>
                  <div class="mb-3">
                    <label style="font-size: 18px; color: black; font-weight: 400;">Hora de inicio</label>
                    <v-select v-model="form.horaInicio" :items="scheduleOptions" variant="outlined"
                      density="comfortable" hide-details class="custom-select"
                      @update:model-value="resetHoraFin"></v-select>
                  </div>
                  <div class="mb-3">
                    <label style="font-size: 18px; color: black; font-weight: 400;">Hora de fin</label>
                    <v-select v-model="form.horaFin" :items="horasFinDisponibles" variant="outlined"
                      density="comfortable" hide-details class="custom-select" :disabled="!form.horaInicio"
                      placeholder="Primero selecciona hora de inicio"></v-select>
                  </div>
                  <div class="d-flex justify-center mt-4">
                    <v-btn type="submit" color="#FFC107" size="large" style="
                        border-radius: 13px;
                        text-transform: none;
                        font-weight: 600;
                        color: #000;
                      " min-width="100px">
                      Enviar
                    </v-btn>
                  </div>
                </v-form>
              </div>
            </v-tabs-window-item>
          </v-tabs-window>
        </v-card>
      </v-col>
      <v-col cols="12" md="6">
        <v-card class="pa-4" style="border-radius: 16px; background-color: #BBBDA7">
          <h3 class="mb-4 text-white text-title">Reservas</h3>
          <div v-if="activeTab === 'solicitud' && solicitudes.length === 0" class="text-center pa-8">
            <v-icon size="48" color="grey-lighten-1" class="mb-3"> mdi-calendar-blank </v-icon>
            <p class="text-body-2 text-grey">No tienes reservas registradas</p>
          </div>
          <div v-if="activeTab === 'area-comun' && areaComunItems.length === 0" class="text-center pa-8">
            <v-icon size="48" color="grey-lighten-1" class="mb-3"> mdi-calendar-blank </v-icon>
            <p class="text-body-2 text-grey">No tienes reservas registradas</p>
          </div>

          <div style="padding: 18px 32px 48px; background-color: #EDEEE2F2; border-radius: 25px; overflow: auto;">
            <v-data-table v-if="activeTab === 'solicitud' && solicitudes.length > 0" :items="solicitudes"
              :items-per-page="5" class="custom-table">
              <template #headers>
                <tr class="table-header">
                  <th>Desde</th>
                  <th>Hasta</th>
                  <th>Estado</th>
                </tr>
              </template>
              <template #item="{ item }">
                <tr>
                  <td>{{ dateFormatV2(item.fecha_salida) }}</td>
                  <td>{{ dateFormatV2(item.fecha_regreso) }}</td>
                  <td>
                    <v-chip :color="getStatusColor(item.estado)" size="small" variant="flat" class="text-caption">
                      {{ item.estado }}
                    </v-chip>
                  </td>
                </tr>
              </template>
            </v-data-table>
            <v-data-table v-if="activeTab === 'area-comun' && areaComunItems.length > 0" :items="areaComunItems"
              :items-per-page="5" class="custom-table">
              <template #headers>
                <tr class="table-header">
                  <th>Lugar</th>
                  <th>Fecha</th>
                  <th>Horario</th>
                  <th>Estado</th>
                  <th v-if="isAdmin">Acción</th>
                </tr>
              </template>
              <template #item="{ item }">
                <tr>
                  <td>{{ item.lugar }}</td>
                  <td>{{ dateFormatV2(item.fecha) }}</td>
                  <td>{{ item.horario }}</td>
                  <td>
                    <v-chip :color="getStatusColor(item.estado)" size="small" variant="flat" class="text-caption">
                      {{ item.estado }}
                    </v-chip>
                  </td>
                  <td v-if="isAdmin">
                    <button @click="deleteReserva(item.id)" style="background: none; border: none; cursor: pointer;"
                      title="Eliminar reserva">
                      <i class="fa-solid fa-trash" style="color: #d32f2f; font-size: 16px;"></i>
                    </button>
                  </td>
                </tr>
              </template>
            </v-data-table>
          </div>


        </v-card>
      </v-col>
    </v-row>
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000" location="top">
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false"> Cerrar </v-btn>
      </template>
    </v-snackbar>
  </ContainerView>

  <!-- Vista para administradores -->
  <ContainerView v-else>
    <v-tabs v-model="adminTab" align-tabs="start" color="#A37801">
      <v-tab value="permisos-salida" class="custom-tab">
        <h4>Permisos de Salida</h4>
      </v-tab>
      <v-tab value="area-comun" class="custom-tab">
        <h4>Área Común</h4>
      </v-tab>
    </v-tabs>

    <v-tabs-window v-model="adminTab">
      <v-tabs-window-item value="permisos-salida">
        <v-data-table :items="solicitudes" :items-per-page="10" class="custom-table-admin">
          <template #headers>
            <tr class="table-header">
              <th>Alumno</th>
              <th>Fecha Salida</th>
              <th>Fecha Regreso</th>
              <th>Motivo</th>
              <th>Acciones</th>
            </tr>
          </template>
          <template #item="{ item }">
            <tr>
              <td>{{ item.nombre_usuario }}</td>
              <td>{{ dateFormatV2(item.fecha_salida) }}</td>
              <td>{{ dateFormatV2(item.fecha_regreso) }}</td>
              <td>{{ item.motivo || 'Sin motivo' }}</td>
              <td>
                <div class="d-flex" style="gap: 8px;">
                  <v-btn icon size="small" :class="getButtonClass('Aprobado', item.estado)"
                    :disabled="item.estado !== 'En revisión'" @click="actualizarEstadoSalida(item.id, 'Aprobado')"
                    title="Aprobar">
                    <i class="fa-solid fa-check" :style="getIconStyle('Aprobado', item.estado)"></i>
                  </v-btn>
                  <v-btn icon size="small" :class="getButtonClass('Denegado', item.estado)"
                    :disabled="item.estado !== 'En revisión'" @click="actualizarEstadoSalida(item.id, 'Denegado')"
                    title="Denegar">
                    <i class="fa-solid fa-times" :style="getIconStyle('Denegado', item.estado)"></i>
                  </v-btn>
                </div>
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-tabs-window-item>

      <v-tabs-window-item value="area-comun">
        <v-data-table :items="areaComunItems" :items-per-page="10" class="custom-table-admin">
          <template #headers>
            <tr class="table-header">
              <th>Alumno</th>
              <th>Lugar</th>
              <th>Fecha</th>
              <th>Horario</th>
              <th>Acciones</th>
            </tr>
          </template>
          <template #item="{ item }">
            <tr>
              <td>{{ item.nombre_usuario }}</td>
              <td>{{ item.lugar }}</td>
              <td>{{ dateFormatV2(item.fecha) }}</td>
              <td>{{ item.horario }}</td>
              <td>
                <div class="d-flex" style="gap: 8px;">
                  <v-btn icon size="small" :class="getButtonClass('Aprobado', item.estado)"
                    :disabled="item.estado !== 'En revisión'" @click="actualizarEstadoAreaComun(item.id, 'Aprobado')"
                    title="Aprobar">
                    <i class="fa-solid fa-check" :style="getIconStyle('Aprobado', item.estado)"></i>
                  </v-btn>
                  <v-btn icon size="small" :class="getButtonClass('Denegado', item.estado)"
                    :disabled="item.estado !== 'En revisión'" @click="actualizarEstadoAreaComun(item.id, 'Denegado')"
                    title="Denegar">
                    <i class="fa-solid fa-times" :style="getIconStyle('Denegado', item.estado)"></i>
                  </v-btn>
                </div>
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-tabs-window-item>
    </v-tabs-window>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000" location="top">
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false"> Cerrar </v-btn>
      </template>
    </v-snackbar>
  </ContainerView>
</template>
<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { dateFormatDB, dateFormatV2 } from '@/util/functions.js'
import LoginService from '@/services/LoginService'
import PermisosService from '@/services/PermisosService'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import ContainerView from '@/components/layout/ContainerView.vue'

const solicitudes = ref([])
const areaComunItems = ref([])
const activeTab = ref('solicitud')
const adminTab = ref('permisos-salida')
const user = ref(LoginService.getCurrentUser())
const isAdmin = LoginService.isAdmin()
const form = reactive({
  rangoFechas: null,
  motivo: '',
  lugar: '',
  fechaAreaComun: null,
  horaInicio: '',
  horaFin: ''
})
const snackbar = reactive({ show: false, message: '', color: 'success' })
const siteOptions = [
  'Hall',
  'patio',
  'Lavandería',
  'Sala de cómputo'
]
const scheduleOptions = [
  '9:00 AM',
  '10:00 AM',
  '11:00 AM',
  '12:00 PM',
  '1:00 PM',
  '2:00 PM',
  '3:00 PM',
  '4:00 PM',
  '5:00 PM',
  '6:00 PM',
  '7:00 PM',
  '8:00 PM'
]

const horasFinDisponibles = computed(() => {
  if (!form.horaInicio) {
    return []
  }

  const indiceInicio = scheduleOptions.findIndex(hora => hora === form.horaInicio)
  if (indiceInicio === -1) {
    return []
  }

  return scheduleOptions.slice(indiceInicio + 1)
})

const resetHoraFin = () => {
  if (form.horaFin) {
    const indiceInicio = scheduleOptions.findIndex(hora => hora === form.horaInicio)
    const indiceFin = scheduleOptions.findIndex(hora => hora === form.horaFin)

    if (indiceFin <= indiceInicio) {
      form.horaFin = ''
    }
  }
}

onMounted(async () => {
  chooosePermisosDeSalida()
  chooosePermisosDeAreaComun()
})

const getStatusColor = (estado) => {
  switch (estado) {
    case 'Aprobado':
      return 'success'
    case 'Denegado':
      return 'error'
    case 'En revisión':
      return 'warning'
    default:
      return 'grey'
  }
}

const deleteReserva = (id) => {
  if (confirm('¿Estás seguro de que quieres eliminar esta reserva?')) {
    const index = solicitudes.value.findIndex((r) => r.id === id)
    if (index > -1) {
      solicitudes.value.splice(index, 1)
      snackbar.message = 'Reserva eliminada'
      snackbar.color = 'info'
      snackbar.show = true
    }
  }
}

async function actualizarEstadoSalida(id, estado) {
  try {
    await PermisosService.actualizarEstadoPermisoSalida(id, estado)
    const permiso = solicitudes.value.find(p => p.id === id)
    if (permiso) {
      permiso.estado = estado
    }
    snackbar.message = `Permiso de salida ${estado.toLowerCase()} exitosamente`
    snackbar.color = estado === 'Aprobado' ? 'success' : 'warning'
    snackbar.show = true
  } catch (error) {
    snackbar.message = 'Error al actualizar el estado del permiso'
    snackbar.color = 'error'
    snackbar.show = true
  }
}

async function actualizarEstadoAreaComun(id, estado) {
  try {
    await PermisosService.actualizarEstadoPermisoAreaComun(id, estado)
    const permiso = areaComunItems.value.find(p => p.id === id)
    if (permiso) {
      permiso.estado = estado
    }
    snackbar.message = `Permiso de área común ${estado.toLowerCase()} exitosamente`
    snackbar.color = estado === 'Aprobado' ? 'success' : 'warning'
    snackbar.show = true
  } catch (error) {
    snackbar.message = 'Error al actualizar el estado del permiso'
    snackbar.color = 'error'
    snackbar.show = true
  }
}

async function submitSolicitudVivienda() {
  if (!form.rangoFechas || !form.rangoFechas[0] || !form.rangoFechas[1] || !form.motivo) {
    snackbar.message = 'Por favor completa todos los campos'
    snackbar.color = 'error'
    snackbar.show = true
    return
  }

  const fechaDesde = form.rangoFechas[0] instanceof Date
    ? form.rangoFechas[0].toISOString().slice(0, 10)
    : form.rangoFechas[0]

  const fechaHasta = form.rangoFechas[1] instanceof Date
    ? form.rangoFechas[1].toISOString().slice(0, 10)
    : form.rangoFechas[1]

  const params = {
    id_usuario: user.value.id,
    fecha_salida: fechaDesde,
    fecha_regreso: fechaHasta,
    motivo: form.motivo,
  }
  await PermisosService.crearPermisoSalida(params)
  loadPermisosDeSalidaPorUsuario();
  form.rangoFechas = null
  form.motivo = ''
  snackbar.message = 'Solicitud enviada exitosamente'
  snackbar.color = 'success'
  snackbar.show = true
}

async function submitAreaComun() {
  if (!form.lugar || !form.fechaAreaComun || !form.horaInicio || !form.horaFin) {
    snackbar.message = 'Por favor completa todos los campos'
    snackbar.color = 'error'
    snackbar.show = true
    return
  }

  const fecha = form.fechaAreaComun instanceof Date
    ? form.fechaAreaComun.toISOString().slice(0, 10)
    : form.fechaAreaComun

  const horario = `${form.horaInicio} a ${form.horaFin}`

  const params = {
    id_usuario: user.value.id,
    lugar: form.lugar,
    fecha: fecha,
    horario: horario,
  }

  try {
    await PermisosService.crearPermisoAreaComun(params)
    loadPermisosDeAreaComunPorUsuario();

    form.lugar = ''
    form.fechaAreaComun = null
    form.horaInicio = ''
    form.horaFin = ''

    snackbar.message = 'Reserva enviada exitosamente'
    snackbar.color = 'success'
    snackbar.show = true
  } catch (error) {
    snackbar.message = 'Error al enviar la reserva'
    snackbar.color = 'error'
    snackbar.show = true
  }
}

async function loadPermisosDeSalidaPorUsuario() {
  const items = await PermisosService.obtenerPermisosDeSalidaPorUsuario(user.value.id)
  solicitudes.value = items.map((a) => ({
    estado: a.estado,
    fecha_regreso: a.fecha_regreso,
    fecha_salida: a.fecha_salida,
    id: a.id,
    id_usuario: a.id_usuario,
    motivo: a.descripcion || '',
  }))
}

async function loadPermisosDeSalida() {
  const items = await PermisosService.obtenerTodosLosPermisosDeSalida()
  solicitudes.value = items.map((a) => ({
    estado: a.estado,
    fecha_regreso: a.fecha_regreso,
    fecha_salida: a.fecha_salida,
    id: a.id,
    id_usuario: a.id_usuario,
    motivo: a.descripcion || '',
    nombre_usuario: a.nombre_usuario || 'Desconocido',
  }))
}

async function loadPermisosDeAreaComunPorUsuario() {
  const items = await PermisosService.obtenerPermisosDeAreaComunPorUsuario(user.value.id)
  areaComunItems.value = items.map((a) => ({
    estado: a.estado,
    fecha: a.fecha,
    horario: a.horario,
    id: a.id,
    id_usuario: a.id_usuario,
    lugar: a.lugar || '',
  }))
}

async function loadPermisosDeAreaComun() {
  const items = await PermisosService.obtenerTodosLosPermisosDeAreaComun()
  areaComunItems.value = items.map((a) => ({
    estado: a.estado,
    fecha: a.fecha,
    horario: a.horario,
    id: a.id,
    id_usuario: a.id_usuario,
    lugar: a.lugar || '',
    nombre_usuario: a.nombre_usuario || 'Desconocido',
  }))
}

function chooosePermisosDeSalida() {
  if (LoginService.isAdmin()) {
    loadPermisosDeSalida()
  } else {
    loadPermisosDeSalidaPorUsuario()
  }
}

function chooosePermisosDeAreaComun() {
  if (LoginService.isAdmin()) {
    loadPermisosDeAreaComun()
  } else {
    loadPermisosDeAreaComunPorUsuario()
  }
}

function getButtonClass(accion, estadoActual) {
  const baseClass = 'action-button'

  if (estadoActual === 'En revisión') {
    return `${baseClass} action-button-enabled`
  }

  if (estadoActual === accion) {
    return accion === 'Aprobado'
      ? `${baseClass} action-button-approved`
      : `${baseClass} action-button-denied`
  }

  return `${baseClass} action-button-disabled`
}

function getIconStyle(accion, estadoActual) {
  if (estadoActual === 'En revisión') {
    return 'color: #666666; font-size: 16px;'
  }

  if (estadoActual === accion) {
    return 'color: white; font-size: 16px;'
  }

  return 'color: #666666; font-size: 16px;'
}
</script>
<style scoped>
.custom-table-admin {
  margin-top: 32px;
}
.custom-table {
  border: none !important;
}
.custom-table thead {
  font-size: 18px;
  color: #163053;
  font-weight: 400;
}
.custom-table th {
  background-color: white !important;
}
.custom-table th:first-child {
  border-top-left-radius: 25px !important;
  border-bottom-left-radius: 25px !important;
}
.custom-table th:last-child {
  border-top-right-radius: 25px !important;
  border-bottom-right-radius: 25px !important;
}
.custom-table td {
  color: #525252;
  font-size: 16px;
  font-weight: 400;
  border: none !important;
}
.v-divider {
  border: 1px solid #D9D9D9 !important;
}
.v-data-table-footer {
  background-color: transparent !important;
  color: #525252 !important;
}

.n-data-table,
.n-data-table-tbody {
  background-color: transparent;
}

.text-title {
  color: white;
  font-size: 28px !important;
  font-size: larger;
  text-transform: none;
  font-family: 'Righteous', cursive;
}

.custom-tab {
  font-size: larger;
  color: #f5f5f5;
  text-transform: none;
  font-weight: 700;
  font-family: 'Righteous', cursive;
}

.active-tab-text {
  color: #A37801;
  font-weight: 600;
  padding-bottom: 4px;
}

.custom-select :deep(.v-field),
.custom-textarea :deep(.v-field) {
  border-radius: 8px;
  background-color: #f5f5f5;
}

.custom-select :deep(.v-field--focused),
.custom-textarea :deep(.v-field--focused) {
  background-color: white;
}

.custom-select :deep(.v-field--disabled) {
  background-color: #e0e0e0;
  opacity: 0.6;
}

.custom-alert :deep(.v-alert__content) {
  padding: 8px 0;
}

:deep(.v-tabs-slider) {
  background-color: #ffc107;
}

:deep(.v-tab--selected) {
  color: #A37801;
}

:deep(.dp__theme_light) {
  --dp-primary-color: #A80038;
  --dp-primary-text-color: #fff;
}

:deep(.dp__input) {
  height: 48px !important;
  border-radius: 8px;
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
}

:deep(.dp__input:focus) {
  background-color: white;
}

.custom-datepicker {
  border-radius: 8px;
  background-color: #f5f5f5;
}

.action-button {
  width: 36px !important;
  height: 36px !important;
  border-radius: 50% !important;
  min-width: 36px !important;
}

.action-button-enabled {
  background-color: white !important;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
}

.action-button-approved {
  background-color: #4caf50 !important;
  box-shadow: 0 2px 4px rgba(76, 175, 80, 0.3) !important;
}

.action-button-denied {
  background-color: #f44336 !important;
  box-shadow: 0 2px 4px rgba(244, 67, 54, 0.3) !important;
}

.action-button-disabled {
  background-color: #f5f5f5 !important;
  opacity: 0.6 !important;
}

.action-button:hover.action-button-enabled {
  background-color: #f5f5f5 !important;
  transform: scale(1.05);
  transition: all 0.2s ease;
}

.action-button:disabled {
  pointer-events: none;
}
</style>
