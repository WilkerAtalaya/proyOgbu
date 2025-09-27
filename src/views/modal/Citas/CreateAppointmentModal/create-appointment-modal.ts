import { ref, reactive, watch, computed, onMounted } from 'vue'
import { dateFormatDB, currentDate } from '@/shared/util/functions'
import { notify } from '@/shared/composables/useNotifier'
import { NotificationType } from '@/shared/enums/notification.enum'
import CitasService from '@/services/CitasService'
import LoginService from '@/services/LoginService'
import '@vuepic/vue-datepicker/dist/main.css'
import { debounce } from 'lodash'
import ReconocimientosService from '@/services/ReconocimientosService'
import type { Alumno } from '@/models/Reconocimiento'

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

  const form = reactive<{
    student: Alumno | null
    reason_id: number | null
    specialist_id: number | null
    description: string
    date: Date | string
    startTime: string | null
    endTime: string | null
  }>({
    student: null,
    reason_id: null,
    specialist_id: null,
    description: '',
    date: '',
    startTime: null,
    endTime: null,
  })

  const rules = {
    required: (v: any) => !!v || 'Este campo es obligatorio',
  }

  const students = ref<Alumno[]>([])
  const searchStudent = ref('')
  const loadingSearchStudent = ref(false)

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
    form.student = null
    students.value = []
    form.reason_id = null
    form.specialist_id = null
    form.description = ''
    form.date = ''
    form.startTime = null
    form.endTime = null
    formRef.value?.reset()
  }

  const closeDialog = () => {
    resetForm()
    emit('update:modelValue', false)
  }

  async function handleSubmit() {
    try {
      const { valid } = await (formRef.value?.validate() ?? { valid: false })
      if (!valid) return

      const appointmentForm: any = {
        id_alumno: form.student?.id ?? undefined,
        id_usuario: user.value.id,
        area: form.specialist_id,
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
        appointmentForm.fecha = dateFormatDB(fechaStr.toString())
      } else {
        appointmentForm.fecha = dateFormatDB(currentDate())
      }

      const response = await CitasService.crearCita(appointmentForm)
      emit('saved')
      closeDialog()
      notify('Cita creada correctamente.', NotificationType.SUCCESS)
    } catch (err: any) {
      notify(err?.response?.data?.error ?? 'Error al crear la cita', NotificationType.ERROR)
    }
  }

  const loadReasons = async () => {
    try {
      const params = { id_usuario: user.value.id }
      reasonList.value = await CitasService.getReasons(params)
    } catch (error) {
      console.log(error)
    }
  }

  const searchDebouncedUsers = debounce(async (search) => {
    if (!search || search.length < 3) return

    loadingSearchStudent.value = true
    students.value = await ReconocimientosService.buscarAlumnos(search)
    loadingSearchStudent.value = false
  }, 500)

  watch(
    () => form.reason_id,
    (newVal) => {
      const specialistId = reasonList.value.find((r: any) => r.id === newVal)?.area
      form.specialist_id = specialistId
    },
  )

  onMounted(async () => {
    loadReasons()
  })

  return {
    user,
    form,
    formRef,
    students,
    searchStudent,
    searchDebouncedUsers,
    loadingSearchStudent,
    reasonList,
    hoursList,
    endHoursList,
    rules,
    resetEndTime,
    handleSubmit,
    closeDialog,
  }
}
