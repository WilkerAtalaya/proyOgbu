<template>
  <ContainerModal v-model="dialog" :title="isEditMode ? 'Actualizar publicación' : 'Realizar una publicación'" colorTheme="#A80038" >
    <v-form @submit.prevent="submitPublicacion">
      <div class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400;">Título</label>
        <v-text-field v-model="form.titulo" variant="outlined" hide-details class="custom-input"
          :disabled="mode" :error="!!errors.titulo"></v-text-field>
        <span v-if="errors.titulo" class="error-message">{{ errors.titulo }}</span>
      </div>

      <div class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400;">Descripción</label>
        <v-textarea v-model="form.descripcion" variant="outlined" rows="4" hide-details class="custom-input"
          :disabled="mode" :error="!!errors.descripcion"></v-textarea>
        <span v-if="errors.descripcion" class="error-message">{{ errors.descripcion }}</span>
      </div>

      <div class="mb-6">
        <label style="font-size: 18px; color: black; font-weight: 400;">Adjuntar imagen</label>
        
        <div v-if="currentImageUrl && !selectedFile" class="current-image-container mb-3">
          <img :src="currentImageUrl" alt="Imagen actual" class="current-image" />
          <v-btn
            size="small"
            color="#A80038"
            variant="outlined"
            @click="removeCurrentImage"
            class="remove-image-btn"
          >
            <i class="fas fa-times mr-2"></i>
            Quitar imagen
          </v-btn>
        </div>

        <v-card v-if="!currentImageUrl || selectedFile" class="upload-area d-flex flex-column align-center justify-center"
          style="min-height: 120px; border: 2px dashed #e0e0e0; background-color: #f5f5f5" @click="triggerFileInput">
          <v-icon size="32" color="grey-lighten-1" class="mb-2"> mdi-cloud-upload </v-icon>
          <span class="text-body-2 text-grey-lighten-1">
            {{ selectedFile ? selectedFile.name : 'Subir Imagen' }}
          </span>
          <input ref="fileInput" type="file" accept="image/*" style="display: none" :disabled="mode"
            @change="handleFileSelect" />
        </v-card>
      </div>

      <div v-if="!mode" class="d-flex justify-center">
        <v-btn type="submit" color="#F2B200" size="large"
          style="border-radius: 15px; text-transform: none; font-weight: 400; font-size: 18px; padding: 12px 24px;"
          min-width="120px">
          {{ isEditMode ? 'Actualizar' : 'Publicar' }}
        </v-btn>
      </div>
    </v-form>
  </ContainerModal>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import AnunciosService from '@/services/AnunciosService'
import LoginService from '@/services/LoginService'
import ContainerModal from '@/components/layout/ContainerModal.vue'

const fileInput = ref(null)
const selectedFile = ref(null)
const currentImageUrl = ref('')
const imageRemoved = ref(false)
const form = reactive({ titulo: '', descripcion: '' })
const errors = reactive({ titulo: '', descripcion: '' })

const props = defineProps({
  modelValue: Boolean,
  mode: Boolean,
  editData: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['update:modelValue', 'agregarPublicacion', 'actualizarPublicacion', 'mostrar-notificacion'])

const isEditMode = computed(() => !!props.editData)

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => {
    if (!val) {
      resetForm()
    } else if (val && props.editData) {
      loadEditData()
    }
    emit('update:modelValue', val)
  }
})

const triggerFileInput = () => {
  fileInput.value.click()
}

const handleFileSelect = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    imageRemoved.value = false
  }
}

const removeCurrentImage = () => {
  currentImageUrl.value = ''
  imageRemoved.value = true
  selectedFile.value = null
}

const resetForm = () => {
  form.titulo = ''
  form.descripcion = ''
  selectedFile.value = null
  currentImageUrl.value = ''
  imageRemoved.value = false
  Object.keys(errors).forEach(key => errors[key] = '')
}

const loadEditData = () => {
  if (props.editData) {
    form.titulo = props.editData.titulo || ''
    form.descripcion = props.editData.descripcion || ''
    currentImageUrl.value = props.editData.archivo?.url || ''
    imageRemoved.value = false
    selectedFile.value = null
  }
}

watch(() => props.editData, (newData) => {
  if (newData && props.modelValue) {
    loadEditData()
  }
}, { immediate: true })

function mostrarNotificacion(mensaje, tipo = 'success') {
  emit('mostrar-notificacion', { mensaje, tipo })
}

function validateField(field, value) {
  switch (field) {
    case 'titulo':
      if (!value || value.trim() === '') {
        errors.titulo = 'El título es obligatorio'
        return false
      }
      errors.titulo = ''
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
  isValid = validateField('titulo', form.titulo) && isValid
  isValid = validateField('descripcion', form.descripcion) && isValid
  return isValid
}

watch(() => form.descripcion, (newValue) => {
  if (errors.descripcion) validateField('descripcion', newValue)
})

watch(() => form.titulo, (newValue) => {
  if (errors.titulo) validateField('titulo', newValue)
})

async function submitPublicacion() {
  if (!validateForm()) {
    return
  }

  try {
    const user = LoginService.getCurrentUser()
    
    if (isEditMode.value) {
      const formData = new FormData()
      formData.append('id_usuario', user.id)
      formData.append('titulo', form.titulo)
      formData.append('descripcion', form.descripcion)
      
      let response
      
      const soloSeEliminoImagen = imageRemoved.value && 
                                  !selectedFile.value && 
                                  form.titulo === props.editData.titulo && 
                                  form.descripcion === props.editData.descripcion
      
      const hayCambiosTexto = form.titulo !== props.editData.titulo || 
                              form.descripcion !== props.editData.descripcion
      
      if (soloSeEliminoImagen) {
        const patchFormData = new FormData()
        patchFormData.append('eliminar_imagen', '1')
        response = await AnunciosService.actualizarAnuncioParcial(props.editData.id, patchFormData)
      } else if (imageRemoved.value && hayCambiosTexto) {
        const patchFormData = new FormData()
        patchFormData.append('eliminar_imagen', '1')
        await AnunciosService.actualizarAnuncioParcial(props.editData.id, patchFormData)
        
        response = await AnunciosService.actualizarAnuncio(props.editData.id, formData)
      } else {
        if (selectedFile.value) {
          formData.append('imagen', selectedFile.value)
        }
        response = await AnunciosService.actualizarAnuncio(props.editData.id, formData)
      }
      
      emit('actualizarPublicacion', {
        ...props.editData,
        titulo: form.titulo,
        descripcion: form.descripcion,
        archivo: response.archivo || (imageRemoved.value ? null : props.editData.archivo)
      })
      
      mostrarNotificacion('Publicación actualizada exitosamente', 'success')
    } else {
      const formData = new FormData()
      formData.append('id_usuario', user.id)
      formData.append('titulo', form.titulo)
      formData.append('descripcion', form.descripcion)
      if (selectedFile.value) {
        formData.append('imagen', selectedFile.value)
      }
      const response = await AnunciosService.crearAnuncio(formData)
      emit('agregarPublicacion', {
        id_usuario: user.id,
        titulo: form.titulo,
        descripcion: form.descripcion,
        archivo: response.archivo || null,
        fecha_publicacion: new Date().toISOString()
      })
      
      mostrarNotificacion('Publicación enviada exitosamente', 'success')
    }

    resetForm()

    setTimeout(() => {
      dialog.value = false
    }, 500)
  } catch (error) {
    if (error.status === 400) {
      mostrarNotificacion(error.response.data.mensaje || 'Error en los datos proporcionados.', 'error')
    } else {
      mostrarNotificacion(`Error al ${isEditMode.value ? 'actualizar' : 'enviar'} la publicación. Por favor, inténtalo de nuevo.`, 'error')
    }
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

.current-image-container {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  border: 2px solid #e0e0e0;
}

.current-image {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  display: block;
}

.remove-image-btn {
  margin-top: 8px;
  font-size: 14px;
}
</style>
