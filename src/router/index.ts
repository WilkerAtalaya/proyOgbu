import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import Login from '../views/Login.vue'
import LoginService from '@/services/LoginService'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: Login,
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/anuncios',
      name: 'anuncios',
      component: () => import('../views/PostsView.vue'),
    },
    {
      path: '/actividades',
      name: 'actividades',
      component: () => import('../views/ActivitiesView.vue'),
    },
    {
      path: '/permisos',
      name: 'permisos',
      component: () => import('../views/PermissionsView.vue'),
    },
    {
      path: '/quejas',
      name: 'quejas',
      component: () => import('../views/ReportsView.vue'),
    },
    {
      path: '/asistencia',
      name: 'asistencia',
      component: () => import('../views/AssistsView.vue'),
    },
    {
      path: '/citas',
      name: 'citas',
      component: () => import('../views/SessionsView.vue'),
    },
  ],
})
// Guard de navegación para proteger rutas
router.beforeEach((to, from, next) => {
  const isAuthenticated = LoginService.isAuthenticated()

  if (to.meta.requiresAuth && !isAuthenticated) {
    // Si la ruta requiere autenticación y no está autenticado, redirige al login
    next({ name: 'login' })
  } else if (to.name === 'login' && isAuthenticated) {
    // Si ya está autenticado y trata de ir al login, redirige a la página principal
    next({ name: 'anuncios' })
  } else {
    next()
  }
})

export default router
