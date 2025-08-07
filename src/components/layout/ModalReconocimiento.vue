<template>
  <v-dialog v-model="dialog" max-width="600px" persistent>
    <v-card style="border-radius: 16px; padding: 32px 45px 36px;">
      <v-card-title class="d-flex justify-space-between align-center pa-0 mb-4">
        <h2 style="color: #A80038; text-align: center; flex: 1; font-size: 35px; font-weight: 400; font-family: 'Righteous', cursive;">Realizar un Reconocimiento</h2>
        <button
          @click="dialog = false"
          style="background: none; border: none; cursor: pointer"
          title="Cerrar Modal"
        >
          <i class="fa-solid fa-xmark" style="color: #1976d2; font-size: 20px"></i>
        </button>
      </v-card-title>

      <v-form @submit.prevent="submitReconocimiento">
        <div class="mb-4">
          <label style="font-size: 18px; color: black; font-weight: 400;"> Alumno </label>
          <v-autocomplete
            v-model="form.alumnoSeleccionado"
            :items="alumnos"
            item-title="nombre"
            item-value="id"
            variant="outlined"
            hide-details
            class="custom-input"
            :disabled="mode"
            :loading="cargandoAlumnos"
            :search="terminoBusqueda"
            @update:search="buscarAlumnos"
            placeholder="Buscar alumno por nombre..."
            return-object
            clearable
          >
            <template v-slot:item="{ props, item }">
              <v-list-item v-bind="props" :title="item.raw.nombre" :subtitle="item.raw.correo"></v-list-item>
            </template>
          </v-autocomplete>
        </div>

        <div class="mb-4">
          <label style="font-size: 18px; color: black; font-weight: 400;"> Descripción </label>
          <v-textarea
            v-model="form.descripcion"
            variant="outlined"
            rows="4"
            hide-details
            class="custom-input"
            :disabled="mode"
          ></v-textarea>
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
import { ref, reactive, computed, watch } from 'vue'
import LoginService from '@/services/LoginService'
import ReconocimientosService from '@/services/ReconocimientosService'

const form = reactive({ 
  descripcion: '', 
  alumnoSeleccionado: null 
})

const alumnos = ref([])
const cargandoAlumnos = ref(false)
const terminoBusqueda = ref('')
let timeoutBusqueda = null

const props = defineProps({
  modelValue: Boolean,
  mode: Boolean,
})
const emit = defineEmits(['update:modelValue', 'agregarReconocimiento'])
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

async function submitReconocimiento() {
  if (!form.alumnoSeleccionado) {
    alert('Por favor selecciona un alumno')
    return
  }
  
  const user = LoginService.getCurrentUser()
  const body = {
    descripcion: form.descripcion,
    fecha: new Date().toISOString().split('T')[0],
    id_usuario: user.id,
    id_alumno: form.alumnoSeleccionado.id
  }
  
  try {
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
    
    dialog.value = false
    alert('Reconocimiento enviado exitosamente')
  } catch (error) {
    console.error('Error al crear reconocimiento:', error)
    alert('Error al enviar el reconocimiento')
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
</style>
