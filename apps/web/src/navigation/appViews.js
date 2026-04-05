export const APP_VIEWS = {
  dashboard: {
    key: "dashboard",
    label: "总览",
    hint: "控制台",
    title: "区域康养平台 Web 管理端",
    description: "面向运营和管理角色的控制台总览，承接首页态势、待办和交付节奏。",
  },
  "elder-list": {
    key: "elder-list",
    label: "长者档案",
    hint: "列表与详情",
    title: "长者档案工作台",
    description: "围绕长者档案、家属关系、入住信息和床位关联的首批业务入口。",
  },
  "elder-intake": {
    key: "elder-intake",
    label: "入住办理",
    hint: "创建草稿",
    title: "长者入住办理",
    description: "先落地创建档案与入住草稿，为后续 FastAPI 联调预留稳定表单结构。",
  },
  "elder-detail": {
    key: "elder-detail",
    label: "长者详情",
    hint: "档案查看",
    title: "长者档案详情",
    description: "查看长者档案、床位、家属关系和基础入住信息。",
  },
};

export const APP_NAV_ITEMS = [
  APP_VIEWS.dashboard,
  APP_VIEWS["elder-list"],
  APP_VIEWS["elder-intake"],
];

export function getViewConfig(viewKey, fallbackKey = "dashboard") {
  return APP_VIEWS[viewKey] ?? APP_VIEWS[fallbackKey];
}
