<template>
  <v-dialog v-model="dialog" max-width="500px" persistent>
    <v-card class="pa-4" style="border-radius: 16px">
      <v-card-title class="d-flex justify-space-between align-center pa-0 mb-4">
        <h2 class="text-h5 font-weight-bold" style="color: #e91e63">Nuevo Reconocimiento</h2>
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
import { ref, reactive, computed } from 'vue'
import LoginService from '@/services/LoginService'
import ReconocimientosService from '@/services/ReconocimientosService'

const form = reactive({ descripcion: '' })
const props = defineProps({
  modelValue: Boolean,
  mode: Boolean,
})
const emit = defineEmits(['update:modelValue', 'agregarReconocimiento'])
const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

async function submitReconocimiento() {
  const user = LoginService.getCurrentUser()
  const body = {
    descripcion: form.descripcion,
    fecha: new Date().toISOString().split('T')[0],
    id_usuario: user.id,
    id_alumno: 5
  }
  const response = await ReconocimientosService.crearReconocimiento(body)
  emit('agregarReconocimiento', {
    id_usuario: user.id,
    descripcion: body.descripcion,
    fecha: body.fecha,
  })
  
  form.descripcion = ''
  dialog.value = false
  alert('Reconocimiento enviado exitosamente')
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
