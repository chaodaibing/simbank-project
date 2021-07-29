import Vue from 'vue';
import axios from 'axios';
import Cookies from 'js-cookie';
import { Message, MessageBox } from 'element-ui'


axios.defaults.headers.post['Content-Type'] = 'application/json';

export const request = (config) => {
  return axios(config);
};

// http request 拦截器
axios.interceptors.request.use(
  (config) => {
    // console.log('-------------------------888888--------------')
    console.log(Cookies.get('ticket'))
    if (Cookies.get('ticket')) {
      //console.log('-----------------------222222222222222222--888888--------------')
      
      //console.log(config.headers.Authorization)
      // 跳过文件服务器的自定义tocken , i made this in a dirty way, if you have better solution ,pls contact yangbinyuan644
      if (config.headers.Authorization != 'Third-System-s1FK2J7las')
        {config.headers.Authorization = Cookies.get('ticket'); }
      //console.log(config.headers.Authorization)
      // console.log('-----------------------222222222222222222--888888--------------')
      // console.log('-----------------------222222222222222222--888888--------------')
    }
    return config;
  },
  (err) => {
    return Promise.reject(err);
  }
);

// http response 拦截器
axios.interceptors.response.use(
  
  (response) => {
    console.log('this is ------------------------response')
    return response;
  },
  (error) => {
    console.error('-------------------------9999--------------')
    console.error(error)
    
    if(error.response) {
      console.error(error.response)
      switch (error.response.status) {
        case 401:
        MessageBox.confirm(
          '会话已经超时，请重新登录',
          '确定登出',
          {
            confirmButtonText: '重新登录',
            cancelButtonText: '取消',
            type: 'warning'
          }
        ).then(function(){
          // console.log('-------------------------$$$$$$$$$$--------------')
          // console.log(Vue.prototype.GLOBAL)
          Cookies.remove('ticket')
          Cookies.remove('username')
          Cookies.remove('teamname')
          Cookies.remove('init')
          Cookies.set('logout','0')
          
          window.location = Vue.prototype.GLOBAL.util.URL4A + 'cas/logout?url=' + Vue.prototype.GLOBAL.util.BASE_logout_back
        })
          break
        case 403:
          Message.error('用户权限不足，禁止使用此功能')
          break
        default:
          Message.error('请求失败')
      }
    }
    return Promise.reject(error);
  }
);

