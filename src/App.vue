<template>
  <div id="app">
    <!-- Layout para páginas que requieren autenticación -->
    <template v-if="showLayout">
      <n-layout class="base-layout" has-sider style="height: 100vh">
        <div class="mobile-header" v-if="isMobile">
          <button class="hamburger-btn" @click="toggleSidebar">
            <i class="fas fa-bars"></i>
          </button>
          <div class="mobile-user-header">
            <div class="mobile-avatar">
              {{ getUserInitials(user?.nombre) }}
            </div>
            <div class="mobile-user-info">
              <span class="mobile-user-name">{{ user?.nombre }}</span>
              <span class="mobile-user-role">{{ capitalize(user?.rol || 'Usuario') }}</span>
            </div>
          </div>
        </div>

        <div 
          v-if="isMobile && sidebarVisible" 
          class="sidebar-overlay"
          @click="closeSidebar"
        ></div>

        <!-- Sidebar izquierdo -->
        <n-layout-sider
          :width="isMobile ? '280px' : '346px'"
          :class="{ 'mobile-sidebar': isMobile, 'sidebar-visible': sidebarVisible }"
          :content-style="sidebarContentStyle"
        >
          <div v-if="isMobile" class="mobile-sidebar-header">
            <img :src="logo" alt="OGBU Logo" class="sidebar-main-logo" />
            <button @click="closeSidebar" class="mobile-close-btn">
              <i class="fas fa-times"></i>
            </button>
          </div>
          
          <div class="sidebar-content" :class="{ 'mobile-content': isMobile }">
            <UserCard 
              v-if="!isMobile"
              :style="{ marginBottom: '20px', flexShrink: 0 }"
              :user="user" 
            />
            <div style="flex: 1; display: flex; flex-direction: column; min-height: 0">
              <SidebarMenu :class="{ 'mobile-sidebar-menu': isMobile }" />
            </div>
            <ButtonAction
              :style="{ marginTop: '20px', flexShrink: 0 }"
              :class="{ 'mobile-logout-btn': isMobile }"
              label="Cerrar Sesión"
              @click="handleLogout"
            />
          </div>
        </n-layout-sider>

        <!-- Contenido principal con fondo -->
        <n-layout-content :style="contentStyle">
          <router-view />
        </n-layout-content>

        <!-- Sidebar derecho -->
        <!-- <n-layout-sider width="25%" content-style="padding: 20px;">
          <n-image width="100%" :src="logo" />
          <CelebrationCard />
          <n-layout-header style="padding: 10px; margin-top: 20px">
            <n-button @click="showModal = true">Abrir Modal</n-button>
            <n-modal v-model:show="showModal">
              <div style="padding: 1em">¡Bienvenido!</div>
            </n-modal>
          </n-layout-header>
        </n-layout-sider> -->
      </n-layout>

      <v-snackbar v-model="snackbar" :color="color" timeout="3000" location="bottom">
        <v-icon class="me-2" size="20">{{ iconByType }}</v-icon>
        {{ message }}
      </v-snackbar>
    </template>

    <!-- Layout para login y páginas públicas -->
    <template v-else>
      <router-view />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { snackbar, message, color } from '@/shared/composables/useNotifier';

import logo from '@/assets/OGBU-logo.png'
import SidebarMenu from '@/components/layout/SidebarMenu.vue'
import CelebrationCard from '@/components/layout/CelebrationCard.vue'
import UserCard from './components/layout/UserCard.vue'
import ButtonAction from './components/layout/ButtonAction.vue'
import LoginService from './services/LoginService'

const iconByType = computed(() => {
  switch (color.value) {
    case 'success':
      return 'mdi-check-circle';
    case 'error':
      return 'mdi-alert-circle';
    case 'warning':
      return 'mdi-alert';
    default:
      return 'mdi-information';
  }
});

const router = useRouter()
const route = useRoute()
const showModal = ref(false)
const user = ref<any>(null)

const isMobile = ref(false)
const sidebarVisible = ref(false)

const checkScreenSize = () => {
  isMobile.value = window.innerWidth <= 768
  if (!isMobile.value) {
    sidebarVisible.value = false
  }
}

const toggleSidebar = () => {
  sidebarVisible.value = !sidebarVisible.value
}

const closeSidebar = () => {
  sidebarVisible.value = false
}

const sidebarContentStyle = computed(() => ({
  padding: isMobile.value ? '0' : '32px',
  display: 'flex',
  flexDirection: 'column',
  height: '100vh',
  background: isMobile.value ? 'transparent' : undefined,
  overflow: 'hidden'
}))

const contentStyle = computed(() => ({
  flex: 1,
  ...(isMobile.value && {
    marginTop: '60px'
  })
}))

onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
})

// Computed para determinar si mostrar el layout con sidebars
const showLayout = computed(() => {
  const publicRoutes = ['login']
  if (publicRoutes.includes(route.name as string)) {
    return false
  }
  user.value = LoginService.getCurrentUser()
  return LoginService.isAuthenticated()
})

const getUserInitials = (name: string | undefined): string => {
  if (!name) return 'U'
  
  const words = name.trim().split(' ')
  if (words.length === 1) {
    return words[0].charAt(0).toUpperCase()
  }
  
  return (words[0].charAt(0) + words[1].charAt(0)).toUpperCase()
}

const capitalize = (text: string | undefined): string => {
  if (!text) return ''
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase()
}

// Función para cerrar sesión
const handleLogout = () => {
  LoginService.logout()
  router.push({ name: 'login' })
}
</script>

<style scoped>
.base-layout {
  min-height: 100vh;
  background: url('../src/assets/background.png');
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

.mobile-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background-color: #A80038;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.hamburger-btn {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.hamburger-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.mobile-user-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mobile-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.mobile-user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mobile-user-name {
  color: white;
  font-size: 14px;
  font-weight: 600;
  line-height: 1;
}

.mobile-user-role {
  color: rgba(255, 255, 255, 0.8);
  font-size: 12px;
  line-height: 1;
}

.mobile-sidebar {
  position: fixed !important;
  top: 0;
  left: -280px;
  height: 100vh !important;
  z-index: 1100;
  transition: left 0.3s ease;
  background: linear-gradient(180deg, #A80038 0%, #7e271b 100%) !important;
  box-shadow: 2px 0 15px rgba(0, 0, 0, 0.3);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.mobile-sidebar.sidebar-visible {
  left: 0;
}

.mobile-sidebar .n-layout-sider__content {
  background: transparent !important;
}

.mobile-sidebar-header {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 20px 60px 20px 20px;
  min-height: 120px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(0, 0, 0, 0.1);
}

.sidebar-main-logo {
  height: 80px;
  width: auto;
  max-width: 180px;
  background: white;
  padding: 12px 16px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  transition: all 0.2s ease;
  object-fit: contain;
  margin: 0 auto;
}

.sidebar-main-logo:hover {
  transform: scale(1.02);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
}

.mobile-close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.mobile-close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}

.sidebar-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-content.mobile-content {
  padding: 20px;
  padding-top: 20px;
  height: calc(100% - 80px);
  overflow-y: auto;
  overflow-x: hidden;
}

.sidebar-content.mobile-content::-webkit-scrollbar {
  width: 4px;
}

.sidebar-content.mobile-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
}

.sidebar-content.mobile-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
}

.sidebar-content.mobile-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}

.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1050;
}

.mobile-sidebar-menu :deep(.card-sidemenu) {
  background: transparent !important;
  border-radius: 0;
  border: none;
  box-shadow: none;
  padding: 0;
}

.mobile-sidebar-menu :deep(.menu-item) {
  color: white !important;
  background: transparent;
  border-radius: 8px;
  margin-bottom: 8px;
  padding: 16px 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s ease;
}

.mobile-sidebar-menu :deep(.menu-item:hover) {
  background: rgba(255, 255, 255, 0.1) !important;
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateX(4px);
}

.mobile-sidebar-menu :deep(.menu-item.active) {
  background: rgba(255, 255, 255, 0.15) !important;
  border-color: rgba(255, 255, 255, 0.3);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.mobile-sidebar-menu :deep(.menu-label) {
  color: white !important;
  font-weight: 500;
}

.mobile-sidebar-menu :deep(.icon-container) {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.mobile-sidebar-menu :deep(.action-buttons) {
  display: none;
}

.mobile-logout-btn :deep(.n-button) {
  background: rgba(255, 255, 255, 0.1) !important;
  color: white !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  transition: all 0.2s ease;
  width: 100%;
  padding: 12px 16px;
  font-weight: 500;
}

.mobile-logout-btn :deep(.n-button:hover) {
  background: rgba(255, 255, 255, 0.2) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.mobile-logout-btn :deep(.n-button__content) {
  color: white !important;
}

@media (max-width: 768px) {
  .base-layout {
    overflow-x: hidden;
  }
  
  .n-layout-sider:not(.mobile-sidebar) {
    display: none;
  }
}

@media (min-width: 769px) {
  .mobile-header {
    display: none;
  }
  
  .mobile-sidebar {
    position: relative !important;
    left: 0 !important;
    box-shadow: none;
  }
  
  .sidebar-overlay {
    display: none;
  }
  
  .mobile-close-btn {
    display: none;
  }
}
</style>
