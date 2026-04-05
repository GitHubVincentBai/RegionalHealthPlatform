<script setup>
import { computed } from "vue";
import SectionCard from "../../components/SectionCard.vue";
import StatCard from "../../components/StatCard.vue";

const props = defineProps({
  summary: {
    type: Object,
    required: true,
  },
  elders: {
    type: Array,
    required: true,
  },
  filters: {
    type: Object,
    required: true,
  },
  pagination: {
    type: Object,
    required: true,
  },
  selectedElderId: {
    type: String,
    required: true,
  },
  selectedElder: {
    type: Object,
    default: null,
  },
  loading: {
    type: Boolean,
    default: false,
  },
  errorMessage: {
    type: String,
    default: "",
  },
  dataSource: {
    type: String,
    default: "api",
  },
  syncWarning: {
    type: String,
    default: "",
  },
});

const emit = defineEmits(["select-elder", "create-draft", "refresh", "apply-filters", "reset-filters", "update:filters"]);

const selectedElder = computed(
  () => props.selectedElder ?? props.elders.find((elder) => elder.elderId === props.selectedElderId) ?? props.elders[0],
);

const dataSourceLabel = computed(() => (props.dataSource === "mock" ? "Mock Fallback" : "elder-service"));

const taskPackages = computed(() => [
  {
    title: "任务 1",
    owner: "PythonAgent",
    summary: "长者档案 create/list/get API 与最小入住字段",
    status: dataSourceLabel.value === "Mock Fallback" ? "待联调" : "已接入",
  },
  {
    title: "任务 2",
    owner: "FrontAgent",
    summary: "列表页、详情页、创建表单与入住信息展示区块",
    status: "已落页面",
  },
  {
    title: "任务 3",
    owner: "TestAgent",
    summary: "建档、入住信息、家属字段与冒烟路径验证",
    status: "待继续补齐",
  },
  {
    title: "任务 4",
    owner: "ArchAgent",
    summary: "合同、费用、护理计划等二期扩展边界预留",
    status: "已预留",
  },
]);

const intakeChecklist = computed(() => [
  {
    label: "长者基础档案",
    value: selectedElder.value ? `${selectedElder.value.fullName} / ${selectedElder.value.elderCode}` : "待创建首条档案",
  },
  {
    label: "家属关系",
    value: selectedElder.value ? `${selectedElder.value.family} / ${selectedElder.value.familyRelation}` : "待补充主联系人",
  },
  {
    label: "入住信息",
    value: selectedElder.value ? `${selectedElder.value.status} / ${selectedElder.value.checkInDate}` : "待安排入住日期",
  },
  {
    label: "房间床位",
    value: selectedElder.value ? `${selectedElder.value.room} / ${selectedElder.value.bed}` : "待分配床位",
  },
]);

const businessScope = [
  "长者基础档案字段展示",
  "家属关系与主联系人展示",
  "入住状态、入住日期、房间与床位展示",
  "风险等级与列表/详情入口",
];

const futureScope = ["正式合同工作流", "缴费、账单和审批流", "护理计划编排", "医疗机构深度接口对接"];
</script>

<template>
  <section class="page-stack">
    <article class="detail-hero">
      <div>
        <p class="eyebrow">长者档案工作台</p>
        <h2>围绕档案、家属关系与入住办理的首批业务入口</h2>
        <p class="summary">
          当前页面按照任务包收敛到“创建档案、查询列表、查看详情、记录入住基础信息、关联房间床位和家属关系”的最小闭环。
        </p>
      </div>
      <div class="detail-hero__tags">
        <span class="pill pill-accent">{{ dataSourceLabel }}</span>
        <span class="pill">档案列表 + 详情入口</span>
        <span class="pill">入住基础信息</span>
        <span class="pill">床位与家属关系</span>
      </div>
    </article>

    <section class="metrics-grid metrics-grid-archive" aria-label="长者档案指标">
      <StatCard label="档案总数" :value="summary.total" helper="覆盖档案、入住与家属关系" />
      <StatCard label="已入住" :value="summary.checkedIn" helper="当前可服务长者" />
      <StatCard label="待入住" :value="summary.waitingCheckIn" helper="待安排床位或资料完善" />
      <StatCard label="高风险" :value="summary.highRisk" helper="需重点关注" />
    </section>

    <section class="content-grid">
      <SectionCard title="首批任务包进度" description="按文档原始拆分同步当前页面承接情况。">
        <div class="task-package-grid">
          <article v-for="item in taskPackages" :key="item.title" class="task-package-card">
            <div class="task-package-card__head">
              <strong>{{ item.title }}</strong>
              <span class="badge">{{ item.status }}</span>
            </div>
            <p>{{ item.summary }}</p>
            <small>责任角色：{{ item.owner }}</small>
          </article>
        </div>
      </SectionCard>

      <SectionCard title="首批范围清单" description="和任务包保持一致，避免页面越界扩写。">
        <ul class="workbench-list">
          <li v-for="item in intakeChecklist" :key="item.label" class="workbench-list__item">
            <div>
              <strong>{{ item.label }}</strong>
              <p>{{ item.value }}</p>
            </div>
            <span class="badge">P0</span>
          </li>
        </ul>
      </SectionCard>
    </section>

    <section class="content-grid content-grid-wide">
      <SectionCard title="长者档案列表" description="用于筛选、查看和进入详情。">
        <div class="archive-toolbar">
          <div class="archive-toolbar__actions">
            <button type="button" class="action-button" @click="emit('create-draft')">
              新建长者档案
            </button>
            <button type="button" class="action-button action-button--ghost" @click="emit('refresh')">
              刷新工作台
            </button>
          </div>
          <span class="toolbar-hint">
            {{
              dataSource === "mock"
                ? "当前为显式 mock 兜底，elder-service 恢复后会回切真实接口。"
                : "已接入 elder-service create/list/get 最小链路。"
            }}
          </span>
        </div>

        <form class="archive-filters" @submit.prevent="emit('apply-filters')">
          <label>
            搜索
            <input
              :value="filters.search"
              type="search"
              placeholder="姓名 / 档案编号"
              @input="emit('update:filters', { search: $event.target.value })"
            />
          </label>
          <label>
            风险等级
            <select :value="filters.riskLevel" @change="emit('update:filters', { riskLevel: $event.target.value })">
              <option value="">全部</option>
              <option value="low">低风险</option>
              <option value="medium">中风险</option>
              <option value="high">高风险</option>
            </select>
          </label>
          <label>
            入住状态
            <select
              :value="filters.checkInStatus"
              @change="emit('update:filters', { checkInStatus: $event.target.value })"
            >
              <option value="">全部</option>
              <option value="pre_admission">待入住</option>
              <option value="checked_in">已入住</option>
              <option value="discharged">已离院</option>
            </select>
          </label>
          <div class="archive-filters__actions">
            <button type="submit" class="action-button action-button--small">应用筛选</button>
            <button type="button" class="action-button action-button--ghost action-button--small" @click="emit('reset-filters')">
              重置
            </button>
          </div>
        </form>

        <p v-if="syncWarning" class="info-banner info-banner--warning">{{ syncWarning }}</p>
        <p v-if="errorMessage" class="info-banner info-banner--danger">{{ errorMessage }}</p>
        <p v-if="loading" class="info-banner">正在同步长者档案...</p>
        <p v-if="!loading" class="toolbar-hint">当前共 {{ pagination.total }} 条档案，默认展示首批可联调数据。</p>

        <p v-if="!loading && elders.length === 0" class="empty-state">当前没有长者档案数据。</p>

        <ul class="archive-list">
          <li
            v-for="elder in elders"
            :key="elder.elderId"
            class="archive-row"
            :class="{ 'is-active': elder.elderId === selectedElderId }"
            @click="emit('select-elder', elder.elderId)"
          >
            <div>
              <strong>{{ elder.fullName }}</strong>
              <p>{{ elder.elderCode }} · {{ elder.gender }} · {{ elder.age }} 岁</p>
            </div>
            <div class="archive-row__meta">
              <span class="tag tag-p2">{{ elder.riskLevel }}</span>
              <span class="archive-row__status">{{ elder.status }}</span>
            </div>
          </li>
        </ul>
      </SectionCard>

      <SectionCard title="档案收口面板" description="根据首批任务包同步呈现档案、家属和入住信息。">
        <div v-if="selectedElder" class="detail-grid">
          <div>
            <span class="detail-label">长者姓名</span>
            <strong>{{ selectedElder.fullName }}</strong>
            <small>{{ selectedElder.gender }} · {{ selectedElder.age }} 岁</small>
          </div>
          <div>
            <span class="detail-label">档案编号</span>
            <strong>{{ selectedElder.elderCode }}</strong>
            <small>{{ selectedElder.elderId }}</small>
          </div>
          <div>
            <span class="detail-label">风险等级</span>
            <strong>{{ selectedElder.riskLevel }}</strong>
            <small>{{ selectedElder.status }}</small>
          </div>
          <div>
            <span class="detail-label">站点 / 站点编码</span>
            <strong>{{ selectedElder.station }}</strong>
            <small>{{ selectedElder.stationId || "待补充" }}</small>
          </div>
          <div>
            <span class="detail-label">房间 / 床位</span>
            <strong>{{ selectedElder.room }}</strong>
            <small>{{ selectedElder.bed }}</small>
          </div>
          <div>
            <span class="detail-label">入住日期</span>
            <strong>{{ selectedElder.checkInDate }}</strong>
            <small>{{ selectedElder.note }}</small>
          </div>
          <div>
            <span class="detail-label">主联系人</span>
            <strong>{{ selectedElder.family }}</strong>
            <small>{{ selectedElder.familyRelation }}</small>
          </div>
          <div>
            <span class="detail-label">长者电话</span>
            <strong>{{ selectedElder.phone }}</strong>
          </div>
          <div>
            <span class="detail-label">家属电话</span>
            <strong>{{ selectedElder.familyPhone }}</strong>
          </div>
        </div>
        <div v-else class="empty-state">
          当前还没有选中长者。
          工作台仍会保留“档案、家属、入住、房间床位、风险等级”的首批字段结构，方便继续联调。
        </div>
      </SectionCard>
    </section>

    <section class="content-grid">
      <SectionCard title="当前工作说明" description="明确首批纳入与暂不纳入的业务边界。">
        <div class="stack">
          <div class="detail-panel detail-panel--compact">
            <h3>本页已覆盖</h3>
            <ul class="workbench-points">
              <li v-for="item in businessScope" :key="item">{{ item }}</li>
            </ul>
          </div>
          <div class="detail-panel detail-panel--compact">
            <h3>本期暂不纳入</h3>
            <ul class="workbench-points">
              <li v-for="item in futureScope" :key="item">{{ item }}</li>
            </ul>
          </div>
        </div>
      </SectionCard>

      <SectionCard title="联调目标" description="收口首批真实业务闭环，而不是一次性做完整入住系统。">
        <ul class="workbench-points">
          <li>创建长者档案功能，前后端集成打通</li>
          <li>查询长者档案功能，前后端集成打通</li>
          <li>记录入住基础信息功能，前后端集成打通</li>
          <li>关联床位和家属关系，前后端集成打通</li>
        </ul>
      </SectionCard>
    </section>
  </section>
</template>
