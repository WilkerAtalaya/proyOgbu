import { dateFormatV2 } from '@/util/functions'
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
import { NButton, NModal, NInput, NSelect, NDataTable } from 'naive-ui'
import CitasService from '@/services/CitasService'
import LoginService from '@/services/LoginService'
import type { CitaAdmin, CitaAlumno } from '@/models/Cita'

export function useSessionList() {
  const isAdmin = LoginService.isAdmin()
  const user = ref(LoginService.getCurrentUser())

  const studentTabActive = ref('appointment-list')
  const adminTabActive = ref('pending')
  const showModalNewSession = ref(false)

  const appointments = ref<any[]>([])
  // const selectedFilterTab = ref('todos')
  const currentPage = ref(1)
  const itemsPerPage = ref(10)

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
  const modalVisible = ref(false)
  const citaSeleccionada = ref<any>(null)
  const form = ref({ motivo: '', descripcion: '', area: '' })
  const selectedItem = ref({
    numero: '',
    asunto: '',
    motivo: '',
    fecha: '',
    estado: '',
    descripcion: '',
    attend: false,
  })

  const filters = ref({
    area_id: null as number | null,
    fecha: null,
    search: '',
    status: 'todos',
  })

  const statusFilter = [
    { value: 'todos', label: 'Todos' },
    { value: 'solicitados', label: 'Solicitados' },
    { value: 'aprobados', label: 'Aprobados' },
    { value: 'reprogramados', label: 'Reprogramados' },
    // { value: 'atendidos', label: 'Atendidos' },
    // { value: 'ausentes', label: 'Ausentes' },
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
      if (isAdmin) {
        if (adminTabActive.value === 'pending') {
          appointments.value = await CitasService.obtenerCitasPendientes(getFilters())
        } else {
          appointments.value = await CitasService.obtenerCitasCulminadas(getFilters())
        }
      } else {
        appointments.value = await CitasService.obtenerCitasSolicitadasPorUsuario(user.value.id)
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

  async function handleConsultar(row: any) {
    const data = await loadCita(row)
    citaSeleccionada.value = data
    modalVisible.value = true
  }

  async function handleAprobar(row: any) {
    console.log('mi row', row)
    const data = await loadCita(row)
    citaSeleccionada.value = data
    modalVisible.value = true
  }

  async function handleReprogramar(row: any) {
    console.log('mi row', row)
    const data = await loadCita(row)
    citaSeleccionada.value = data
    modalVisible.value = true
  }

  async function handleDetalle(row: any) {
    console.log('mi row', row)
    const data = await loadCita(row)
    citaSeleccionada.value = data
    modalVisible.value = true
  }

  const submitCita = () => {
    console.log('Formulario enviado:', form.value, selectedSlot.value)
    showModal.value = false
  }

  async function loadCita(row: any) {
    console.log('rowID', row)
    const items = await CitasService.obtenerCitaPorId(row.id)
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
    filters.value.area_id = null
    filters.value.fecha = null
    // handleBuscar()
  }

  function openModalNewSession() {
    selectedItem.value = {
      numero: '',
      asunto: '',
      motivo: '',
      fecha: '',
      estado: '',
      descripcion: '',
      attend: false,
    }
    showModalNewSession.value = true
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Solicitado':
        return 'yellow'
      case 'Aprobado':
        return 'success'
      case 'Reprogramado':
        return 'deep-orange'
      case 'Atendido':
        return 'primary'
      case 'Ausente':
        return 'error'
      default:
        return 'secondary'
    }
  }

  const matchesFilters = (ap: any) => {
    const search = filters.value.search.toLowerCase()

    const matchesSearch =
      ap.nombre?.toLowerCase().includes(search) || ap.motivo?.toLowerCase().includes(search)

    const matchesArea = !filters.value.area_id || ap.area === filters.value.area_id

    const matchesFecha =
      !filters.value.fecha ||
      ap.fecha?.slice(0, 10) === new Date(filters.value.fecha).toISOString().slice(0, 10)

    const matchesTab =
      filters.value.status === 'todos' ||
      (filters.value.status === 'solicitados' && ap.estado === 'Solicitado') ||
      (filters.value.status === 'aprobados' && ap.estado === 'Aprobado') ||
      (filters.value.status === 'reprogramados' && ap.estado === 'Reprogramado')

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
    statusFilter,
    clearFilters,
    form,
    submitCita,
    showModal,
    selectedSlot,
    dateFormatV2,
    dataTableInst: ref(null),
    modalVisible,
    citaSeleccionada,
    selectedItem,
    showModalNewSession,
    openModalNewSession,
    getStatusColor,
  }
}
