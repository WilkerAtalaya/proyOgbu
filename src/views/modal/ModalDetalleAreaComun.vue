<template>
  <ContainerModal 
    v-model="dialog" 
    :title="`Reserva de Área Común #${reserva?.id || 'N/A'}`" 
    :max-width="650"
    :colorTheme="'#53696D'"
  >
    <div v-if="reserva" class="contenido-modal">
      <div class="mb-6">
        <div class="info-cards-container">
          <div class="info-card empleado-card">
            <div class="card-icon">
              <i class="fa-solid fa-user"></i>
            </div>
            <div class="card-content">
              <span class="card-label">Residente</span>
              <span class="card-value empleado-value">{{ reserva.nombre_usuario }}</span>
            </div>
          </div>

          <div class="info-card estado-card" :class="getEstadoCardClass(reserva.estado)">
            <div class="card-icon">
              <i :class="getEstadoIcon(reserva.estado)"></i>
            </div>
            <div class="card-content">
              <span class="card-label">Estado</span>
              <span class="card-value estado-value">{{ reserva.estado }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="mb-4">
        <label class="field-label">Lugar Reservado</label>
        <div class="lugar-container">
          <div class="lugar-icon">
            <i class="fa-solid fa-map-marker-alt"></i>
          </div>
          <div class="lugar-info">
            <span class="lugar-nombre">{{ reserva.lugar }}</span>
            <span class="lugar-fecha">{{ formatFecha(reserva.fecha) }}</span>
          </div>
        </div>
      </div>

      <div class="mb-4">
        <label class="field-label">Horario de Reserva</label>
        <div class="info-field horario-field">
          <i class="fa-solid fa-clock" style="color: #53696D; margin-right: 8px;"></i>
          {{ reserva.horario }}
        </div>
      </div>

      <div v-if="reserva.Fecha_solicitada" class="mb-4">
        <label class="field-label">Fecha de Solicitud</label>
        <div class="info-field">
          <i class="fa-solid fa-calendar-plus" style="color: #53696D; margin-right: 8px;"></i>
          {{ formatFechaCompleta(reserva.Fecha_solicitada) }}
        </div>
      </div>

      <div class="mb-4">
        <label class="field-label">Motivo de la Reserva</label>
        <div class="motivo-container">
          <i class="fa-solid fa-comment-dots" style="color: #53696D; margin-right: 8px;"></i>
          <p class="motivo-texto">{{ reserva.motivo || 'Sin motivo especificado' }}</p>
        </div>
      </div>

      <div class="mb-6">
        <div class="info-adicional-container">
          <div class="info-adicional-item">
            <div class="info-icon">
              <i class="fa-solid fa-hashtag"></i>
            </div>
            <div class="info-content">
              <span class="info-label">ID Usuario</span>
              <span class="info-value">{{ reserva.id_usuario }}</span>
            </div>
          </div>
          <div class="info-adicional-item">
            <div class="info-icon">
              <i class="fa-solid fa-calendar-check"></i>
            </div>
            <div class="info-content">
              <span class="info-label">ID Reserva</span>
              <span class="info-value">{{ reserva.id }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="isAdmin && reserva.estado === 'En revisión'" class="acciones-container">
        <div class="acciones-header">
          <i class="fa-solid fa-clipboard-check" style="color: #53696D; margin-right: 8px;"></i>
          <span>Acciones del Administrador</span>
        </div>
        <div class="acciones-buttons">
          <button 
            @click="actualizarEstado('Aprobado')"
            class="btn-accion aprobar"
            :disabled="procesando"
          >
            <i class="fa-solid fa-check"></i>
            <span>{{ procesando ? 'Procesando...' : 'Aprobar Reserva' }}</span>
          </button>
          <button 
            @click="actualizarEstado('Denegado')"
            class="btn-accion rechazar"
            :disabled="procesando"
          >
            <i class="fa-solid fa-times"></i>
            <span>{{ procesando ? 'Procesando...' : 'Rechazar Reserva' }}</span>
          </button>
        </div>
      </div>

      <div v-if="reserva.estado !== 'En revisión'" class="estado-final-info">
        <div class="estado-final-header">
          <i :class="getEstadoIcon(reserva.estado)" :style="{ color: getEstadoColor(reserva.estado) }"></i>
          <span>Esta reserva ya ha sido {{ reserva.estado.toLowerCase() }}</span>
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
  reserva: {
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

const actualizarEstado = async (nuevoEstado) => {
  if (!props.reserva?.id) return
  
  procesando.value = true
  
  try {
    emit('estado-actualizado', {
      id: props.reserva.id,
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

.lugar-container {
  display: flex;
  align-items: center;
  gap: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e9ecef;
}

.lugar-icon {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #53696D, #3e5357);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: white;
}

.lugar-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.lugar-nombre {
  font-size: 18px;
  color: #333;
  font-weight: 600;
}

.lugar-fecha {
  font-size: 14px;
  color: #6c757d;
  font-weight: 500;
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

.horario-field {
  background: linear-gradient(135deg, #e8f5e8, #c8e6c9);
  border-color: #53696D;
  color: #53696D;
  font-weight: 600;
  font-size: 18px;
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

.info-adicional-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
  border: 1px solid #e9ecef;
}

.info-adicional-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #53696D, #3e5357);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 16px;
}

.info-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.info-label {
  font-size: 11px;
  color: #6c757d;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 14px;
  color: #333;
  font-weight: 600;
}

.acciones-container {
  background: linear-gradient(135deg, #e8f4f8, #e1f0f5);
  border: 2px solid #53696D;
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
  color: #53696D;
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
  
  .info-adicional-container {
    grid-template-columns: 1fr;
  }
  
  .acciones-buttons {
    flex-direction: column;
  }
}
</style>
