<template>
  <ContainerView>
    <v-tabs v-model="tab" align-tabs="start" color="#A37801">
      <v-tab :value="1" class="custom-tab"><h3 class="mb-4 text-title">{{ isAdmin ? 'Act. Aprobadas' : 'Actividades' }}</h3></v-tab>
      <v-tab :value="2" class="custom-tab"><h3  class="mb-4 text-title">{{ isAdmin ? 'Solicitudes' : 'Mis Solicitudes' }}</h3></v-tab>
      <v-spacer></v-spacer>
      <v-btn variant="outlined" class="mb-6 custom-button" @click="openModalNuevo">
        <span v-if="isAdmin">Agregar actividad</span>
        <span v-else>Solicitar una actividad</span>
      </v-btn>
    </v-tabs>
    <v-tabs-window v-model="tab">
      <v-tabs-window-item :value="1">
        <v-container fluid>
          <div v-for="(actividad, index) in actividades" :key="index" class="actividad-card">
            <div class="info">
              <div class="titulo-actividad">
                📌 <strong>{{ actividad.titulo }}</strong>
                <div class="fecha">({{ actividad.fecha }})</div>
              </div>
              <div class="descripcion">
                <small>Descripción</small><br />
                {{ actividad.descripcion || 'Sin descripción' }}
              </div>
            </div>
            <div class="tipo">{{ actividad.tipo.toUpperCase() }}</div>
            <div class="accion">
              <n-button style="background-color:#ffc107;" type="warning" @click="abrirDetalleActividad(actividad)">{{ isAdmin ? 'Ver detalle' : 'Acceder al formulario' }}</n-button>
            </div>
          </div>
        </v-container>
      </v-tabs-window-item>
      <v-tabs-window-item :value="2">
        <v-data-table :items="items" :items-per-page="10" class="custom-table">
          <template #headers>
            <tr class="table-header">
              <th>Código</th>
              <th>Título</th>
              <th>Fecha</th>
              <th>Tipo</th>
              <th>Estado</th>
              <th>Acción</th>
            </tr>
          </template>
          <template #item="{ item }">
            <tr>
              <td>{{ item.codigo }}</td>
              <td>{{ item.titulo }}</td>
              <td>{{ item.fecha }}</td>
              <td>{{ item.tipo }}</td>
              <td>{{ item.estado || 'Pendiente' }}</td>
              <td>
                <button
                  @click="openModalSolicitudes(item)"
                  style="background: none; border: none; cursor: pointer;"
                  title="Ver detalle"
                >
                  <i class="fa-solid fa-eye" style="color: #1976d2; font-size: 20px;"></i>
                </button>
              </td>
            </tr>
          </template>
        </v-data-table>
      </v-tabs-window-item>
    </v-tabs-window>
  </ContainerView>
  <ModalActividades :type="modalType" v-model="showModal" :item="selectedItem" :user="user" @actividad-creada="onActividadCreada" />
  <ModalMisSolicitudes v-model="showModalSolicitudes" :item="selectedItem" :user="user" />
  <ModalDetalleActividad v-model="showModalDetalle" :actividad="selectedActividad" :is-admin="isAdmin" @inscripcion-exitosa="onInscripcionExitosa" />
  <ModalDetalleSolicitud v-model="showModalDetalleSolicitud" :solicitud="selectedSolicitud" :is-admin="isAdmin" @estado-actualizado="onEstadoActualizado" />
</template>
<script setup>
import { NButton } from 'naive-ui'
import { ref, reactive, onMounted } from 'vue'
import LoginService from '@/services/LoginService'
import ActividadesService from '@/services/ActividadesService'
import ModalActividades from './modal/ModalActividades.vue'
import ModalMisSolicitudes from './modal/ModalMisSolicitudes.vue'
import ModalDetalleActividad from './modal/ModalDetalleActividad.vue'
import ModalDetalleSolicitud from './modal/ModalDetalleSolicitud.vue'
import ContainerView from '@/components/layout/ContainerView.vue'

const tab = ref(1)
const items = ref([])
const actividades = ref([])
const showModal = ref(false)
const modalType = ref('actividad')
const showModalSolicitudes = ref(false)
const showModalDetalle = ref(false)
const showModalDetalleSolicitud = ref(false)
const selectedItem = ref(null)
const selectedActividad = ref(null)
const selectedSolicitud = ref(null)
const user = ref(LoginService.getCurrentUser())
const isAdmin = LoginService.isAdmin()

onMounted(async () => {
  await Promise.all([loadActividadesAprobadas(), chooseSolicitudes()])
})

function abrirDetalleActividad(actividad) {
  selectedActividad.value = {
    id: actividad.id || extractIdFromCodigo(actividad.codigo),
    titulo: actividad.titulo,
    tipo: actividad.tipo,
    fecha_actividad: actividad.fecha,
    descripcion: actividad.descripcion,
    stock: actividad.stock,
    cupos_restantes: actividad.cupos_restantes || actividad.stock,
    archivo: actividad.archivo
  }
  showModalDetalle.value = true
}

function extractIdFromCodigo(codigo) {
  return parseInt(codigo.split('-')[1]) || 0
}

function onInscripcionExitosa() {
  loadActividadesAprobadas()
  showModalDetalle.value = false
}

async function onActividadCreada({ esAdmin }) {
  await Promise.all([loadActividadesAprobadas(), chooseSolicitudes()])
  
  if (esAdmin) {
    tab.value = 1
  } else {
    tab.value = 2
  }
}

async function onEstadoActualizado() {
  await Promise.all([loadActividadesAprobadas(), chooseSolicitudes()])
}

function openModalNuevo( type = 'actividad', actividad = null) {
  const user = LoginService.getCurrentUser()
  if (actividad) {
    selectedItem.value = {
      tipo: actividad.tipo,
      titulo: actividad.titulo,
      descripcion: actividad.descripcion,
      fecha_actividad: actividad.fecha_actividad,
      stock: actividad.stock,
      attend: false
    }
  } else {
    selectedItem.value = {
    numero: '',
    asunto: '',
    motivo: '',
    fecha: '',
    estado: '',
    descripcion: '',
    attend : false
  }
  }
  modalType.value = type
  showModal.value = true
}

function openModalSolicitudes(item) {
  selectedSolicitud.value = {
    id: item.id,
    titulo: item.titulo,
    tipo: item.tipo,
    fecha_actividad: item.fecha,
    fecha_solicitud: item.fecha_solicitud || item.fecha,
    descripcion: item.descripcion,
    stock: item.stock,
    estado: item.estado,
    archivo: item.archivo
  }
  showModalDetalleSolicitud.value = true
}

function chooseSolicitudes() {
  if (LoginService.isAdmin()) {
    loadSolicitudes()
  } else {
    loadSolicitudesPorUsuario()
  }
}

async function loadSolicitudesPorUsuario() {
  try {
    const activities = await ActividadesService.obtenerActividadesPorUsuario(user.value.id)
    items.value = activities.map((a) => ({
      id: a.id,
      codigo: `UNMSM-${a.id}`,
      titulo: a.titulo,
      fecha: a.fecha_actividad,
      fecha_solicitud: a.fecha_solicitud,
      resumen: a.descripcion,
      descripcion: a.descripcion,
      tipo: a.tipo,
      stock: a.stock,
      estado: a.estado || 'Pendiente',
      archivo: a.archivo,
    }))
  } catch (error) {
    console.error(error)
  }
}

async function loadSolicitudes() {
  try {
    const activities = await ActividadesService.obtenerTodas()
    items.value = activities.map((a) => ({
      id: a.id,
      codigo: `UNMSM-${a.id}`,
      titulo: a.titulo,
      fecha: a.fecha_actividad,
      fecha_solicitud: a.fecha_solicitud,
      resumen: a.descripcion,
      descripcion: a.descripcion,
      tipo: a.tipo,
      stock: a.stock,
      estado: a.estado || 'Pendiente',
      archivo: a.archivo,
    }))
  } catch (error) {
    console.error(error)
  }
}

async function loadActividadesAprobadas() {
  try {
    const activities = await ActividadesService.obtenerActividadesAprobadas()
    actividades.value = activities.map((a) => ({
      id: a.id,
      codigo: `UNMSM-${a.id}`,
      fecha: a.fecha_actividad,
      descripcion: a.descripcion,
      titulo: a.titulo,
      tipo: a.tipo.toUpperCase(),
      stock: a.stock,
      cupos_restantes: a.cupos_restantes,
      archivo: a.archivo,
    }))
  } catch (error) {
    console.error(error)
  }
}
</script>

<style scoped>
.custom-tab {
  font-size: larger;
  color: #f5f5f5;
  font-size: 20px;
  font-weight: 700;
  font-family: 'Righteous', cursive;
}

.actividades-wrapper {
  display: flex;
  gap: 20px;
  padding: 30px;
  background: url('/ruta/a/tu/fondo.png') no-repeat center;
  background-size: cover;
  min-height: 100vh;
  position: relative;
}

.perfil {
  position: absolute;
  top: 20px;
  left: 20px;
  background: #1e1e1e;
  color: white;
  padding: 8px 16px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.estado {
  width: 10px;
  height: 10px;
  background: limegreen;
  border-radius: 50%;
}

.sidebar {
  width: 220px;
  margin-top: 100px;
}

.contenido {
  flex: 1;
  background: #BBBDA7;
  padding: 20px;
  border-radius: 20px;
  margin-left: auto;
}

.titulo {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
}

.titulo .resaltado {
  color: #b28700;
  margin-right: 10px;
}

.actividad-card {
  display: flex;
  align-items: center;
  background: #f5f5f5;
  border-radius: 12px;
  padding: 15px 20px;
  margin-bottom: 16px;
  justify-content: space-between;
  box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
}

.info {
  flex: 1;
}

.titulo-actividad {
  color: #163053;
  font-size: 16px;
  font-weight: bold;
}

.fecha {
  font-size: 13px;
  color: #555;
}

.descripcion {
  font-size: 14px;
  margin-top: 5px;
}

.tipo {
  font-size: 12px;
  text-align: center;
  color: #555;
  width: 100px;
}

.accion {
  min-width: 160px;
  display: flex;
  justify-content: flex-end;
}

.custom-table {
  margin-top: 32px;
}

.custom-table :deep(.v-data-table__wrapper) {
  border-radius: 12px;
}

.custom-table :deep(.v-data-table-header) {
  background-color: #f5f5f5;
}

.custom-table :deep(.v-data-table-header__content) {
  font-weight: 600;
  color: #424242;
}

.custom-table :deep(.v-data-table__td) {
  padding: 16px 12px;
  border-bottom: 1px solid #e0e0e0;
}

.custom-table :deep(.v-data-table__th) {
  padding: 16px 12px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #616161;
}

.custom-table :deep(tbody tr:last-child td) {
  border-bottom: none;
}
.text-title{
  font-size: 28px !important;
  font-size: larger;
  text-transform: none;
  font-family: 'Righteous', cursive;
}
.custom-button {
  background-color: #53696D !important;
  border-radius: 25px !important;
  border: none !important;
  padding: 16px 24px !important;
  height: auto !important;
  margin: 0 !important;
}

.custom-button span {
  color: white !important;
}
</style>
