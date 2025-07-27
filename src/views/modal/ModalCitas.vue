<template>
  <v-dialog v-model="dialog" max-width="500px" persistent>
    <v-card class="pa-4" style="border-radius: 16px">
      <v-card-title class="d-flex justify-space-between align-center pa-0 mb-4">
        <h2 class="text-h5 font-weight-bold" style="color: #e91e63">{{ type === 'form' ? 'Formulario de actividad' : 'Agendar Cita' }}</h2>
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
          <label class="text-body-2 font-weight-medium mb-2 d-block"> Fecha </label>
          <VueDatePicker
            v-model="form.fecha"
            locale="es"
            format="dd/MM/yyyy"
            :ui="{ input: 'custom-input' }"
            :enable-time-picker="false"
            placeholder="Selecciona la fecha"
          />
        </div>
        <div class="mb-4">
          <label class="text-body-2 font-weight-medium mb-2 d-block"> Horario </label>
          <v-text-field
            v-model="form.horario"
            variant="outlined"
            density="comfortable"
            hide-details
            class="custom-input"
          ></v-text-field>
        </div>
        <div class="mb-4">
          <label class="text-body-2 font-weight-medium mb-2 d-block"> Área </label>
           <v-text-field
            v-model="form.area"
            variant="outlined"
            density="comfortable"
            hide-details
            class="custom-input"
          ></v-text-field>
        </div>
        <div class="mb-4">
          <label class="text-body-2 font-weight-medium mb-2 d-block"> Motivo</label>
          <v-text-field
            v-model="form.motivo"
            variant="outlined"
            density="comfortable"
            hide-details
            class="custom-input"
          ></v-text-field>
        </div>

        <div class="mb-4">
          <label class="text-body-2 font-weight-medium mb-2 d-block"> Descripción</label>
          <v-textarea
            v-model="form.descripcion"
            variant="outlined"
            rows="4"
            hide-details
            class="custom-input"
          ></v-textarea>
        </div>

        <div>
            <n-checkbox
              v-if="type === 'form'"
              v-model:checked="item.participa"
              label="Participaré en esta actividad"
            />
        </div>
        <div class="d-flex justify-center">
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
import { dateFormatDB, currentDate } from '@/util/functions.js'
import { ref, reactive, watch, computed } from 'vue'
import CitasService from '@/services/CitasService'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'

const props = defineProps({
  modelValue: Boolean,
  item: Object,
  type: String,
})

const emit = defineEmits(['update:modelValue'])
const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})
const fileInput = ref(null)
const selectedFile = ref(null)

const form = reactive({
  numero: '',
  tipo: '',
  titulo: '',
  fecha: '',
  estado: '',
  descripcion: '',
})

watch(
  () => props.item,
  (val) => {
    if (val) {
      console.log('Objeto recibido en ModalActividades:', val)
      form.numero = val.numero || ''
      form.asunto = val.tipo || ''
      form.titulo = val.titulo || ''
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
  console.log(form)
  const newForm = { ...form }
  newForm.id_alumno = 5
  newForm.id_usuario = 5
  if (form.fecha) {
    let fechaStr = form.fecha
    if (form.fecha instanceof Date) {
      const dia = form.fecha.getDate().toString().padStart(2, '0')
      const mes = (form.fecha.getMonth() + 1).toString().padStart(2, '0')
      const anio = form.fecha.getFullYear()
      fechaStr = `${dia}/${mes}/${anio}`
    }
    newForm.fecha = dateFormatDB(fechaStr)
  } else {
    newForm.fecha = dateFormatDB(currentDate())
  }
  await CitasService.crearCita(newForm)
  dialog.value = false
  alert('Actividad enviada exitosamente')
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
  --dp-primary-color: #e91e63;
  --dp-primary-text-color: #fff;
}
</style>
