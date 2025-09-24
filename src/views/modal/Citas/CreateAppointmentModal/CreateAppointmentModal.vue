<template>
  <v-dialog v-model="dialog" max-width="500px" persistent>
    <v-card class="pa-4 rounded-xl">
      <v-card-title class="d-flex justify-space-between align-center pa-0 mb-4">
        <h2 class="text-h5 font-weight-bold text-pink">Agendar Cita</h2>
        <v-btn icon="fa-solid fa-xmark" variant="text" color="primary" @click="dialog = false" />
      </v-card-title>

      <v-form ref="formRef" @submit.prevent="handleSubmit">
        <div class="mb-4">
          <label class="text-body-2 font-weight-medium mb-2 d-block">Motivo</label>
          <v-select
            v-model="form.reason_id"
            :items="reasonList"
            item-title="motivo"
            item-value="id"
            :rules="[rules.required]"
            variant="outlined"
            density="compact"
            class="custom-input"
          />
        </div>

        <div class="mb-4">
          <label class="text-body-2 font-weight-medium mb-2 d-block">Especialista</label>
          <v-text-field
            v-model="form.specialist"
            variant="outlined"
            density="compact"
            class="custom-input"
            disabled
            hide-details
          />
        </div>

        <div class="mb-4">
          <label class="text-body-2 font-weight-medium mb-2 d-block"> Descripción</label>
          <v-textarea
            v-model="form.description"
            variant="outlined"
            rows="4"
            density="compact"
            class="custom-input"
            hide-details
          />
        </div>

        <v-row class="mb-4" dense>
          <v-col cols="12" md="12">
            <label class="text-body-2 font-weight-medium mb-2 d-block">Fecha</label>
            <VueDatePicker
              v-model="form.date"
              :rules="[rules.required]"
              locale="es"
              format="dd/MM/yyyy"
              :ui="{ input: 'custom-input' }"
              :enable-time-picker="false"
              placeholder="Selecciona la fecha"
              density="compact"
            />
          </v-col>
        </v-row>

        <v-row class="mb-4" dense>
          <v-col cols="12" md="6" sm="6">
            <label class="text-body-2 font-weight-medium mb-2 d-block">Horario Inicio</label>
            <v-select
              v-model="form.startTime"
              :items="hoursList"
              :rules="[rules.required]"
              variant="outlined"
              density="compact"
              class="custom-input"
              @update:model-value="resetEndTime"
            />
          </v-col>

          <v-col cols="12" md="6" sm="6">
            <label class="text-body-2 font-weight-medium mb-2 d-block">Horario Fin</label>
            <v-select
              v-model="form.endTime"
              :items="endHoursList"
              :rules="[rules.required]"
              variant="outlined"
              density="compact"
              class="custom-input"
              :disabled="!form.startTime"
            />
          </v-col>
        </v-row>

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

<script setup lang="ts">
import { watch, computed } from 'vue'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import { useCreateAppointmentModal } from './create-appointment-modal'
import './CreateAppointmentModal.scss'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'saved'): void
}>()

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const { form, formRef, reasonList, hoursList, endHoursList, rules, resetEndTime, handleSubmit } =
  useCreateAppointmentModal(emit)
</script>
