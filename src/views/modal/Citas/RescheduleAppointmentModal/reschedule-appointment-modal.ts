import { dateFormatDB, currentDate } from '@/shared/util/functions'
import { ref, reactive, watch, computed, onMounted } from 'vue'
import CitasService from '@/services/CitasService'
import LoginService from '@/services/LoginService'
import '@vuepic/vue-datepicker/dist/main.css'

type EmitFn = {
  (e: 'update:modelValue', v: boolean): void
}

export function useRescheduleAppointmentModal(appointmentId: Ref<number | null>, emit: EmitFn) {
  const user = ref(LoginService.getCurrentUser())

  const formRef = ref()
  const form = reactive<{ date: String; startTime: String; endTime: String }>({
    date: '',
    startTime: '',
    endTime: '',
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
    if (form.endTime) {
      const startIndex = hoursList.indexOf(form.startTime)
      const endIndex = hoursList.indexOf(form.endTime)
      if (endIndex <= startIndex) form.endTime = ''
    }
  }

  const endHoursList = computed(() => {
    const startIndex = hoursList.indexOf(form.startTime)
    return startIndex === -1 ? [] : hoursList.slice(startIndex + 1)
  })

  const resetForm = () => {
    form.date = ''
    form.startTime = ''
    form.endTime = ''

    formRef.value?.reset()
  }

  const closeDialog = () => emit('update:modelValue', false)

  async function submitComplaint() {
    const { valid } = await (formRef.value?.validate() ?? { valid: false })
    if (!valid) return

    const rescheduleForm: any = {
      horario: `${form.startTime} - ${form.endTime}`,
    }

    if (form.date) {
      let fechaStr = form.date
      if (form.date instanceof Date) {
        const dia = form.date.getDate().toString().padStart(2, '0')
        const mes = (form.date.getMonth() + 1).toString().padStart(2, '0')
        const anio = form.date.getFullYear()
        fechaStr = `${dia}/${mes}/${anio}`
      }
      rescheduleForm.fecha = dateFormatDB(fechaStr)
    } else {
      rescheduleForm.fecha = dateFormatDB(currentDate())
    }

    const params = { id_usuario: user.value.id }

    const response = await CitasService.rescheduleAppointment(
      appointmentId.value,
      rescheduleForm,
      params,
    )
    console.log(form)
    closeDialog()
    resetForm()
    alert('Cita reprogramada exitosamente')
  }

  return {
    form,
    formRef,
    hoursList,
    endHoursList,
    rules,
    resetEndTime,
    submitComplaint,
  }
}
