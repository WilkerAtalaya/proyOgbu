<template>
  <div class="citas-container">
    <div class="citas-header">
    <table cellspacing="0" cellpadding="8"style="border-collapse: collapse; width: auto; text-align: left; margin: 0; font-family: sans-serif;">
      <thead>
        <tr style="background-color: #f9f9f9;">
          <th style="border: 1px solid #ccc; padding: 12px;">Mes</th>
          <th style="border: 1px solid #ccc; padding: 12px;">Hora de atención</th>
        </tr>
      </thead>
      <tbody>
        <tr style="background-color: #e0e0e0;">
          <td style="border: 1px solid #ccc; padding: 12px;">Mayo</td>
          <td style="border: 1px solid #ccc; padding: 12px;">
            <div>09:00am - 12:00pm</div>
            <div>02:00pm - 05:00pm</div>
          </td>
        </tr>
      </tbody>
    </table>
    <div class="text-right">
      <v-btn variant="outlined" class="mb-6" @click="openModalNewSession()">Agendar Cita</v-btn>
    </div>
    </div>
    <template v-if="!isAdmin">
      <n-data-table
        class="data-table"
        ref="dataTableInst"
        :columns="columnsAlumno"
        :data="dataAlumno"
        :pagination="pagination"
      />
      <!-- <n-modal v-model:show="showModal" preset="dialog" class="modal-cita">
        <template #header>
          <h2 style="color: #a1003c; text-align: center">Agendar Cita</h2>
        </template>
        <div class="form-cita">
          <div>
            <label>Motivo:</label>
            <n-input placeholder="Motivo de la cita" v-model:value="form.motivo" />
          </div>
          <div>
            <label>Descripción:</label>
            <n-input
              type="textarea"
              placeholder="Describe el motivo..."
              v-model:value="form.descripcion"
            />
          </div>
          <div>
            <label>Área disponible:</label>
            <n-select
              v-model:value="form.area"
              :options="[
                { label: 'Psicología', value: 'psicologia' },
                { label: 'Bienestar', value: 'bienestar' },
              ]"
            />
          </div>
          <div class="horario-seleccionado">
            <label>Horario elegido:</label>
            <div class="slot-box">
              <strong>{{ selectedSlot?.day }}</strong>
              <span>{{ selectedSlot?.hour }}</span>
            </div>
          </div>
          <div style="text-align: center; margin-top: 16px">
            <n-button type="primary" style="background-color: #a1003c" @click="submitCita"
              >Enviar</n-button
            >
          </div>
        </div>
      </n-modal> -->
    </template>
    <template v-else>
      <div>
        <div style="display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 16px">
          <n-input v-model:value="filtros.area" placeholder="Área" style="flex: 1; min-width: 150px" />
          <n-input v-model:value="filtros.nombre" placeholder="Nombre" style="flex: 1; min-width: 150px" />
          <n-input v-model:value="filtros.id_numero" placeholder="ID número" style="flex: 1; min-width: 150px" />
          <n-date-picker
            v-model:value="filtros.fecha"
            type="date"
            placeholder="Fecha"
            format="dd/MM/yyyy"
            value-format="yyyy-MM-dd"
          />
          <n-button @click="handleBuscar" type="primary" style="min-width: 100px">Buscar</n-button>
          <n-button @click="clearFilters" secondary style="min-width: 100px">Limpiar</n-button>
        </div>
        <n-tabs v-model:value="tabActivo" type="line">
          <n-tab-pane name="pendientes" tab="Pendientes">
            <n-data-table
              ref="tablaPendientes"
              :columns="columnsAdmin"
              :data="dataPendiente"
              :pagination="pagination"
            />
          </n-tab-pane>
          <n-tab-pane name="culminadas" tab="Culminadas">
            <n-data-table
              ref="tablaCulminadas"
              :columns="columnsAdmin"
              :data="dataCulminada"
              :pagination="pagination"
            />
          </n-tab-pane>
        </n-tabs>
      </div>
      <n-modal v-model:show="modalVisible" preset="dialog" title="Detalle de Cita">
        <template #default>
          <div style="background-color: white; padding: 16px; border-radius: 6px">
            <p><strong>Fecha:</strong> {{ dateFormatV2(citaSeleccionada?.fecha) }}</p>
            <p><strong>Horario:</strong> {{ citaSeleccionada?.horario }}</p>
            <p><strong>Área:</strong> {{ citaSeleccionada?.area }}</p>
            <p><strong>Nombre:</strong> {{ citaSeleccionada?.nombre }}</p>
            <p><strong>Estado:</strong> {{ citaSeleccionada?.estado }}</p>
          </div>
        </template>
      </n-modal>
       </template>
  </div>
  <ModalCitas v-model="showModalNewSession" :item="selectedItem"/>
</template>
<script lang="ts">
// @ts-ignore
import { dateFormatV2 } from '@/util/functions'
import { defineComponent, ref, h, onMounted, reactive, resolveComponent } from 'vue'
import { NButton, NModal, NInput, NSelect, NDataTable } from 'naive-ui'
import CitasService from '@/services/CitasService'
import LoginService from '@/services/LoginService'
import ModalCitas from './modal/ModalCitas.vue'
import type { CitaAdmin, CitaAlumno } from '@/models/Cita'

export default defineComponent({
  components: {
    NButton,
    NModal,
    NInput,
    NSelect,
    NDataTable,
    ModalCitas
  },
  setup() {
    const showModalNewSession = ref(false)
    const tabActivo = ref('pendientes')
    const dataAlumno = ref<CitaAlumno[]>([])
    const dataPendiente = ref<CitaAdmin[]>([])
    const dataCulminada = ref<CitaAdmin[]>([])
    const showModal = ref(false)
    const selectedSlot = ref<any>(null)
    const isAdmin = LoginService.isAdmin()
    const user = ref(LoginService.getCurrentUser())
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
      attend: false
    })
    const filtros = reactive({
      area: '',
      nombre: '',
      id_numero: '',
      fecha: null,
    })
    const columnsAdmin = [
      { title: 'Fecha', key: 'fecha' },
      { title: 'Area', key: 'area' },
      { title: 'Nombre', key: 'nombre' },
      { title: 'Estado', key: 'estado' },
      {
        title: 'Acción',
        key: 'accion',
        render(row: any) {
          const NButton = resolveComponent('n-button')
          return h(
            NButton,
            {
              type: 'secondary',
              size: 'small',
              onClick: () => handleConsultar(row)
            },
            { default: () => 'Consultar' }
          )
        }
      }
    ]
    const columnsAlumno = [
      { title: 'Número', key: 'index' },
      { title: 'Fecha', key: 'fecha' },
      { title: 'Horario', key: 'horario' },
      { title: 'Motivo', key: 'motivo' },
      { title: 'Area', key: 'area' },
      {
        title: 'Estado',
        key: 'estado',
        render(row: any) {
          if (row.estado === 'Solicitado') {
            return h(
              NButton,
              {
                size: 'small',
                class: 'btn-disponible',
                onClick: () => {
                  selectedSlot.value = row
                  showModal.value = true
                },
              },
              { default: () => 'Solicitado' },
            )
          } else {
            return h(
              NButton,
              {
                size: 'small',
                class: 'btn-no-disponible',
                disabled: true,
              },
              { default: () => 'Aprobado' },
            )
          }
        },
      },
    ]

    onMounted(async () => {
      chooseCitas()
    })

    async function handleConsultar(row: any) {
      const data = await loadCita(row)
      citaSeleccionada.value = data
      modalVisible.value = true
    }

    const submitCita = () => {
      console.log('Formulario enviado:', form.value, selectedSlot.value)
      showModal.value = false
    }

    async function loadCitasSolicitadasPorUsuario() {
      try {
        const items = await CitasService.obtenerCitasSolicitadasPorUsuario(user.value.id)
        dataAlumno.value = items.map((a, i) => ({
          index: i + 1,
          area: a.area,
          descripcion: a.descripcion,
          estado: a.estado ?? '',
          fecha: dateFormatV2(a.fecha),
          horario: a.horario,
          id: a.id,
          motivo: a.motivo,
        }))
      } catch (error) {
        console.log(error)
      }
    }

    async function loadCita(row: any) {
      const items = await CitasService.obtenerCitaPorId(row.id)
      return items
    }

    function getFilters() {
      const params: Record<string, any> = {}
      if (filtros.area) params.area = filtros.area
      if (filtros.nombre) params.nombre = filtros.nombre
      if (filtros.id_numero) params.id_numero = Number(filtros.id_numero)
      if (filtros.fecha) {
        const fechaObj = new Date(filtros.fecha)
        params.fecha = fechaObj.toISOString().split('T')[0]
      }
      return params
    }

    function clearFilters() {
      filtros.area = ''
      filtros.nombre = ''
      filtros.id_numero = ''
      filtros.fecha = null
      handleBuscar()
    }

    async function loadCitasPendientes() {
      try {
        const items = await CitasService.obtenerCitasPendientes(getFilters())
        dataPendiente.value = items.map((a, i) => ({
          index: i + 1,
          area: a.area,
          estado: a.estado,
          fecha: dateFormatV2(a.fecha),
          horario: a.horario,
          id: a.id,
          id_alumno: a.id_alumno,
          motivo: a.motivo,
          nombre: a.nombre,
        }))
      } catch (error) {
        console.log(error)
      }
    }

    async function loadCitasCulminadas() {
      try {
        const items = await CitasService.obtenerCitasCulminadas(getFilters())
        dataCulminada.value = items.map((a, i) => ({
          index: i + 1,
          area: a.area,
          estado: a.estado,
          fecha: dateFormatV2(a.fecha),
          horario: a.horario,
          id: a.id,
          id_alumno: a.id_alumno,
          motivo: a.motivo,
          nombre: a.nombre,
        }))
      } catch (error) {
        console.log(error)
      }
    }

    function chooseCitas() {
      if (isAdmin) {
        loadCitasPendientes()
        loadCitasCulminadas()
      } else {
        loadCitasSolicitadasPorUsuario()
      }
    }

    function handleBuscar() {
      if (tabActivo.value === 'pendientes') {
        loadCitasPendientes()
      } else {
        loadCitasCulminadas()
      }
    }

    function openModalNewSession() {
      selectedItem.value = {
        numero: '',
        asunto: '',
        motivo: '',
        fecha: '',
        estado: '',
        descripcion: '',
        attend : false
      }
      showModalNewSession.value = true
    }

    return {
      filtros,
      dataAlumno,
      columnsAlumno,
      dataPendiente,
      dataCulminada,
      columnsAdmin,
      showModal,
      selectedSlot,
      form,
      submitCita,
      clearFilters,
      loadCitasPendientes,
      loadCitasCulminadas,
      handleBuscar,
      dateFormatV2,
      pagination: ref({ pageSize: 7 }),
      dataTableInst: ref(null),
      isAdmin,
      tabActivo,
      modalVisible,
      citaSeleccionada,
      selectedItem,
      showModalNewSession,
      user,
      openModalNewSession,
    }
  },
})
</script>

<style scoped>
.citas-container {
  background-color: #BBBDA7;
  width: 95%;
  padding: 20px;
  border-radius: 15px;
  margin: 0 auto;
}
.citas-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.mes {
  font-size: 24px;
  font-weight: bold;
}
.horario {
  text-align: right;
}

/* Botones */
.btn-disponible {
  background-color: #f0c929;
  color: black;
}
.btn-no-disponible {
  background-color: #bdbdbd;
  color: white;
}

/* Modal */
.modal-cita .n-dialog {
  border-radius: 12px;
  padding: 24px;
  background-color: #fff8f8;
}
.form-cita {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form-cita label {
  font-weight: bold;
  margin-bottom: 4px;
  display: block;
}
.slot-box {
  background-color: #e0e0e0;
  padding: 10px;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  font-weight: bold;
}
::v-deep(.n-data-table-table) {
  border-radius: 20px !important;
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: white;
}
::v-deep(.n-data-table) {
  border-radius: 20px !important;
  background-color: transparent !important;
  border: none !important;
  box-shadow: none !important;
  color: white;
}

::v-deep(.n-data-table-th) {
  background-color: #D9D9D9;
  color: black;
  font-weight: bold !important;
}

::v-deep(.n-data-table-td) {
  background-color: transparent !important;
  padding: 8px;
}

::v-deep(.n-data-table-th__title){
  color: #163053 !important;
}
</style>
