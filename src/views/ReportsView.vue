<template>
  <ContainerView>
    <v-tabs v-model="tab" align-tabs="start" color="#A37801">
      <h3 class="mb-4 text-title">{{ isAdmin ? 'Reportes' : 'Mis reportes' }}</h3>
      <v-spacer></v-spacer>
      <v-btn v-if="!isAdmin" variant="outlined" class="mb-6 custom-button" @click="openModalNuevo">
        <span>🚨 Realizar una Queja</span>
      </v-btn>
    </v-tabs>
    
    <!-- Vista para administradores -->
    <div v-if="isAdmin">
      <div class="dashboard-cards mb-6 mt-6">
        <div class="stat-card">
          <div class="stat-icon blue">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="stat-content">
            <p class="stat-label">Total Reportes</p>
            <p class="stat-value">{{ data.length }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon yellow">
            <i class="fas fa-clock"></i>
          </div>
          <div class="stat-content">
            <p class="stat-label">Recibidos</p>
            <p class="stat-value">{{ data.filter(r => r.estado === 'Recibido').length }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon yellow">
            <i class="fas fa-eye"></i>
          </div>
          <div class="stat-content">
            <p class="stat-label">En Revisión</p>
            <p class="stat-value">{{ data.filter(r => r.estado === 'En revisión').length }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon blue">
            <i class="fas fa-cogs"></i>
          </div>
          <div class="stat-content">
            <p class="stat-label">En Proceso</p>
            <p class="stat-value">{{ data.filter(r => r.estado === 'En proceso').length }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green">
            <i class="fas fa-check"></i>
          </div>
          <div class="stat-content">
            <p class="stat-label">Resueltos</p>
            <p class="stat-value">{{ data.filter(r => r.estado === 'Resuelto').length }}</p>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon red">
            <i class="fas fa-flag-checkered"></i>
          </div>
          <div class="stat-content">
            <p class="stat-label">Cerrados</p>
            <p class="stat-value">{{ data.filter(r => r.estado === 'Cerrado').length }}</p>
          </div>
        </div>
      </div>

      <div class="search-filter-section">
        <div class="search-input-container">
          <i class="fas fa-search search-icon"></i>
          <input type="text" placeholder="Buscar por asunto o motivo..." class="search-input" v-model="searchTermReportes" />
        </div>
        <div class="filter-tabs">
          <button v-for="estado in filtrosReportes" :key="estado.value" @click="filtroEstadoReportes = estado.value"
            :class="['filter-tab', { 'active': filtroEstadoReportes === estado.value }]">
            {{ estado.label }}
          </button>
        </div>
      </div>

      <div class="permisos-table-container">
        <div class="table-wrapper">
          <table class="permisos-table">
            <thead>
              <tr>
                <th>N° Reporte</th>
                <th>Asunto y Descripción</th>
                <th>Motivo</th>
                <th>Fecha</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="reporte in reportesPaginados" :key="reporte.id" class="table-row">
                <td>
                  <div class="reporte-numero">
                    <div class="numero-badge">
                      {{ reporte.numero }}
                    </div>
                  </div>
                </td>
                <td>
                  <div class="reporte-info">
                    <div class="reporte-asunto">{{ reporte.asunto }}</div>
                    <div class="reporte-descripcion" :title="reporte.descripcion">
                      {{ reporte.descripcion?.substring(0, 50) }}{{ reporte.descripcion?.length > 50 ? '...' : '' }}
                    </div>
                  </div>
                </td>
                <td>
                  <div class="motivo-info">
                    <i class="fas fa-tag" style="color: #53696D; margin-right: 8px;"></i>
                    {{ reporte.motivo }}
                  </div>
                </td>
                <td>
                  <div class="fecha-info">
                    <i class="fas fa-calendar" style="color: #A37801; margin-right: 8px;"></i>
                    {{ reporte.fecha }}
                  </div>
                </td>
                <td>
                  <span :class="['status-badge', getStatusClassReporte(reporte.estado)]">
                    <i :class="getStatusIconReporte(reporte.estado)"></i>
                    {{ reporte.estado }}
                  </span>
                </td>
                <td>
                  <div class="actions">
                    <button v-if="reporte.prueba" @click="downloadFile(reporte.prueba)" 
                      class="action-btn download" title="Descargar evidencia">
                      <i class="fas fa-download"></i>
                    </button>
                    <button @click="openModal(reporte)" class="action-btn view" title="Ver detalles">
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
          <select v-model="itemsPerPageReportes" class="items-select">
            <option value="5">5</option>
            <option value="10">10</option>
            <option value="25">25</option>
            <option value="50">50</option>
          </select>
          <span>de {{ totalFilteredItemsReportes }} resultados</span>
        </div>
        <div class="pagination-controls">
          <button @click="currentPageReportes = Math.max(currentPageReportes - 1, 1)" :disabled="currentPageReportes === 1"
            class="pagination-btn">
            <i class="fas fa-chevron-left"></i>
          </button>
          <span class="pagination-text">
            Página {{ currentPageReportes }} de {{ totalPagesReportes }}
          </span>
          <button @click="currentPageReportes = Math.min(currentPageReportes + 1, totalPagesReportes)" :disabled="currentPageReportes === totalPagesReportes"
            class="pagination-btn">
            <i class="fas fa-chevron-right"></i>
          </button>
        </div>
      </div>
    </div>

    <!-- Vista para estudiantes -->
    <div v-else>
      <v-container fluid>
        <div class="actividades-grid">
          <div v-for="(reporte, index) in filteredData" :key="index" class="actividad-card reporte-card">
            <div class="card-header">
              <div v-if="reporte.prueba" class="card-image" @click="downloadFile(reporte.prueba)"
                style="cursor: pointer;">
                <n-image v-if="isImageFile(reporte.prueba)" :src="getImageUrl(reporte.prueba)"
                  :alt="reporte.asunto" object-fit="cover"
                  :style="{ width: '100%', height: '160px', borderRadius: '0' }" :preview-disabled="false" />
                <div v-else-if="isPDFFile(reporte.prueba)" class="file-placeholder pdf-file">
                  <i class="fa-solid fa-file-pdf" style="font-size: 48px; color: #d32f2f;"></i>
                  <span class="file-label">PDF</span>
                </div>
                <div v-else-if="isWordFile(reporte.prueba)" class="file-placeholder word-file">
                  <i class="fa-solid fa-file-word" style="font-size: 48px; color: #1976d2;"></i>
                  <span class="file-label">WORD</span>
                </div>
                <div v-else class="file-placeholder generic-file">
                  <i class="fa-solid fa-file" style="font-size: 48px; color: #757575;"></i>
                  <span class="file-label">ARCHIVO</span>
                </div>
              </div>
              <div v-else class="image-placeholder">
                <i class="fa-solid fa-exclamation-triangle" style="font-size: 48px; color: #53696D;"></i>
              </div>
              <div class="motivo-badge">{{ reporte.motivo }}</div>
              <div class="estado-reporte-badge" :class="getEstadoReporteClass(reporte.estado)">
                {{ reporte.estado }}
              </div>
            </div>

            <div class="card-content">
              <h3 class="titulo-actividad">{{ reporte.asunto }}</h3>

              <div class="info-container">
                <div class="numero-card">
                  <div class="numero-icon">
                    <i class="fa-solid fa-hashtag" style="color: white; font-size: 18px;"></i>
                  </div>
                  <div class="numero-details">
                    <span class="numero-texto">Código</span>
                    <span class="numero-codigo">{{ reporte.numero }}</span>
                  </div>
                </div>

                <div class="fecha-card">
                  <div class="fecha-icon">
                    <i class="fa-solid fa-calendar" style="color: white; font-size: 18px;"></i>
                  </div>
                  <div class="fecha-details">
                    <span class="fecha-dia">{{ getDiaFecha(reporte.fecha) }}</span>
                    <span class="fecha-mes">{{ getMesFecha(reporte.fecha) }}</span>
                    <span class="fecha-hora">{{ getHoraFecha(reporte.fecha) }}</span>
                  </div>
                </div>
              </div>

              <p class="descripcion-actividad">
                {{ reporte.descripcion || 'Sin descripción disponible' }}
              </p>
            </div>

            <div class="card-footer">
              <v-btn @click="openModal(reporte)" color="#A37801" variant="outlined" block
                class="btn-ver-detalle">
                <i class="fa-solid fa-eye" style="margin-right: 8px; font-size: 16px;"></i>
                Ver detalle
              </v-btn>

              <v-btn v-if="reporte.prueba" @click="downloadFile(reporte.prueba)" variant="text" size="small"
                class="btn-mas-info" color="#53696D">
                <i class="fa-solid fa-download" style="margin-right: 4px; font-size: 14px;"></i>
                Descargar evidencia
              </v-btn>
            </div>
          </div>
        </div>
      </v-container>
    </div>
    
    <ModalQueja :type="modalType" v-model="showModal" :item="selectedItem" :user="user" :mode="isView"  @agregar-queja="agregarQueja" @actualizar-estado="onEstadoActualizado" @mostrar-notificacion="onMostrarNotificacion" />
    
    <ModalDetalleReporte 
      v-model="showModalDetalle" 
      :reporte="selectedReporte" 
      :is-admin="isAdmin" 
      @estado-actualizado="onEstadoActualizadoDetalle" 
    />
    
    <v-snackbar 
      v-model="snackbar.show" 
      :color="snackbar.color" 
      timeout="4000"
      location="top"
    >
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false">
          Cerrar
        </v-btn>
      </template>
    </v-snackbar>
  </ContainerView>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue'
import QuejasService from '@/services/QuejasService'
import ModalQueja from './modal/ModalQueja.vue'
import ModalDetalleReporte from './modal/ModalDetalleReporte.vue'
import LoginService from '@/services/LoginService'
import ContainerView from '@/components/layout/ContainerView.vue'


const data = ref([])
const isView = ref("")
const showModal = ref(false)
const showModalDetalle = ref(false)
const selectedItem = ref(null)
const selectedReporte = ref(null)
const selectedAddress = ref(null)
const modalType = ref('queja')
const user = ref(LoginService.getCurrentUser())
const isAdmin = LoginService.isAdmin()

const searchTermReportes = ref('')
const filtroEstadoReportes = ref('Todos')
const currentPageReportes = ref(1)
const itemsPerPageReportes = ref(10)

const filtrosReportes = [
  { label: 'Todos', value: 'Todos' },
  { label: 'Recibidos', value: 'Recibido' },
  { label: 'En Revisión', value: 'En revisión' },
  { label: 'En Proceso', value: 'En proceso' },
  { label: 'Resueltos', value: 'Resuelto' },
  { label: 'Cerrados', value: 'Cerrado' }
]

const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
})

const filteredData = computed(() => {
  if (!selectedAddress.value) return data.value
  return data.value.filter((item) => item.address?.includes(selectedAddress.value))
})

const reportesFiltradasAdmin = computed(() => {
  let filtered = data.value

  if (searchTermReportes.value) {
    const searchTerm = searchTermReportes.value.toLowerCase()
    filtered = filtered.filter(reporte => 
      reporte.asunto?.toLowerCase().includes(searchTerm) ||
      reporte.motivo?.toLowerCase().includes(searchTerm) ||
      reporte.descripcion?.toLowerCase().includes(searchTerm)
    )
  }

  if (filtroEstadoReportes.value !== 'Todos') {
    filtered = filtered.filter(reporte => {
      const estado = reporte.estado || 'Recibido'
      return estado.toLowerCase() === filtroEstadoReportes.value.toLowerCase()
    })
  }

  return filtered
})

const totalFilteredItemsReportes = computed(() => reportesFiltradasAdmin.value.length)

const totalPagesReportes = computed(() => 
  Math.ceil(totalFilteredItemsReportes.value / itemsPerPageReportes.value)
)

const reportesPaginados = computed(() => {
  const start = (currentPageReportes.value - 1) * itemsPerPageReportes.value
  const end = start + itemsPerPageReportes.value
  return reportesFiltradasAdmin.value.slice(start, end)
})

onMounted(async () => {
  chooseQuejas()
})

function getStatusClassReporte(estado) {
  switch (estado?.toLowerCase()) {
    case 'resuelto':
      return 'status-approved'
    case 'cerrado':
      return 'status-completed'
    case 'en proceso':
      return 'status-processing'
    case 'en revisión':
      return 'status-review'
    case 'recibido':
    default:
      return 'status-pending'
  }
}

function getStatusIconReporte(estado) {
  switch (estado?.toLowerCase()) {
    case 'resuelto':
      return 'fas fa-check'
    case 'cerrado':
      return 'fas fa-flag-checkered'
    case 'en proceso':
      return 'fas fa-cogs'
    case 'en revisión':
      return 'fas fa-eye'
    case 'recibido':
    default:
      return 'fas fa-clock'
  }
}

function downloadFile(fileName) {
  if (!fileName) return
  
  const baseUrl = 'http://localhost:5000/uploads/quejas/'
  const fileUrl = baseUrl + fileName
  
  const link = document.createElement('a')
  link.href = fileUrl
  link.download = fileName
  link.target = '_blank'
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function isImageFile(fileName) {
  if (!fileName) return false
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
  return imageExtensions.some(ext => fileName.toLowerCase().endsWith(ext))
}

function isPDFFile(fileName) {
  if (!fileName) return false
  return fileName.toLowerCase().endsWith('.pdf')
}

function isWordFile(fileName) {
  if (!fileName) return false
  const wordExtensions = ['.doc', '.docx']
  return wordExtensions.some(ext => fileName.toLowerCase().endsWith(ext))
}

function getImageUrl(fileName) {
  if (!fileName) return ''
  return `http://localhost:5000/uploads/quejas/${fileName}`
}

function getDiaFecha(fecha) {
  if (!fecha) return ''
  const date = new Date(fecha.split('/').reverse().join('-'))
  return date.getDate().toString().padStart(2, '0')
}

function getMesFecha(fecha) {
  if (!fecha) return ''
  const date = new Date(fecha.split('/').reverse().join('-'))
  const meses = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC']
  return meses[date.getMonth()]
}

function getHoraFecha(fecha) {
  if (!fecha) return ''
  return '00:00'
}

function getEstadoReporteClass(estado) {
  switch (estado?.toLowerCase()) {
    case 'resuelto':
      return 'estado-resuelto'
    case 'cerrado':
      return 'estado-cerrado'
    case 'en proceso':
      return 'estado-proceso'
    case 'en revisión':
      return 'estado-revision'
    case 'recibido':
    default:
      return 'estado-recibido'
  }
}

function openModal(item) {
  selectedReporte.value = {
    id: item.id,
    numero: item.numero,
    asunto: item.asunto,
    motivo: item.motivo,
    fecha: item.fecha,
    estado: item.estado,
    descripcion: item.descripcion,
    prueba: item.prueba
  }
  showModalDetalle.value = true
}

function agregarQueja(queja) {
  data.value.unshift(queja)
}

function openModalNuevo(type = 'queja') {
  selectedItem.value = {
    numero: '',
    asunto: '',
    motivo: '',
    fecha: '',
    estado: '',
    descripcion: '',
  }
  isView.value = false
  modalType.value = type
  showModal.value = true
}

async function loadQuejasPorUsuario() {
  try {
    const quejas = await QuejasService.obtenerQuejasPorUsuario(user.value.id)
    data.value = quejas.map((a) => ({
      id: a.id,
      numero: a.codigo,
      asunto: a.asunto,
      motivo: a.motivo ?? '',
      fecha: a.fecha,
      estado: a.estado,
      descripcion: a.descripcion,
      prueba: a.prueba
    }))
  } catch (error) {
    console.error(error)
  }
}

async function loadQuejas() {
  try {
    const quejas = await QuejasService.obtenerTodos()
    data.value = quejas.map((a) => ({
      id: a.id,
      numero: a.codigo,
      asunto: a.asunto,
      motivo: a.motivo ?? '',
      fecha: a.fecha,
      estado: a.estado,
      descripcion: a.descripcion,
      prueba: a.prueba
    }))
  } catch (error) {
    console.error(error)
  }
}

function chooseQuejas() {
  if (LoginService.isAdmin()) {
    loadQuejas()
  } else {
    loadQuejasPorUsuario()
  }
}

function onEstadoActualizado() {
  chooseQuejas()
}

function onEstadoActualizadoDetalle({ id, estado }) {
  const index = data.value.findIndex(item => item.id === id)
  if (index !== -1) {
    data.value[index].estado = estado
  }
  
  onMostrarNotificacion({ 
    mensaje: `Estado del reporte actualizado a: ${estado}`, 
    tipo: 'success' 
  })
  
  chooseQuejas()
}

function onMostrarNotificacion({ mensaje, tipo }) {
  snackbar.value = {
    show: true,
    message: mensaje,
    color: tipo
  }
}
</script>
<style scoped>
.custom-table {
  margin-top: 32px;
}
.n-data-table,
.n-data-table-tbody {
  background-color: transparent;
}

.text-title{
  color: white;
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

.reporte-numero {
  display: flex;
  align-items: center;
}

.numero-badge {
  background: #A37801;
  color: white;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.reporte-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.reporte-asunto {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  margin-bottom: 2px;
}

.reporte-descripcion {
  font-size: 12px;
  color: #111827;
  line-height: 1.4;
}

.motivo-info {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  display: flex;
  align-items: center;
}

.fecha-info {
  font-size: 14px;
  font-weight: 500;
  color: #111827;
  display: flex;
  align-items: center;
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

.status-badge.status-completed {
  background: #dbeafe;
  color: #1e40af;
  border-color: #bfdbfe;
}

.status-badge.status-processing {
  background: #e0f2fe;
  color: #0277bd;
  border-color: #b3e5fc;
}

.status-badge.status-review {
  background: #fff3e0;
  color: #e65100;
  border-color: #ffcc02;
}

.status-badge.status-pending {
  background: #fef3c7;
  color: #92400e;
  border-color: #fde68a;
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

.reporte-card {
  border-left: 4px solid #A37801;
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

.motivo-badge {
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

.estado-reporte-badge {
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

.estado-resuelto {
  background: #4caf50;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.estado-cerrado {
  background: #2196f3;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
}

.estado-proceso {
  background: #ff9800;
  box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
}

.estado-revision {
  background: #9c27b0;
  box-shadow: 0 2px 8px rgba(156, 39, 176, 0.3);
}

.estado-recibido {
  background: #795548;
  box-shadow: 0 2px 8px rgba(121, 85, 72, 0.3);
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

.numero-card {
  flex: 1;
  background: linear-gradient(135deg, #A37801, #8a6600);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 2px 8px rgba(163, 120, 1, 0.2);
}

.numero-icon {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.numero-details {
  display: flex;
  flex-direction: column;
  color: white;
}

.numero-texto {
  font-size: 11px;
  font-weight: 600;
  opacity: 0.9;
  line-height: 1;
}

.numero-codigo {
  font-size: 12px;
  font-weight: 700;
  line-height: 1;
  margin-top: 2px;
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

.btn-ver-detalle {
  border-radius: 12px !important;
  font-weight: 600 !important;
  text-transform: none !important;
  height: 44px !important;
  border-color: #A37801 !important;
  color: #A37801 !important;
}

.btn-mas-info {
  font-size: 12px !important;
  text-transform: none !important;
  font-weight: 500 !important;
  height: auto !important;
  min-height: 32px !important;
  margin-top: 8px !important;
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
  background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
}

.file-placeholder.generic-file:hover {
  background: linear-gradient(135deg, #eeeeee 0%, #bdbdbd 100%);
}

.file-label {
  font-size: 12px;
  font-weight: 600;
  color: #555;
  margin-top: 4px;
}

.card-image :deep(.n-image) {
  width: 100% !important;
  height: 100% !important;
  border-radius: 0 !important;
}

.card-image :deep(.n-image img) {
  width: 100% !important;
  height: 160px !important;
  object-fit: cover !important;
  transition: transform 0.3s ease !important;
}

.card-image:hover :deep(.n-image img) {
  transform: scale(1.05) !important;
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
</style>
