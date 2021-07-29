import Vue from 'vue'
import Router from 'vue-router'
import Simbanks from '@/views/simbank/index'

Vue.use(Router)

export const constantRouterMap = [
  {
    path: '/simbank',
    component: Simbanks,
    name: 'simbank',
  },
]

export default new Router({
  mode: 'history',
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRouterMap
})