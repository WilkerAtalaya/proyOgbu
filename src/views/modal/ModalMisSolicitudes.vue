<template>
  <v-dialog v-model="dialog" max-width="500px" persistent>
    <v-card class="pa-4" style="border-radius: 16px">
      <v-card-title class="d-flex justify-space-between align-center pa-0 mb-4">
        <h2 class="text-h5 font-weight-bold" style="color: #e91e63">Detalles de solicitud:</h2>
        <button
          @click="dialog = false"
          style="background: none; border: none; cursor: pointer"
          title="Cerrar Modal"
        >
          <i class="fa-solid fa-xmark" style="color: #1976d2; font-size: 20px"></i>
        </button>
      </v-card-title>

      <v-form 
         @submit.prevent="submitComplaint"
      >
        <div class="mb-4">
          <label class="text-body-2 font-weight-medium mb-2 d-block"> Título </label>
          <v-text-field
            v-model="form.titulo"
            variant="outlined"
            density="comfortable"
            hide-details
            class="custom-input"
            disabled
          ></v-text-field>
        </div>
        <div class="mb-4">
          <label class="text-body-2 font-weight-medium mb-2 d-block"> Fecha </label>
          <v-text-field
            v-model="form.fecha"
            variant="outlined"
            density="comfortable"
            hide-details
            class="custom-input"
            disabled
          ></v-text-field>
        </div>

        <div class="mb-4">
          <label class="text-body-2 font-weight-medium mb-2 d-block"> Descripción </label>
          <v-textarea
            v-model="form.descripcion"
            variant="outlined"
            rows="3"
            hide-details
            class="custom-input"
            disabled
          ></v-textarea>
        </div>

        <div class="mb-6">
          <label class="text-body-2 font-weight-medium mb-2 d-block"> Archivo adjunto </label>
          <v-card
            class="upload-area d-flex flex-column align-center justify-center"
            style="min-height: 120px; border: 2px dashed #e0e0e0; background-color: #f5f5f5"
            @click="triggerFileInput"
            disabled
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
              @change="handleFileSelect"
            />
          </v-card>
        </div>

        <!-- <div class="d-flex justify-center">
          <v-btn
            type="submit"
            color="#e91e63"
            size="large"
            style="border-radius: 20px; text-transform: none; font-weight: 500"
            min-width="120px"
          >
            Enviar
          </v-btn>
        </div> -->
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { currentDate } from '@/util/functions.js'
import { ref, reactive, watch, computed } from 'vue'

const props = defineProps({
  modelValue: Boolean,
  item: Object,
})

const emit = defineEmits(['update:modelValue'])
const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})
const fileInput = ref(null)
const selectedFile = ref(null)

const form = reactive({
  codigo: '',
  descripcion: '',
  fecha: '',
  id: '',
  resumen: '',
  tipo: '',
  titulo: '',
})

const motivosOptions = [
  'Robo',
  'Daños a la propiedad',
  'Ruido excesivo',
  'Acoso',
  'Incumplimiento de normas',
  'Otro',
]

watch(
  () => props.item,
  (val) => {
    if (val) {
      console.log('Objeto recibido en ModalActividades:', val)
      form.codigo = val.codigo || ''
      form.descripcion = val.descripcion || ''
      form.fecha = val.fecha || ''
      form.id = val.id || ''
      form.resumen = val.resumen || ''
      form.tipo = val.tipo || ''
      form.titulo = val.titulo || ''
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

const submitComplaint = () => {
  console.log('Formulario enviado:', {
    ...form,
    archivo: selectedFile.value,
  })

  dialog.value = false

  alert('Queja enviada exitosamente')
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
