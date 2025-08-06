import { reactive } from 'vue'

interface ModalState {
  mostrarModalPublicacion: boolean
  mostrarModalReconocimiento: boolean
}

export const modalStore = reactive<ModalState>({
  mostrarModalPublicacion: false,
  mostrarModalReconocimiento: false
})

export const modalActions = {
  showModalPublicacion() {
    modalStore.mostrarModalPublicacion = true
  },
  
  hideModalPublicacion() {
    modalStore.mostrarModalPublicacion = false
  },
  
  showModalReconocimiento() {
    modalStore.mostrarModalReconocimiento = true
  },
  
  hideModalReconocimiento() {
    modalStore.mostrarModalReconocimiento = false
  }
}
