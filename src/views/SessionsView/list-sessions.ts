import { ref, onMounted, watch, computed } from 'vue'
import { notify } from '@/shared/composables/useNotifier'
import { NotificationType } from '@/shared/enums/notification.enum'
import CitasService from '@/services/CitasService'
import LoginService from '@/services/LoginService'
import type { Cita } from '@/models/Cita'
import { UserRole } from '@/shared/enums/role.enum'
import { AppointmentStatus } from '@/shared/enums/appointment-status.enum'

export function useSessionList() {
  const user = ref(LoginService.getCurrentUser())
  const isStudent = LoginService.getUserRole() == UserRole.STUDENT

  /* ************ Pestañas ************ */
  const studentTabActive = ref('appointment-list')
  const adminTabActive = ref<'pending' | 'completed'>('pending')

  const showModalNewSession = ref(false)

  const appointments = ref<any[]>([])

  /* ************ STUDENT PROFILE ************ */

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
  const selectedAppointment = ref<Cita | null>(null)
  const form = ref({ motivo: '', descripcion: '', area: '' })

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
        fecha: filtersBusySchedulesStudent.value.date ?? undefined,
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

  function openModalNewSession() {
    showModalNewSession.value = true
  }

  async function loadCita(appointmentId: number) {
    const params = { id_usuario: user.value.id }
    const items = await CitasService.obtenerCitaPorId(appointmentId, params)
    return items
  }

  async function handleDetail(appointmentId: number) {
    const data = await loadCita(appointmentId)
    selectedAppointment.value = data
    showModalDetail.value = true
  }

  async function updateAppointmentStatus(status: string) {
    try {
      if (!selectedAppointment.value) return true

      const params = { id_usuario: user.value.id }
      const newStatus = { estado: status }
      const response = await CitasService.updateStatus(
        selectedAppointment.value.id,
        newStatus,
        params,
      )
      console.log(response)

      if (status !== AppointmentStatus.REPROGRAMADO)
        notify('Estado de cita actualizado correctamente.', NotificationType.SUCCESS)

      loadAppointments()
    } catch (err: any) {
      notify(
        err?.response?.data?.error ?? 'Error al actualizar estado de la cita',
        NotificationType.ERROR,
      )
    }
  }

  async function acceptReschedule() {
    try {
      if (!selectedAppointment.value) return true

      const params = { id_usuario: user.value.id }
      const body = { aceptar: true }

      const response = await CitasService.acceptReschedule(
        selectedAppointment.value.id,
        body,
        params,
      )
      console.log(response)

      notify('Cita aceptada correctamente.', NotificationType.SUCCESS)
      loadAppointments()
    } catch (err: any) {
      notify(
        err?.response?.data?.error ?? 'Error al aceptar la reprogramación de la cita',
        NotificationType.ERROR,
      )
    }
  }

  async function openModalReschedule(appointment: Cita) {
    selectedAppointment.value = appointment
    showModalReschedule.value = true
  }

  function getFilters() {
    const params: Record<string, any> = {}
    params.id_usuario = user.value.id
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

  function clearFiltersStudent() {
    filtersBusySchedulesStudent.value = { area_id: null, date: null }
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

  watch(studentTabActive, () => {
    clearFiltersStudent()
    loadBusySchedules()
  })

  watch(adminTabActive, () => {
    clearFilters()
    loadAppointments()
  })

  watch(
    () => [filtersBusySchedulesStudent.value.area_id, filtersBusySchedulesStudent.value.date],
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
    isStudent,
    listAreas,
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
    handleDetail,
    showModalDetail,
    selectedAppointment,
    openModalNewSession,
    showModalNewSession,
    openModalReschedule,
    showModalReschedule,
    updateAppointmentStatus,
    acceptReschedule,
    getStatusColor,
  }
}
