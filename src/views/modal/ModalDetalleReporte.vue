<template>
  <ContainerModal 
    v-model="dialog" 
    :title="`Reporte #${reporte?.numero || 'N/A'}`" 
    :max-width="650"
    :colorTheme="'#A37801'"
  >
    <div v-if="reporte" class="contenido-modal">
      <div class="mb-6">
        <div class="info-cards-container">
          <div class="info-card empleado-card">
            <div class="card-icon">
              <i class="fa-solid fa-exclamation-triangle"></i>
            </div>
            <div class="card-content">
              <span class="card-label">Reporte</span>
              <span class="card-value empleado-value">{{ reporte.numero }}</span>
            </div>
          </div>

          <div class="info-card estado-card" :class="getEstadoCardClass(reporte.estado)">
            <div class="card-icon">
              <i :class="getEstadoIcon(reporte.estado)"></i>
            </div>
            <div class="card-content">
              <span class="card-label">Estado</span>
              <span class="card-value estado-value">{{ reporte.estado }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="mb-4">
        <label class="field-label">Asunto del Reporte</label>
        <div class="info-field asunto-field">
          <i class="fa-solid fa-clipboard-question" style="color: #A37801; margin-right: 8px;"></i>
          {{ reporte.asunto }}
        </div>
      </div>

      <div class="mb-4">
        <label class="field-label">Motivo/Categoría</label>
        <div class="info-field motivo-field">
          <i class="fa-solid fa-tag" style="color: #A37801; margin-right: 8px;"></i>
          {{ reporte.motivo }}
        </div>
      </div>

      <div class="mb-4">
        <label class="field-label">Fecha del Reporte</label>
        <div class="info-field">
          <i class="fa-solid fa-calendar" style="color: #A37801; margin-right: 8px;"></i>
          {{ fechaFormateada }}
        </div>
      </div>

      <div class="mb-4">
        <label class="field-label">Descripción Detallada</label>
        <div class="descripcion-container">
          <i class="fa-solid fa-comment-dots" style="color: #A37801; margin-right: 8px;"></i>
          <p class="descripcion-texto">{{ reporte.descripcion || 'Sin descripción proporcionada' }}</p>
        </div>
      </div>

      <div v-if="reporte.prueba" class="mb-6">
        <label class="field-label">Archivo de Evidencia</label>
        <div class="archivo-container">
          <div class="archivo-preview">
            <div class="archivo-icon">
              <i class="fa-solid fa-file-image"></i>
            </div>
            <div class="archivo-info">
              <span class="archivo-nombre">{{ getFileName(reporte.prueba) }}</span>
              <span class="archivo-accion">Evidencia adjunta</span>
            </div>
          </div>
          <button 
            @click="downloadFile(reporte.prueba)"
            class="btn-descargar-archivo"
          >
            <i class="fa-solid fa-download"></i>
            Descargar Evidencia
          </button>
        </div>
      </div>

      <div v-if="isAdmin && puedeActualizar(reporte.estado)" class="acciones-container">
        <div class="acciones-header">
          <i class="fa-solid fa-clipboard-check" style="color: #A37801; margin-right: 8px;"></i>
          <span>Acciones del Administrador</span>
        </div>
        <div class="acciones-grid">
          <button 
            @click="actualizarEstado('En revisión')"
            class="btn-accion revision"
            :disabled="procesando || reporte.estado === 'En revisión'"
          >
            <i class="fa-solid fa-eye"></i>
            <span>{{ procesando ? 'Procesando...' : 'En Revisión' }}</span>
          </button>
          <button 
            @click="actualizarEstado('En proceso')"
            class="btn-accion proceso"
            :disabled="procesando || reporte.estado === 'En proceso'"
          >
            <i class="fa-solid fa-cogs"></i>
            <span>{{ procesando ? 'Procesando...' : 'En Proceso' }}</span>
          </button>
          <button 
            @click="actualizarEstado('Resuelto')"
            class="btn-accion resuelto"
            :disabled="procesando || reporte.estado === 'Resuelto'"
          >
            <i class="fa-solid fa-check"></i>
            <span>{{ procesando ? 'Procesando...' : 'Resolver' }}</span>
          </button>
          <button 
            @click="actualizarEstado('Cerrado')"
            class="btn-accion cerrado"
            :disabled="procesando || reporte.estado === 'Cerrado'"
          >
            <i class="fa-solid fa-flag-checkered"></i>
            <span>{{ procesando ? 'Procesando...' : 'Cerrar' }}</span>
          </button>
        </div>
      </div>

      <div v-if="!puedeActualizar(reporte.estado)" class="estado-final-info">
        <div class="estado-final-header">
          <i :class="getEstadoIcon(reporte.estado)" :style="{ color: getEstadoColor(reporte.estado) }"></i>
          <span>Este reporte se encuentra {{ reporte.estado.toLowerCase() }}</span>
        </div>
      </div>
    </div>
  </ContainerModal>
</template>

<script setup>
import { ref, computed } from 'vue'
import ContainerModal from '@/components/layout/ContainerModal.vue'
import { formatBackendDate } from '@/util/functions.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  reporte: {
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

const fechaFormateada = computed(() => {
  if (!props.reporte?.fecha) return 'Sin fecha'
  return formatBackendDate(props.reporte.fecha, true)
})

const getEstadoCardClass = (estado) => {
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

const getEstadoIcon = (estado) => {
  switch (estado?.toLowerCase()) {
    case 'resuelto':
      return 'fa-solid fa-check-circle'
    case 'cerrado':
      return 'fa-solid fa-flag-checkered'
    case 'en proceso':
      return 'fa-solid fa-cogs'
    case 'en revisión':
      return 'fa-solid fa-eye'
    case 'recibido':
    default:
      return 'fa-solid fa-clock'
  }
}

const getEstadoColor = (estado) => {
  switch (estado?.toLowerCase()) {
    case 'resuelto':
      return '#4caf50'
    case 'cerrado':
      return '#2196f3'
    case 'en proceso':
      return '#03a9f4'
    case 'en revisión':
      return '#ff9800'
    case 'recibido':
    default:
      return '#ffc107'
  }
}

const puedeActualizar = (estado) => {
  return estado !== 'Resuelto' && estado !== 'Cerrado'
}

const getFileName = (archivo) => {
  if (!archivo) return 'evidencia'
  return archivo.split('/').pop() || archivo
}

const downloadFile = (fileUrl) => {
  if (!fileUrl) return
  
  const link = document.createElement('a')
  link.href = fileUrl
  link.download = fileUrl.split('/').pop()
  link.target = '_blank'
  
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const actualizarEstado = async (nuevoEstado) => {
  if (!props.reporte?.id) return
  
  procesando.value = true
  
  try {
    emit('estado-actualizado', {
      id: props.reporte.id,
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
  background: linear-gradient(135deg, #ff9800, #f57c00);
}

.estado-card .card-icon {
  background: #6c757d;
}

.estado-resuelto .card-icon {
  background: linear-gradient(135deg, #4caf50, #388e3c);
}

.estado-cerrado .card-icon {
  background: linear-gradient(135deg, #2196f3, #1976d2);
}

.estado-proceso .card-icon {
  background: linear-gradient(135deg, #03a9f4, #0288d1);
}

.estado-revision .card-icon {
  background: linear-gradient(135deg, #ff9800, #f57c00);
}

.estado-recibido .card-icon {
  background: linear-gradient(135deg, #ffc107, #ff8f00);
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

.asunto-field {
  background: linear-gradient(135deg, #fff3cd, #ffeaa7);
  border-color: #A37801;
  color: #A37801;
  font-weight: 600;
}

.motivo-field {
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  border-color: #2196f3;
  color: #1976d2;
  font-weight: 600;
}

.descripcion-container {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.descripcion-texto {
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

.acciones-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.btn-accion {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
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

.btn-accion.revision {
  background: linear-gradient(135deg, #ff9800, #f57c00);
  color: white;
}

.btn-accion.revision:hover:not(:disabled) {
  background: linear-gradient(135deg, #f57c00, #ef6c00);
  transform: translateY(-1px);
}

.btn-accion.proceso {
  background: linear-gradient(135deg, #03a9f4, #0288d1);
  color: white;
}

.btn-accion.proceso:hover:not(:disabled) {
  background: linear-gradient(135deg, #0288d1, #0277bd);
  transform: translateY(-1px);
}

.btn-accion.resuelto {
  background: linear-gradient(135deg, #4caf50, #388e3c);
  color: white;
}

.btn-accion.resuelto:hover:not(:disabled) {
  background: linear-gradient(135deg, #388e3c, #2e7d32);
  transform: translateY(-1px);
}

.btn-accion.cerrado {
  background: linear-gradient(135deg, #2196f3, #1976d2);
  color: white;
}

.btn-accion.cerrado:hover:not(:disabled) {
  background: linear-gradient(135deg, #1976d2, #1565c0);
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
  
  .acciones-grid {
    grid-template-columns: 1fr;
  }
  
  .archivo-container {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
