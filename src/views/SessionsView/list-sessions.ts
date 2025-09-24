import {
  defineComponent,
  ref,
  h,
  onMounted,
  reactive,
  resolveComponent,
  watch,
  computed,
} from 'vue'
import { dateFormatV2 } from '@/shared/util/functions'
import { NButton, NModal, NInput, NSelect, NDataTable } from 'naive-ui'
import { notify } from '@/shared/composables/useNotifier'
import { NotificationType } from '@/shared/enums/notification.enum'
import CitasService from '@/services/CitasService'
import LoginService from '@/services/LoginService'
import type { Cita } from '@/models/Cita'
import { UserRole } from '@/shared/enums/role.enum'

export function useSessionList() {
  const isAdmin = LoginService.isAdmin()
  const isStudent = LoginService.getUserRole() == UserRole.STUDENT
  const user = ref(LoginService.getCurrentUser())

  /* ************ Pestañas ************ */
  const studentTabActive = ref('appointment-list')
  const adminTabActive = ref<'pending' | 'completed'>('pending')

  const showModalNewSession = ref(false)
  const snackbar = reactive({ show: false, message: '', color: 'success' })

  const appointments = ref<any[]>([])

  /* ************ STUDENT PROFILE ************ */

  const showModal = ref(false)
  const selectedSlot = ref<any>(null)

  const listReasons = ref()

  // Busy Schedules
  const listAreas = ref()
  const listBusySchedules = ref()

  const columnsBusySchedulesStudent = [
    { title: 'Especialista', key: 'area' },
    { title: 'Fecha', key: 'fecha' },
    { title: 'Horario', key: 'horario' },
  ]

  const filtersBusySchedulesStudent = ref({
    area_id: null,
    date: null,
  })

  /* ************ ADMIN PROFILE ************ */
  const showModalDetail = ref(false)
  const showModalReschedule = ref(false)
  const appointmentToView = ref<Cita | null>(null)
  const form = ref({ motivo: '', descripcion: '', area: '' })
  const selectedAppointmentId = ref<number | null>(null)

  const currentPage = ref(1)
  const itemsPerPage = ref(10)

  const filters = ref<any>({
    area_id: null as number | null,
    fecha: null as string | null,
    search: '',
    status: 'todos',
  })

  const statusFilter = [
    { value: 'todos', label: 'Todos' },
    { tab: 'pending', value: 'solicitados', label: 'Solicitados' },
    { tab: 'pending', value: 'aprobados', label: 'Aprobados' },
    { tab: 'pending', value: 'reprogramados', label: 'Reprogramados' },
    { tab: 'completed', value: 'atendidos', label: 'Atendidos' },
    { tab: 'completed', value: 'ausentes', label: 'Ausentes' },
  ]

  // const columnsAlumno = [
  //   { title: 'Número', key: 'index' },
  //   { title: 'Fecha', key: 'fecha' },
  //   { title: 'Horario', key: 'horario' },
  //   { title: 'Motivo', key: 'motivo' },
  //   { title: 'Area', key: 'area' },
  //   {
  //     title: 'Estado',
  //     key: 'estado',
  //     render(row: any) {
  //       if (row.estado === 'Solicitado') {
  //         return h(
  //           NButton,
  //           {
  //             size: 'small',
  //             class: 'btn-disponible',
  //             onClick: () => {
  //               selectedSlot.value = row
  //               showModal.value = true
  //             },
  //           },
  //           { default: () => 'Solicitado' },
  //         )
  //       } else {
  //         return h(
  //           NButton,
  //           {
  //             size: 'small',
  //             class: 'btn-no-disponible',
  //             disabled: true,
  //           },
  //           { default: () => 'Aprobado' },
  //         )
  //       }
  //     },
  //   },
  // ]

  const loadAppointments = async () => {
    try {
      if (isStudent) {
        appointments.value = await CitasService.obtenerCitasSolicitadasPorUsuario(user.value.id)
      } else {
        appointments.value =
          adminTabActive.value === 'pending'
            ? await CitasService.obtenerCitasPendientes(getFilters())
            : await CitasService.obtenerCitasCulminadas(getFilters())
      }
    } catch (error) {
      console.error('Error al cargar citas:', error)
    }
  }

  const loadBusySchedules = async () => {
    try {
      const params: any = {
        area:
          listAreas.value?.find((a: any) => a.id_area == filtersBusySchedulesStudent.value.area_id)
            ?.area ?? undefined,
        date: filtersBusySchedulesStudent.value.date ?? undefined,
      }

      listBusySchedules.value = await CitasService.getBusySchedules(params)
    } catch (error) {
      console.log(error)
    }
  }

  const loadAreas = async () => {
    try {
      listAreas.value = await CitasService.getAreas()
    } catch (error) {
      console.log(error)
    }
  }

  async function handleDetail(appointmentId: number) {
    const data = await loadCita(appointmentId)
    appointmentToView.value = data
    showModalDetail.value = true
  }

  async function openModalReschedule(appointmentId: number) {
    selectedAppointmentId.value = appointmentId
    showModalReschedule.value = true
  }

  async function updateAppointmentStatus(status: string) {
    try {
      if (!appointmentToView.value) return true

      const params = { id_usuario: user.value.id }
      const newStatus = { estado: status }
      const response = await CitasService.updateStatus(
        appointmentToView.value.id,
        newStatus,
        params,
      )
      console.log(response)

      notify('Estado de cita actualizado correctamente.', NotificationType.SUCCESS)
      loadAppointments()
    } catch (error) {
      notify('Error al actualizar estado de la cita.', NotificationType.ERROR)
    }
  }

  const submitCita = () => {
    console.log('Formulario enviado:', form.value, selectedSlot.value)
    showModal.value = false
  }

  async function loadCita(appointmentId: number) {
    const params = { id_usuario: user.value.id }
    const items = await CitasService.obtenerCitaPorId(appointmentId, params)
    return items
  }

  function getFilters() {
    const params: Record<string, any> = {}
    if (filters.value.area_id) params.area = filters.value.area_id
    if (filters.value.fecha) {
      const fechaObj = new Date(filters.value.fecha)
      params.fecha = fechaObj.toISOString().split('T')[0]
    }
    return params
  }

  function clearFilters() {
    filters.value = { area_id: null, fecha: null, search: '', status: 'todos' }
  }

  function openModalNewSession() {
    showModalNewSession.value = true
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Solicitado':
        return 'indigo'
      case 'Aprobado':
        return 'success'
      case 'Reprogramado':
        return 'warning'
      case 'Atendido':
        return 'teal'
      case 'Ausente':
        return 'grey'
      default:
        return 'secondary'
    }
  }

  const statusFilterByTab = computed(() =>
    statusFilter.filter(
      (s) => !s.tab || s.tab === adminTabActive.value, // incluye "Todos" siempre
    ),
  )

  const matchesFilters = (ap: any) => {
    const search = filters.value.search.toLowerCase()

    const matchesSearch =
      ap.nombre?.toLowerCase().includes(search) || ap.motivo?.toLowerCase().includes(search)

    const matchesArea = !filters.value.area_id || ap.area_id === filters.value.area_id

    const matchesFecha =
      !filters.value.fecha ||
      ap.fecha?.slice(0, 10) === new Date(filters.value.fecha).toISOString().slice(0, 10)

    const matchesTab =
      filters.value.status === 'todos' ||
      (adminTabActive.value === 'pending' &&
        ((filters.value.status === 'solicitados' && ap.estado === 'Solicitado') ||
          (filters.value.status === 'aprobados' && ap.estado === 'Aprobado') ||
          (filters.value.status === 'reprogramados' && ap.estado === 'Reprogramado'))) ||
      (adminTabActive.value === 'completed' &&
        ((filters.value.status === 'atendidos' && ap.estado === 'Atendido') ||
          (filters.value.status === 'ausentes' && ap.estado === 'Ausente')))

    return matchesSearch && matchesArea && matchesFecha && matchesTab
  }

  // Base filtrada (sin paginación)
  const appointmentsFilteredTotal = computed(() => appointments.value.filter(matchesFilters))

  // Con paginación
  const appointmentsFiltered = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage.value
    return appointmentsFilteredTotal.value.slice(start, start + itemsPerPage.value)
  })

  // Total ítems filtrados
  const totalFilteredItems = computed(() => appointmentsFilteredTotal.value.length)

  // Total de páginas
  const totalPages = computed(() => {
    return Math.ceil(totalFilteredItems.value / itemsPerPage.value)
  })

  watch(adminTabActive, () => {
    clearFilters() // 🔥 limpia filtros al cambiar de pestaña
    loadAppointments()
  })

  watch(
    () => filtersBusySchedulesStudent.value.area_id,
    () => {
      loadBusySchedules()
    },
  )

  watch(
    () => ({ ...filters.value, itemsPerPage: itemsPerPage.value }),
    () => {
      currentPage.value = 1
    },
    { deep: true },
  )

  watch(totalPages, (newTotalPages) => {
    if (currentPage.value > newTotalPages && newTotalPages > 0) {
      currentPage.value = newTotalPages
    }
  })

  onMounted(async () => {
    loadAppointments()
    loadBusySchedules()
    loadAreas()
  })

  return {
    isAdmin,
    isStudent,
    user,
    listAreas,
    listReasons,
    studentTabActive,
    columnsBusySchedulesStudent,
    filtersBusySchedulesStudent,
    listBusySchedules,
    adminTabActive,
    loadAppointments,
    appointmentsFiltered,
    appointmentsFilteredTotal,
    currentPage,
    itemsPerPage,
    totalPages,
    pagination: ref({ pageSize: 7 }),
    filters,
    statusFilterByTab,
    clearFilters,
    form,
    submitCita,
    showModal,
    selectedSlot,
    dateFormatV2,
    dataTableInst: ref(null),
    handleDetail,
    showModalDetail,
    appointmentToView,
    selectedAppointmentId,
    showModalNewSession,
    openModalNewSession,
    showModalReschedule,
    openModalReschedule,
    getStatusColor,
    updateAppointmentStatus,
    snackbar,
  }
}
