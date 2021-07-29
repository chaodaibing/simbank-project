<template>
  <div class="app-container">
    <h2>Simbank版本管理平台</h2>
    <el-alert title="注意，升级或者降级后不会自动更新数据库的配置信息，需要点击更新后方才更新数据库的配置信息,注意升级完成会有卡条继续重启中,不要立刻更新"
      type="info" effect="dark" :closable="true">
    </el-alert>
    <el-tabs type="border-card">
      <el-tab-pane label="主板管理">
        <el-row type="flex" class="row-bg" justify="space-between">
          <el-col :span="12">
            <el-input v-model="listQuery.id" placeholder="请输入id搜索" style="width:200px;" @keyup.enter.native="handleFilter" />
            <el-button type="primary" icon="el-icon-search" @click="handleFilter">search</el-button>
          </el-col>
          <el-col :span="12">
            <el-button type="info" :loading="check_loading" icon="el-icon-check" @click="checkall">全量更新</el-button>
            <el-button type="warning" :loading="export_loading" icon="el-icon-downloadload" @click="exports()">数据导出</el-button>
          </el-col>
        </el-row>     
        <el-table :loading="board_loading" :data="board_data" stripe style="width: 100%">
          <el-table-column prop="id" label="主板序号" width="100"></el-table-column>
          <el-table-column prop="board_version" label="主板版本号" width="360">
          </el-table-column>
          <el-table-column prop="ip_address" label="主板IP" width="150"></el-table-column>
          <el-table-column prop="sn" label="主板标识SN" width="300"></el-table-column>
          <el-table-column prop="updated_date" label="更新时刻" width="200"></el-table-column>
          <el-table-column width="300">
            <template slot="header" slot-scope="scope">
              操作
            </template>
            <template slot-scope="scope">
              <el-button :loading="scope.row['check_loading']"  @click="checkone(scope.$index)">更新</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination :total="board_total" :current-page="listQuery.page" :page-sizes="[10, 20, 30, 50]" :page-size="listQuery.limit"
          layout="total, sizes, prev, pager, next, jumper" background @size-change="BoardSizeChange" @current-change="BoardCurrentChange" />
        </el-pagination>
      </el-tab-pane>

      <el-tab-pane label="卡条管理">
        <el-row type="flex" class="row-bg" justify="space-between">
          <el-col :span="12">
            <el-input v-model="listQuery.id" placeholder="请输入主板id搜索" style="width:200px;" @keyup.enter.native="handleFilter" />
            <el-button type="primary" icon="el-icon-search" @click="handleFilter">search</el-button>
          </el-col>
        </el-row>     
        <el-table :loading="blade_loading" :data="blade_data" stripe style="width: 100%">
          <el-table-column prop="stick_id" label="卡条位置ID" width="100"></el-table-column>
          <el-table-column prop="board_id" label="主板ID" width="150"></el-table-column>
          <el-table-column prop="stick_version" label="卡条版本号" width="360">
            <template slot-scope="scope">
              {{scope.row['stick_version']}}
            </template>
          </el-table-column>
          <el-table-column prop="state" label="卡条使用状态" width="200"></el-table-column>
          <el-table-column label="主板SN" width="200">
            <template slot-scope="scope">
              <el-popover placement="right" title="主板信息:" trigger="hover">
                <table class="blueTable">
                  <tr v-for="(key,item) of boardinfo">
                    <td>{{item}}</td>
                    <td>{{key}}</td>
                  </tr>
                </table>
                <a slot="reference" @mouseenter="getboardinfo(scope.row['board_sn'])">{{ scope.row['board_sn']}}</a>
              </el-popover>
            </template>
          </el-table-column>
          <el-table-column prop="updated_date" label="更新时刻" width="200"></el-table-column>
          <el-table-column width="350">
            <template slot="header" slot-scope="scope">
              操作
            </template>
            <template slot-scope="scope">
              <el-button :loading="scope.row['check_loading']"  @click="checkblade(scope.$index)">更新</el-button>
              <el-button type="danger" :loading="scope.row['upgrade_loading']" icon="el-icon-upload2" @click="upgradeone(scope.$index,'upgrade')">升级</el-button>
              <el-button type="warning" :loading="scope.row['upgrade_loading']" icon="el-icon-download" @click="upgradeone(scope.$index,'degrade')">降级</el-button>
            </template>
          </el-table-column>
        </el-table>
        <el-pagination :total="blade_total" :current-page="listQuery.page" :page-sizes="[10, 20, 30, 50]" :page-size="listQuery.limit"
          layout="total, sizes, prev, pager, next, jumper" background @size-change="BladeSizeChange" @current-change="BladeCurrentChange" />
        </el-pagination>
      </el-tab-pane>

      <el-tab-pane label="批量升级IP">
        <el-input placeholder="请输入要升级的IP列表" v-model="iplist" :disabled="wait" clearable></el-input>
        <el-button type="danger" :loading="upgrade_loading" icon="el-icon-upload" @click="upgradeall('upgrade')">全量升级</el-button>
        <el-button type="warning" :loading="upgrade_loading" icon="el-icon-upload" @click="upgradeall('degrade')">全量降级</el-button>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import axios from 'axios'
import XLSX from 'xlsx'
import '@/styles/oprtools.css'
var FileSaver = require('file-saver')
export default {
  name: 'index',
  data () {
    return {
      stick_id: '',
      stick_version: '',
      board_id:'',
      board_version: '',
      board_sn:'',
      boardinfo:{},
      blade_total:0,
      board_total:0,
      listQuery: {
        page: 1,            //第几页
        limit: 10,          //每页的条目数
        id:''
      },
      checkQuery:{
        mode:'all',
        ip:''
      },
      board_data:[],
      blade_data:[],
      loading:false,
      check_loading:false,
      upgrade_loading:false,
      export_loading:false,
      iplist:'',
      wait:false,
    }
  },
  created() {
    this.getdata('blade')                //请求数据
    this.getdata('board')
  },
  methods:  {
    //获取表格数据
    getdata(type) {
      if(type=='board'){
        this.board_loading = true
        var url='/api/getboardlist'
      }
      if(type=='blade'){
        this.blade_loading = true
        var url='/api/getbladelist'
      }
      axios.post(this.GLOBAL.util.BASE_backend + url,this.listQuery).then((response) => {
        var res = response.data
        this.total = res.total
        if(type=='board'){
          this.board_data = res.result
          this.board_total = res.total
        }
        if(type=='blade'){
          this.blade_data = res.result
          this.blade_total = res.total
        }
        this.loading = false
        }, (error) => {
          this.board_loading = false
          this.blade_loading = false
          alert('请求失败')
      })
    },
    //全量巡检
    checkall() {
      this.check_loading = true
      this.checkQuery.mode='all'
      this.checkQuery.ip=''
      axios.post(this.GLOBAL.util.BASE_backend + '/api/checkall',this.checkQuery).then((response) => {
        var res = response.data
        this.check_loading = false
        alert(res.msg)
        }, (error) => {
          this.check_loading = false
          alert('请求失败')
        })
      this.getdata('board')
      this.getdata('blade')
    },
    //巡检单一IP
    checkone(idx){
      this.board_data[idx]['check_loading'] = true
      this.checkQuery.mode='one'
      this.checkQuery.ip=this.board_data[idx]['ip_address']
      axios.post(this.GLOBAL.util.BASE_backend + '/api/checkall',this.checkQuery).then((response) => {
        var res = response.data
        alert(res.msg)
        this.getdata('board')
        this.getdata('blade')
      }, (error) => {
        this.board_data[idx]['check_loading'] = false
        alert('请求失败')
      })
    },
    //巡检单一Blade
    checkblade(idx){
      this.blade_data[idx]['check_loading'] = true
      var board_id=this.blade_data[idx]['board_id']
      var stick_id=this.blade_data[idx]['stick_id']
      var datapost={"board_id":board_id,"stick_id":stick_id}
      axios.post(this.GLOBAL.util.BASE_backend + '/api/checkblade',datapost).then((response) => {
        var res = response.data
        alert(res.msg)
        this.blade_data[idx]['check_loading'] = false
        this.getdata('blade')
      }, (error) => {
        this.blade_data[idx]['check_loading'] = false
        alert('请求失败')
      })
    },
    //根据输入的IP列表全量升级或者降级
    upgradeall(method) {
      this.upgrade_loading = true
      var datapost={'iplist':this.iplist,'method':method}
      axios.post(this.GLOBAL.util.BASE_backend + '/api/upgradeall',datapost).then((response) => {
        var res = response.data
        alert(res.msg)
        this.upgrade_loading = false
        }, (error) => {
          this.upgrade_loading = false
          alert('请求失败')
      })
    },
    //单一卡条升级或者降级
    upgradeone(idx,method) {    
      this.blade_data[idx]['upgrade_loading'] = true
      var board_id=this.blade_data[idx]['board_id']
      var stick_id=this.blade_data[idx]['stick_id']
      var datapost={'board_id':board_id,'stick_id':stick_id,'method':method} 
      this.$message.warning("主板序号为"+board_id+" 卡条位置为"+stick_id+"的卡条开始升级")
      axios.post(this.GLOBAL.util.BASE_backend + '/api/upgradeone',datapost).then((response) => {
        var res = response.data
        alert(res.msg)
        this.blade_data[idx]['upgrade_loading'] = false
        this.getdata('blade')
      },(error) => {
        this.blade_data[idx]['upgrade_loading'] = false
        alert('请求失败')
      })
    },
    //导出必需
    s2ab(s) {
      const buf = new ArrayBuffer(s.length)
      const view = new Uint8Array(buf)
      for (let i = 0; i !== s.length; ++i) view[i] = s.charCodeAt(i) & 0xFF
      return buf
    },
    exports() {
      const defaultCellStyle = { font: { name: 'Verdana', sz: 11, color: 'FF00FF88' }, fill: { fgColor: { rgb: 'FFFFAA00' }}}
      const wopts = { bookType: 'xlsx', bookSST: false, type: 'binary', defaultCellStyle: defaultCellStyle, showGridLines: false }
      const wb = { SheetNames: ['主板信息','卡条信息'], Sheets: {}, Props: {}}    //各个sheet的名字   
      wb.Sheets['主板信息'] = XLSX.utils.json_to_sheet(this.board_data)
      wb.Sheets['卡条信息'] = XLSX.utils.json_to_sheet(this.blade_data)
      const tmpDown = new Blob([this.s2ab(XLSX.write(wb, wopts))], { type: 'application/octet-stream' })
      FileSaver.saveAs(tmpDown, '版本信息.xlsx')
      this.$message.success("导出成功！")  
    },
    BoardSizeChange(val) {           //获取每页的条目数
      this.listQuery.limit = val
      this.getdata('board')                    
    },
    BoardCurrentChange(val) {        //获取现在的第几页
      this.listQuery.page = val
      this.getdata('board')
    },
    BladeSizeChange(val) {           //获取每页的条目数
      this.listQuery.limit = val   
      this.getdata('blade')                 
    },
    BladeCurrentChange(val) {        //获取现在的第几页
      this.listQuery.page = val
      this.getdata('blade') 
    },
    //search触发
    handleFilter() {
      this.listQuery.page = 1
      this.getdata('blade')
      this.getdata('board')
    },
    //弹框显示board信息
    getboardinfo(board_sn) {
      axios.get(this.GLOBAL.util.BASE_backend + '/api/getboardinfo?board_sn=' + board_sn).then((response)=>{
        var res=response.data
        var temp={}
        res=res[0]
        temp['id']=res['id']
        temp['SN']=res['sn']
        temp['IP']=res['ip_address']
        temp['board_version']=res['board_version']
        this.boardinfo=temp
      },(error)=>{
        alert('请求board信息失败')
      })
    },
  }
}
</script>

<style scoped>
.app-container {
  padding: 20px;
}
</style>
