let address = window.location.hostname
let util = {}
var envrunning = window.location.href

util.BASE = location.protocol + '//' + address + ':80'
util.BASE_backend = location.protocol + '//' + address + ':9528'

export default {
  util
}
