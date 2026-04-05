<script setup>
import { computed } from "vue";

const emit = defineEmits(["back"]);

const props = defineProps({
  elder: {
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

const familyContacts = computed(() => (Array.isArray(props.elder?.familyContacts) ? props.elder.familyContacts : []));

const staySteps = computed(() => [
  { label: "档案建档", state: props.elder ? "已完成" : "待建档" },
  {
    label: "家属关联",
    state: props.elder?.family && props.elder.family !== "待补充" ? "已完成" : "待补充",
  },
  {
    label: "入住信息",
    state: props.elder?.checkInDate && props.elder.checkInDate !== "待安排" ? "已登记" : "待登记",
  },
  {
    label: "床位分配",
    state: props.elder?.bed && props.elder.bed !== "待安排" ? "已分配" : "待分配",
  },
]);

const reservedCapabilities = ["合同信息", "费用账单", "护理计划", "审批流", "消息通知优先级"];
</script>

<template>
  <section class="page-stack">
    <article class="detail-hero">
      <div>
        <p class="eyebrow">长者详情</p>
        <h2>{{ elder?.fullName || "长者详情待加载" }}</h2>
        <p class="summary">
          {{
            elder
              ? `${elder.elderCode} · ${elder.gender} · ${elder.age} 岁 · ${elder.status}`
              : "点击档案列表后会通过 elder-service 获取详情。"
          }}
        </p>
      </div>
      <div class="detail-hero__tags">
        <span class="pill pill-accent">{{ elder?.riskLevel || "待补充" }}</span>
        <span class="pill">{{ dataSource === "mock" ? "Mock Fallback" : "elder-service" }}</span>
        <span class="pill">家属关系</span>
      </div>
    </article>

    <div class="inline-actions">
      <button type="button" class="action-button action-button--ghost" @click="emit('back')">
        返回档案列表
      </button>
    </div>

    <p v-if="syncWarning" class="info-banner info-banner--warning">{{ syncWarning }}</p>
    <p v-if="errorMessage" class="info-banner info-banner--danger">{{ errorMessage }}</p>
    <p v-if="loading" class="info-banner">正在获取长者详情...</p>

    <section v-if="elder" class="content-grid">
      <article class="detail-panel">
        <h3>基础信息</h3>
        <dl class="detail-dl">
          <div>
            <dt>档案编号</dt>
            <dd>{{ elder.elderCode }}</dd>
          </div>
          <div>
            <dt>站点编码</dt>
            <dd>{{ elder.stationId || elder.station }}</dd>
          </div>
          <div>
            <dt>风险等级</dt>
            <dd>{{ elder.riskLevel }}</dd>
          </div>
          <div>
            <dt>联系电话</dt>
            <dd>{{ elder.phone }}</dd>
          </div>
          <div>
            <dt>身份证号</dt>
            <dd>{{ elder.idCard }}</dd>
          </div>
          <div>
            <dt>出生日期</dt>
            <dd>{{ elder.birthDate }}</dd>
          </div>
        </dl>
      </article>

      <article class="detail-panel">
        <h3>入住信息</h3>
        <dl class="detail-dl">
          <div>
            <dt>当前状态</dt>
            <dd>{{ elder.status }}</dd>
          </div>
          <div>
            <dt>入住时间</dt>
            <dd>{{ elder.checkInDate }}</dd>
          </div>
          <div>
            <dt>房间</dt>
            <dd>{{ elder.room }}</dd>
          </div>
          <div>
            <dt>床位</dt>
            <dd>{{ elder.bed }}</dd>
          </div>
          <div>
            <dt>站点名称</dt>
            <dd>{{ elder.station }}</dd>
          </div>
          <div>
            <dt>备注</dt>
            <dd>{{ elder.note }}</dd>
          </div>
        </dl>
      </article>
    </section>

    <section v-if="elder" class="content-grid">
      <article class="detail-panel">
        <h3>家属关系</h3>
        <dl class="detail-dl">
          <div>
            <dt>家属姓名</dt>
            <dd>{{ elder.family }}</dd>
          </div>
          <div>
            <dt>关系</dt>
            <dd>{{ elder.familyRelation }}</dd>
          </div>
          <div>
            <dt>联系电话</dt>
            <dd>{{ elder.familyPhone }}</dd>
          </div>
          <div>
            <dt>联系人数量</dt>
            <dd>{{ familyContacts.length || 1 }}</dd>
          </div>
        </dl>

        <ul v-if="familyContacts.length" class="contact-list">
          <li v-for="contact in familyContacts" :key="`${contact.family_name}-${contact.phone}`" class="contact-list__item">
            <strong>{{ contact.family_name }}</strong>
            <p>{{ contact.relation_type }} · {{ contact.phone }}</p>
          </li>
        </ul>
      </article>

      <article class="detail-panel">
        <h3>入住办理进度</h3>
        <ul class="timeline">
          <li v-for="(step, index) in staySteps" :key="step.label" class="timeline-item">
            <span class="timeline-index">{{ index + 1 }}</span>
            <div>
              <strong>{{ step.label }}</strong>
              <p>{{ step.state }}</p>
            </div>
            <span class="tag tag-p2">{{ step.state }}</span>
          </li>
        </ul>
      </article>
    </section>

    <section v-if="elder" class="content-grid">
      <article class="detail-panel">
        <h3>二期扩展预留</h3>
        <div class="reserve-grid">
          <div v-for="item in reservedCapabilities" :key="item" class="reserve-grid__item">
            <strong>{{ item }}</strong>
            <p>当前页面只预留信息位与结构，不提前做重业务流程。</p>
          </div>
        </div>
      </article>

      <article class="detail-panel detail-panel--accent">
        <h3>首批验收对照</h3>
        <ul class="workbench-points">
          <li>支持从列表进入长者详情查看页</li>
          <li>展示长者基础档案、风险等级和状态</li>
          <li>展示家属关系、主联系人与电话</li>
          <li>展示入住信息、房间与床位关联</li>
        </ul>
      </article>
    </section>

    <article v-else class="detail-panel">
      <h3>暂无详情</h3>
      <p class="summary">当前未选中长者，或详情接口尚未返回。</p>
    </article>
  </section>
</template>
