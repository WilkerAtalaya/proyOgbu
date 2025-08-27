<template>
  <div class="sidebar-menu-wrapper">
    <div class="card-sidemenu">
      <div class="menu-items-container">
        <div 
          v-for="option in menuOptions" 
          :key="option.key"
          class="menu-item" 
          :class="{ active: route.path === option.key }"
          @click="navigate(option.key)"
        >
          <div 
            class="icon-container circular-icon"
          >
            <img :src="option.iconSrc" :alt="option.label" class="menu-icon-img" />
          </div>
          <span class="menu-label">{{ option.label }}</span>
        </div>
      </div>
    </div>
    
    <div v-if="route.path === '/anuncios' && isAdmin" class="action-buttons">
      <button 
        class="action-button"
        @click="modalActions.showModalPublicacion()"
      >
        Realizar una publicación
      </button>
      <button 
        class="action-button"
        @click="modalActions.showModalReconocimiento()"
      >
        Realizar un Reconocimiento
      </button>
    </div>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import LoginService from '@/services/LoginService'
import { modalActions } from '@/stores/modalStore'
import anuncioIcon from '@/assets/icons/anuncio.png'
import quejaIcon from '@/assets/icons/queja.png'
import actividadIcon from '@/assets/icons/actividad.png'
import permisoIcon from '@/assets/icons/permiso.png'
import citaIcon from '@/assets/icons/cita.png'
import asistenciaIcon from '@/assets/icons/asistencia.png'

const router = useRouter()
const route = useRoute()
const isAdmin = LoginService.isAdmin()

const menuOptions = [
  {
    label: 'Anuncios',
    key: '/anuncios',
    iconSrc: anuncioIcon,
  },
  {
    label: 'Quejas',
    key: '/quejas',
    iconSrc: quejaIcon,
  },
  {
    label: 'Actividades',
    key: '/actividades',
    iconSrc: actividadIcon,
  },
  {
    label: 'Permisos',
    key: '/permisos',
    iconSrc: permisoIcon,
  },
  {
    label: 'Citas',
    key: '/citas',
    iconSrc: citaIcon,
  },
  {
    label: 'Asistencia',
    key: '/asistencia',
    iconSrc: asistenciaIcon,
  },
]

function navigate(key) {
  router.push(key)
}
</script>

<style scoped>
.sidebar-menu-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.card-sidemenu {
  background: #7E271BF2;
  width: 100%;
  padding: 32px 24px;
  border-radius: 25px;
  border: none;
  display: flex;
  flex-direction: column;
  box-shadow: 0px 10px 4px 0px #00000040;
  min-height: 0;
  overflow: hidden;
}

.menu-items-container {
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  overflow-x: hidden;
  flex: 1;
  min-height: 0;
  padding-right: 4px;
}

.menu-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 25px;
  padding: 8px 12px;
  flex-shrink: 0;
  min-height: 53px;
}

.menu-item:not(:last-child) {
  margin-bottom: 8px;
}

.menu-item:hover {
  background-color: #dcc1c136;
}

.menu-item.active {
  background-color: #DCC1C1;
}

.circular-icon {
  background-color: white;
  border-radius: 50%;
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;
}

.menu-icon-img {
  width: 30px;
  height: 30px;
  object-fit: contain;
}

.menu-label {
  color: white;
  font-size: 16px;
  font-weight: 500;
  flex: 1;
}

.menu-item.active .menu-label {
  color: #163053;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
  margin-top: 16px;
  flex-shrink: 0;
}

.action-button {
  background-color: #EAE6C9;
  color: black;
  border-radius: 25px;
  padding: 16px 12px;
  border: none;
  font-weight: 400;
  font-size: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0px 10px 4px 0px #00000040;
}

.action-button:hover {
  background-color: #c7c4ac;
  transform: translateY(-2px);
  box-shadow: 0px 12px 8px 0px #00000040;
}

.action-button:active {
  transform: translateY(0);
  box-shadow: 0px 2px 4px rgba(0, 0, 0, 0.2);
}

/* Estilo personalizado para la barra de scroll de los menu items */
.menu-items-container::-webkit-scrollbar {
  width: 6px;
}

.menu-items-container::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.menu-items-container::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 3px;
}

.menu-items-container::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}
</style>