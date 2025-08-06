<template>
  <n-card class="card-sidemenu">
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
        <i :class="option.iconClass"></i>
      </div>
      <span class="menu-label">{{ option.label }}</span>
    </div>
  </n-card>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const menuOptions = [
  {
    label: 'Anuncios',
    key: '/anuncios',
    iconClass: 'fa-solid fa-bullhorn icon',
  },
  {
    label: 'Quejas',
    key: '/quejas',
    iconClass: 'fa-regular fa-clipboard icon',
  },
  {
    label: 'Actividades',
    key: '/actividades',
    iconClass: 'fa-solid fa-person-running icon',
  },
  {
    label: 'Permisos',
    key: '/permisos',
    iconClass: 'fa-solid fa-person-circle-check icon',
  },
  {
    label: 'Citas',
    key: '/citas',
    iconClass: 'fa-regular fa-calendar-days icon',
  },
  {
    label: 'Asistencia',
    key: '/asistencia',
    iconClass: 'fa-regular fa-calendar-check icon',
  },
]

function navigate(key) {
  router.push(key)
}
</script>

<style scoped>
.card-sidemenu {
  background: #7E271BF2;
  width: 100%;
  padding: 32px 24px;
  border-radius: 25px;
  border: none;
  display: flex;
  flex-direction: column;
  box-shadow: 0px 10px 4px 0px #00000040;
}

.menu-item {
  display: flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 25px;
  padding: 8px 12px;
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

.icon {
  color: #aac4c8;
  font-size: 18px;
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
</style>