<template>
  <div id="app">
    <!-- Layout para páginas que requieren autenticación -->
    <template v-if="showLayout">
      <n-layout has-sider style="height: 100vh">
        <!-- Sidebar izquierdo -->
        <n-layout-sider bordered width="15%" content-style="padding: 10px 20px;">
          <UserCard style="margin-bottom: 20px" :user="user" />
          <SidebarMenu />
          <ButtonAction style="margin-top: 20px" label="Cerrar Sesión" @click="handleLogout" />
        </n-layout-sider>

        <!-- Contenido principal con fondo -->
        <n-layout-content class="base-layout" style="padding: 20px; flex: 1">
          <router-view />
        </n-layout-content>

        <!-- Sidebar derecho -->
        <n-layout-sider width="25%" content-style="padding: 20px;">
          <n-image width="100%" :src="logo" />
          <CelebrationCard />
          <n-layout-header style="padding: 10px; margin-top: 20px">
            <n-button @click="showModal = true">Abrir Modal</n-button>
            <n-modal v-model:show="showModal">
              <div style="padding: 1em">¡Hola desde Naive UI!</div>
            </n-modal>
          </n-layout-header>
        </n-layout-sider>
      </n-layout>
    </template>

    <!-- Layout para login y páginas públicas -->
    <template v-else>
      <router-view />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

import logo from '@/assets/OGBU-logo.png'
import SidebarMenu from '@/components/layout/SidebarMenu.vue'
import CelebrationCard from '@/components/layout/CelebrationCard.vue'
import UserCard from './components/layout/UserCard.vue'
import ButtonAction from './components/layout/ButtonAction.vue'
import LoginService from './services/LoginService'

const router = useRouter()
const route = useRoute()
const showModal = ref(false)
const user = ref(null)

// Computed para determinar si mostrar el layout con sidebars
const showLayout = computed(() => {
  const publicRoutes = ['login']
  if (publicRoutes.includes(route.name as string)) {
    return false
  }
  user.value = LoginService.getCurrentUser()
  return LoginService.isAuthenticated()
})

// Función para cerrar sesión
const handleLogout = () => {
  LoginService.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.base-layout {
  min-height: 100vh;
  background: url('../src/assets/background.jpg');
  background-size: cover;
  background-position: center;
  position: relative;
}

.base-layout::before {
  content: '';
  position: absolute;
  inset: 0;
  background-color: rgba(255, 255, 255, 0.8);
  z-index: 1;
}

.base-layout > * {
  position: relative;
  z-index: 2;
}
</style>
