<template>
  <ContainerModal v-model="dialog" :title="`${actividad?.titulo || 'Detalle de la Actividad'}`" :max-width="600"
    :colorTheme="'#71C82F'">
    <div v-if="actividad" class="contenido-modal">
      <div class="mb-4">
        <div class="tipo-badge">
          {{ actividad.tipo }}
        </div>
      </div>

      <div v-if="actividad.archivo" class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">
          {{ isImageFile(actividad.archivo) ? 'Imagen de la actividad' : 'Archivo de la actividad' }}
        </label>
        <v-card class="archivo-container" @click="handleFileClick(actividad.archivo)" style="cursor: pointer;">
          <n-image 
            v-if="isImageFile(actividad.archivo)"
            :src="getImageUrl(actividad.archivo)" 
            :alt="actividad.titulo"
            object-fit="cover"
            :style="{ width: '100%', height: '200px', borderRadius: '8px' }"
            :preview-disabled="false"
          />
          <div v-else-if="isPDFFile(actividad.archivo)" class="file-placeholder pdf-file" style="height: 200px;">
            <i class="fa-solid fa-file-pdf" style="font-size: 64px; color: #d32f2f;"></i>
            <span class="file-label">PDF</span>
            <span class="file-name">{{ actividad.archivo.split('/').pop() }}</span>
          </div>
          <div v-else-if="isWordFile(actividad.archivo)" class="file-placeholder word-file" style="height: 200px;">
            <i class="fa-solid fa-file-word" style="font-size: 64px; color: #1976d2;"></i>
            <span class="file-label">WORD</span>
            <span class="file-name">{{ actividad.archivo.split('/').pop() }}</span>
          </div>
          <div v-else class="file-placeholder generic-file" style="height: 200px;">
            <i class="fa-solid fa-file" style="font-size: 64px; color: #757575;"></i>
            <span class="file-label">ARCHIVO</span>
            <span class="file-name">{{ actividad.archivo.split('/').pop() }}</span>
          </div>
        </v-card>
      </div>

      <div class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Fecha de la
          Actividad</label>
        <div class="info-field">
          <i class="fa-solid fa-calendar" style="color: #71C82F; margin-right: 8px;"></i>
          {{ formatFechaCompleta(actividad.fecha_actividad) }}
        </div>
      </div>

      <div v-if="esActividadInscrita && actividad.fecha_registro" class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Fecha de
          Inscripción</label>
        <div class="info-field">
          <i class="fa-solid fa-user-check" style="color: #2196f3; margin-right: 8px;"></i>
          {{ formatFechaCompleta(actividad.fecha_registro) }}
        </div>
      </div>

      <div v-if="esActividadInscrita && actividad.estado_actividad" class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Estado de la
          Actividad</label>
        <div class="info-field">
          <i class="fa-solid fa-info-circle" style="color: #71C82F; margin-right: 8px;"></i>
          <span class="estado-texto" :class="getEstadoClass(actividad.estado_actividad)">
            {{ actividad.estado_actividad }}
          </span>
        </div>
      </div>

      <div class="mb-4">
        <label
          style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Descripción</label>
        <div class="info-field descripcion-text">
          {{ actividad.descripcion }}
        </div>
      </div>

      <div v-if="!esActividadInscrita" class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Cupos
          Disponibles</label>
        <div class="info-field">
          <i class="fa-solid fa-users" style="color: #71C82F; margin-right: 8px;"></i>
          <span :class="{ 'cupos-bajos': actividad.cupos_restantes < 10 }">
            {{ actividad.cupos_restantes }} de {{ actividad.stock }} cupos disponibles
          </span>
        </div>
      </div>

      <div v-if="!esActividadInscrita && !isAdmin" class="d-flex justify-center mt-6">
        <v-btn @click="inscribirse" color="#71C82F" size="large"
          style="border-radius: 20px; text-transform: none; font-weight: 500" min-width="150px"
          :disabled="actividad.cupos_restantes <= 0 || inscribiendose" :loading="inscribiendose">
          <template v-if="actividad.cupos_restantes <= 0">
            Sin cupos disponibles
          </template>
          <template v-else>
            Inscribirse
          </template>
        </v-btn>
      </div>
    </div>
    
    <div v-else class="d-flex justify-center align-center" style="min-height: 200px;">
      <v-progress-circular indeterminate color="#71C82F" size="64"></v-progress-circular>
    </div>
  </ContainerModal>
</template>

<script setup>
import { ref, computed } from 'vue'
import { NImage } from 'naive-ui'
import LoginService from '@/services/LoginService'
import ActividadesService from '@/services/ActividadesService'
import ContainerModal from '@/components/layout/ContainerModal.vue'

const props = defineProps({
  modelValue: Boolean,
  actividad: {
    type: Object,
    default: () => null
  },
  isAdmin: {
    type: Boolean,
    default: false
  },
  esActividadInscrita: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'inscripcionExitosa', 'mostrarNotificacion'])

const isAdmin = computed(() => props.isAdmin)

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const inscribiendose = ref(false)
const user = ref(LoginService.getCurrentUser())

function getImageUrl(archivo) {
  if (archivo && archivo.startsWith('http')) {
    return archivo
  }
  return `http://localhost:5000/uploads/actividades/${archivo}`
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

function formatFechaCompleta(fecha) {
  const date = new Date(fecha)
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
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

function mostrarNotificacion(mensaje, tipo = 'success') {
  emit('mostrarNotificacion', { mensaje, tipo })
}

async function inscribirse() {
  if (!user.value || !props.actividad || !props.actividad.id) {
    mostrarNotificacion('Error: No se pudo obtener la información del usuario o la actividad', 'error')
    return
  }

  inscribiendose.value = true

  try {
    await ActividadesService.inscribirse(props.actividad.id, {
      id_usuario: user.value.id
    })

    mostrarNotificacion('¡Te has inscrito exitosamente a la actividad!', 'success')
    emit('inscripcionExitosa')

    setTimeout(() => {
      dialog.value = false
    }, 500)
  } catch (error) {
    console.error('Error al inscribirse:', error)

    if (error.response && error.response.status === 409) {
      mostrarNotificacion('Ya te encuentras inscrito en esta actividad', 'warning')
      setTimeout(() => {
        dialog.value = false
      }, 500)
    } else if (error.response && error.response.status === 400) {
      mostrarNotificacion('No hay cupos disponibles para esta actividad', 'error')
    } else {
      mostrarNotificacion('Error al inscribirse. Por favor, inténtalo de nuevo', 'error')
    }
  } finally {
    inscribiendose.value = false
  }
}
</script>

<style scoped>
.tipo-badge {
  display: inline-block;
  background-color: #71C82F;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
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

.cupos-bajos {
  color: #d32f2f;
  font-weight: 600;
}

.estado-texto {
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 8px;
}

.estado-aprobado {
  color: #4caf50;
  background-color: #e8f5e8;
}

.estado-finalizado {
  color: #2196f3;
  background-color: #e3f2fd;
}

.estado-cancelado {
  color: #f44336;
  background-color: #ffebee;
}

.estado-pendiente {
  color: #ff9800;
  background-color: #fff3e0;
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
  background: #71C82F;
  border-radius: 3px;
}

.contenido-modal::-webkit-scrollbar-thumb:hover {
  background: #8a0030;
}
</style>
