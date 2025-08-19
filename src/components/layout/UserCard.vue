<template>
  <n-card class="user-card">
    <div class="user-content">
      <div class="avatar-container">
        <div class="avatar">
          {{ getUserInitials(props.user?.nombre) }}
        </div>
        <i class="fa-solid fa-circle status-icon"></i>
      </div>
      <div class="user-info">
        <p class="user-name">{{ props.user?.nombre }}</p>
        <p class="user-role">{{ capitalize(props.user?.rol || 'Usuario') }}</p>
      </div>
    </div>
  </n-card>
</template>
<script setup>
const props = defineProps({
  user: Object
})

const getUserInitials = (name) => {
  if (!name) return 'U'
  
  const words = name.trim().split(' ')
  if (words.length === 1) {
    return words[0].charAt(0).toUpperCase()
  }
  
  return (words[0].charAt(0) + words[1].charAt(0)).toUpperCase()
}

const capitalize = (text) => {
  if (!text) return ''
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase()
}
</script>
<style scoped>
.user-card {
  background-color: #373b41;
  padding: 16px 20px;
  border-radius: 25px;
  box-shadow: 0px 10px 4px 0px #00000040;
  border: none;
}

.user-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-container {
  position: relative;
  display: flex;
  align-items: center;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background-color: #4a90e2;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 18px;
  margin-right: 8px;
}

.status-icon {
  color: #4caf50;
  font-size: 12px;
  position: absolute;
  bottom: 2px;
  right: 4px;
  background-color: #373b41;
  border-radius: 50%;
  padding: 2px;
}

.user-info {
  flex: 1;
}

.user-name {
  margin: 0 0 4px 0;
  color: white;
  font-size: 18px;
  font-weight: 500;
  line-height: 1.2;
}

.user-role {
  margin: 0;
  color: #a0a0a0;
  font-size: 14px;
  font-weight: 400;
  line-height: 1.2;
}
</style>
