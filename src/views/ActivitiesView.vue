<template>
  <ContainerView>
    <v-tabs v-model="tab" align-tabs="start" color="#A37801">
      <v-tab :value="1" class="custom-tab">
        <h3 class="mb-4 text-title">Actividades</h3>
      </v-tab>
      <v-tab v-if="!isAdmin" :value="2" class="custom-tab">
        <h3 class="mb-4 text-title">Act. Inscritas</h3>
      </v-tab>
      <v-tab :value="3" class="custom-tab">
        <h3 class="mb-4 text-title">{{ isAdmin ? 'Solicitudes' : 'Mis Solicitudes' }}</h3>
      </v-tab>
      <v-spacer></v-spacer>
      <v-btn variant="outlined" class="mb-6 custom-button" @click="openModalNuevo">
        <span v-if="isAdmin">Agregar actividad</span>
        <span v-else>Solicitar una actividad</span>
      </v-btn>
    </v-tabs>
    <v-tabs-window v-model="tab">
      <v-tabs-window-item :value="1">
        <v-container fluid>
          <div class="actividades-grid">
            <div v-for="(actividad, index) in actividades" :key="index" class="actividad-card">
              <div class="card-header">
                <div v-if="actividad.archivo" class="card-image" @click="handleFileClick(actividad.archivo)"
                  style="cursor: pointer;">
                  <n-image v-if="isImageFile(actividad.archivo)" :src="getImageUrl(actividad.archivo)"
                    :alt="actividad.titulo" object-fit="cover"
                    :style="{ width: '100%', height: '160px', borderRadius: '0' }" :preview-disabled="false" />
                  <div v-else-if="isPDFFile(actividad.archivo)" class="file-placeholder pdf-file">
                    <i class="fa-solid fa-file-pdf" style="font-size: 48px; color: #d32f2f;"></i>
                    <span class="file-label">PDF</span>
                  </div>
                  <div v-else-if="isWordFile(actividad.archivo)" class="file-placeholder word-file">
                    <i class="fa-solid fa-file-word" style="font-size: 48px; color: #1976d2;"></i>
                    <span class="file-label">WORD</span>
                  </div>
                  <div v-else class="file-placeholder generic-file">
                    <i class="fa-solid fa-file" style="font-size: 48px; color: #757575;"></i>
                    <span class="file-label">ARCHIVO</span>
                  </div>
                </div>
                <div v-else class="image-placeholder">
                  <i class="fa-solid fa-calendar-days" style="font-size: 48px; color: #53696D;"></i>
                </div>
                <div class="tipo-badge">{{ actividad.tipo }}</div>
              </div>

              <div class="card-content">
                <h3 class="titulo-actividad">{{ actividad.titulo }}</h3>

                <div class="info-container">
                  <div class="fecha-card">
                    <div class="fecha-icon">
                      <i class="fa-solid fa-calendar" style="color: white; font-size: 18px;"></i>
                    </div>
                    <div class="fecha-details">
                      <span class="fecha-dia">{{ getDiaFecha(actividad.fecha) }}</span>
                      <span class="fecha-mes">{{ getMesFecha(actividad.fecha) }}</span>
                      <span class="fecha-hora">{{ getHoraFecha(actividad.fecha) }}</span>
                    </div>
                  </div>

                  <div class="cupos-card" :class="{ 'cupos-criticos': actividad.cupos_restantes < 10 }">
                    <div class="cupos-icon">
                      <i class="fa-solid fa-users" style="color: white; font-size: 18px;"></i>
                    </div>
                    <div class="cupos-details">
                      <span class="cupos-numero">{{ actividad.cupos_restantes || actividad.stock }}</span>
                      <span class="cupos-texto">cupos</span>
                      <span class="cupos-total">de {{ actividad.stock }}</span>
                    </div>
                  </div>
                </div>

                <p class="descripcion-actividad">
                  {{ actividad.descripcion || 'Sin descripción disponible' }}
                </p>
              </div>

              <div class="card-footer">
                <v-btn v-if="!isAdmin" @click="inscribirseDirecto(actividad)" color="#53696D" variant="flat" block
                  class="btn-inscribirse"
                  :disabled="(actividad.cupos_restantes || actividad.stock) <= 0 || inscribiendose[actividad.id]"
                  :loading="inscribiendose[actividad.id]">
                  <template v-if="(actividad.cupos_restantes || actividad.stock) <= 0">
                    Sin cupos disponibles
                  </template>
                  <template v-else>
                    <i class="fa-solid fa-user-plus" style="margin-right: 8px; font-size: 16px;"></i>
                    Inscribirse
                  </template>
                </v-btn>

                <v-btn v-else @click="abrirDetalleActividad(actividad)" color="#A37801" variant="outlined" block
                  class="btn-ver-detalle">
                  <i class="fa-solid fa-eye" style="margin-right: 8px; font-size: 16px;"></i>
                  Ver detalle
                </v-btn>

                <v-btn v-if="isAdmin" @click="abrirModalInscritos(actividad)" color="#53696D" variant="outlined" block
                  class="btn-ver-inscritos" style="margin-top: 8px;">
                  <i class="fa-solid fa-users" style="margin-right: 8px; font-size: 16px;"></i>
                  Ver Inscritos
                </v-btn>

                <v-btn v-if="!isAdmin" @click="abrirDetalleActividad(actividad)" variant="text" size="small"
                  class="btn-mas-info" color="#53696D">
                  <i class="fa-solid fa-info-circle" style="margin-right: 4px; font-size: 14px;"></i>
                  Más información
                </v-btn>
              </div>
            </div>
          </div>
        </v-container>
      </v-tabs-window-item>
      <v-tabs-window-item v-if="!isAdmin" :value="2">
        <v-container fluid>
          <div class="actividades-grid">
            <div v-for="(actividad, index) in actividadesInscritas" :key="index" class="actividad-card inscrita-card">
              <div class="card-header">
                <div v-if="actividad.archivo" class="card-image" @click="handleFileClick(actividad.archivo)"
                  style="cursor: pointer;">
                  <n-image v-if="isImageFile(actividad.archivo)" :src="getImageUrl(actividad.archivo)" :alt="actividad.titulo"
                    object-fit="cover" :style="{ width: '100%', height: '160px', borderRadius: '0' }"
                    :preview-disabled="false" />
                  <div v-else-if="isPDFFile(actividad.archivo)" class="file-placeholder pdf-file">
                    <i class="fa-solid fa-file-pdf" style="font-size: 48px; color: #d32f2f;"></i>
                    <span class="file-label">PDF</span>
                  </div>
                  <div v-else-if="isWordFile(actividad.archivo)" class="file-placeholder word-file">
                    <i class="fa-solid fa-file-word" style="font-size: 48px; color: #1976d2;"></i>
                    <span class="file-label">WORD</span>
                  </div>
                  <div v-else class="file-placeholder generic-file">
                    <i class="fa-solid fa-file" style="font-size: 48px; color: #757575;"></i>
                    <span class="file-label">ARCHIVO</span>
                  </div>
                </div>
                <div v-else class="image-placeholder">
                  <i class="fa-solid fa-calendar-days" style="font-size: 48px; color: #53696D;"></i>
                </div>
                <div class="tipo-badge">{{ actividad.tipo }}</div>
                <div v-if="actividad.estado_actividad === 'Cancelado' || actividad.estado_actividad === 'Finalizado'"
                  class="estado-badge" :class="getEstadoClass(actividad.estado_actividad)">
                  {{ actividad.estado_actividad }}
                </div>
              </div>

              <div class="card-content">
                <h3 class="titulo-actividad">{{ actividad.titulo }}</h3>

                <div class="info-container">
                  <div class="fecha-card">
                    <div class="fecha-icon">
                      <i class="fa-solid fa-calendar" style="color: white; font-size: 18px;"></i>
                    </div>
                    <div class="fecha-details">
                      <span class="fecha-dia">{{ getDiaFecha(actividad.fecha_actividad) }}</span>
                      <span class="fecha-mes">{{ getMesFecha(actividad.fecha_actividad) }}</span>
                      <span class="fecha-hora">{{ getHoraFecha(actividad.fecha_actividad) }}</span>
                    </div>
                  </div>

                  <div class="registro-card">
                    <div class="registro-icon">
                      <i class="fa-solid fa-user-check" style="color: white; font-size: 18px;"></i>
                    </div>
                    <div class="registro-details">
                      <span class="registro-texto">Inscrito</span>
                      <span class="registro-fecha">{{ formatFechaRegistro(actividad.fecha_registro) }}</span>
                    </div>
                  </div>
                </div>

                <p class="descripcion-actividad">
                  {{ actividad.descripcion || 'Sin descripción disponible' }}
                </p>
              </div>

              <div class="card-footer">
                <v-btn @click="abrirDetalleActividadInscrita(actividad)" variant="outlined" size="small"
                  class="btn-mas-info-inscrita" color="#53696D" block>
                  <i class="fa-solid fa-info-circle" style="margin-right: 4px; font-size: 14px;"></i>
                  Más información
                </v-btn>
              </div>
            </div>
          </div>
        </v-container>
      </v-tabs-window-item>
      <v-tabs-window-item :value="3">
        <v-container fluid v-if="isAdmin">
          <div class="dashboard-cards mb-6 mt-6">
            <div class="stat-card">
              <div class="stat-icon blue">
                <i class="fas fa-calendar-alt"></i>
              </div>
              <div class="stat-content">
                <p class="stat-label">Total Solicitudes</p>
                <p class="stat-value">{{ items.length }}</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon yellow">
                <i class="fas fa-clock"></i>
              </div>
              <div class="stat-content">
                <p class="stat-label">Pendientes</p>
                <p class="stat-value">{{items.filter(s => s.estado === 'Pendiente').length}}</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon green">
                <i class="fas fa-check"></i>
              </div>
              <div class="stat-content">
                <p class="stat-label">Aprobadas</p>
                <p class="stat-value">{{items.filter(s => s.estado === 'Aprobado').length}}</p>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon red">
                <i class="fas fa-times"></i>
              </div>
              <div class="stat-content">
                <p class="stat-label">Canceladas</p>
                <p class="stat-value">{{items.filter(s => s.estado === 'Cancelado').length}}</p>
              </div>
            </div>
          </div>

          <div class="search-filter-section">
            <div class="search-input-container">
              <i class="fas fa-search search-icon"></i>
              <input type="text" placeholder="Buscar por título o usuario..." class="search-input"
                v-model="searchTermActividades" />
            </div>
            <div class="filter-tabs">
              <button v-for="estado in filtrosActividades" :key="estado.value"
                @click="filtroEstadoActividades = estado.value"
                :class="['filter-tab', { 'active': filtroEstadoActividades === estado.value }]">
                {{ estado.label }}
              </button>
            </div>
          </div>

          <div class="permisos-table-container">
            <div class="table-wrapper">
              <table class="permisos-table">
                <thead>
                  <tr>
                    <th>Solicitante</th>
                    <th>Actividad</th>
                    <th>Tipo y Fecha</th>
                    <th>Cupos</th>
                    <th>Estado</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="solicitud in solicitudesPaginadas" :key="solicitud.id" class="table-row">
                    <td>
                      <div class="employee-info">
                        <div class="avatar">
                          {{ getInitials(solicitud.nombre_usuario) }}
                        </div>
                        <div class="employee-details">
                          <div class="employee-name">{{ solicitud.nombre_usuario }}</div>
                          <div class="employee-id">ID: {{ solicitud.id }}</div>
                        </div>
                      </div>
                    </td>
                    <td>
                      <div class="actividad-info">
                        <div class="actividad-titulo">{{ solicitud.titulo }}</div>
                        <div class="actividad-descripcion" :title="solicitud.descripcion">
                          {{ solicitud.descripcion?.substring(0, 50) }}{{ solicitud.descripcion?.length > 50 ? '...' :
                          '' }}
                        </div>
                        <div class="fecha-solicitud">
                          Solicitado: {{ formatFechaRegistro(solicitud.fecha_solicitud) }}
                        </div>
                      </div>
                    </td>
                    <td>
                      <div class="tipo-fecha-info">
                        <div class="tipo-actividad">
                          <i class="fas fa-tag" style="color: #53696D; margin-right: 8px;"></i>
                          {{ solicitud.tipo }}
                        </div>
                        <div class="fecha-actividad">
                          <i class="fas fa-calendar" style="color: #A37801; margin-right: 8px;"></i>
                          {{ formatFechaActividad(solicitud.fecha_actividad) }}
                        </div>
                      </div>
                    </td>
                    <td>
                      <div class="cupos-info">
                        <i class="fas fa-users" style="color: #53696D; margin-right: 8px;"></i>
                        {{ solicitud.stock }} cupos
                      </div>
                    </td>
                    <td>
                      <span :class="['status-badge', getStatusClassActividad(solicitud.estado)]">
                        <i :class="getStatusIconActividad(solicitud.estado)"></i>
                        {{ solicitud.estado }}
                      </span>
                    </td>
                    <td>
                      <div class="actions">
                        <button v-if="solicitud.archivo" @click="downloadFile(solicitud.archivo)"
                          class="action-btn download" title="Descargar archivo">
                          <i class="fas fa-download"></i>
                        </button>
                        <button @click="openModalSolicitudes(solicitud)" class="action-btn view" title="Ver detalles">
                          <i class="fas fa-eye"></i>
                        </button>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="pagination-container">
            <div class="pagination-info">
              <span>Mostrar</span>
              <select v-model="itemsPerPageActividades" class="items-select">
                <option value="5">5</option>
                <option value="10">10</option>
                <option value="25">25</option>
                <option value="50">50</option>
              </select>
              <span>de {{ totalFilteredItemsActividades }} resultados</span>
            </div>
            <div class="pagination-controls">
              <button @click="currentPageActividades = Math.max(currentPageActividades - 1, 1)"
                :disabled="currentPageActividades === 1" class="pagination-btn">
                <i class="fas fa-chevron-left"></i>
              </button>
              <span class="pagination-text">
                Página {{ currentPageActividades }} de {{ totalPagesActividades }}
              </span>
              <button @click="currentPageActividades = Math.min(currentPageActividades + 1, totalPagesActividades)"
                :disabled="currentPageActividades === totalPagesActividades" class="pagination-btn">
                <i class="fas fa-chevron-right"></i>
              </button>
            </div>
          </div>
        </v-container>

        <v-container fluid v-else>
          <div class="actividades-grid">
            <div v-for="(solicitud, index) in solicitudesFiltradas" :key="index" class="actividad-card solicitud-card">
              <div class="card-header">
                <div v-if="solicitud.archivo" class="card-image" @click="handleFileClick(solicitud.archivo)"
                  style="cursor: pointer;">
                  <n-image v-if="isImageFile(solicitud.archivo)" :src="getImageUrl(solicitud.archivo)"
                    :alt="solicitud.titulo" object-fit="cover"
                    :style="{ width: '100%', height: '160px', borderRadius: '0' }" :preview-disabled="false" />
                  <div v-else-if="isPDFFile(solicitud.archivo)" class="file-placeholder pdf-file">
                    <i class="fa-solid fa-file-pdf" style="font-size: 48px; color: #d32f2f;"></i>
                    <span class="file-label">PDF</span>
                  </div>
                  <div v-else-if="isWordFile(solicitud.archivo)" class="file-placeholder word-file">
                    <i class="fa-solid fa-file-word" style="font-size: 48px; color: #1976d2;"></i>
                    <span class="file-label">WORD</span>
                  </div>
                  <div v-else class="file-placeholder generic-file">
                    <i class="fa-solid fa-file" style="font-size: 48px; color: #757575;"></i>
                    <span class="file-label">ARCHIVO</span>
                  </div>
                </div>
                <div v-else class="image-placeholder">
                  <i class="fa-solid fa-calendar-plus" style="font-size: 48px; color: #53696D;"></i>
                </div>
                <div class="tipo-badge">{{ solicitud.tipo }}</div>
                <div class="estado-solicitud-badge" :class="getEstadoSolicitudClass(solicitud.estado)">
                  {{ solicitud.estado }}
                </div>
              </div>

              <div class="card-content">
                <h3 class="titulo-actividad">{{ solicitud.titulo }}</h3>

                <div class="info-container">
                  <div class="solicitud-card-info">
                    <div class="solicitud-icon">
                      <i class="fa-solid fa-calendar-check" style="color: white; font-size: 18px;"></i>
                    </div>
                    <div class="solicitud-details">
                      <span class="solicitud-texto">Solicitado</span>
                      <span class="solicitud-fecha">{{ formatFechaRegistro(solicitud.fecha_solicitud) }}</span>
                    </div>
                  </div>

                  <div class="cupos-card">
                    <div class="cupos-icon">
                      <i class="fa-solid fa-users" style="color: white; font-size: 18px;"></i>
                    </div>
                    <div class="cupos-details">
                      <span class="cupos-numero">{{ solicitud.stock }}</span>
                      <span class="cupos-texto">cupos</span>
                      <span class="cupos-total">solicitados</span>
                    </div>
                  </div>
                </div>

                <div class="info-adicional">
                  <div class="fecha-actividad-solicitud">
                    <i class="fa-solid fa-calendar" style="color: #A37801; margin-right: 8px;"></i>
                    <span>Fecha programada: {{ formatFechaActividad(solicitud.fecha_actividad) }}</span>
                  </div>
                  
                  <div v-if="solicitud.motivo_cancelacion" class="motivo-cancelacion">
                    <i class="fa-solid fa-exclamation-triangle" style="margin-right: 8px;"></i>
                    <span>{{ solicitud.motivo_cancelacion }}</span>
                  </div>
                </div>

                <p class="descripcion-actividad">
                  {{ solicitud.descripcion || 'Sin descripción disponible' }}
                </p>

              </div>

              <div class="card-footer">
                <v-btn @click="openModalSolicitudes(solicitud)" color="#A37801" variant="outlined" block
                  class="btn-ver-detalle">
                  <i class="fa-solid fa-eye" style="margin-right: 8px; font-size: 16px;"></i>
                  Ver detalle
                </v-btn>

                <v-btn v-if="solicitud.archivo" @click="handleFileClick(solicitud.archivo)" variant="text" size="small"
                  class="btn-mas-info" color="#53696D">
                  <i class="fa-solid fa-download" style="margin-right: 4px; font-size: 14px;"></i>
                  Ver archivo adjunto
                </v-btn>
              </div>
            </div>
          </div>
        </v-container>
      </v-tabs-window-item>
    </v-tabs-window>
  </ContainerView>
  <ModalActividades :type="modalType" v-model="showModal" :item="selectedItem" :user="user"
    @actividad-creada="onActividadCreada" @mostrar-notificacion="onMostrarNotificacion" />
  <ModalDetalleActividad v-model="showModalDetalle" :actividad="selectedActividad" :is-admin="isAdmin"
    :es-actividad-inscrita="esModalActividadInscrita" @inscripcion-exitosa="onInscripcionExitosa"
    @mostrar-notificacion="onMostrarNotificacion" />
  <ModalMisSolicitudes v-model="showModalSolicitudes" :item="selectedItem" :user="user" />
  <ModalDetalleSolicitud v-model="showModalDetalleSolicitud" :solicitud="selectedSolicitud" :is-admin="isAdmin"
    @estado-actualizado="onEstadoActualizado" />
  <ModalInscritosActividad v-model="showModalInscritos" :actividad="selectedActividadInscritos" />

  <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="4000" location="top">
    {{ snackbar.message }}
    <template v-slot:actions>
      <v-btn variant="text" @click="snackbar.show = false">
        Cerrar
      </v-btn>
    </template>
  </v-snackbar>
</template>
<script setup>
import { NImage } from 'naive-ui'
import { ref, onMounted, computed } from 'vue'
import LoginService from '@/services/LoginService'
import ActividadesService from '@/services/ActividadesService'
import ModalActividades from './modal/ModalActividades.vue'
import ModalMisSolicitudes from './modal/ModalMisSolicitudes.vue'
import ModalDetalleActividad from './modal/ModalDetalleActividad.vue'
import ModalDetalleSolicitud from './modal/ModalDetalleSolicitud.vue'
import ModalInscritosActividad from './modal/ModalInscritosActividad.vue'
import ContainerView from '@/components/layout/ContainerView.vue'

const tab = ref(1)
const items = ref([])
const actividades = ref([])
const actividadesInscritas = ref([])
const showModal = ref(false)
const modalType = ref('actividad')
const showModalSolicitudes = ref(false)
const showModalDetalle = ref(false)
const showModalDetalleSolicitud = ref(false)
const showModalInscritos = ref(false)
const selectedItem = ref(null)
const selectedActividad = ref(null)
const selectedSolicitud = ref(null)
const selectedActividadInscritos = ref(null)
const user = ref(LoginService.getCurrentUser())
const isAdmin = LoginService.isAdmin()
const inscribiendose = ref({})
const esModalActividadInscrita = ref(false)
const filtroEstado = ref('Todos')

const searchTermActividades = ref('')
const filtroEstadoActividades = ref('Todos')
const currentPageActividades = ref(1)
const itemsPerPageActividades = ref(10)

const filtrosActividades = [
  { label: 'Todos', value: 'Todos' },
  { label: 'Pendientes', value: 'Pendiente' },
  { label: 'Aprobadas', value: 'Aprobado' },
  { label: 'Finalizadas', value: 'Finalizado' },
  { label: 'Canceladas', value: 'Cancelado' }
]

const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
})

const solicitudesFiltradas = computed(() => {
  if (!isAdmin || filtroEstado.value === 'Todos') {
    return items.value
  }

  return items.value.filter(solicitud => {
    const estado = solicitud.estado || 'Pendiente'
    return estado.toLowerCase() === filtroEstado.value.toLowerCase()
  })
})

const solicitudesFiltradasAdmin = computed(() => {
  let filtered = items.value

  if (searchTermActividades.value) {
    const searchTerm = searchTermActividades.value.toLowerCase()
    filtered = filtered.filter(solicitud =>
      solicitud.titulo?.toLowerCase().includes(searchTerm) ||
      solicitud.nombre_usuario?.toLowerCase().includes(searchTerm) ||
      solicitud.descripcion?.toLowerCase().includes(searchTerm)
    )
  }

  if (filtroEstadoActividades.value !== 'Todos') {
    filtered = filtered.filter(solicitud => {
      const estado = solicitud.estado || 'Pendiente'
      return estado.toLowerCase() === filtroEstadoActividades.value.toLowerCase()
    })
  }

  return filtered
})

const totalFilteredItemsActividades = computed(() => solicitudesFiltradasAdmin.value.length)

const totalPagesActividades = computed(() =>
  Math.ceil(totalFilteredItemsActividades.value / itemsPerPageActividades.value)
)

const solicitudesPaginadas = computed(() => {
  const start = (currentPageActividades.value - 1) * itemsPerPageActividades.value
  const end = start + itemsPerPageActividades.value
  return solicitudesFiltradasAdmin.value.slice(start, end)
})

function getInitials(name) {
  if (!name) return 'U'
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

function getStatusClassActividad(estado) {
  switch (estado?.toLowerCase()) {
    case 'aprobado':
      return 'status-approved'
    case 'finalizado':
      return 'status-completed'
    case 'cancelado':
      return 'status-rejected'
    case 'pendiente':
    default:
      return 'status-pending'
  }
}

function getStatusIconActividad(estado) {
  switch (estado?.toLowerCase()) {
    case 'aprobado':
      return 'fas fa-check'
    case 'finalizado':
      return 'fas fa-flag-checkered'
    case 'cancelado':
      return 'fas fa-times'
    case 'pendiente':
    default:
      return 'fas fa-clock'
  }
}

function formatFechaActividad(fecha) {
  if (!fecha) return 'Sin fecha'
  const date = new Date(fecha)
  return date.toLocaleDateString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(async () => {
  await Promise.all([
    loadActividadesAprobadas(),
    chooseSolicitudes(),
    !isAdmin ? loadActividadesInscritas() : Promise.resolve()
  ])
})

function getImageUrl(archivo) {
  return archivo || ''
}

function isImageFile(fileUrl) {
  if (!fileUrl) return false
  const fileName = fileUrl.split('/').pop()
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
  const extension = fileName.toLowerCase().substring(fileName.lastIndexOf('.'))
  return imageExtensions.includes(extension)
}

function isPDFFile(fileUrl) {
  if (!fileUrl) return false
  const fileName = fileUrl.split('/').pop()
  return fileName.toLowerCase().endsWith('.pdf')
}

function isWordFile(fileUrl) {
  if (!fileUrl) return false
  const fileName = fileUrl.split('/').pop()
  const wordExtensions = ['.doc', '.docx']
  const extension = fileName.toLowerCase().substring(fileName.lastIndexOf('.'))
  return wordExtensions.includes(extension)
}

function handleFileClick(archivo) {
  if (!isImageFile(archivo)) {
    downloadFile(archivo)
  }
}

function downloadFile(fileUrl) {
  const link = document.createElement('a')
  link.href = fileUrl
  link.download = fileUrl.split('/').pop() || 'archivo'
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function getDiaFecha(fecha) {
  const date = new Date(fecha)
  return date.getDate().toString().padStart(2, '0')
}

function getMesFecha(fecha) {
  const date = new Date(fecha)
  const meses = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']
  return meses[date.getMonth()]
}

function getHoraFecha(fecha) {
  const date = new Date(fecha)
  return date.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit' })
}

function formatFechaRegistro(fecha) {
  const date = new Date(fecha)
  return date.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

function getEstadoClass(estado) {
  switch (estado?.toLowerCase()) {
    case 'aprobado':
      return 'estado-aprobado'
    case 'finalizado':
      return 'estado-finalizado'
    case 'cancelado':
      return 'estado-cancelado'
    default:
      return 'estado-pendiente'
  }
}

function getEstadoSolicitudClass(estado) {
  switch (estado?.toLowerCase()) {
    case 'aprobado':
      return 'solicitud-aprobada'
    case 'finalizado':
      return 'solicitud-finalizada'
    case 'rechazado':
    case 'cancelado':
      return 'solicitud-rechazada'
    default:
      return 'solicitud-pendiente'
  }
}

function abrirDetalleActividadInscrita(actividad) {
  esModalActividadInscrita.value = true
  selectedActividad.value = {
    id: actividad.id_actividad,
    titulo: actividad.titulo,
    tipo: actividad.tipo,
    fecha_actividad: actividad.fecha_actividad,
    descripcion: actividad.descripcion,
    archivo: actividad.archivo,
    estado_actividad: actividad.estado_actividad,
    fecha_registro: actividad.fecha_registro
  }
  showModalDetalle.value = true
}

async function inscribirseDirecto(actividad) {
  if (!user.value || !actividad.id) {
    onMostrarNotificacion({ mensaje: 'Error: No se pudo obtener la información del usuario o la actividad', tipo: 'error' })
    return
  }

  inscribiendose.value[actividad.id] = true

  try {
    await ActividadesService.inscribirse(actividad.id, {
      id_usuario: user.value.id
    })

    onMostrarNotificacion({ mensaje: '¡Te has inscrito exitosamente a la actividad!', tipo: 'success' })
    await loadActividadesAprobadas()
    await loadActividadesInscritas()
  } catch (error) {
    console.error('Error al inscribirse:', error)

    if (error.response && error.response.status === 409) {
      onMostrarNotificacion({ mensaje: 'Ya te encuentras inscrito en esta actividad', tipo: 'warning' })
    } else if (error.response && error.response.status === 400) {
      onMostrarNotificacion({ mensaje: 'No hay cupos disponibles para esta actividad', tipo: 'error' })
    } else {
      onMostrarNotificacion({ mensaje: 'Error al inscribirse. Por favor, inténtalo de nuevo', tipo: 'error' })
    }
  } finally {
    inscribiendose.value[actividad.id] = false
  }
}

function abrirDetalleActividad(actividad) {
  esModalActividadInscrita.value = false
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

function abrirModalInscritos(actividad) {
  selectedActividadInscritos.value = {
    id: actividad.id || extractIdFromCodigo(actividad.codigo),
    titulo: actividad.titulo,
    tipo: actividad.tipo,
    fecha_actividad: actividad.fecha,
    descripcion: actividad.descripcion,
    stock: actividad.stock,
    cupos_restantes: actividad.cupos_restantes || actividad.stock
  }
  showModalInscritos.value = true
}

function extractIdFromCodigo(codigo) {
  return parseInt(codigo.split('-')[1]) || 0
}

function onInscripcionExitosa() {
  loadActividadesAprobadas()
  if (!isAdmin) {
    loadActividadesInscritas()
  }
}

function onMostrarNotificacion({ mensaje, tipo }) {
  snackbar.value = {
    show: true,
    message: mensaje,
    color: tipo
  }
}

async function onActividadCreada({ esAdmin }) {
  await Promise.all([loadActividadesAprobadas(), chooseSolicitudes()])

  if (esAdmin) {
    tab.value = 1
  } else {
    tab.value = 3
  }
}

async function onEstadoActualizado() {
  await Promise.all([loadActividadesAprobadas(), chooseSolicitudes()])
}

function openModalNuevo(type = 'actividad', actividad = null) {
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
      attend: false
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
    archivo: item.archivo,
    motivo_cancelacion: item.motivo_cancelacion
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
      fecha_actividad: a.fecha_actividad,
      fecha_solicitud: a.fecha_solicitud,
      resumen: a.descripcion,
      descripcion: a.descripcion,
      tipo: a.tipo,
      stock: a.stock,
      estado: a.estado || 'Pendiente',
      archivo: a.archivo_obj?.url || null,
      motivo_cancelacion: a.motivo_cancelacion
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
      fecha_actividad: a.fecha_actividad,
      fecha_solicitud: a.fecha_solicitud,
      resumen: a.descripcion,
      descripcion: a.descripcion,
      tipo: a.tipo,
      stock: a.stock,
      estado: a.estado || 'Pendiente',
      archivo: a.archivo_obj?.url || null,
      motivo_cancelacion: a.motivo_cancelacion,
      nombre_usuario: a.nombre_usuario
    }))
  } catch (error) {
    console.error(error)
  }
}

async function loadActividadesAprobadas() {
  try {
    let activities
    if (isAdmin) {
      activities = await ActividadesService.obtenerActividadesAprobadas()
    } else {
      activities = await ActividadesService.obtenerActividadesDisponibles(user.value.id)
    }
    
    actividades.value = activities.map((a) => ({
      id: a.id,
      codigo: `UNMSM-${a.id}`,
      fecha: a.fecha_actividad,
      descripcion: a.descripcion,
      titulo: a.titulo,
      tipo: a.tipo.toUpperCase(),
      stock: a.stock,
      cupos_restantes: a.cupos_restantes,
      archivo: a.archivo_obj?.url || null,
    }))
  } catch (error) {
    console.error(error)
  }
}

async function loadActividadesInscritas() {
  try {
    const activities = await ActividadesService.obtenerActividadesInscritas(user.value.id)
    actividadesInscritas.value = activities.map((a) => ({
      id_actividad: a.id_actividad,
      id_inscripcion: a.id_inscripcion,
      titulo: a.titulo,
      tipo: a.tipo,
      descripcion: a.descripcion,
      fecha_actividad: a.fecha_actividad,
      fecha_registro: a.fecha_registro,
      estado_actividad: a.estado_actividad,
      archivo: a.archivo_obj?.url || null,
    }))
  } catch (error) {
    console.error('Error al cargar actividades inscritas:', error)
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

.actividades-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  padding: 20px 0;
}

.actividad-card {
  background: #FFFBED;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s ease;
  height: 480px;
  display: flex;
  flex-direction: column;
  border: 1px solid #e0e0e0;
}

.actividad-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.card-header {
  position: relative;
  height: 160px;
  overflow: hidden;
}

.card-image,
.image-placeholder {
  width: 100%;
  height: 100%;
}

.image-placeholder {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-actividad {
  border-radius: 0;
}

.tipo-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: #53696D;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 8px rgba(83, 105, 109, 0.3);
}

.estado-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.estado-aprobado {
  background: #4caf50;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.estado-finalizado {
  background: #2196f3;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.estado-cancelado {
  background: #f44336;
  box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3);
}

.estado-pendiente {
  background: #ff9800;
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
}

.inscrita-card {
  border-left: 4px solid #53696D;
}

.solicitud-card {
  border-left: 4px solid #A37801;
}

.estado-solicitud-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.solicitud-aprobada {
  background: #4caf50;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.solicitud-finalizada {
  background: #2196f3;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.solicitud-rechazada {
  background: #f44336;
  box-shadow: 0 2px 8px rgba(244, 67, 54, 0.3);
}

.solicitud-pendiente {
  background: #ff9800;
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
}

.card-content {
  padding: 20px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.titulo-actividad {
  font-size: 18px;
  font-weight: 700;
  color: #163053;
  line-height: 1.3;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.info-container {
  display: flex;
  gap: 12px;
  justify-content: space-between;
}

.fecha-card {
  flex: 1;
  background: linear-gradient(135deg, #53696D, #3e5357);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 2px 8px rgba(83, 105, 109, 0.2);
}

.fecha-icon {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fecha-details {
  display: flex;
  flex-direction: column;
  color: white;
}

.fecha-dia {
  font-size: 16px;
  font-weight: 700;
  line-height: 1;
}

.fecha-mes {
  font-size: 11px;
  font-weight: 600;
  opacity: 0.9;
  line-height: 1;
}

.fecha-hora {
  font-size: 12px;
  font-weight: 500;
  opacity: 0.8;
  margin-top: 2px;
}

.cupos-card {
  flex: 1;
  background: linear-gradient(135deg, #53696D, #3e5357);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 2px 8px rgba(83, 105, 109, 0.2);
  transition: all 0.3s ease;
}

.cupos-card.cupos-criticos {
  background: linear-gradient(135deg, #f44336, #d32f2f);
  box-shadow: 0 2px 8px rgba(244, 67, 54, 0.2);
}

.cupos-icon {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cupos-details {
  display: flex;
  flex-direction: column;
  color: white;
}

.cupos-numero {
  font-size: 16px;
  font-weight: 700;
  line-height: 1;
}

.cupos-texto {
  font-size: 11px;
  font-weight: 600;
  opacity: 0.9;
  line-height: 1;
}

.cupos-total {
  font-size: 10px;
  font-weight: 500;
  opacity: 0.8;
  margin-top: 1px;
}

.registro-card {
  flex: 1;
  background: linear-gradient(135deg, #2196f3, #1976d2);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.2);
}

.registro-icon {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.registro-details {
  display: flex;
  flex-direction: column;
  color: white;
}

.registro-texto {
  font-size: 11px;
  font-weight: 600;
  opacity: 0.9;
  line-height: 1;
}

.registro-fecha {
  font-size: 12px;
  font-weight: 500;
  opacity: 0.8;
  margin-top: 2px;
}

.solicitud-card-info {
  flex: 1;
  background: linear-gradient(135deg, #A37801, #8a6600);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 2px 8px rgba(163, 120, 1, 0.2);
}

.solicitud-icon {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.solicitud-details {
  display: flex;
  flex-direction: column;
  color: white;
}

.solicitud-texto {
  font-size: 11px;
  font-weight: 600;
  opacity: 0.9;
  line-height: 1;
}

.solicitud-fecha {
  font-size: 12px;
  font-weight: 500;
  opacity: 0.8;
  margin-top: 2px;
}

.info-adicional {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.fecha-actividad-solicitud {
  display: flex;
  align-items: center;
  font-size: 14px;
  font-weight: 500;
  color: #A37801;
  background: #fffbed;
  padding: 8px 12px;
  border-radius: 8px;
  border-left: 3px solid #A37801;
}

.cupos-solicitud {
  display: flex;
  align-items: center;
  font-size: 14px;
  font-weight: 500;
  color: #A37801;
}

.motivo-cancelacion {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #f44336;
  background: #ffebee;
  padding: 8px 12px;
  border-radius: 8px;
  border-left: 3px solid #f44336;
}

.descripcion-actividad {
  color: #555;
  font-size: 14px;
  line-height: 1.5;
  flex: 1;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  padding: 16px 20px 20px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.btn-inscribirse {
  border-radius: 12px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  height: 44px !important;
  box-shadow: 0 2px 8px rgba(83, 105, 109, 0.2) !important;
}

.btn-inscribirse:hover {
  box-shadow: 0 4px 12px rgba(83, 105, 109, 0.3) !important;
}

.btn-ver-detalle {
  border-radius: 12px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  height: 44px !important;
  border-color: #A37801 !important;
  color: #A37801 !important;
}

.btn-ver-inscritos {
  border-radius: 12px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  height: 44px !important;
  border-color: #53696D !important;
  color: #53696D !important;
}

.btn-mas-info {
  font-size: 12px !important;
  text-transform: none !important;
  font-weight: 500 !important;
  height: auto !important;
  min-height: 32px !important;
  margin-top: 8px !important;
}

.btn-mas-info-inscrita {
  font-size: 14px !important;
  text-transform: none !important;
  font-weight: 500 !important;
  height: 40px !important;
  border-radius: 12px !important;
  border-color: #53696D !important;
  color: #53696D !important;
}

@media (max-width: 768px) {
  .actividades-grid {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 16px 0;
  }

  .actividad-card {
    height: auto;
    min-height: 420px;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .actividades-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1025px) {
  .actividades-grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  }
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

.text-title {
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

.file-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  transition: all 0.3s ease;
  gap: 8px;
}

.file-placeholder:hover {
  transform: scale(1.05);
  background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
}

.file-placeholder.pdf-file {
  background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
}

.file-placeholder.pdf-file:hover {
  background: linear-gradient(135deg, #fce4ec 0%, #f8bbd9 100%);
}

.file-placeholder.word-file {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
}

.file-placeholder.word-file:hover {
  background: linear-gradient(135deg, #e1f5fe 0%, #b3e5fc 100%);
}

.file-placeholder.generic-file {
  background: linear-gradient(135deg, #fafafa 0%, #e0e0e0 100%);
}

.file-placeholder.generic-file:hover {
  background: linear-gradient(135deg, #f5f5f5 0%, #eeeeee 100%);
}

.file-label {
  font-size: 12px;
  font-weight: 600;
  color: #424242;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 4px;
}

.card-image :deep(.n-image) {
  display: block;
  width: 100%;
  height: 160px;
  border-radius: 0;
  overflow: hidden;
}

.card-image :deep(.n-image img) {
  width: 100%;
  height: 160px;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.card-image:hover :deep(.n-image img) {
  transform: scale(1.05);
}

.filtro-container {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px 20px;
  border: 1px solid #e0e0e0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.filtro-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.filtro-label {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  white-space: nowrap;
}

.filtro-select :deep(.v-field) {
  border-radius: 8px !important;
  border-color: #A37801 !important;
}

.filtro-select :deep(.v-field--focused) {
  border-color: #A37801 !important;
  box-shadow: 0 0 0 2px rgba(163, 120, 1, 0.2) !important;
}

.filtro-select :deep(.v-field__outline) {
  color: #A37801 !important;
}

/* Estilos para la nueva tabla de administrador */
.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: transparent;
  padding: 24px;
  border-radius: 12px;
  border: 1px solid #A37801;
  display: flex;
  align-items: center;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
}

.stat-icon.blue {
  background-color: #dbeafe;
  color: #2563eb;
}

.stat-icon.yellow {
  background-color: #fef3c7;
  color: #d97706;
}

.stat-icon.green {
  background-color: #dcfce7;
  color: #16a34a;
}

.stat-icon.red {
  background-color: #fee2e2;
  color: #dc2626;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  font-weight: 500;
  color: #293a5f;
  margin: 0 0 4px 0;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

/* Search and Filter Section */
.search-filter-section {
  background: transparent;
  border-radius: 12px;
  border: 1px solid #A37801;
  padding: 24px;
  margin-bottom: 24px;
}

.search-input-container {
  position: relative;
  margin-bottom: 16px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #111827;
  font-size: 16px;
}

.search-input {
  width: 100%;
  padding: 12px 12px 12px 40px;
  border: 1px solid #A37801;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s ease;
}

.search-input::placeholder {
  color: #111827;
}

.search-input:focus {
  outline: none;
  box-shadow: 0 0 0 3px #A37801;
}

.filter-tabs {
  display: flex;
  gap: 8px;
}

.filter-tab {
  padding: 10px 16px;
  border-radius: 8px;
  border: 1px solid transparent;
  background: #FFFBED;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-tab:hover {
  background: #A37801;
  color: white;
}

.filter-tab.active {
  background: #A37801;
  color: white;
}

/* Table Styles */
.permisos-table-container {
  background: transparent;
  border-radius: 12px;
  border: 1px solid #A37801;
  overflow: hidden;
  margin-bottom: 24px;
}

.table-wrapper {
  overflow-x: auto;
}

.permisos-table {
  width: 100%;
  border-collapse: collapse;
}

.permisos-table thead {
  background: #FFFBED;
}

.permisos-table th {
  padding: 16px 24px;
  text-align: left;
  font-size: 12px;
  font-weight: 500;
  color: #525252;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #A37801;
}

.permisos-table th:last-child {
  text-align: right;
}

.permisos-table tbody tr {
  border-bottom: 1px solid #A37801;
  transition: background-color 0.2s ease;
}

.permisos-table tbody tr:hover {
  background: #FFFBED;
}

.permisos-table td {
  padding: 16px 24px;
  vertical-align: top;
}

.employee-info {
  display: flex;
  align-items: center;
}

.avatar {
  width: 40px;
  height: 40px;
  background: #A37801;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
  margin-right: 16px;
}

.employee-details {
  flex: 1;
}

.employee-name {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  margin-bottom: 2px;
}

.employee-id {
  font-size: 12px;
  color: #111827;
}

.date-info {
  display: flex;
  flex-direction: column;
}

.date-range {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  margin-bottom: 2px;
}

.date-requested {
  font-size: 12px;
  color: #111827;
}

.duration {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
}

.motivo {
  font-size: 14px;
  color: #111827;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 500;
  border: 1px solid;
  gap: 8px;
}

.status-badge i {
  margin-right: 4px;
  font-size: 10px;
}

.status-badge.status-approved {
  background: #dcfce7;
  color: #166534;
  border-color: #bbf7d0;
}

.status-badge.status-rejected {
  background: #fee2e2;
  color: #991b1b;
  border-color: #fecaca;
}

.status-badge.status-pending {
  background: #fef3c7;
  color: #92400e;
  border-color: #fde68a;
}

.status-badge.status-completed {
  background: #dbeafe;
  color: #1e40af;
  border-color: #bfdbfe;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #111827;
}

.action-btn:hover {
  transform: scale(1.05);
}

.action-btn.view:hover {
  background: #dbeafe;
  color: #2563eb;
}

.action-btn.download:hover {
  background: #dbeafe;
  color: #2563eb;
}

/* Pagination */
.pagination-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: transparent;
  border-radius: 12px;
  border: 1px solid #A37801;
}

.pagination-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #374151;
}

.items-select {
  padding: 4px 8px;
  border: 1px solid #A37801;
  border-radius: 4px;
  font-size: 14px;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.pagination-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #FFFBED;
  color: #6b7280;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: #f3f4f6;
  color: #374151;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-text {
  font-size: 14px;
  color: #374151;
}

.actividad-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.actividad-titulo {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  margin-bottom: 2px;
}

.actividad-descripcion {
  font-size: 12px;
  color: #111827;
  line-height: 1.4;
}

.fecha-solicitud {
  font-size: 12px;
  color: #111827;
}

.tipo-fecha-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tipo-actividad {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  display: flex;
  align-items: center;
}

.fecha-actividad {
  font-size: 12px;
  color: #111827;
  display: flex;
  align-items: center;
}

.cupos-info {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  display: flex;
  align-items: center;
}

.motivo-cancelacion-small {
  font-size: 10px;
  color: #dc2626;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
}

@media (max-width: 768px) {
  .dashboard-cards {
    grid-template-columns: 1fr;
  }

  .search-filter-section {
    padding: 16px;
  }

  .filter-tabs {
    flex-wrap: wrap;
  }

  .pagination-container {
    flex-direction: column;
    gap: 16px;
  }

  .permisos-table th,
  .permisos-table td {
    padding: 12px 16px;
  }
}
</style>
