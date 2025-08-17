<template>
  <ContainerModal
    v-model="dialog"
    :title="`${solicitud?.titulo || 'Detalle de la Solicitud'}`"
    :max-width="600"
    :colorTheme="'#CF990D'"
  >
    <div class="contenido-modal">
      <div class="mb-6">
        <div class="info-cards-container">
          <div class="info-card tipo-card">
            <div class="card-icon">
              <i class="fa-solid fa-tag"></i>
            </div>
            <div class="card-content">
              <span class="card-label">Tipo de Actividad</span>
              <span class="card-value tipo-value">{{ solicitud.tipo }}</span>
            </div>
          </div>

          <div class="info-card estado-card" :class="getEstadoCardClass(solicitud.estado)">
            <div class="card-icon">
              <i :class="getEstadoIcon(solicitud.estado)"></i>
            </div>
            <div class="card-content">
              <span class="card-label">Estado</span>
              <span class="card-value estado-value">{{ solicitud.estado }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Código de
          Solicitud</label>
        <div class="info-field">
          <i class="fa-solid fa-hashtag" style="color: #CF990D; margin-right: 8px;"></i>
          UNMSM-{{ solicitud.id }}
        </div>
      </div>

      <div v-if="solicitud.archivo" class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">
          {{ isImageFile(solicitud.archivo) ? 'Imagen de la solicitud' : 'Archivo de la solicitud' }}
        </label>
        <v-card class="archivo-container" @click="handleFileClick(solicitud.archivo)" style="cursor: pointer;">
          <n-image 
            v-if="isImageFile(solicitud.archivo)"
            :src="getImageUrl(solicitud.archivo)" 
            :alt="solicitud.titulo"
            object-fit="cover"
            :style="{ width: '100%', height: '200px', borderRadius: '8px' }"
            :preview-disabled="false"
          />
          <div v-else-if="isPDFFile(solicitud.archivo)" class="file-placeholder pdf-file" style="height: 200px;">
            <i class="fa-solid fa-file-pdf" style="font-size: 64px; color: #d32f2f;"></i>
            <span class="file-label">PDF</span>
            <span class="file-name">{{ solicitud.archivo.split('/').pop() }}</span>
          </div>
          <div v-else-if="isWordFile(solicitud.archivo)" class="file-placeholder word-file" style="height: 200px;">
            <i class="fa-solid fa-file-word" style="font-size: 64px; color: #1976d2;"></i>
            <span class="file-label">WORD</span>
            <span class="file-name">{{ solicitud.archivo.split('/').pop() }}</span>
          </div>
          <div v-else class="file-placeholder generic-file" style="height: 200px;">
            <i class="fa-solid fa-file" style="font-size: 64px; color: #757575;"></i>
            <span class="file-label">ARCHIVO</span>
            <span class="file-name">{{ solicitud.archivo.split('/').pop() }}</span>
          </div>
        </v-card>
      </div>

      <div class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Fecha de
          Solicitud</label>
        <div class="info-field">
          <i class="fa-solid fa-calendar-plus" style="color: #CF990D; margin-right: 8px;"></i>
          {{ formatearFechaSolicitud(solicitud.fecha_solicitud) }}
        </div>
      </div>

      <div class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Fecha
          Propuesta
          para la Actividad</label>
        <div class="info-field">
          <i class="fa-solid fa-calendar-check" style="color: #CF990D; margin-right: 8px;"></i>
          {{ formatearFechaSolicitud(solicitud.fecha_actividad) }}
        </div>
      </div>

      <div class="mb-4">
        <label
          style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Descripción</label>
        <div class="info-field descripcion-text">
          {{ solicitud.descripcion }}
        </div>
      </div>

      <div class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Cupos
          Solicitado</label>
        <div class="info-field">
          <i class="fa-solid fa-users" style="color: #CF990D; margin-right: 8px;"></i>
          {{ solicitud.stock }} participantes
        </div>
      </div>

      <div v-if="solicitud.motivo_cancelacion" class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">
          Motivo de Cancelación
        </label>
        <v-card class="motivo-cancelacion-card" elevation="0" variant="outlined">
          <v-card-text class="motivo-cancelacion-content">
            <div class="d-flex align-start">
              <i class="fa-solid fa-exclamation-triangle" style="color: #f44336; margin-right: 12px; margin-top: 2px; font-size: 18px;"></i>
              <div class="motivo-text">
                {{ solicitud.motivo_cancelacion }}
              </div>
            </div>
          </v-card-text>
        </v-card>
      </div>

      <div v-if="!isAdmin">
        <div v-if="isEstadoPendiente(solicitud.estado)" class="mb-4">
          <v-alert type="warning" variant="tonal" :icon="false" class="mb-0">
            <div class="d-flex align-center" style="gap: 10px;">
              <i class="fa-solid fa-clock"></i>
              Tu solicitud de actividad está pendiente de revisión por parte del equipo administrativo.
            </div>
          </v-alert>
        </div>

        <div v-if="isEstadoAprobado(solicitud.estado)" class="mb-4">
          <v-alert type="success" variant="tonal" :icon="false" class="mb-0">
            <div class="d-flex align-center" style="gap: 10px;">
              <i class="fa-solid fa-check-circle"></i>
              ¡Excelente! Tu solicitud ha sido aprobada. La actividad estará disponible próximamente para inscripciones.
            </div>
          </v-alert>
        </div>

        <div v-if="isEstadoDenegado(solicitud.estado)" class="mb-4">
          <v-alert type="error" variant="tonal" :icon="false" class="mb-0">
            <div class="d-flex align-center" style="gap: 10px;">
              <i class="fa-solid fa-times-circle"></i>
              Tu solicitud ha sido denegada por el administrador. Puedes contactar al equipo administrativo para conocer
              los
              motivos.
            </div>
          </v-alert>
        </div>
      </div>

      <div v-if="isAdmin && isEstadoPendiente(solicitud.estado)" class="d-flex justify-center mt-6" style="gap: 20px;">
        <v-btn @click="aprobarSolicitud" color="#CF990D" size="large"
          style="border-radius: 20px; text-transform: none; font-weight: 500" min-width="120px"
          :loading="actualizandoEstado" :disabled="actualizandoEstado">
          Aprobar
        </v-btn>

        <v-btn @click="denegarSolicitud" color="#CF990D" size="large"
          style="border-radius: 20px; text-transform: none; font-weight: 500" min-width="120px"
          :loading="actualizandoEstado" :disabled="actualizandoEstado">
          Denegar
        </v-btn>
      </div>
    </div>

    <v-dialog v-model="showMotivoModal" max-width="500px" persistent>
      <v-card class="motivo-modal">
        <v-card-title class="motivo-modal-title">
          <i class="fa-solid fa-exclamation-triangle" style="color: #f44336; margin-right: 12px;"></i>
          Denegar Solicitud
        </v-card-title>
        
        <v-card-text class="motivo-modal-content">
          <p class="motivo-descripcion">
            Estás a punto de denegar la solicitud "<strong>{{ solicitud.titulo }}</strong>". 
            Por favor, proporciona un motivo para esta decisión:
          </p>
          
          <v-textarea
            v-model="motivoDenegacion"
            label="Motivo"
            placeholder="Explica las razones por las cuales se deniega esta solicitud..."
            variant="outlined"
            rows="4"
            counter="500"
            maxlength="500"
            class="motivo-textarea"
            :rules="[v => !!v.trim() || 'El motivo es requerido']"
          >
            <template v-slot:prepend-inner>
              <i class="fa-solid fa-comment-dots" style="color: #666; margin-right: 8px; margin-top: 8px;"></i>
            </template>
          </v-textarea>
        </v-card-text>
        
        <v-card-actions class="motivo-modal-actions">
          <v-btn
            @click="cancelarDenegacion"
            variant="outlined"
            color="grey"
            :disabled="actualizandoEstado"
          >
            Cancelar
          </v-btn>
          
          <v-spacer></v-spacer>
          
          <v-btn
            @click="confirmarDenegacion"
            color="#f44336"
            variant="flat"
            :loading="actualizandoEstado"
            :disabled="!motivoDenegacion.trim() || actualizandoEstado"
          >
            <i class="fa-solid fa-times-circle" style="margin-right: 8px;"></i>
            Confirmar Denegación
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000" location="top center"
      style="z-index: 9999;">
      <div class="text-center font-weight-medium">
        {{ snackbar.message }}
      </div>
    </v-snackbar>
  </ContainerModal>
</template>

<script setup>
import { computed, ref } from 'vue'
import { NImage } from 'naive-ui'
import ActividadesService from '@/services/ActividadesService'
import ContainerModal from '@/components/layout/ContainerModal.vue'

const props = defineProps({
  modelValue: Boolean,
  solicitud: {
    type: Object,
    default: () => ({})
  },
  isAdmin: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'estadoActualizado'])

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const actualizandoEstado = ref(false)
const showMotivoModal = ref(false)
const motivoDenegacion = ref('')

const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
})

function mostrarNotificacion(mensaje, tipo = 'success') {
  snackbar.value = {
    show: true,
    message: mensaje,
    color: tipo
  }
}

function getImageUrl(archivo) {
  return `${archivo}`
}

function isImageFile(archivo) {
  if (!archivo) return false
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']
  const extension = archivo.toLowerCase().substring(archivo.lastIndexOf('.'))
  return imageExtensions.includes(extension)
}

function isPDFFile(archivo) {
  if (!archivo) return false
  return archivo.toLowerCase().endsWith('.pdf')
}

function isWordFile(archivo) {
  if (!archivo) return false
  const wordExtensions = ['.doc', '.docx']
  const extension = archivo.toLowerCase().substring(archivo.lastIndexOf('.'))
  return wordExtensions.includes(extension)
}

function handleFileClick(archivo) {
  if (!isImageFile(archivo)) {
    downloadFile(archivo)
  }
}

function downloadFile(archivo) {
  const link = document.createElement('a')
  link.href = getImageUrl(archivo)
  link.download = archivo.split('/').pop() || 'archivo'
  link.target = '_blank'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

function getEstadoCardClass(estado) {
  switch (estado) {
    case 'Aprobado':
      return 'estado-card-aprobada'
    case 'Cancelado':
      return 'estado-card-rechazada'
    case 'Pendiente':
    default:
      return 'estado-card-pendiente'
  }
}

function getEstadoIcon(estado) {
  switch (estado) {
    case 'Aprobado':
      return 'fa-solid fa-check-circle'
    case 'Cancelado':
      return 'fa-solid fa-times-circle'
    case 'Pendiente':
    default:
      return 'fa-solid fa-clock'
  }
}

function isEstadoPendiente(estado) {
  return estado === 'Pendiente'
}

function isEstadoAprobado(estado) {
  return estado === 'Aprobado'
}

function isEstadoDenegado(estado) {
  return estado === 'Cancelado'
}

async function aprobarSolicitud() {
  try {
    actualizandoEstado.value = true
    await ActividadesService.actualizarEstado(props.solicitud.id, 'Aprobado', '')
    mostrarNotificacion('Solicitud aprobada exitosamente', 'success')
    emit('estadoActualizado')

    setTimeout(() => {
      dialog.value = false
    }, 1500)
  } catch (error) {
    console.error('Error al aprobar solicitud:', error)
    mostrarNotificacion('Error al aprobar la solicitud', 'error')
  } finally {
    actualizandoEstado.value = false
  }
}

async function denegarSolicitud() {
  showMotivoModal.value = true
}

async function confirmarDenegacion() {
  if (!motivoDenegacion.value.trim()) {
    mostrarNotificacion('Por favor, ingresa un motivo para la denegación', 'error')
    return
  }

  try {
    actualizandoEstado.value = true
    showMotivoModal.value = false
    
    await ActividadesService.actualizarEstado(props.solicitud.id, 'Cancelado', motivoDenegacion.value.trim())
    mostrarNotificacion('Solicitud cancelada exitosamente', 'warning')
    emit('estadoActualizado')

    setTimeout(() => {
      dialog.value = false
      motivoDenegacion.value = ''
    }, 1500)
  } catch (error) {
    console.error('Error al cancelar solicitud:', error)
    mostrarNotificacion('Error al cancelar la solicitud', 'error')
  } finally {
    actualizandoEstado.value = false
  }
}

function formatearFechaSolicitud(fecha) {
  if (!fecha) return 'No especificada'
  
  const date = new Date(fecha)
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function cancelarDenegacion() {
  showMotivoModal.value = false
  motivoDenegacion.value = ''
}
</script>

<style scoped>
.info-cards-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 8px;
}

.info-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 2px solid transparent;
  transition: all 0.3s ease;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
}

.card-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: white;
  flex-shrink: 0;
}

.tipo-card .card-icon {
  background: linear-gradient(135deg, #CF990D 0%, #d63384 100%);
}

.card-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.card-label {
  font-size: 12px;
  font-weight: 500;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.card-value {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.estado-card-pendiente {
  border-color: #ff9800;
  background: linear-gradient(135deg, #fff3e0 0%, #ffffff 100%);
}

.estado-card-pendiente .card-icon {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
}

.estado-card-aprobada {
  border-color: #4caf50;
  background: linear-gradient(135deg, #e8f5e8 0%, #ffffff 100%);
}

.estado-card-aprobada .card-icon {
  background: linear-gradient(135deg, #4caf50 0%, #388e3c 100%);
}

.estado-card-rechazada {
  border-color: #f44336;
  background: linear-gradient(135deg, #ffebee 0%, #ffffff 100%);
}

.estado-card-rechazada .card-icon {
  background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
}

@media (max-width: 600px) {
  .info-cards-container {
    grid-template-columns: 1fr;
  }

  .info-card {
    padding: 16px;
  }

  .card-icon {
    width: 40px;
    height: 40px;
    font-size: 16px;
  }
}

.info-field {
  background-color: #f8f9fa;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  font-size: 16px;
  display: flex;
  align-items: center;
}

.descripcion-text {
  line-height: 1.5;
  text-align: justify;
}

.archivo-container {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.archivo-container:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
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
  gap: 12px;
  padding: 20px;
}

.file-placeholder:hover {
  transform: scale(1.02);
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
  font-size: 14px;
  font-weight: 600;
  color: #424242;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-top: 8px;
}

.file-name {
  font-size: 12px;
  font-weight: 400;
  color: #666;
  text-align: center;
  max-width: 200px;
  word-break: break-word;
  margin-top: 4px;
}

.contenido-modal::-webkit-scrollbar {
  width: 6px;
}

.contenido-modal::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.contenido-modal::-webkit-scrollbar-thumb {
  background: #CF990D;
  border-radius: 3px;
}

.contenido-modal::-webkit-scrollbar-thumb:hover {
  background: #8a0030;
}

.motivo-modal {
  border-radius: 16px !important;
  overflow: hidden;
}

.motivo-modal-title {
  background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
  color: #d32f2f;
  padding: 20px 24px;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 1px solid #ffcdd2;
}

.motivo-modal-content {
  padding: 24px !important;
}

.motivo-descripcion {
  margin-bottom: 20px;
  color: #333;
  line-height: 1.5;
  font-size: 14px;
}

.motivo-textarea :deep(.v-field) {
  border-radius: 12px !important;
}

.motivo-textarea :deep(.v-field--focused) {
  border-color: #f44336 !important;
  box-shadow: 0 0 0 2px rgba(244, 67, 54, 0.2) !important;
}

.motivo-modal-actions {
  padding: 16px 24px 24px !important;
  background: #fafafa;
}

.motivo-modal-actions .v-btn {
  border-radius: 8px !important;
  text-transform: none !important;
  font-weight: 500 !important;
}

.motivo-cancelacion-card {
  border-color: #f44336 !important;
  border-width: 2px !important;
  background: #ffebee !important;
}

.motivo-cancelacion-content {
  padding: 16px !important;
}

.motivo-text {
  flex: 1;
  color: #d32f2f;
  font-size: 14px;
  line-height: 1.5;
  font-weight: 500;
}
</style>
