export const environment = {
  baseUrlApi: 'http://localhost:5000',
  endPoint: {
    login: {
      crear: '/login',
    },
    anuncios: {
      listar: '/anuncios',
      crear: '/anuncios',
    },
    actividades: {
      obtenerPorUsuario: '/actividades/usuario',
      obtenerTodas: '/actividades/admin',
      obtenerPorId: '/actividades',
      obtenerAprobadas: '/actividades/aprobadas',
      crearActividad: '/actividades/admin',
      crearSolicitud: '/actividades',
      actualizar: '/actividades',
      eliminar: '/actividades',
    },
    quejas: {
      obtenerPorUsuario: '/quejas/usuario',
      listar: '/quejas',
      crear: '/quejas'
    },
    reconocimientos: {
      obtenerReconocimientos: '/reconocimientos',
      crearReconocimiento: '/reconocimientos',
      obtenerCumpleanos: '/cumpleaños',
      buscarAlumnos: '/alumnos/buscar',
      eliminarReconocimiento: '/reconocimientos'
    },
    permisos: {
      crearSalida: '/api/permisos/salida',
      obtenerSalidaPorUsuario: '/api/permisos/salida/usuario',
      todasLasSalidas: '/api/permisos/salida/admin',
      crearAreaComun: '/api/permisos/area-comun',
      obtenerAreaComunPorUsuario: '/api/permisos/area-comun/usuario',
      todasLasAreaComun: '/api/permisos/area-comun/admin',
    },
    citas: {
      obtenerSolicitadasPorUsuario: '/citas/alumno',
      obtenerPendientes: '/citas/pendientes',
      obtenerCulminadas: '/citas/culminadas',
      consultar: '/citas',
      crear: '/citas',
    },
    asistencia: {
      obtenerFechasMarcadasPorUsuario: '/asistencia/fechas',
      obtenerDetallePorFechaYUsuario: '/asistencia/detalle'
    }

  },
}
