import { ref, reactive, watch, computed, onMounted } from 'vue'
import { dateFormatDB, currentDate } from '@/shared/util/functions'
import { notify } from '@/shared/composables/useNotifier'
import { NotificationType } from '@/shared/enums/notification.enum'
import CitasService from '@/services/CitasService'
import LoginService from '@/services/LoginService'
import '@vuepic/vue-datepicker/dist/main.css'

type EmitFn = {
  (e: 'update:modelValue', v: boolean): void
  (e: 'saved'): void
}

export function useCreateAppointmentModal(emit: EmitFn) {
  const formRef = ref()

  const user = ref(LoginService.getCurrentUser())
  const isAdmin = LoginService.isAdmin()

  // const fileInput = ref(null)
  // const selectedFile = ref(null)

  const form = reactive<any>({
    reason_id: null,
    specialist: '',
    description: '',
    date: '',
    startTime: '',
    endTime: '',
    // numero: '',
    // tipo: '',
    // titulo: '',
    // estado: '',
  })

  const rules = {
    required: (v: any) => !!v || 'Este campo es obligatorio',
  }

  const reasonList = ref()

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

  // const triggerFileInput = () => {
  //   fileInput.value.click()
  // }

  // const handleFileSelect = (event) => {
  //   const file = event.target.files[0]
  //   if (file) {
  //     selectedFile.value = file
  //   }
  // }

  const resetForm = () => {
    form.reason_id = null
    form.specialist = ''
    form.description = ''
    form.date = ''
    form.startTime = ''
    form.endTime = ''

    formRef.value?.reset()
  }

  const closeDialog = () => emit('update:modelValue', false)

  async function handleSubmit() {
    try {
      const { valid } = await (formRef.value?.validate() ?? { valid: false })
      if (!valid) return

      const appointmentForm: any = {
        id_usuario: user.value.id,
        area: form.specialist,
        horario: `${form.startTime} - ${form.endTime}`,
        motivo: reasonList.value.find((r: any) => r.id == form.reason_id)?.motivo,
        descripcion: form.description,
      }

      if (form.date) {
        let fechaStr = form.date
        if (form.date instanceof Date) {
          const dia = form.date.getDate().toString().padStart(2, '0')
          const mes = (form.date.getMonth() + 1).toString().padStart(2, '0')
          const anio = form.date.getFullYear()
          fechaStr = `${dia}/${mes}/${anio}`
        }
        appointmentForm.fecha = dateFormatDB(fechaStr)
      } else {
        appointmentForm.fecha = dateFormatDB(currentDate())
      }

      const response = await CitasService.crearCita(appointmentForm)

      emit('saved')
      closeDialog()
      resetForm()
      notify('Cita creada correctamente.', NotificationType.SUCCESS)
    } catch (err) {
      notify(err, NotificationType.ERROR)
    }
  }

  const loadReasons = async () => {
    try {
      reasonList.value = await CitasService.getReasons()
    } catch (error) {
      console.log(error)
    }
  }

  watch(
    () => form.reason_id,
    (newVal) => {
      const specialistId = reasonList.value.find((r: any) => r.id === newVal)?.area
      form.specialist = specialistId ?? ''
    },
  )

  onMounted(async () => {
    loadReasons()
  })

  return {
    form,
    formRef,
    reasonList,
    hoursList,
    endHoursList,
    rules,
    resetEndTime,
    handleSubmit,
  }
}
