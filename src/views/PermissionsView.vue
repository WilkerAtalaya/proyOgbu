<template>
  <div class="pa-4">
    <v-row>
      <v-col cols="12" md="6">
        <v-card
          class="pa-4"
          style="border-radius: 16px; background-color: #BBBDA7"
        >
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
              <div class="mb-4">
                <p class="text-body-2 mb-4 text-grey-darken-2">
                  Registre el rango de días que estarás fuera de la vivienda universitaria:
                </p>
                <v-form @submit.prevent="submitRequest">
                  <div class="mb-3">
                    <label class="text-body-2 font-weight-medium mb-2 d-block"> Desde </label>
                    <v-select
                      v-model="form.desde"
                      :items="dateOptions"
                      variant="outlined"
                      density="comfortable"
                      hide-details
                      class="custom-select"
                    ></v-select>
                  </div>
                  <div class="mb-3">
                    <label class="text-body-2 font-weight-medium mb-2 d-block"> Hasta </label>
                    <v-select
                      v-model="form.hasta"
                      :items="dateOptions"
                      variant="outlined"
                      density="comfortable"
                      hide-details
                      class="custom-select"
                    ></v-select>
                  </div>
                  <div class="mb-4">
                    <label class="text-body-2 font-weight-medium mb-2 d-block"> Motivo </label>
                    <v-textarea
                      v-model="form.motivo"
                      variant="outlined"
                      rows="4"
                      hide-details
                      class="custom-textarea"
                    ></v-textarea>
                  </div>
                  <v-alert
                    type="warning"
                    variant="text"
                    class="mb-4 custom-alert"
                    density="compact"
                  >
                    <span class="text-caption text-black">
                      *Según el reglamento tu rango de salida de la ciudad universitaria tendrá a
                      ser revisada para su aprobación.
                    </span>
                  </v-alert>
                  <div class="d-flex justify-start">
                    <v-btn
                      type="submit"
                      color="#FFC107"
                      size="large"
                      style="
                        border-radius: 13px;
                        text-transform: none;
                        font-weight: 600;
                        color: #000;
                      "
                      min-width="100px"
                    >
                      Enviar
                    </v-btn>
                  </div>
                </v-form>
              </div>
            </v-tabs-window-item>
            <v-tabs-window-item value="area-comun">
               <div class="mb-4">
                <p class="text-body-2 mb-4 text-grey-darken-2">
                  Registre el lugar, fecha y horario que quieres reservar:
                </p>
                <v-form @submit.prevent="submitRequest">
                  <div class="mb-3">
                    <label class="text-body-2 font-weight-medium mb-2 d-block">Lugar</label>
                    <v-select
                      v-model="form.lugar"
                      :items="siteOptions"
                      variant="outlined"
                      density="comfortable"
                      hide-details
                      class="custom-select"
                    ></v-select>
                  </div>
                  <div class="mb-3">
                    <label class="text-body-2 font-weight-medium mb-2 d-block">Fecha</label>
                    <v-select
                      v-model="form.hasta"
                      :items="dateOptions"
                      variant="outlined"
                      density="comfortable"
                      hide-details
                      class="custom-select"
                    ></v-select>
                  </div>
                  <div class="mb-3">
                    <label class="text-body-2 font-weight-medium mb-2 d-block">Horario</label>
                    <v-select
                      v-model="form.horario"
                      :items="scheduleOptions"
                      variant="outlined"
                      density="comfortable"
                      hide-details
                      class="custom-select"
                    ></v-select>
                  </div>
                  <div class="d-flex justify-start">
                    <v-btn
                      type="submit"
                      color="#FFC107"
                      size="large"
                      style="
                        border-radius: 13px;
                        text-transform: none;
                        font-weight: 600;
                        color: #000;
                      "
                      min-width="100px"
                    >
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
        <v-card
          class="pa-4"
          style="border-radius: 16px; background-color: #BBBDA7"
        >
          <h3 class="mb-4 text-white text-title">Reservas</h3>
          <div v-if="solicitudes.length === 0" class="text-center pa-8">
            <v-icon size="48" color="grey-lighten-1" class="mb-3"> mdi-calendar-blank </v-icon>
            <p class="text-body-2 text-grey">No tienes reservas registradas</p>
          </div>
          <div v-else>
            <v-card
              v-if="activeTab === 'solicitud'"
              v-for="permiso in solicitudes"
              :key="permiso.id"
              class="mb-3 pa-3"
              variant="outlined"
              style="border: 1px solid #B8BAA3; border-radius: 12px;  background-color: #EAEBDF;"
            >
              <div class="d-flex justify-space-between align-center">
                <div>
                  <p class="text-body-1 font-weight-medium mb-1" style="color: #636363;">
                    {{ dateFormatV2(permiso.fecha_salida) }} al
                    {{ dateFormatV2(permiso.fecha_regreso) }}
                  </p>
                  <div class="d-flex flex-column gap-1">
                    <v-chip
                      :color="getStatusColor(permiso.estado)"
                      size="small"
                      variant="flat"
                      class="text-caption"
                    >
                      {{ permiso.estado }}
                    </v-chip>
                  </div>
                </div>
                <v-btn
                  icon
                  color="red"
                  variant="text"
                  size="small"
                  @click="deleteReserva(permiso.id)"
                >
                <i class="fa-solid fa-trash" style="color: #d32f2f; font-size: 20px;"></i>
                </v-btn>
              </div>
            </v-card>
            <v-card
              v-else
              v-for="areaComun in areaComunItems"
              :key="areaComun.id"
              class="mb-3 pa-3"
              variant="outlined"
              style="border: 1px solid #B8BAA3; border-radius: 12px;  background-color: #EAEBDF;"
            >
              <div class="d-flex justify-space-between align-center">
                <div>
                  <p class="text-body-1 font-weight-medium mb-1">
                   <span style="color:#636363">Lugar: </span>{{areaComun.lugar}}
                  </p>
                  <p class="text-body-1 font-weight-medium mb-1">
                    {{ dateFormatV2(areaComun.fecha) }} - {{ areaComun.horario }}
                  </p>
                  <div class="d-flex flex-column gap-1">
                    <v-chip
                      :color="getStatusColor(areaComun.estado)"
                      size="small"
                      variant="flat"
                      class="text-caption"
                    >
                      {{ areaComun.estado }}
                    </v-chip>
                  </div>
                </div>
                <v-btn
                  icon="mdi-close"
                  variant="text"
                  size="small"
                  color="red"
                  @click="deleteReserva(areaComun.id)"
                >
                </v-btn>
              </div>
            </v-card>
          </div>
        </v-card>
      </v-col>
    </v-row>
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false"> Cerrar </v-btn>
      </template>
    </v-snackbar>
  </div>
</template>
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { dateFormatDB, dateFormatV2 } from '@/util/functions.js'
import LoginService from '@/services/LoginService'
import PermisosService from '@/services/PermisosService'

const solicitudes = ref([])
const areaComunItems = ref([])
const activeTab = ref('solicitud')
const user = ref(LoginService.getCurrentUser())
const form = reactive({ desde: '', hasta: '', motivo: '' })
const snackbar = reactive({ show: false, message: '', color: 'success' })
const dateOptions = [
  '01/01/2025',
  '02/01/2025',
  '03/01/2025',
  '15/01/2025',
  '20/01/2025',
  '01/02/2025',
  '15/02/2025',
  '01/03/2025',
  '15/03/2025',
  '01/04/2025',
  '15/04/2025',
  '17/04/2025',
  '24/04/2025',
]
const siteOptions = [
  'Hall',
  'patio',
  'Lavandería',
  'Sala de cómputo'
]
const scheduleOptions = [
  '9:00 a 10:00',
  '10:00 a 11:00 ',
  '11:00 a 12:00',
  '12:00 a 13:00',
  '14:00 a 15:00',
  '15:00 a 16:00'
]

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

async function submitRequest() {
  if (!form.desde || !form.hasta || !form.motivo) {
    snackbar.message = 'Por favor completa todos los campos'
    snackbar.color = 'error'
    snackbar.show = true
    return
  }
  const params = {
    id_usuario: user.value.id,
    fecha_salida: dateFormatDB(form.desde),
    fecha_regreso: dateFormatDB(form.hasta),
    motivo: form.motivo,
  }
  await PermisosService.crearPermisoSalida(params)
  params.estado = 'En revisión'
  solicitudes.value.push(params)
  form.desde = ''
  form.hasta = ''
  form.motivo = ''
  snackbar.message = 'Solicitud enviada exitosamente'
  snackbar.color = 'success'
  snackbar.show = true
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
</script>
<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Righteous&display=swap');

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

.custom-alert :deep(.v-alert__content) {
  padding: 8px 0;
}
.text-title{
  font-size: 28px !important;
  font-size: larger;
  color: #f5f5f5;
  text-transform: none;
  font-family: 'Righteous', cursive;
}

:deep(.v-tabs-slider) {
  background-color: #ffc107;
}

:deep(.v-tab--selected) {
  color:  #A37801;
}
</style>
