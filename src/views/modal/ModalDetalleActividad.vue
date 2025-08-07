<template>
  <v-dialog v-model="dialog" max-width="600px" persistent>
    <v-card style="border-radius: 16px; padding: 32px 45px 36px;">
      <v-card-title class="d-flex justify-space-between align-center pa-0 mb-4">
        <h2 style="color: #A80038; text-align: center; flex: 1; font-size: 35px; font-weight: 400; font-family: 'Righteous', cursive;">Detalle de Actividad</h2>
        <button
          @click="dialog = false"
          style="background: none; border: none; cursor: pointer; color: #A80038"
          title="Cerrar Modal"
        >
          <i class="fa-solid fa-xmark" style="font-size: 20px"></i>
        </button>
      </v-card-title>

      <div class="contenido-modal">
        <div class="mb-4">
          <h3 style="color: #A80038; font-size: 24px; font-weight: 600; margin-bottom: 8px;">
            {{ actividad.titulo }}
          </h3>
          <div class="tipo-badge">
            {{ actividad.tipo }}
          </div>
        </div>

        <div v-if="actividad.archivo" class="mb-4">
          <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Imagen de la actividad</label>
          <v-card class="imagen-container">
            <v-img
              :src="getImageUrl(actividad.archivo)"
              :alt="actividad.titulo"
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
          <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Fecha de la Actividad</label>
          <div class="info-field">
            <i class="fa-solid fa-calendar" style="color: #A80038; margin-right: 8px;"></i>
            {{ actividad.fecha_actividad }}
          </div>
        </div>

        <div class="mb-4">
          <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Descripción</label>
          <div class="info-field descripcion-text">
            {{ actividad.descripcion }}
          </div>
        </div>

        <div class="mb-4">
          <label style="font-size: 18px; color: black; font-weight: 400; margin-bottom: 8px; display: block;">Cupos Disponibles</label>
          <div class="info-field">
            <i class="fa-solid fa-users" style="color: #A80038; margin-right: 8px;"></i>
            <span :class="{ 'cupos-bajos': actividad.cupos_restantes < 10 }">
              {{ actividad.cupos_restantes }} de {{ actividad.stock }} cupos disponibles
            </span>
          </div>
        </div>

        <div v-if="!isAdmin" class="d-flex justify-center mt-6">
          <v-btn
            @click="inscribirse"
            color="#A80038"
            size="large"
            style="border-radius: 20px; text-transform: none; font-weight: 500"
            min-width="150px"
            :disabled="actividad.cupos_restantes <= 0 || inscribiendose"
            :loading="inscribiendose"
          >
            <template v-if="actividad.cupos_restantes <= 0">
              Sin cupos disponibles
            </template>
            <template v-else>
              Inscribirse
            </template>
          </v-btn>
        </div>
      </div>
      
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
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, computed } from 'vue'
import LoginService from '@/services/LoginService'
import ActividadesService from '@/services/ActividadesService'

const props = defineProps({
  modelValue: Boolean,
  actividad: {
    type: Object,
    default: () => ({})
  },
  isAdmin: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'inscripcionExitosa'])

const isAdmin = computed(() => props.isAdmin)

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const inscribiendose = ref(false)
const user = ref(LoginService.getCurrentUser())

const snackbar = ref({
  show: false,
  message: '',
  color: 'success'
})

function getImageUrl(archivo) {
  return `http://localhost:5000/uploads/actividades/${archivo}`
}

function mostrarNotificacion(mensaje, tipo = 'success') {
  snackbar.value = {
    show: true,
    message: mensaje,
    color: tipo
  }
}

async function inscribirse() {
  if (!user.value || !props.actividad.id) {
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
    }, 1500)
  } catch (error) {
    console.error('Error al inscribirse:', error)
    
    if (error.response && error.response.status === 409) {
      mostrarNotificacion('Ya te encuentras inscrito en esta actividad', 'warning')
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
.contenido-modal {
  max-height: 70vh;
  overflow-y: auto;
}

.tipo-badge {
  display: inline-block;
  background-color: #A80038;
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
