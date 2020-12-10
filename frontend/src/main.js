// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
/* eslint-disable */
import Vue from 'vue'
import Vuex from 'vuex'

// 3rd party
import VueFuse from 'vue-fuse'
import debugLib from 'debug'
import vuetify from '@/plugins/vuetify' // path to vuetify export


// our own libraries
import { fetchCurrentUser } from './utils'
import validationLocalizedStrings from './formValidation'
import router from './routes'
import store from './store'
import i18n from './i18n'
import App from './App'

const debug = debugLib('cl8.main.js')

Vue.config.productionTip = false
Vue.config.devtools = true

Vue.use(Vuex)
Vue.use(VueFuse)


const VueStore = new Vuex.Store(store)

const app = new Vue({
  vuetify,
  i18n,
  router,
  store: VueStore,
  render: h => h(App)
}).$mount('#app')

app.$validator.localize('en', validationLocalizedStrings)

router.beforeEach(async (to, from, next) => {

  debug({to: to.name}, {from: to.from})

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const currentUser = await fetchCurrentUser(VueStore)

  if (currentUser && to.name === 'signin') {
    next('home')
  }

  if (requiresAuth && !currentUser) {
    // you need to be logged in, so log the user in
    if (to.name === 'signin') {
      next()
    }
    else {
      next('signin')
    }

  } else {
    next()
  }
})
