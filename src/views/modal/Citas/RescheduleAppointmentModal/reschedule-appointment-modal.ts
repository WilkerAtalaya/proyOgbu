import { ref, reactive, computed, nextTick } from 'vue'
import { notify } from '@/shared/composables/useNotifier'
import { NotificationType } from '@/shared/enums/notification.enum'
import { AppointmentStatus } from '@/shared/enums/appointment-status.enum'
import type { Cita } from '@/models/Cita'
import CitasService from '@/services/CitasService'
import LoginService from '@/services/LoginService'

type EmitFn = {
  (e: 'update:modelValue', v: boolean): void
  (e: 'update-status', status: string): void
  (e: 'saved'): void
}

export function useRescheduleAppointmentModal(emit: EmitFn) {
  const user = ref(LoginService.getCurrentUser())

  const formRef = ref()
  const isEditing = ref(false)
  const editingId = ref<number | null>(null)

  const form = reactive<{ date: string | Date; startTime: string | null; endTime: string | null }>({
    date: '',
    startTime: null,
    endTime: null,
  })

  const rules = {
    required: (v: any) => !!v || 'Este campo es obligatorio',
  }

  const hoursList = [
    '9:00 AM',
    '10:00 AM',
    '11:00 AM',
    '12:00 PM',
    '1:00 PM',
    '2:00 PM',
    '3:00 PM',
    '4:00 PM',
    '5:00 PM',
    '6:00 PM',
    '7:00 PM',
    '8:00 PM',
  ]

  const resetEndTime = () => {
    if (form.startTime && form.endTime) {
      const startIndex = hoursList.indexOf(form.startTime)
      const endIndex = hoursList.indexOf(form.endTime)
      if (endIndex <= startIndex) form.endTime = ''
    }
  }

  const endHoursList = computed(() => {
    if (!form.startTime) return
    const startIndex = hoursList.indexOf(form.startTime)
    return startIndex === -1 ? [] : hoursList.slice(startIndex + 1)
  })

  const setFormForEdit = async (appointment: Cita) => {
    await nextTick()
    editingId.value = appointment.id
    isEditing.value = true

    if (appointment.estado == AppointmentStatus.REPROGRAMADO) {
      const horario = appointment.reprog?.horario || ''
      const [startTime, endTime] = horario
        ? horario.split('-').map((h: string) => h.trim())
        : ['', '']

      form.startTime = startTime ?? ''
      form.endTime = endTime ?? ''
      form.date = appointment.reprog?.fecha ?? ''
    }
  }

  const resetForm = () => {
    form.date = ''
    form.startTime = null
    form.endTime = null
    editingId.value = null
    isEditing.value = false

    formRef.value?.reset()
  }

  const closeDialog = () => emit('update:modelValue', false)

  async function handleSubmit() {
    try {
      const { valid } = await (formRef.value?.validate() ?? { valid: false })
      if (!valid) return

      if (!editingId.value) return

      const rescheduleForm: any = {
        fecha: form.date,
        horario: `${form.startTime} - ${form.endTime}`,
      }

      const params = { id_usuario: user.value.id }

      await CitasService.rescheduleAppointment(editingId.value, rescheduleForm, params)

      emit('update-status', AppointmentStatus.REPROGRAMADO)
      emit('saved')
      resetForm()
      closeDialog()
      notify('Cita reprogramada correctamente.', NotificationType.SUCCESS)
    } catch (err: any) {
      notify(err?.response?.data?.error ?? 'Error al reprogramar la cita', NotificationType.ERROR)
    }
  }

  const handleUpdateStatus = (status: string) => {
    emit('update-status', status)
    emit('saved')
    resetForm()
    closeDialog()
  }

  return {
    user,
    form,
    formRef,
    hoursList,
    endHoursList,
    rules,
    resetEndTime,
    handleSubmit,
    closeDialog,
    setFormForEdit,
    isEditing,
    handleUpdateStatus,
  }
}
