<template>
  <v-dialog v-model="dialog" max-width="500px" persistent>
    <v-card class="pa-4" style="border-radius: 16px">
      <v-card-title class="d-flex justify-space-between align-center pa-0 mb-4">
        <h2 class="text-h5 font-weight-bold" style="color: #e91e63">{{ type === 'form' ? 'Visualizar queja' : 'Reportar una Queja' }}</h2>
        <button
          @click="dialog = false"
          style="background: none; border: none; cursor: pointer"
          title="Cerrar Modal"
        >
          <i class="fa-solid fa-xmark" style="color: #1976d2; font-size: 20px"></i>
        </button>
      </v-card-title>

      <v-form @submit.prevent="submitComplaint">
        <div class="mb-4">
          <label class="text-body-2 font-weight-medium mb-2 d-block"> Asunto </label>
          <v-text-field
            v-model="form.asunto"
            variant="outlined"
            density="comfortable"
            hide-details
            class="custom-input"
            :disabled="mode"
          ></v-text-field>
        </div>

        <div class="mb-4">
          <label class="text-body-2 font-weight-medium mb-2 d-block"> Motivo </label>
          <v-select
            v-model="form.motivo"
            :items="motivosOptions"
            variant="outlined"
            density="comfortable"
            hide-details
            class="custom-input"
            :disabled="mode"
          ></v-select>
        </div>

        <div class="mb-4">
          <label class="text-body-2 font-weight-medium mb-2 d-block"> Descripción </label>
          <v-textarea
            v-model="form.descripcion"
            variant="outlined"
            rows="4"
            hide-details
            class="custom-input"
            :disabled="mode"
          ></v-textarea>
        </div>

        <div class="mb-6">
          <label class="text-body-2 font-weight-medium mb-2 d-block"> Prueba multimedia </label>
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
    </v-card>
  </v-dialog>
</template>

<script setup>
import { currentDate } from '@/util/functions.js'
import { ref, reactive, watch, computed } from 'vue'
import QuejasService from '@/services/QuejasService'

const fileInput = ref(null)
const selectedFile = ref(null)
const form = reactive({ numero: '', asunto: '', motivo: '', fecha: '', estado: '', descripcion: ''})
const motivosOptions = ['Robo', 'Daños a la propiedad', 'Ruido excesivo', 'Acoso', 'Incumplimiento de normas', 'Otro']

const props = defineProps({
  modelValue: Boolean,
  item: Object,
  user: Object,
  mode: Boolean,
  type: String,
})

const emit = defineEmits(['update:modelValue', 'agregarQueja'])

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

watch(
  () => props.item,
  (val) => {
    if (val) {
      console.log('Objeto recibido en ModalQueja:', val)
      form.numero = val.numero || ''
      form.asunto = val.asunto || ''
      form.motivo = val.motivo || ''
      form.fecha = val.fecha || ''
      form.estado = val.estado || ''
      form.descripcion = val.descripcion || ''
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

async function submitComplaint() {
  const formData = new FormData();
  formData.append('asunto', form.asunto);
  formData.append('motivo', form.motivo);
  formData.append('descripcion', form.descripcion);
  formData.append('id_usuario', props.user.id);
  formData.append('prueba', selectedFile.value);
  const response = await QuejasService.crearQueja(formData);
  emit('agregarQueja', {
    asunto: form.asunto,    
    numero: response.codigo_reporte,
    descripcion: form.descripcion,    
    estado: 'Recibido',
    fecha: currentDate(), 
    motivo: form.motivo,     
    prueba: ''
  })
  dialog.value = false;
  alert('Queja enviada exitosamente');
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
</style>
