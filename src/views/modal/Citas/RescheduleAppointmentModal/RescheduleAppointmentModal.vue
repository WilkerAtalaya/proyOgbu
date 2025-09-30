<template>
  <v-dialog v-model="dialog" max-width="500px" persistent>
    <v-card class="pa-4 rounded-xl">
      <v-card-title class="d-flex justify-space-between align-center pa-0 mb-4">
        <h2 class="text-h5 font-weight-bold text-pink">
          {{ isEditing ? 'Cita Reprogramada' : 'Reprogramar Cita' }}
        </h2>
        <v-btn icon="fa-solid fa-xmark" variant="text" color="primary" @click="closeDialog" />
      </v-card-title>

      <v-form ref="formRef" @submit.prevent="handleSubmit">
        <v-row class="mb-4" dense>
          <v-col cols="12" md="12">
            <label class="text-body-2 font-weight-medium mb-2 d-block">Nueva Fecha</label>
            <VueDatePicker
              v-model="form.date"
              :rules="[rules.required]"
              :min-date="new Date()"
              :disabled-dates="disableWeekends"
              locale="es"
              format="dd/MM/yyyy"
              :ui="{ input: 'custom-input' }"
              :enable-time-picker="false"
              placeholder="Selecciona la fecha"
              density="compact"
              model-type="yyyy-MM-dd"
              :disabled="appointment?.reprog?.solicitada_por !== null"
            />
          </v-col>
        </v-row>

        <v-row class="mb-4" dense>
          <v-col cols="12" md="6" sm="6">
            <label class="text-body-2 font-weight-medium mb-2 d-block">Nueva Hora de Inicio</label>
            <v-select
              v-model="form.startTime"
              :items="hoursList"
              :rules="[rules.required]"
              placeholder="Seleccionar hora inicio"
              variant="outlined"
              density="compact"
              clearable
              class="custom-input"
              @update:model-value="resetEndTime"
              :disabled="appointment?.reprog?.solicitada_por !== null"
            />
          </v-col>

          <v-col cols="12" md="6" sm="6">
            <label class="text-body-2 font-weight-medium mb-2 d-block">Nueva Hora de Fin</label>
            <v-select
              v-model="form.endTime"
              :items="endHoursList"
              :rules="[rules.required]"
              placeholder="Seleccionar hora fin"
              variant="outlined"
              density="compact"
              clearable
              class="custom-input"
              :disabled="!form.startTime || appointment?.reprog?.solicitada_por !== null"
            />
          </v-col>
        </v-row>

        <div class="d-flex justify-center">
          <template
            v-if="
              !!appointment?.reprog?.solicitada_por &&
              user.id !== appointment?.reprog?.solicitada_por
            "
          >
            <v-btn
              type="button"
              color="success"
              rounded="xl"
              size="large"
              min-width="130"
              elevation="2"
              variant="flat"
              @click="handleUpdateStatus(AppointmentStatus.APROBADO, true)"
            >
              Aceptar
            </v-btn>
          </template>
          <template v-if="appointment?.reprog?.solicitada_por == null">
            <v-btn
              type="submit"
              color="#e91e63"
              size="large"
              style="border-radius: 20px; text-transform: none; font-weight: 500"
              min-width="120px"
            >
              Reprogramar
            </v-btn>
          </template>
        </div>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'
import { useRescheduleAppointmentModal } from './reschedule-appointment-modal'
import './RescheduleAppointmentModal.scss'
import type { Cita } from '@/models/Cita'
import { AppointmentStatus } from '@/shared/enums/appointment-status.enum'

const props = defineProps<{
  modelValue: boolean
  appointment: Cita | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'update-status', status: string, reschedule?: boolean): void
  (e: 'saved'): void
}>()

const dialog = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

watch(
  () => props.appointment,
  (newAppointment) => {
    if (newAppointment) {
      setFormForEdit(newAppointment)
    }
  },
)

const {
  user,
  form,
  formRef,
  disableWeekends,
  hoursList,
  endHoursList,
  rules,
  resetEndTime,
  handleSubmit,
  closeDialog,
  setFormForEdit,
  isEditing,
  handleUpdateStatus,
} = useRescheduleAppointmentModal(emit)
</script>
