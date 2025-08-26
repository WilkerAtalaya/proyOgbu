<template>
  <ContainerModal
    v-model="dialog"
    :title="`${actividad?.titulo || 'Actividad'}`"
    :max-width="700"
    :colorTheme="'#53696D'"
  >
    <div class="contenido-modal">
      <div class="mb-6">
        <div class="info-cards-container">
          <div class="info-card cupos-card">
            <div class="card-icon">
              <i class="fa-solid fa-users"></i>
            </div>
            <div class="card-content">
              <span class="card-label">Cupos</span>
              <span class="card-value">{{ inscritos.length }} / {{ actividad?.stock }}</span>
            </div>
          </div>
        </div>
      </div>

      <div v-if="loading" class="loading-container">
        <v-progress-circular
          indeterminate
          color="#53696D"
          size="48"
        ></v-progress-circular>
        <p class="loading-text">Cargando residentes inscritos...</p>
      </div>

      <div v-else-if="inscritos.length === 0" class="empty-state">
        <div class="empty-icon">
          <i class="fa-solid fa-user-slash" style="font-size: 64px; color: #ccc;"></i>
        </div>
        <h3 class="empty-title">No hay residentes inscritos</h3>
        <p class="empty-description">
          Aún no hay residentes inscritos en esta actividad.
        </p>
      </div>

      <div v-else class="inscritos-list">
        <h3 class="section-title">
          <i class="fa-solid fa-list-ul" style="margin-right: 8px; color: #53696D;"></i>
          Lista de Residentes Inscritos
        </h3>
        
        <div class="inscritos-grid">
          <div 
            v-for="(inscrito, index) in inscritos" 
            :key="inscrito.id_inscripcion" 
            class="inscrito-card"
          >
            <div class="inscrito-info">
              <div class="inscrito-avatar">
                <i class="fa-solid fa-user"></i>
              </div>
              <div class="inscrito-details">
                <h4 class="inscrito-nombre">{{ inscrito.nombre }}</h4>
                <div class="inscrito-metadata">
                  <div class="metadata-item">
                    <i class="fa-solid fa-calendar-plus"></i>
                    <span>Inscrito el {{ formatearFecha(inscrito.fecha_registro) }}</span>
                  </div>
                  <div class="metadata-item">
                    <i class="fa-solid fa-hashtag"></i>
                    <span>ID: {{ inscrito.id_usuario }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="inscrito-contador">
              <div class="numero-inscrito">
                {{ index + 1 }}
              </div>
            </div>
          </div>
        </div>
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
  </ContainerModal>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import ActividadesService from '@/services/ActividadesService'
import ContainerModal from '@/components/layout/ContainerModal.vue'

const props = defineProps({
  modelValue: Boolean,
  actividad: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

const dialog = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const inscritos = ref([])
const loading = ref(false)

const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
})

watch(() => props.modelValue, (newValue) => {
  if (newValue && props.actividad?.id) {
    cargarInscritos()
  }
})

watch(() => props.actividad?.id, (newId) => {
  if (newId && props.modelValue) {
    cargarInscritos()
  }
})

async function cargarInscritos() {
  if (!props.actividad?.id) return
  
  loading.value = true
  try {
    const response = await ActividadesService.obtenerInscritosActividad(props.actividad.id)
    inscritos.value = response || []
  } catch (error) {
    console.error('Error al cargar inscritos:', error)
    mostrarNotificacion('Error al cargar la lista de inscritos', 'error')
    inscritos.value = []
  } finally {
    loading.value = false
  }
}

function formatearFecha(fecha) {
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

function mostrarNotificacion(mensaje, tipo = 'success') {
  snackbar.value = {
    show: true,
    message: mensaje,
    color: tipo
  }
}
</script>

<style scoped>
.contenido-modal {
  padding: 0;
}

.info-cards-container {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 24px;
}

.info-card {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 1px solid #dee2e6;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.3s ease;
}

.info-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.info-card.fecha-card {
  border-left: 4px solid #2196f3;
}

.info-card.tipo-card {
  border-left: 4px solid #A37801;
}

.info-card.cupos-card {
  border-left: 4px solid #28a745;
}

.card-icon {
  background: #53696D;
  color: white;
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.fecha-card .card-icon {
  background: #2196f3;
}

.tipo-card .card-icon {
  background: #A37801;
}

.cupos-card .card-icon {
  background: #28a745;
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.card-label {
  font-size: 12px;
  font-weight: 600;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.card-value {
  font-size: 16px;
  font-weight: 700;
  color: #212529;
  line-height: 1.2;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  gap: 16px;
}

.loading-text {
  color: #6c757d;
  font-size: 14px;
  margin: 0;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
}

.empty-icon {
  margin-bottom: 16px;
}

.empty-title {
  color: #495057;
  margin-bottom: 8px;
  font-size: 20px;
  font-weight: 600;
}

.empty-description {
  color: #6c757d;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
}

.inscritos-list {
  margin-top: 8px;
}

.section-title {
  color: #212529;
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
}

.inscritos-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.inscrito-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: all 0.3s ease;
}

.inscrito-card:hover {
  background: #f8f9fa;
  border-color: #53696D;
  box-shadow: 0 2px 8px rgba(83, 105, 109, 0.1);
}

.inscrito-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.inscrito-avatar {
  background: linear-gradient(135deg, #53696D, #3e5357);
  color: white;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.inscrito-details {
  flex: 1;
}

.inscrito-contador {
  background: linear-gradient(135deg, #53696D, #3e5357);
  color: white;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  margin-left: 16px;
  min-width: 40px;
  text-align: center;
}

.inscrito-nombre {
  color: #212529;
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 8px 0;
  line-height: 1.2;
}

.inscrito-metadata {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metadata-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #6c757d;
  font-size: 12px;
}

.metadata-item i {
  color: #53696D;
  width: 12px;
}

.inscrito-fecha {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.fecha-inscripcion {
  background: linear-gradient(135deg, #f8f9fa, #e9ecef);
  color: #495057;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  border: 1px solid #dee2e6;
}

.fecha-inscripcion i {
  color: #53696D;
}

@media (max-width: 600px) {
  .info-cards-container {
    justify-content: center;
  }
  
  .inscrito-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .inscrito-fecha {
    align-self: flex-end;
  }
  
  .inscrito-metadata {
    flex-direction: column;
  }
  
  .inscrito-contador {
    align-self: flex-end;
    margin-left: 0;
    margin-top: 8px;
  }
}

@media (min-width: 601px) and (max-width: 900px) {
  .info-cards-container {
    justify-content: center;
  }
}
</style>
