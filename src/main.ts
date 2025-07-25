import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { aliases, fa } from 'vuetify/iconsets/fa'
import naive from 'naive-ui'
import '@fortawesome/fontawesome-free/css/all.css'
import '@fortawesome/fontawesome-free/js/all.js'
import App from './App.vue'
import router from './router'

import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'fa',
    aliases,
    sets: {
      fa,
    },
  },
})

const app = createApp(App)

app.use(createPinia())
app.use(naive)
app.use(router)
app.use(vuetify)
app.mount('#app')
