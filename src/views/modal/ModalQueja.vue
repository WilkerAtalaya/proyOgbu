<template>
  <ContainerModal
    v-model="dialog"
    :title="mode ? `Reporte ${form.numero}` : 'Realizar una Queja'"
    :max-width="600"
    :colorTheme="mode ? '#CF990D' : '#A80038'"
  >
    <v-form @submit.prevent="submitComplaint">
      <div class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400;"> Asunto </label>
        <v-text-field
          v-model="form.asunto"
          variant="outlined"
          density="comfortable"
          hide-details
          class="custom-input"
          :error="!!errors.asunto"
          :disabled="mode"
        ></v-text-field>
        <span v-if="errors.asunto" class="error-message">{{ errors.asunto }}</span>
      </div>

      <div class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400;"> Motivo </label>
        <v-select
          v-model="form.motivo"
          :items="motivosOptions"
          variant="outlined"
          density="comfortable"
          hide-details
          class="custom-input"
          :error="!!errors.motivo"
          :disabled="mode"
        ></v-select>
        <span v-if="errors.motivo" class="error-message">{{ errors.motivo }}</span>
      </div>

      <div class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400;"> Descripción </label>
        <v-textarea
          v-model="form.descripcion"
          variant="outlined"
          rows="4"
          hide-details
          class="custom-input"
          :error="!!errors.descripcion"
          :disabled="mode"
        ></v-textarea>
        <span v-if="errors.descripcion" class="error-message">{{ errors.descripcion }}</span>
      </div>

      <div v-if="mode" class="mb-4">
        <v-row>
          <v-col cols="6">
            <label style="font-size: 18px; color: black; font-weight: 400;"> Fecha </label>
            <v-text-field
              v-model="form.fecha"
              variant="outlined"
              density="comfortable"
              hide-details
              class="custom-input"
              disabled
            ></v-text-field>
          </v-col>
          <v-col cols="6">
            <label style="font-size: 18px; color: black; font-weight: 400;"> Estado </label>
            <v-select
              v-model="form.estado"
              :items="estadosOptions"
              variant="outlined"
              density="comfortable"
              hide-details
              class="custom-input"
              :disabled="!LoginService.isAdmin()"
            ></v-select>
          </v-col>
        </v-row>
      </div>

      <div class="mb-6">
        <label style="font-size: 18px; color: black; font-weight: 400;"> Prueba </label>
        <v-card
          class="upload-area d-flex flex-column align-center justify-center"
          style="min-height: 120px; border: 2px dashed #e0e0e0; background-color: #f5f5f5"
          @click="triggerFileInput"
        >
          <v-icon size="32" color="grey-lighten-1" class="mb-2"> mdi-cloud-upload </v-icon>
          <span class="text-body-2 text-grey-lighten-1">
            {{ selectedFile ? selectedFile.name : 'Adjuntar imagen' }}
          </span>
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            style="display: none"
            :disabled="mode"
            @change="handleFileSelect"
          />
        </v-card>
      </div>

      <div v-if="!mode" class="d-flex justify-center">
        <v-btn
          type="submit"
          color="#e91e63"
          size="large"
          style="border-radius: 20px; text-transform: none; font-weight: 500"
          min-width="120px"
        >
          Enviar
        </v-btn>
      </div>
    </v-form>

    <div v-if="mode && LoginService.isAdmin()" class="d-flex justify-center mt-4">
      <v-btn
        @click="updateEstado"
        color="#CF990D"
        size="large"
        style="border-radius: 20px; text-transform: none; font-weight: 500"
        min-width="120px"
        :disabled="form.estado === originalEstado"
      >
        Actualizar Estado
      </v-btn>
    </div>
  </ContainerModal>
</template>

<script setup>
import { currentDate } from '@/util/functions.js'
import { ref, reactive, watch, computed } from 'vue'
import QuejasService from '@/services/QuejasService'
import LoginService from '@/services/LoginService'
import ContainerModal from '@/components/layout/ContainerModal.vue'

const fileInput = ref(null)
const selectedFile = ref(null)
const form = reactive({ numero: '', asunto: '', motivo: '', fecha: '', estado: '', descripcion: ''})
const errors = reactive({ asunto: '', motivo: '', descripcion: '' })
const motivosOptions = ['Robo', 'Daños a la propiedad', 'Ruido excesivo', 'Acoso', 'Incumplimiento de normas', 'Otro']
const estadosOptions = ['Recibido', 'En revisión', 'En proceso', 'Resuelto', 'Cerrado']
const originalEstado = ref('')

const props = defineProps({
  modelValue: Boolean,
  item: Object,
  user: Object,
  mode: Boolean,
  type: String,
})

const emit = defineEmits(['update:modelValue', 'agregarQueja', 'actualizarEstado', 'mostrarNotificacion'])

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

watch(
  () => props.item,
  (val) => {
    if (val) {
      console.log('Objeto recibido en ModalQueja:', val)
      console.log('Propiedades del objeto:', Object.keys(val))
      console.log('ID encontrado:', val.id)
      form.numero = val.numero || ''
      form.asunto = val.asunto || ''
      form.motivo = val.motivo || ''
      form.fecha = val.fecha || ''
      form.estado = val.estado || ''
      form.descripcion = val.descripcion || ''
      originalEstado.value = val.estado || ''
      
      Object.keys(errors).forEach(key => errors[key] = '')
    }
  },
  { immediate: true },
)

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

function validateField(field, value) {
  switch (field) {
    case 'asunto':
      if (!value || value.trim() === '') {
        errors.asunto = 'El asunto es obligatorio'
        return false
      }
      errors.asunto = ''
      return true
    case 'motivo':
      if (!value) {
        errors.motivo = 'Debe seleccionar un motivo'
        return false
      }
      errors.motivo = ''
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
  isValid = validateField('asunto', form.asunto) && isValid
  isValid = validateField('motivo', form.motivo) && isValid
  isValid = validateField('descripcion', form.descripcion) && isValid
  return isValid
}

// Watchers para validación en tiempo real
watch(() => form.asunto, (newValue) => {
  if (errors.asunto) validateField('asunto', newValue)
})

watch(() => form.motivo, (newValue) => {
  if (errors.motivo) validateField('motivo', newValue)
})

watch(() => form.descripcion, (newValue) => {
  if (errors.descripcion) validateField('descripcion', newValue)
})

async function submitComplaint() {
  if (!validateForm()) {
    return
  }

  try {
    const formData = new FormData();
    formData.append('asunto', form.asunto);
    formData.append('motivo', form.motivo);
    formData.append('descripcion', form.descripcion);
    formData.append('id_usuario', props.user.id);
    if (selectedFile.value) {
      formData.append('prueba', selectedFile.value);
    }
    
    const response = await QuejasService.crearQueja(formData);
    emit('agregarQueja', {
      asunto: form.asunto,    
      numero: response.codigo_reporte,
      descripcion: form.descripcion,    
      estado: 'Recibido',
      fecha: currentDate(), 
      motivo: form.motivo,     
      prueba: response.archivo?.url || null
    })
    
    emit('actualizarEstado')
    
    // Limpiar formulario
    Object.keys(form).forEach(key => form[key] = '')
    Object.keys(errors).forEach(key => errors[key] = '')
    selectedFile.value = null
    
    mostrarNotificacion('Queja enviada exitosamente', 'success')
    
    setTimeout(() => {
      dialog.value = false
    }, 500)
  } catch (error) {
    console.error('Error al enviar queja:', error);
    mostrarNotificacion('Error al enviar la queja. Por favor, inténtalo de nuevo.', 'error')
  }
}

async function updateEstado() {
  if (form.estado !== originalEstado.value && props.item?.id) {
    try {
      console.log('Actualizando estado de queja ID:', props.item.id, 'a:', form.estado);
      await QuejasService.actualizarEstadoQueja(props.item.id, form.estado);
      originalEstado.value = form.estado;
      emit('actualizarEstado');
      mostrarNotificacion('Estado actualizado exitosamente', 'success')
      
      setTimeout(() => {
        dialog.value = false
      }, 500)
    } catch (error) {
      console.error('Error al actualizar estado:', error);
      mostrarNotificacion('Error al actualizar el estado', 'error')
    }
  } else {
    console.log('No se actualizó - Estado igual o ID faltante');
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

.error-message {
  color: #d32f2f;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}
</style>
