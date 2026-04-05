<script setup>
const emit = defineEmits(["back"]);

defineProps({
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
            <dt>入住时间</dt>
            <dd>{{ elder.checkInDate }}</dd>
          </div>
          <div>
            <dt>床位</dt>
            <dd>{{ elder.bed }}</dd>
          </div>
          <div>
            <dt>风险等级</dt>
            <dd>{{ elder.riskLevel }}</dd>
          </div>
        </dl>
      </article>

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
            <dt>备注</dt>
            <dd>{{ elder.note }}</dd>
          </div>
        </dl>
      </article>
    </section>

    <article v-else class="detail-panel">
      <h3>暂无详情</h3>
      <p class="summary">当前未选中长者，或详情接口尚未返回。</p>
    </article>
  </section>
</template>
