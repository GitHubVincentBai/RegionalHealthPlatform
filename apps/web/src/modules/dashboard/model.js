export function dashboardModel() {
  return {
    stats: [
      {
        label: "站点接入",
        value: "32",
        helper: "1 个中心 + 31 个社区站点",
      },
      {
        label: "今日呼叫",
        value: "18",
        helper: "平均响应 4 分 18 秒",
      },
      {
        label: "在线设备",
        value: "126",
        helper: "在线率 98.4%",
      },
      {
        label: "异常处置",
        value: "96%",
        helper: "本周闭环完成率",
      },
    ],
    tasks: [
      {
        title: "核对龙湖邻里中心巡检结果",
        owner: "运营值班组",
        deadline: "今天 17:00 前",
        priority: "P1",
      },
      {
        title: "处理老人档案缺失字段",
        owner: "前台登记员",
        deadline: "今天 18:30 前",
        priority: "P2",
      },
      {
        title: "复核夜间设备离线告警",
        owner: "设备运维",
        deadline: "今日持续跟进",
        priority: "P1",
      },
    ],
    alerts: [
      {
        name: "健康告警处置中",
        site: "龙湖邻里中心",
        status: "处理中",
        ratio: 0.72,
      },
      {
        name: "门禁事件升级",
        site: "三好街站点",
        status: "待确认",
        ratio: 0.41,
      },
      {
        name: "设备离线恢复",
        site: "社区 12 号站点",
        status: "已恢复",
        ratio: 0.89,
      },
    ],
    services: [
      {
        name: "老人档案",
        stage: "核心",
        summary: "承接老人、家属、床位、风险等级等基础主数据。",
        touchpoints: 7,
      },
      {
        name: "健康管理",
        stage: "核心",
        summary: "汇聚监测数据、趋势分析、预警与人工干预记录。",
        touchpoints: 9,
      },
      {
        name: "呼叫中心",
        stage: "高频",
        summary: "覆盖受理、分派、到场、完成和超时升级闭环。",
        touchpoints: 8,
      },
      {
        name: "家属协同",
        stage: "增长",
        summary: "面向家属查询、消息触达和服务反馈的多端入口。",
        touchpoints: 6,
      },
    ],
    releases: [
      {
        name: "设计对齐",
        detail: "先固化页面信息架构、接口契约和权限边界。",
      },
      {
        name: "组件拆分",
        detail: "再按区块拆出可复用模块，方便未来切换 Vue。",
      },
      {
        name: "联调验证",
        detail: "最后接真实 API、补测试并进入 CI / PR 流程。",
      },
    ],
  };
}
