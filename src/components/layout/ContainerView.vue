<template>
  <div class="main-container">
    <div class="first-row">
      <n-image width="282px" :src="logo" />
    </div>
    
    <div class="second-row">
      <div :style="{ backgroundColor: backgroundColor, width: '100%', height: '100%', padding: padding, borderRadius: '25px' }">
        <slot />
      </div>
    </div>
  </div>
</template>
<script setup>
import logo from '@/assets/OGBU-logo.png'

const props = defineProps({
  backgroundColor: {
    type: String,
    default: '#B8BAA3F2'
  },
  padding: {
    type: String,
    default: '32px 60px'
  }
})
</script>
<style scoped>
.main-container {
  display: flex;
  flex-direction: column;
  gap: 32px;
  min-height: 100vh;
  padding: 32px;
}
.first-row {
  width: 100%;
  display: flex;
  justify-content: end;
  align-items: center;
}
.second-row {
  flex: 1;
}
</style>
