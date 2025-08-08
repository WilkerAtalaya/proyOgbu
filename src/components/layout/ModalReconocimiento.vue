<template>
  <ContainerModal v-model="dialog" colorTheme="#A80038" title="Realizar un Reconocimiento">
    <v-form @submit.prevent="submitReconocimiento">
      <div class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400;"> Alumno </label>
        <v-autocomplete v-model="form.alumnoSeleccionado" :items="alumnos" item-title="nombre" item-value="id"
          variant="outlined" hide-details class="custom-input" :disabled="mode" :loading="cargandoAlumnos"
          :search="terminoBusqueda" @update:search="buscarAlumnos" placeholder="Buscar alumno por nombre..."
          return-object clearable :error="!!errors.alumnoSeleccionado">
          <template v-slot:item="{ props, item }">
            <v-list-item v-bind="props" :title="item.raw.nombre" :subtitle="item.raw.correo"></v-list-item>
          </template>
        </v-autocomplete>
        <span v-if="errors.alumnoSeleccionado" class="error-message">{{ errors.alumnoSeleccionado }}</span>
      </div>

      <div class="mb-4">
        <label style="font-size: 18px; color: black; font-weight: 400;"> Descripción </label>
        <v-textarea v-model="form.descripcion" variant="outlined" rows="4" hide-details class="custom-input"
          :disabled="mode" :error="!!errors.descripcion"></v-textarea>
        <span v-if="errors.descripcion" class="error-message">{{ errors.descripcion }}</span>
      </div>

      <div v-if="!mode" class="d-flex justify-center">
        <v-btn type="submit" color="#F2B200" size="large"
          style="border-radius: 15px; text-transform: none; font-weight: 400; font-size: 18px; padding: 12px 24px;"
          min-width="120px">
          Publicar
        </v-btn>
      </div>
    </v-form>
  </ContainerModal>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import LoginService from '@/services/LoginService'
import ReconocimientosService from '@/services/ReconocimientosService'
import ContainerModal from './ContainerModal.vue'

const form = reactive({
  descripcion: '',
  alumnoSeleccionado: null
})
const errors = reactive({
  descripcion: '',
  alumnoSeleccionado: ''
})

const alumnos = ref([])
const cargandoAlumnos = ref(false)
const terminoBusqueda = ref('')
let timeoutBusqueda = null

const props = defineProps({
  modelValue: Boolean,
  mode: Boolean,
})
const emit = defineEmits(['update:modelValue', 'agregarReconocimiento', 'mostrar-notificacion'])
const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const buscarAlumnos = (termino) => {
  terminoBusqueda.value = termino

  if (timeoutBusqueda) {
    clearTimeout(timeoutBusqueda)
  }

  if (!termino || termino.length < 2) {
    alumnos.value = []
    return
  }

  timeoutBusqueda = setTimeout(async () => {
    try {
      cargandoAlumnos.value = true
      const resultados = await ReconocimientosService.buscarAlumnos(termino)
      alumnos.value = resultados
    } catch (error) {
      console.error('Error al buscar alumnos:', error)
      alumnos.value = []
    } finally {
      cargandoAlumnos.value = false
    }
  }, 500)
}

function mostrarNotificacion(mensaje, tipo = 'success') {
  emit('mostrar-notificacion', { mensaje, tipo })
}

function validateField(field, value) {
  switch (field) {
    case 'descripcion':
      if (!value || value.trim() === '') {
        errors.descripcion = 'La descripción es obligatoria'
        return false
      }
      errors.descripcion = ''
      return true
    case 'alumnoSeleccionado':
      if (!value) {
        errors.alumnoSeleccionado = 'Debe seleccionar un alumno'
        return false
      }
      errors.alumnoSeleccionado = ''
      return true
    default:
      return true
  }
}

function validateForm() {
  let isValid = true
  isValid = validateField('descripcion', form.descripcion) && isValid
  isValid = validateField('alumnoSeleccionado', form.alumnoSeleccionado) && isValid
  return isValid
}

watch(() => form.descripcion, (newValue) => {
  if (errors.descripcion) validateField('descripcion', newValue)
})

watch(() => form.alumnoSeleccionado, (newValue) => {
  if (errors.alumnoSeleccionado) validateField('alumnoSeleccionado', newValue)
})

async function submitReconocimiento() {
  if (!validateForm()) {
    return
  }

  try {
    const user = LoginService.getCurrentUser()
    const body = {
      descripcion: form.descripcion,
      fecha: new Date().toISOString().split('T')[0],
      id_usuario: user.id,
      id_alumno: form.alumnoSeleccionado.id
    }

    const response = await ReconocimientosService.crearReconocimiento(body)
    emit('agregarReconocimiento', {
      id_usuario: user.id,
      descripcion: body.descripcion,
      fecha: body.fecha,
      nombre_alumno: form.alumnoSeleccionado.nombre
    })

    form.descripcion = ''
    form.alumnoSeleccionado = null
    alumnos.value = []
    terminoBusqueda.value = ''
    Object.keys(errors).forEach(key => errors[key] = '')

    mostrarNotificacion('Reconocimiento enviado exitosamente', 'success')

    setTimeout(() => {
      dialog.value = false
    }, 500)
  } catch (error) {
    console.error('Error al crear reconocimiento:', error)
    mostrarNotificacion('Error al enviar el reconocimiento. Por favor, inténtalo de nuevo.', 'error')
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

.error-message {
  color: #d32f2f;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}
</style>
