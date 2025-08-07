<template>
  <div class="main-container">
    <div class="first-row">
      <n-image width="282px" :src="logo" />
    </div>
    
    <div class="second-row">
      <div style="background-color: #B8BAA3F2; width: 100%; height: 100%; padding: 32px 60px; border-radius: 25px;">
        <slot />
      </div>
    </div>
  </div>
</template>
<script setup>
import logo from '@/assets/OGBU-logo.png'
</script>
<style scoped>
.main-container {
  display: flex;
  flex-direction: column;
  gap: 32px;
  height: 100vh;
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
