<template>
  <v-dialog v-model="dialog" max-width="600px" persistent>
    <v-card style="border-radius: 16px; padding: 32px 45px 36px;">
      <v-card-title class="d-flex justify-space-between align-center pa-0 mb-4">
        <h2 style="color: #A80038; text-align: center; flex: 1; font-size: 35px; font-weight: 400; font-family: 'Righteous', cursive;">Realizar una Publicación</h2>
        <button
          @click="dialog = false"
          style="background: none; border: none; cursor: pointer"
          title="Cerrar Modal"
        >
          <i class="fa-solid fa-xmark" style="color: #1976d2; font-size: 20px"></i>
        </button>
      </v-card-title>

      <v-form @submit.prevent="submitPublicacion">
        <div class="mb-4">
          <label style="font-size: 18px; color: black; font-weight: 400;">Descripción</label>
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
          <label style="font-size: 18px; color: black; font-weight: 400;">Adjuntar imagen</label>
          <v-card
            class="upload-area d-flex flex-column align-center justify-center"
            style="min-height: 120px; border: 2px dashed #e0e0e0; background-color: #f5f5f5"
            @click="triggerFileInput"
          >
            <v-icon size="32" color="grey-lighten-1" class="mb-2"> mdi-cloud-upload </v-icon>
            <span class="text-body-2 text-grey-lighten-1">
              {{ selectedFile ? selectedFile.name : 'Subir Imagen' }}
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
            color="#F2B200"
            size="large"
            style="border-radius: 15px; text-transform: none; font-weight: 400; font-size: 18px; padding: 12px 24px;"
            min-width="120px"
          >
            Publicar
          </v-btn>
        </div>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import AnunciosService from '@/services/AnunciosService'
import LoginService from '@/services/LoginService'

const fileInput = ref(null)
const selectedFile = ref(null)
const form = reactive({ descripcion: '' })

const props = defineProps({
  modelValue: Boolean,
  mode: Boolean,
})

const emit = defineEmits(['update:modelValue', 'agregarPublicacion'])

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
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

async function submitPublicacion() {
  const user = LoginService.getCurrentUser()
  const formData = new FormData()
  formData.append('id_usuario', user.id)
  formData.append('descripcion', form.descripcion)
  formData.append('imagen', selectedFile.value)
  const response = await AnunciosService.crearAnuncio(formData)
  emit('agregarPublicacion', {
    id_usuario: user.id,
    descripcion: form.descripcion,
    imagen: response.imagen_url || '',
    fecha_publicacion: new Date()
  })
  
  form.descripcion = ''
  selectedFile.value = null
  dialog.value = false
  alert('Publicación enviada exitosamente')
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
