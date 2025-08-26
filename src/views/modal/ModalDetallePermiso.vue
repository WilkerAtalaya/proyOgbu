<template>
  <ContainerModal 
    v-model="dialog" 
    :title="`Permiso de Salida #${permiso?.id || 'N/A'}`" 
    :max-width="650"
    :colorTheme="'#A37801'"
  >
    <div v-if="permiso" class="contenido-modal">
      <div class="mb-6">
        <div class="info-cards-container">
          <div class="info-card empleado-card">
            <div class="card-icon">
              <i class="fa-solid fa-user"></i>
            </div>
            <div class="card-content">
              <span class="card-label">Residente</span>
              <span class="card-value empleado-value">{{ permiso.nombre_usuario }}</span>
            </div>
          </div>

          <div class="info-card estado-card" :class="getEstadoCardClass(permiso.estado)">
            <div class="card-icon">
              <i :class="getEstadoIcon(permiso.estado)"></i>
            </div>
            <div class="card-content">
              <span class="card-label">Estado</span>
              <span class="card-value estado-value">{{ permiso.estado }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="mb-4">
        <label class="field-label">Fechas del Permiso</label>
        <div class="fechas-container">
          <div class="fecha-item">
            <div class="fecha-icon salida">
              <i class="fa-solid fa-plane-departure"></i>
            </div>
            <div class="fecha-info">
              <span class="fecha-tipo">Fecha de Salida</span>
              <span class="fecha-valor">{{ formatFecha(permiso.fecha_salida) }}</span>
            </div>
          </div>
          <div class="fecha-separador">
            <i class="fa-solid fa-arrow-right"></i>
          </div>
          <div class="fecha-item">
            <div class="fecha-icon regreso">
              <i class="fa-solid fa-plane-arrival"></i>
            </div>
            <div class="fecha-info">
              <span class="fecha-tipo">Fecha de Regreso</span>
              <span class="fecha-valor">{{ formatFecha(permiso.fecha_regreso) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="mb-4">
        <label class="field-label">Duración del Permiso</label>
        <div class="info-field duracion-field">
          <i class="fa-solid fa-calendar-days" style="color: #A37801; margin-right: 8px;"></i>
          {{ calculateDays(permiso.fecha_salida, permiso.fecha_regreso) }} días
        </div>
      </div>

      <div v-if="permiso.Fecha_solicitada" class="mb-4">
        <label class="field-label">Fecha de Solicitud</label>
        <div class="info-field">
          <i class="fa-solid fa-clock" style="color: #A37801; margin-right: 8px;"></i>
          {{ formatFechaCompleta(permiso.Fecha_solicitada) }}
        </div>
      </div>

      <div class="mb-4">
        <label class="field-label">Motivo del Permiso</label>
        <div class="motivo-container">
          <i class="fa-solid fa-comment-dots" style="color: #A37801; margin-right: 8px;"></i>
          <p class="motivo-texto">{{ permiso.motivo || 'Sin motivo especificado' }}</p>
        </div>
      </div>

      <div v-if="permiso.archivo_justificacion" class="mb-6">
        <label class="field-label">Archivo de Justificación</label>
        <div class="archivo-container">
          <div class="archivo-preview">
            <div class="archivo-icon">
              <i class="fa-solid fa-file-alt"></i>
            </div>
            <div class="archivo-info">
              <span class="archivo-nombre">{{ getFileName(permiso.archivo_justificacion) }}</span>
              <span class="archivo-accion">Archivo de justificación</span>
            </div>
          </div>
          <button 
            @click="downloadFile(permiso.archivo_justificacion)"
            class="btn-descargar-archivo"
          >
            <i class="fa-solid fa-download"></i>
            Descargar Archivo
          </button>
        </div>
      </div>

      <div v-if="isAdmin && permiso.estado === 'En revisión'" class="acciones-container">
        <div class="acciones-header">
          <i class="fa-solid fa-clipboard-check" style="color: #A37801; margin-right: 8px;"></i>
          <span>Acciones del Administrador</span>
        </div>
        <div class="acciones-buttons">
          <button 
            @click="actualizarEstado('Aprobado')"
            class="btn-accion aprobar"
            :disabled="procesando"
          >
            <i class="fa-solid fa-check"></i>
            <span>{{ procesando ? 'Procesando...' : 'Aprobar Permiso' }}</span>
          </button>
          <button 
            @click="actualizarEstado('Denegado')"
            class="btn-accion rechazar"
            :disabled="procesando"
          >
            <i class="fa-solid fa-times"></i>
            <span>{{ procesando ? 'Procesando...' : 'Rechazar Permiso' }}</span>
          </button>
        </div>
      </div>

      <div v-if="permiso.estado !== 'En revisión'" class="estado-final-info">
        <div class="estado-final-header">
          <i :class="getEstadoIcon(permiso.estado)" :style="{ color: getEstadoColor(permiso.estado) }"></i>
          <span>Este permiso ya ha sido {{ permiso.estado.toLowerCase() }}</span>
        </div>
      </div>
    </div>
  </ContainerModal>
</template>

<script setup>
import { ref, computed } from 'vue'
import ContainerModal from '@/components/layout/ContainerModal.vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  permiso: {
    type: Object,
    default: null
  },
  isAdmin: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'estado-actualizado'])

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const procesando = ref(false)

const getEstadoCardClass = (estado) => {
  switch (estado?.toLowerCase()) {
    case 'aprobado':
      return 'estado-aprobado'
    case 'denegado':
      return 'estado-denegado'
    case 'en revisión':
      return 'estado-pendiente'
    default:
      return 'estado-default'
  }
}

const getEstadoIcon = (estado) => {
  switch (estado?.toLowerCase()) {
    case 'aprobado':
      return 'fa-solid fa-check-circle'
    case 'denegado':
      return 'fa-solid fa-times-circle'
    case 'en revisión':
      return 'fa-solid fa-clock'
    default:
      return 'fa-solid fa-question-circle'
  }
}

const getEstadoColor = (estado) => {
  switch (estado?.toLowerCase()) {
    case 'aprobado':
      return '#4caf50'
    case 'denegado':
      return '#f44336'
    case 'en revisión':
      return '#ff9800'
    default:
      return '#757575'
  }
}

const formatFecha = (fecha) => {
  if (!fecha) return 'No especificada'
  const date = new Date(fecha)
  return date.toLocaleDateString('es-ES', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const formatFechaCompleta = (fecha) => {
  if (!fecha) return 'No especificada'
  const date = new Date(fecha)
  return date.toLocaleDateString('es-ES', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const calculateDays = (startDate, endDate) => {
  if (!startDate || !endDate) return 0
  const start = new Date(startDate)
  const end = new Date(endDate)
  const diffTime = Math.abs(end - start)
  return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1
}

const getFileName = (archivo) => {
  if (!archivo) return 'archivo_justificacion'
  return archivo.split('/').pop() || archivo
}

const viewFile = (url) => {
  window.open(url, '_blank', 'noopener,noreferrer')
}

const downloadFile = (fileName) => {
  if (!fileName) return
  
  const baseUrl = 'http://localhost:5000/uploads/justificacion/'
  const fileUrl = baseUrl + fileName
  
  const link = document.createElement('a')
  link.href = fileUrl
  link.download = fileName
  link.target = '_blank'
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const actualizarEstado = async (nuevoEstado) => {
  if (!props.permiso?.id) return
  
  procesando.value = true
  
  try {
    emit('estado-actualizado', {
      id: props.permiso.id,
      estado: nuevoEstado
    })
    
    setTimeout(() => {
      dialog.value = false
    }, 500)
  } catch (error) {
    console.error('Error al actualizar estado:', error)
  } finally {
    procesando.value = false
  }
}
</script>

<style scoped>
.contenido-modal {
  padding: 0;
}

.field-label {
  font-size: 18px;
  color: #333;
  font-weight: 600;
  margin-bottom: 8px;
  display: block;
}

.info-cards-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 8px;
}

.info-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: white;
}

.empleado-card .card-icon {
  background: linear-gradient(135deg, #2196f3, #1976d2);
}

.estado-card .card-icon {
  background: #6c757d;
}

.estado-aprobado .card-icon {
  background: linear-gradient(135deg, #4caf50, #388e3c);
}

.estado-denegado .card-icon {
  background: linear-gradient(135deg, #f44336, #d32f2f);
}

.estado-pendiente .card-icon {
  background: linear-gradient(135deg, #ff9800, #f57c00);
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.card-label {
  font-size: 12px;
  color: #6c757d;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-value {
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.estado-value {
  text-transform: uppercase;
}

.fechas-container {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e9ecef;
}

.fecha-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
}

.fecha-icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: white;
}

.fecha-icon.salida {
  background: linear-gradient(135deg, #f44336, #d32f2f);
}

.fecha-icon.regreso {
  background: linear-gradient(135deg, #4caf50, #388e3c);
}

.fecha-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  flex: 1;
}

.fecha-tipo {
  font-size: 12px;
  color: #6c757d;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.fecha-valor {
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.fecha-separador {
  color: #A37801;
  font-size: 20px;
  margin: 0 8px;
}

.info-field {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 12px 16px;
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

.duracion-field {
  background: linear-gradient(135deg, #fff3cd, #ffeaa7);
  border-color: #A37801;
  color: #A37801;
  font-weight: 600;
}

.motivo-container {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.motivo-texto {
  margin: 0;
  font-size: 16px;
  line-height: 1.5;
  color: #333;
}

.archivo-container {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 16px;
}

.archivo-preview {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 12px;
  border-radius: 8px;
  transition: background-color 0.2s ease;
}

.archivo-preview:hover {
  background: rgba(163, 120, 1, 0.1);
}

.archivo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #A37801, #8a6600);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
}

.archivo-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.archivo-nombre {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.archivo-accion {
  font-size: 12px;
  color: #6c757d;
}

.btn-ver-archivo {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #A37801;
  color: white;
  border-radius: 8px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-ver-archivo:hover {
  background: #8a6600;
  transform: translateY(-1px);
}

.btn-descargar-archivo {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-descargar-archivo:hover {
  background: #1d4ed8;
  transform: translateY(-1px);
}

.acciones-container {
  background: linear-gradient(135deg, #fff9e6, #fef3e2);
  border: 2px solid #A37801;
  border-radius: 12px;
  padding: 20px;
  margin-top: 8px;
}

.acciones-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
  color: #A37801;
}

.acciones-buttons {
  display: flex;
  gap: 12px;
}

.btn-accion {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-accion:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-accion.aprobar {
  background: linear-gradient(135deg, #4caf50, #388e3c);
  color: white;
}

.btn-accion.aprobar:hover:not(:disabled) {
  background: linear-gradient(135deg, #388e3c, #2e7d32);
  transform: translateY(-1px);
}

.btn-accion.rechazar {
  background: linear-gradient(135deg, #f44336, #d32f2f);
  color: white;
}

.btn-accion.rechazar:hover:not(:disabled) {
  background: linear-gradient(135deg, #d32f2f, #c62828);
  transform: translateY(-1px);
}

.estado-final-info {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-top: 8px;
  text-align: center;
}

.estado-final-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  color: #6c757d;
}

@media (max-width: 768px) {
  .info-cards-container {
    grid-template-columns: 1fr;
  }
  
  .fechas-container {
    flex-direction: column;
    gap: 16px;
  }
  
  .fecha-separador {
    transform: rotate(90deg);
  }
  
  .acciones-buttons {
    flex-direction: column;
  }
  
  .archivo-container {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
