<template>
  <v-dialog v-model="dialog" max-width="600px" persistent>
    <v-card style="border-radius: 16px; padding: 32px 45px 36px;">
      <v-card-title class="d-flex justify-space-between align-center pa-0 mb-4">
        <h2 style="color: #A80038; text-align: center; flex: 1; font-size: 35px; font-weight: 400; font-family: 'Righteous', cursive;">Detalle de Solicitud</h2>
        <button
          @click="dialog = false"
          style="background: none; border: none; cursor: pointer; color: #A80038"
          title="Cerrar Modal"
        >
          <i class="fa-solid fa-xmark" style="font-size: 20px"></i>
        </button>
      </v-card-title>

      <div class="contenido-modal">
        <div class="mb-6">
          <h3 style="color: #A80038; font-size: 24px; font-weight: 600; margin-bottom: 16px;">
            {{ solicitud.titulo }}
          </h3>
          
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
          <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Código de Solicitud</label>
          <div class="info-field">
            <i class="fa-solid fa-hashtag" style="color: #A80038; margin-right: 8px;"></i>
            UNMSM-{{ solicitud.id }}
          </div>
        </div>

        <div v-if="solicitud.archivo" class="mb-4">
          <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Imagen de la solicitud</label>
          <v-card class="imagen-container">
            <v-img
              :src="getImageUrl(solicitud.archivo)"
              :alt="solicitud.titulo"
              cover
              style="border-radius: 8px;"
              height="200"
            >
              <template v-slot:error>
                <div class="d-flex align-center justify-center fill-height">
                  <v-icon size="64" color="grey-lighten-1">mdi-image-broken</v-icon>
                </div>
              </template>
            </v-img>
          </v-card>
        </div>

        <div class="mb-4">
          <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Fecha de Solicitud</label>
          <div class="info-field">
            <i class="fa-solid fa-calendar-plus" style="color: #A80038; margin-right: 8px;"></i>
            {{ solicitud.fecha_solicitud }}
          </div>
        </div>

        <div class="mb-4">
          <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Fecha Propuesta para la Actividad</label>
          <div class="info-field">
            <i class="fa-solid fa-calendar-check" style="color: #A80038; margin-right: 8px;"></i>
            {{ solicitud.fecha_actividad }}
          </div>
        </div>

        <div class="mb-4">
          <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Descripción</label>
          <div class="info-field descripcion-text">
            {{ solicitud.descripcion }}
          </div>
        </div>

        <div class="mb-4">
          <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Stock Solicitado</label>
          <div class="info-field">
            <i class="fa-solid fa-users" style="color: #A80038; margin-right: 8px;"></i>
            {{ solicitud.stock }} participantes
          </div>
        </div>

        <div v-if="!isAdmin">
          <div v-if="isEstadoPendiente(solicitud.estado)" class="mb-4">
            <v-alert
              type="warning"
              variant="tonal"
              :icon="false"
              class="mb-0"
            >
              <div class="d-flex align-center" style="gap: 10px;">
                <i class="fa-solid fa-clock"></i>
                Tu solicitud de actividad está pendiente de revisión por parte del equipo administrativo.
              </div>
            </v-alert>
          </div>

          <div v-if="isEstadoAprobado(solicitud.estado)" class="mb-4">
            <v-alert
              type="success"
              variant="tonal"
              :icon="false"
              class="mb-0"
            >
              <div class="d-flex align-center" style="gap: 10px;">
                <i class="fa-solid fa-check-circle"></i>
                ¡Excelente! Tu solicitud ha sido aprobada. La actividad estará disponible próximamente para inscripciones.
              </div>
            </v-alert>
          </div>

          <div v-if="isEstadoDenegado(solicitud.estado)" class="mb-4">
            <v-alert
              type="error"
              variant="tonal"
              :icon="false"
              class="mb-0"
            >
              <div class="d-flex align-center" style="gap: 10px;">
                <i class="fa-solid fa-times-circle"></i>
                Tu solicitud ha sido denegada por el administrador. Puedes contactar al equipo administrativo para conocer los motivos.
              </div>
            </v-alert>
          </div>
        </div>

        <div v-if="isAdmin && isEstadoPendiente(solicitud.estado)" class="d-flex justify-center mt-6" style="gap: 20px;">
          <v-btn
            @click="aprobarSolicitud"
            color="#A80038"
            size="large"
            style="border-radius: 20px; text-transform: none; font-weight: 500"
            min-width="120px"
            :loading="actualizandoEstado"
            :disabled="actualizandoEstado"
          >
            Aprobar
          </v-btn>
          
          <v-btn
            @click="denegarSolicitud"
            color="#A80038"
            size="large"
            style="border-radius: 20px; text-transform: none; font-weight: 500"
            min-width="120px"
            :loading="actualizandoEstado"
            :disabled="actualizandoEstado"
          >
            Denegar
          </v-btn>
        </div>
      </div>
      
      <v-snackbar 
        v-model="snackbar.show" 
        :color="snackbar.color" 
        timeout="3000"
        location="top center"
        style="z-index: 9999;"
      >
        <div class="text-center font-weight-medium">
          {{ snackbar.message }}
        </div>
      </v-snackbar>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { computed, ref } from 'vue'
import ActividadesService from '@/services/ActividadesService'

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
  return `http://localhost:5000/uploads/actividades/${archivo}`
}

function getEstadoClass(estado) {
  switch (estado) {
    case 'Aprobado':
      return 'estado-aprobada'
    case 'Denegado':
      return 'estado-rechazada'
    case 'Pendiente':
    default:
      return 'estado-pendiente'
  }
}

function getEstadoCardClass(estado) {
  switch (estado) {
    case 'Aprobado':
      return 'estado-card-aprobada'
    case 'Denegado':
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
    case 'Denegado':
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
  return estado === 'Denegado'
}

async function aprobarSolicitud() {
  try {
    actualizandoEstado.value = true
    await ActividadesService.actualizarEstado(props.solicitud.id, 'Aprobado')
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
  try {
    actualizandoEstado.value = true
    await ActividadesService.actualizarEstado(props.solicitud.id, 'Denegado')
    mostrarNotificacion('Solicitud denegada exitosamente', 'warning')
    emit('estadoActualizado')
    
    setTimeout(() => {
      dialog.value = false
    }, 1500)
  } catch (error) {
    console.error('Error al denegar solicitud:', error)
    mostrarNotificacion('Error al denegar la solicitud', 'error')
  } finally {
    actualizandoEstado.value = false
  }
}
</script>

<style scoped>
.contenido-modal {
  max-height: 70vh;
  overflow-y: auto;
  padding-right: 16px;
}

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
  background: linear-gradient(135deg, #A80038 0%, #d63384 100%);
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

.imagen-container {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.contenido-modal::-webkit-scrollbar {
  width: 6px;
}

.contenido-modal::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.contenido-modal::-webkit-scrollbar-thumb {
  background: #A80038;
  border-radius: 3px;
}

.contenido-modal::-webkit-scrollbar-thumb:hover {
  background: #8a0030;
}
</style>
