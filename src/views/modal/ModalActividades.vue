<template>
  <ContainerModal v-model="dialog" :title="isAdmin ? 'Agregar Actividad' : 'Solicitar Actividad'" :max-width="600"
    colorTheme="#A80038">
    <v-form @submit.prevent="submitComplaint()">
      <div class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400;"> Tipo </label>
        <v-select v-model="form.tipo" :items="tipoOptions" variant="outlined" density="comfortable" hide-details
          class="custom-input" :error="!!errors.tipo"></v-select>
        <span v-if="errors.tipo" class="error-message">{{ errors.tipo }}</span>
      </div>
      <div class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400;"> Título </label>
        <v-text-field v-model="form.titulo" variant="outlined" density="comfortable" hide-details class="custom-input"
          :error="!!errors.titulo"></v-text-field>
        <span v-if="errors.titulo" class="error-message">{{ errors.titulo }}</span>
      </div>
      <div class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400;"> Stock </label>
        <v-text-field v-model="form.stock" type="number" min="0" variant="outlined" density="comfortable" hide-details
          class="custom-input" :error="!!errors.stock"></v-text-field>
        <span v-if="errors.stock" class="error-message">{{ errors.stock }}</span>
      </div>

      <div class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400;"> Fecha de la Actividad </label>
        <VueDatePicker v-model="form.fecha_actividad" locale="es" format="dd/MM/yyyy" :ui="{ input: 'custom-input' }"
          :enable-time-picker="false" :min-date="new Date()" placeholder="Selecciona la fecha" />
        <span v-if="errors.fecha_actividad" class="error-message">{{ errors.fecha_actividad }}</span>
      </div>

      <div class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400;"> Descripción </label>
        <v-textarea v-model="form.descripcion" variant="outlined" rows="4" hide-details class="custom-input"
          :error="!!errors.descripcion"></v-textarea>
        <span v-if="errors.descripcion" class="error-message">{{ errors.descripcion }}</span>
      </div>

      <div class="mb-6">
        <label style="font-size: 18px; color: black; font-weight: 400;"> Prueba </label>
        <v-card class="upload-area d-flex flex-column align-center justify-center"
          style="min-height: 120px; border: 2px dashed #e0e0e0; background-color: #f5f5f5" @click="triggerFileInput">
          <v-icon size="32" color="grey-lighten-1" class="mb-2"> mdi-cloud-upload </v-icon>
          <span class="text-body-2 text-grey-lighten-1">
            {{ selectedFile ? selectedFile.name : 'Adjuntar imagen' }}
          </span>
          <input ref="fileInput" type="file" accept="image/*" style="display: none" @change="handleFileSelect" />
        </v-card>
      </div>
      <div>
        <n-checkbox v-if="type === 'form'" v-model:checked="item.participa" label="Participaré en esta actividad" />
      </div>
      <div class="d-flex justify-center">
        <v-btn type="submit" color="#A80038" size="large"
          style="border-radius: 20px; text-transform: none; font-weight: 500" min-width="120px">
          Enviar
        </v-btn>
      </div>

    </v-form>
  </ContainerModal>
</template>

<script setup>
import { currentDate } from '@/util/functions.js'
import { ref, reactive, watch, computed } from 'vue'
import LoginService from '@/services/LoginService'
import ActividadesService from '@/services/ActividadesService'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import ContainerModal from '@/components/layout/ContainerModal.vue'

const props = defineProps({
  modelValue: Boolean,
  item: Object,
  type: String,
})
const user = ref(LoginService.getCurrentUser())
const isAdmin = LoginService.isAdmin()

const emit = defineEmits(['update:modelValue', 'actividadCreada', 'mostrarNotificacion'])
const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})
const fileInput = ref(null)
const selectedFile = ref(null)

function resetForm() {
  form.numero = ''
  form.tipo = ''
  form.titulo = ''
  form.fecha = ''
  form.estado = ''
  form.descripcion = ''
  form.stock = ''
  form.fecha_actividad = ''
  selectedFile.value = null
  
  errors.tipo = ''
  errors.titulo = ''
  errors.stock = ''
  errors.fecha_actividad = ''
  errors.descripcion = ''
}

const errors = reactive({
  tipo: '',
  titulo: '',
  stock: '',
  fecha_actividad: '',
  descripcion: ''
})

const form = reactive({
  numero: '',
  tipo: '',
  titulo: '',
  fecha: '',
  estado: '',
  descripcion: '',
  stock: '',
  fecha_actividad: '',
})

const tipoOptions = ['Viaje', 'Taller', 'Visita']

function validateField(field, value) {
  switch (field) {
    case 'tipo':
      if (!value || value.trim() === '') {
        errors.tipo = 'El tipo es obligatorio'
        return false
      }
      errors.tipo = ''
      return true
    case 'titulo':
      if (!value || value.trim() === '') {
        errors.titulo = 'El título es obligatorio'
        return false
      }
      errors.titulo = ''
      return true
    case 'stock':
      if (!value || value === '' || Number(value) <= 0) {
        errors.stock = 'El stock debe ser mayor a 0'
        return false
      }
      errors.stock = ''
      return true
    case 'fecha_actividad':
      if (!value) {
        errors.fecha_actividad = 'La fecha de actividad es obligatoria'
        return false
      }
      errors.fecha_actividad = ''
      return true
    case 'descripcion':
      if (!value || value.trim() === '') {
        errors.descripcion = 'La descripción es obligatoria'
        return false
      }
      errors.descripcion = ''
      return true
    default:
      return true
  }
}

function validateForm() {
  let isValid = true
  isValid = validateField('tipo', form.tipo) && isValid
  isValid = validateField('titulo', form.titulo) && isValid
  isValid = validateField('stock', form.stock) && isValid
  isValid = validateField('fecha_actividad', form.fecha_actividad) && isValid
  isValid = validateField('descripcion', form.descripcion) && isValid
  return isValid
}

watch(
  () => props.item,
  (val) => {
    if (val && props.type === 'edit') {
      console.log('Objeto recibido en ModalActividades:', val)
      form.codigo = val.codigo || ''
      form.descripcion = val.descripcion || ''
      form.fecha = val.fecha || ''
      form.id = val.id || ''
      form.resumen = val.resumen || ''
      form.tipo = val.tipo || ''
      form.titulo = val.titulo || ''
      form.stock = val.stock || ''
    }
  },
  { immediate: true },
)

watch(() => form.tipo, (newValue) => {
  if (errors.tipo) validateField('tipo', newValue)
})

watch(() => form.titulo, (newValue) => {
  if (errors.titulo) validateField('titulo', newValue)
})

watch(() => form.stock, (newValue) => {
  if (errors.stock) validateField('stock', newValue)
})

watch(() => form.fecha_actividad, (newValue) => {
  if (errors.fecha_actividad) validateField('fecha_actividad', newValue)
})

watch(() => form.descripcion, (newValue) => {
  if (errors.descripcion) validateField('descripcion', newValue)
})

watch(() => props.modelValue, (newValue) => {
  if (newValue) {
    resetForm()
  }
})

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
  }
}

function mostrarNotificacion(mensaje, tipo = 'success') {
  emit('mostrarNotificacion', { mensaje, tipo })
}

async function submitComplaint() {
  if (!validateForm()) {
    return
  }

  const formData = new FormData()
  formData.append('tipo', form.tipo)
  formData.append('titulo', form.titulo)
  formData.append('descripcion', form.descripcion)

  let fechaActividad = new Date().toISOString().slice(0, 10)
  if (form.fecha_actividad) {
    if (form.fecha_actividad instanceof Date) {
      fechaActividad = form.fecha_actividad.toISOString().slice(0, 10)
    } else {
      const [dia, mes, anio] = form.fecha_actividad.split('/')
      fechaActividad = `${anio}-${mes.padStart(2, '0')}-${dia.padStart(2, '0')}`
    }
  }

  formData.append('fecha_actividad', fechaActividad)
  formData.append('id_usuario', user.value.id)
  formData.append('stock', Number(form.stock))

  try {
    if (isAdmin) {
      await ActividadesService.crearActividad(formData)
    } else {
      await ActividadesService.crearSolicitud(formData)
    }

    emit('actividadCreada', { esAdmin: isAdmin })
    mostrarNotificacion('Actividad enviada exitosamente', 'success')
    
    setTimeout(() => {
      dialog.value = false
    }, 500)
  } catch (error) {
    console.error('Error al crear actividad:', error)
    mostrarNotificacion('Error al enviar la actividad. Por favor, inténtalo de nuevo.', 'error')
  }
}
</script>

<style scoped>
.custom-input :deep(.v-field) {
  border-radius: 8px;
  background-color: #f8f9fa;
}

.custom-input :deep(.v-field--focused) {
  background-color: white;
}

.upload-area {
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.upload-area:hover {
  border-color: #e91e63;
  background-color: #fce4ec;
}

:deep(.dp__theme_light) {
  --dp-primary-color: #A80038;
  --dp-primary-text-color: #fff;
}

:deep(.dp__input) {
  height: 48px !important;
  border-radius: 8px;
  background-color: #f8f9fa;
}

:deep(.dp__input:focus) {
  background-color: white;
}

.error-message {
  color: #d32f2f;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}
</style>
