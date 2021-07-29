// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App.vue'
import router from './router'

import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import locale from 'element-ui/lib/locale/lang/en' // lang i18n
Vue.use(ElementUI, { locale })

import BootstrapVue from 'bootstrap-vue'
Vue.use(BootstrapVue)

import axios from 'axios'
Vue.prototype.$axios= axios

import global_ from '../config/global.js'
Vue.prototype.GLOBAL = global_;

Vue.config.productionTip = false

new Vue({
  el: '#app',
  router,
  render: h => h(App)
})